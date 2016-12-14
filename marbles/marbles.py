'''Extends :mod:`unittest` functionality by augmenting the way failed
assertions are handled to provide more actionable failure information
to the test consumer.

Briefly, by inheriting from :class:`marbles.AnnotatedTestCase` rather
than :class:`unittest.TestCase`, the test author gains the ability to
provide richer failure messages in their assert statements. These
messages can be format strings which are expanded using local
variables defined within the test itself. The inclusion of this
additional information is enforced within the class.
'''

import ast
import collections.abc
import functools
import inspect
import itertools
import linecache
import sys
import textwrap
import traceback
import unittest


class _StatementFinder(ast.NodeVisitor):
    '''Finds the line of the statement containing a target line.

    For reasons passing understanding, :meth:`ast.walk` traverses the
    tree in breadth-first order rather than depth-first. In order to
    traverse depth-first (which we want), you have to implement a
    :class:`ast.NodeVisitor`.

    Startlingly, :meth:`ast.walk`'s documentation says that it traverses
    "in no particular order". While I respect the decision to document
    the fact that the order should not be relied on as it might change
    in the future, to claim that it traverses "in no particular order"
    is simply a lie.

    In any case, this visitor will traverse the tree, and when it finds
    a node on the target line, it sets ``self.found`` to the line number
    of the innermost ancestor which is a Statement.

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


class AnnotatedAssertionError(AssertionError):
    '''AnnotatedAssertionError is an :class:`AssertionError` that
    expects a dictionary or tuple of additionional information beyond
    the static message string accepted by :class:`AssertionError`.

    The additional information provided is formatted with the context
    of the locals where the assertion error is raised. Annotated
    assertions expect an 'advice' key describing what to do if/when
    the assertion fails.

    See :class:`marbles.AnnotatedTestCase` for example usage. To make
    annotated assertions in your tests, your tests should inherit from
    :class:`marbles.AnnotatedTestCase` instead of
    :class:`unittest.TestCase`.
    '''

    _META_FORMAT_STRING = '''{standardMsg}

Source:
{assert_stmt}
Locals:
{locals}
Advice:
{advice}
    '''
    REQUIRED_KEYS = ['advice']
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

        Annotation is a dictionary containing at least the key
        'advice'. See the documentation for :class:`AnnotatedTestCase`
        to see what the user API looks like.

        ``advice``
            This string is meant to inform the test consumer of what
            to do when the test fails. It can contain format string
            directives that will be formatted with local variables
            defined within the test itself.
        '''
        # These attributes are publicly exposed as properties below to
        # facilitate programmatic interactions with test failures
        # (e.g., aggregating and formatting output into a consolidated
        # report)
        annotation, standardMsg = args[0]
        locals_, filename, linenumber = self._get_stack_info()

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
        setattr(self, '_filename', filename)
        setattr(self, '_linenumber', linenumber)

        super(AnnotatedAssertionError, self).__init__(self.formattedMsg)

    @property
    def advice(self):
        formatted_advice = self._advice.format(**self.locals)
        return textwrap.fill(formatted_advice, width=72,
                             break_long_words=False, initial_indent='\t',
                             subsequent_indent='\t')

    @property
    def locals(self):
        return self._locals

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
        line_range, lineno = self._find_assert_stmt(self.filename,
                                                    self.linenumber)
        source = [linecache.getline(self.filename, x) for x in line_range]

        # Dedent the source, removing the final newline added by dedent
        dedented_lines = textwrap.dedent(''.join(source)).split('\n')[:-1]

        formatted_lines = []
        for i, line in zip(line_range, dedented_lines):
            prefix = '>' if i == lineno else ' '
            formatted_lines.append(' {0} {1:4d} {2}'.format(prefix, i, line))

        return '\n'.join(formatted_lines)

    @property
    def formattedMsg(self):  # mimic unittest's name for standardMsg
        return self._META_FORMAT_STRING.format(
            standardMsg=self.standardMsg, assert_stmt=self.assert_stmt,
            advice=self.advice, locals=self._format_locals(self.locals))

    @classmethod
    def _format_locals(cls, locals_):
        locals_ = {k: v for k, v in locals_.items()
                   if k not in cls._IGNORE_LOCALS and not k.startswith('_')}
        return '\n'.join('\t{0}={1}'.format(k, v) for k, v in locals_.items())

    @staticmethod
    def _get_stack_info():
        '''Capture locals, filename, and line number from the stacktrace
        to provide the source of the assertion error and formatted
        advice.
        '''
        tb = traceback.walk_stack(sys._getframe().f_back)
        stack = traceback.StackSummary.extract(tb, capture_locals=True)

        # We want locals from the test definition (which always begins
        # with 'test_' in unittest), which will be at a different
        # level in the stack depending on how many tests are in each
        # test case, how many test cases there are, etc.

        # The branch where we exhaust this loop is not covered
        # because we always find a test.
        for frame in stack:  # pragma: no branch
            if frame.name.startswith('test_'):
                return frame.locals.copy(), frame.filename, frame.lineno

    @staticmethod
    def _find_assert_stmt(filename, linenumber, leading=1, following=2):
        '''Given a Python filename and line number, find the lines that
        are a part of the statement containing that line.

        Python stacktraces, when reporting which line they're on, always
        show the last line of the statement. This can be confusing if
        the statement spans multiple lines. This function helps
        reconstruct the whole statement, and is used by
        :meth:`marbles.AnnotatedAssertionError.assert_stmt`.

        Returns a tuple of the range of lines spanned by the source
        being returned, the number of the line on which the interesting
        statement starts.
        '''
        _source = ''.join(linecache.getlines(filename))
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

    def __init__(self, case, msg, advice):
        self._case = case
        self._msg = msg
        self._advice = advice

    @staticmethod
    def _validate_annotation(annotation):
        '''Ensures that the annotation has the right fields.'''
        required = set(AnnotatedAssertionError.REQUIRED_KEYS)
        present = set(key for key, val in annotation.items() if val)
        missing = required.difference(present)
        if missing:
            error = 'Annotation missing required fields: {0}'.format(missing)
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


def _find_msg_argument(signature):
    '''Locates the msg argument in a function signature.

    We need to determine where we expect to find msg if it's passed
    positionally, so we can extract it if the user passed it.

    :returns: The index of the ``msg`` param, the default value for
        it, and the number of non-``msg`` positional parameters we
        expect.
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

    :returns: The found ``msg``, the args and kwargs with that ``msg``
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


class AnnotatedTestCase(unittest.TestCase):
    '''AnnotatedTestCase is an extension of :class:`unittest.TestCase`.

    When writing a test class based on :class:`AnnotatedTestCase`, all
    assert statements like :meth:`unittest.TestCase.assertEqual`, in
    addition to accepting an optional final string parameter ``msg``,
    expect a keyword parameter ``advice``, which should describe what
    steps should be taken when the test fails.

    The advice string (and the ``msg`` parameter, if provided) are
    formatted with :meth:`str.format` given the local variables
    defined within the test itself. Every assertion checks to make
    sure both message and advice are provided, and if not, raises an
    :class:`AnnotationError`.

    Example:

    .. code-block:: py

        import os
        import re

        from marbles import AnnotatedTestCase

        class ExampleTestCase(AnnotatedTestCase):

            def test_filename_pattern(self):
                expected = '^file_[0-9]{8}$'
                actual = os.path.splitext('file_2016_01_01.py')[0]

                advice = ('Determine if this is a one-off error or if the file naming '
                          'pattern has changed. If the file naming pattern has changed, '
                          'consider updating this test.')
                self.assertRegex(actual, expected, advice=advice)

    '''  # noqa: E501

    failureException = AnnotatedAssertionError

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

            with AnnotationContext(self, msg, advice) as annotation:
                if rem_args:
                    return attr(*args, annotation, *rem_args, **kwargs)
                return attr(*args, msg=annotation, **kwargs)
        return wrapper

    def __wrap_fail(self, attr):
        signature = inspect.signature(attr)
        msg_idx, default_msg, non_msg_params = _find_msg_argument(signature)

        # For TestCase.fail, we're not going to call _formatMessage,
        # so we need to call the real TestCase.fail function with the
        # thing we want passed to AnnotatedAssertionError. Thus, we
        # extract msg and advice as usual, but when we call the
        # wrapped function, we do what our _formatMessage would do and
        # pass the tuple directly.
        @functools.wraps(attr)
        def wrapper(*args, **kwargs):
            msg, args, rem_args, kwargs = _extract_msg(
                args, kwargs, msg_idx, default_msg, non_msg_params)
            # TestCase.fail doesn't have args after msg
            assert len(rem_args) == 0

            advice = kwargs.pop('advice', None)

            with AnnotationContext(self, msg, advice) as annotation:
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
        args in AnnotatedAssertionError.__init__, and you should watch
        out for backwards compatibility with existing usage.
        '''
        attr = object.__getattribute__(self, key)

        if callable(attr) and key.startswith('assert'):
            attr = self.__wrap_assertion(attr)
        elif callable(attr) and key == 'fail':
            attr = self.__wrap_fail(attr)

        return attr
