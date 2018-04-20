#
#       Copyright (c) 2017 Two Sigma Investments, LP
#       All Rights Reserved
#
#       THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE OF
#       Two Sigma Investments, LP.
#
#       The copyright notice above does not evidence any
#       actual or intended publication of such source code.
#

'''Extends :mod:`unittest` to provide more information to the test
consumer on test failure.

A :class:`marbles.TestCase` can be used anywhere a
:class:`unittest.TestCase` is used. By simply inheriting from
:class:`marbles.TestCase` instead, test failures will have better
error messages that include the full assertion statement highlighting
the error and any local variables defined within the test at the time
it failed. All assertion methods on a :class:`marbles.TestCase` accept
an additional ``advice`` annotation which complements the traditional
``msg`` parameter, containing additional information about the test
that will be exposed to the test consumer on test failure. This
annotation can be a format string that will be expanded with local
variables that are defined at the time the test fails.

The :class:`marbles.AnnotatedTestCase` goes one step further than the
:class:`marbles.TestCase` and requires the test author to provide an
advice annotation. Calling an assertion in this context without the
``advice`` parameter produces an error.
'''

import ast
import collections.abc
import functools
import inspect
import itertools
import linecache
import logging
import re
import sys
import textwrap
import unittest

from . import log
from . import _stack


_log = logging.getLogger(__name__)


# We subclass TextWrapper (instead of just writing a wrap()
# function) because we ultimately use TextWrapper.fill() to
# return the advice as a wrapped string.
class _AdviceWrapper(textwrap.TextWrapper):

    def wrap(self, text, **kwargs):
        '''Wraps each paragraph in ``text`` individually.

        Parameters
        ----------
        text : str

        Returns
        -------
        str
            Single string containing the wrapped paragraphs.
        '''
        pilcrow = re.compile(r'(\n\s*\n)', re.MULTILINE)
        list_prefix = re.compile(r'\s*(?:\w|[0-9]+)[\.\)]\s+')

        paragraphs = pilcrow.split(text)
        wrapped_lines = []
        for paragraph in paragraphs:
            if paragraph.isspace():
                wrapped_lines.append('')
            else:
                wrapper = textwrap.TextWrapper(**vars(self))
                list_item = re.match(list_prefix, paragraph)
                if list_item:
                    wrapper.subsequent_indent += ' ' * len(list_item.group(0))
                wrapped_lines.extend(wrapper.wrap(paragraph))

        return wrapped_lines


class _StatementFinder(ast.NodeVisitor):
    '''Finds the line of the statement containing a target line.

    For reasons passing understanding, :meth:`ast.walk` traverses the
    tree in breadth-first order rather than depth-first. In order to
    traverse depth-first (which we want), you have to implement a
    :class:`ast.NodeVisitor`.

    Startlingly, :meth:`ast.walk`'s documentation says that it
    traverses "in no particular order". While I respect the decision
    to document the fact that the order should not be relied on as it
    might change in the future, to claim that it traverses "in no
    particular order" is simply a lie.

    In any case, this visitor will traverse the tree, and when it finds
    a node on the target line, it sets ``self.found`` to the line
    number of the innermost ancestor which is a Statement.

    Example::

        finder = _StatementFinder(target_linenumber)
        finder.visit(tree)
        containing_statement_linenumber = finder.found
    '''

    def __init__(self, target):
        self.target = target
        self.stack = []
        self.found = None

    @property
    def current_stmt(self):
        return self.stack[-1]

    def visit(self, node):
        lineno = getattr(node, 'lineno', None)
        if lineno == self.target and self.found is None:
            if isinstance(node, ast.stmt):
                self.found = node.lineno
            else:
                self.found = self.current_stmt.lineno

        if isinstance(node, ast.stmt):
            self.stack.append(node)
            try:
                self.generic_visit(node)
            finally:
                self.stack.pop()
        else:
            self.generic_visit(node)


class AnnotationError(Exception):
    '''Raised when there is a problem with the way an assertion was
    annotated.
    '''
    pass


class ContextualAssertionError(AssertionError):
    '''ContextualAssertionError is an :class:`AssertionError` that
    expects a dictionary or tuple of additionional information beyond
    the static message string accepted by :class:`AssertionError`.

    The additional information provided is formatted with the context
    of the locals where the assertion error is raised. Annotated
    assertions may also include an 'advice' key describing what to do
    if/when the assertion fails.

    This information includes the full assertion statement highlighting
    the error and any local variables in scope at the time the test
    failed.
    '''

    _META_FORMAT_STRING = '''{standardMsg}

Source:
{assert_stmt}
Locals:
{locals}
'''
    _ADVICE_META_FORMAT_STRING = _META_FORMAT_STRING + '''Advice:
{advice}
'''
    # If msg and/or advice are declared in the test's scope and passed
    # as variables to the assert statement, instead of being declared
    # directly in the assert statement, we don't want to display them
    # in the Locals section of the test output because both the msg
    # and the advice will be displayed elsewhere in the output anyway
    _IGNORE_LOCALS = ['msg', 'advice', 'self']

    def __init__(self, *args):
        '''Assume args contains a tuple of two arguments:
            1. the annotation provided by the test author, and
            2. the "standardMsg" from :mod:`unittest` which is the
               string representation of the asserted fact that wasn't
               true

        Annotation is a dictionary containing at least the key 'advice'.
        See the documentation for :class:`AnnotatedTestCase` to see
        what the user API looks like.

        Parameters
        ----------
        advice : str
            This string is meant to inform the test consumer of what
            to do when the test fails. It can contain format string
            fields that will be formatted with local variables
            defined within the test itself.
        '''
        # These attributes are publicly exposed as properties below to
        # facilitate programmatic interactions with test failures
        # (e.g., aggregating and formatting output into a consolidated
        # report)
        annotation, standardMsg = args[0]
        locals_, module, filename, linenumber = _stack.get_stack_info()

        # When the wrapper in AnnotatedTestCase sees both msg and
        # advice, it bundles msg with advice in order to thread it
        # down the stack. So if the user was trying to override the
        # standard message, their value would actually be here.
        msg = annotation.pop('msg', None)
        if not msg:
            msg = standardMsg

        setattr(self, '_advice', annotation['advice'])
        setattr(self, 'standardMsg', msg)
        setattr(self, '_locals', locals_)
        setattr(self, '_module', module)
        setattr(self, '_filename', filename)
        setattr(self, '_linenumber', linenumber)

        super(ContextualAssertionError, self).__init__(self.formattedMsg)

    @property
    def advice(self):
        if self._advice is None:
            return None
        else:
            formatted_advice = self._advice.format(**self.locals)
            wrapper = _AdviceWrapper(width=72,
                                     break_long_words=False,
                                     initial_indent='\t',
                                     subsequent_indent='\t')
            return wrapper.fill(formatted_advice)

    @property
    def locals(self):
        '''Returns a string displaying the public (a.k.a., not internal
        or name-mangled) locals defined within the test.

        .. note:

           The public local variables ``self``, ``advice``, and
           ``msg``, if present, are excluded.
        '''
        return self._locals

    @property
    def module(self):
        return self._module

    @property
    def filename(self):
        return self._filename

    @property
    def linenumber(self):
        return self._linenumber

    @property
    def assert_stmt(self):
        '''Returns a string displaying the whole statement that failed,
        with a '>' indicator on the line starting the expression.
        '''
        # This will be used by linecache to read the source of this
        # module. See the docstring for _find_assert_stmt below which
        # explains how.
        #
        # We don't have a test for this because automating the
        # creation of an egg, installation into an environment,
        # running of tests, and verification that marbles found the
        # right source and was able to print it is a lot of
        # automation. We have tested manually, and marbles works with
        # all check installation mechanisms we know of right now
        # (setup.py install, setup.py develop, pip install, bdist_egg,
        # bdist_wheel).
        module_globals = vars(sys.modules[self.module])
        line_range, lineno = self._find_assert_stmt(
            self.filename, self.linenumber, module_globals=module_globals)
        source = [linecache.getline(self.filename, x,
                                    module_globals=module_globals)
                  for x in line_range]

        # Dedent the source, removing the final newline added by dedent
        dedented_lines = textwrap.dedent(''.join(source)).split('\n')[:-1]

        formatted_lines = []
        for i, line in zip(line_range, dedented_lines):
            prefix = '>' if i == lineno else ' '
            formatted_lines.append(' {0} {1:4d} {2}'.format(prefix, i, line))

        return '\n'.join(formatted_lines)

    @property
    def formattedMsg(self):  # mimic unittest's name for standardMsg
        if self.advice is not None:
            fmt = self._ADVICE_META_FORMAT_STRING
        else:
            fmt = self._META_FORMAT_STRING
        return fmt.format(
            standardMsg=self.standardMsg, assert_stmt=self.assert_stmt,
            advice=self.advice, locals=self._format_locals(self.locals))

    @classmethod
    def _format_locals(cls, locals_):
        locals_ = {k: v for k, v in locals_.items()
                   if k not in cls._IGNORE_LOCALS and not k.startswith('_')}
        return '\n'.join('\t{0}={1}'.format(k, v) for k, v in locals_.items())

    @staticmethod
    def _find_assert_stmt(filename, linenumber, leading=1, following=2,
                          module_globals=None):
        '''Given a Python module name, filename and line number, find
        the lines that are part of the statement containing that line.

        Python stacktraces, when reporting which line they're on, always
        show the last line of the statement. This can be confusing if
        the statement spans multiple lines. This function helps
        reconstruct the whole statement, and is used by
        :meth:`marbles.ContextualAssertionError.assert_stmt`.

        Returns a tuple of the range of lines spanned by the source
        being returned, the number of the line on which the interesting
        statement starts.

        We may need the ``module_globals`` in order to tell
        :mod:`linecache` how to find the file, if it comes from inside
        an egg. In that case, ``module_globals`` should contain a key
        ``__loader__`` which knows how to read from that file.
        '''
        lines = linecache.getlines(
            filename, module_globals=module_globals)
        _source = ''.join(lines)
        _tree = ast.parse(_source)

        finder = _StatementFinder(linenumber)
        finder.visit(_tree)
        line_range = range(finder.found - leading, linenumber + following)
        return line_range, finder.found


class AnnotationContext(object):
    '''Validates and packs msg and advice, and stashes advice for use
    down the stack.

    Within this context manager, if another assertion is called
    without passing advice, we use the advice from the earlier call
    rather than raising an error about missing advice. This allows
    e.g. :meth:`unittest.TestCase.assertMultiLineEqual` to make some
    additional assertions and pass its own msg without advice, without
    causing an error there.
    '''

    def __init__(self, case, assertion, required_keys,
                 msg, advice, args, kwargs):
        setattr(self, '_case', case)
        setattr(self, '_assertion', assertion)
        setattr(self, '_required_keys', required_keys)
        setattr(self, '_msg', msg)
        setattr(self, '_advice', advice)
        setattr(self, '_args', args)
        setattr(self, '_kwargs', kwargs)

    def _validate_annotation(self, annotation):
        '''Ensures that the annotation has the right fields.'''
        required_keys = set(self._required_keys)
        keys = set(key for key, val in annotation.items() if val)
        missing_keys = required_keys.difference(keys)
        if missing_keys:
            error = 'Annotation missing required fields: {0}'.format(
                missing_keys)
            raise AnnotationError(error)

    def __enter__(self):
        current_advice = getattr(self._case, '__current_advice', None)
        advice = self._advice or current_advice
        if isinstance(self._msg, collections.abc.Mapping):
            annotation = self._msg
        else:
            annotation = {'msg': self._msg, 'advice': advice}
        if not current_advice:
            self._validate_annotation(annotation)
        setattr(self, '_old_advice', current_advice)
        setattr(self._case, '__current_advice', advice)
        return annotation

    def __exit__(self, *exc_info):
        setattr(self._case, '__current_advice', self._old_advice)
        if self._old_advice is None:
            try:
                log.logger._log_assertion(self._case, self._assertion,
                                          self._args, self._kwargs, self._msg,
                                          self._advice, *exc_info)
            except Exception:
                _log.exception('Failed to log assertion')


def _find_msg_argument(signature):
    '''Locates the msg argument in a function signature.

    We need to determine where we expect to find msg if it's passed
    positionally, so we can extract it if the user passed it.

    Returns
    -------
    tuple
        The index of the ``msg`` param, the default value for it,
        and the number of non-``msg`` positional parameters we expect.
    '''
    names = signature.parameters.keys()
    try:
        msg_idx = list(names).index('msg')
        default_msg = signature.parameters['msg'].default
    except ValueError:  # 'msg' is not in list
        # It's likely that this is a custom assertion that's just
        # passing all remaining args and kwargs through
        # (e.g. tests.marbles.ReversingTestCaseMixin). Unfortunately,
        # we can't inspect its code to find the assert it's wrapping,
        # so we just have to assume it's of the standard form with msg
        # in the last position with a default of None.
        msg_idx = -1
        default_msg = None

    # We also don't want to steal any actually positional arguments if
    # we can help it. Therefore, we leave the default msg if there are
    # fewer than this many args passed. We stop counting at a
    # parameter named 'msg' or when we hit a varargs or keyword-only
    # parameter. See
    # https://gitlab.twosigma.com/jane/marbles/issues/10.
    kinds = (inspect.Parameter.POSITIONAL_ONLY,
             inspect.Parameter.POSITIONAL_OR_KEYWORD)
    non_msg_params = itertools.takewhile(
        lambda param: param.name != 'msg' and param.kind in kinds,
        signature.parameters.values())
    non_msg_params = sum(1 for _ in non_msg_params)
    return msg_idx, default_msg, non_msg_params


def _extract_msg(args, kwargs, msg_idx, default_msg, non_msg_params):
    '''Extracts the msg argument from the passed args.

    Returns
    -------
    tuple
        The found ``msg``, the args and kwargs with that ``msg``
        removed, and any remaining positional args after ``msg``.
    '''
    rem_args = []
    if 'msg' in kwargs:
        msg = kwargs.pop('msg')
    elif len(args) > non_msg_params and msg_idx < len(args):
        msg = args[msg_idx]
        if 0 <= msg_idx:
            rem_args = args[msg_idx + 1:]
        args = args[:msg_idx]
    else:
        msg = default_msg
    return msg, args, rem_args, kwargs


class TestCase(unittest.TestCase):
    '''The marbles TestCase is an extension of :class:`unittest.TestCase`.

    When writing a test class based on
    :class:`marbles.AnnotatedTestCase`, all assert statements, e.g.
    :meth:`unittest.TestCase.assertEqual`, in addition to accepting an
    optional final string parameter ``msg``, also accept a keyword
    parameter ``advice``, which should provide more context about the
    test and describe what to do if/when the test fails.

    The advice string (and the ``msg`` parameter, if provided) are
    formatted with :meth:`str.format` given the local variables
    defined within the test itself.

    Example:

    .. literalinclude:: ../examples/sla.py
    '''

    failureException = ContextualAssertionError

    _REQUIRED_KEYS = []

    def _formatMessage(self, msg, standardMsg):
        return (msg, standardMsg)

    def __wrap_assertion(self, attr):
        signature = inspect.signature(attr)
        msg_idx, default_msg, non_msg_params = _find_msg_argument(signature)

        @functools.wraps(attr)
        def wrapper(*args, **kwargs):
            msg, args, rem_args, kwargs = _extract_msg(
                args, kwargs, msg_idx, default_msg, non_msg_params)

            advice = kwargs.pop('advice', None)

            with AnnotationContext(
                    self, attr, self._REQUIRED_KEYS, msg, advice,
                    list(args) + list(rem_args), kwargs) as annotation:
                if rem_args:
                    return attr(*args, annotation, *rem_args, **kwargs)
                return attr(*args, msg=annotation, **kwargs)
        return wrapper

    def __wrap_fail(self, attr):
        signature = inspect.signature(attr)
        msg_idx, default_msg, non_msg_params = _find_msg_argument(signature)

        # For TestCase.fail, we're not going to call _formatMessage,
        # so we need to call the real TestCase.fail function with the
        # thing we want passed to ContextualAssertionError. Thus, we
        # extract msg and advice as usual, but when we call the
        # wrapped function, we do what our _formatMessage would do and
        # pass the tuple directly.
        @functools.wraps(attr)
        def wrapper(*args, **kwargs):
            msg, args, rem_args, kwargs = _extract_msg(
                args, kwargs, msg_idx, default_msg, non_msg_params)
            # TestCase.fail doesn't have args after msg
            if rem_args:
                raise ValueError(
                    'TestCase.fail() received extra args: {}'.format(rem_args)
                )

            advice = kwargs.pop('advice', None)

            with AnnotationContext(
                    self, attr, self._REQUIRED_KEYS, msg, advice,
                    list(args) + list(rem_args), kwargs) as annotation:
                # Some builtin assertions (like assertIsNotNone)
                # have already called _formatMessage and pass that
                # to TestCase.fail, so if what we get is already a
                # tuple, we just pass it along.
                if isinstance(msg, tuple):
                    return attr(*args, msg=msg, **kwargs)
                packed_msg = self._formatMessage(annotation, msg)
                return attr(*args, msg=packed_msg, **kwargs)
        return wrapper

    def __getattribute__(self, key):
        '''Keyword argument support for assertions.

        We want AnnotatedTestCases to be able to call assertions with
        syntax like this:

            self.assertTrue(True, msg='message', advice='advice')
            self.assertTrue(True, 'message', advice='advice')

        To do so, we override __getattribute__ so that any method that
        gets looked up and starts with 'assert' gets wrapped so that
        it does what we want. We override __getattribute__ rather than
        __getattr__ because __getattr__ doesn't get called when the
        method just exists.

        To add other keyword arguments in the future, you have to make
        sure that the way the underlying assertion gets called is
        going to work with _formatMessage above, and the unpacking of
        args in ContextualAssertionError.__init__, and you should watch
        out for backwards compatibility with existing usage.
        '''
        attr = object.__getattribute__(self, key)

        if callable(attr) and key.startswith('assert'):
            attr = self.__wrap_assertion(attr)
        elif callable(attr) and key == 'fail':
            attr = self.__wrap_fail(attr)

        return attr


class AnnotatedTestCase(TestCase):
    '''AnnotatedTestCase is an extension of :class:`marbles.TestCase`.

    An :class:`~marbles.AnnotatedTestCase` is only different from a
    :class:`marbles.TestCase` in that it enforces that advice is
    provided for every assertion.

    For other details, see :class:`marbles.TestCase`.

    Assertion methods on this TestCase may raise
    :class:`AnnotationError`. Every assertion checks to make sure that
    both message and advice are provided and raises that error if not.
    '''

    _REQUIRED_KEYS = ['advice']
