#
#  Copyright (c) 2018 Two Sigma Open Source, LLC
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#

''':mod:`~marbles.core.marbles` can log information about each
assertion called.

If configured, the :data:`marbles.core.log.logger` will log a json
object for each assertion and its success or failure, as well as any
other attributes of interest specified by the test author.

The captured information includes the assertion's args and kwargs,
msg, note, local variables (for failed assertions, and also for
passing assertions if verbose logging is turned on), and the result of
the assertion.

Configuration is handled via the environment variables
:envvar:`MARBLES_LOGFILE`, :envvar:`MARBLES_TEST_CASE_ATTRS`,
:envvar:`MARBLES_TEST_CASE_ATTRS_VERBOSE`,
:envvar:`MARBLES_LOG_VERBOSE`, or via the
:meth:`AssertionLogger.configure` method. Environment variables
override those set with the :meth:`~AssertionLogger.configure` method,
so if a :mod:`marbles` program configures these programmatically, they
can always be overridden without changing the program.

Note that :class:`AssertionLogger` should not be instantiated
directly; instead, test authors should import and configure the
:data:`marbles.core.log.logger` as needed.
'''

import datetime
import inspect
import json
import os

from . import _stack
from . import __version__


# XXX(leif): I don't think it's worth the gymnastics it would take to
#            test this function. We do test whether mixins are
#            identified but catching all the cases here would be a
#            lot.
def _class_defining_method(meth):  # pragma: no cover
    '''Gets the name of the class that defines meth.

    Adapted from
    http://stackoverflow.com/questions/3589311/get-defining-class-of-unbound-method-object-in-python-3/25959545#25959545.
    '''
    if inspect.ismethod(meth):
        for cls in inspect.getmro(meth.__self__.__class__):
            if cls.__dict__.get(meth.__name__) is meth:
                return '{}.{}'.format(cls.__module__, cls.__name__)
        meth = meth.__func__
    if inspect.isfunction(meth):
        module = meth.__qualname__.split('.<locals>', 1)[0]
        cls = getattr(inspect.getmodule(meth), module.rsplit('.', 1)[0])
        if isinstance(cls, type):
            return '{}.{}'.format(cls.__module__, cls.__name__)


class AssertionLogger(object):
    '''The :class:`AssertionLogger` logs json about each assertion.

    This module exposes a single :class:`AssertionLogger`,
    :data:`marbles.core.log.logger`, that is used during a marbles test
    run. It can be configured with :meth:`configure` before running
    the tests or via environment variables.

    Example:

    .. code-block:: py

       import marbles.core
       from marbles.core import log

       if __name__ == '__main__':
           log.logger.configure(logfile='/path/to/marbles.log',
                                attrs=['filename', 'date'])
           marbles.core.main()
    '''

    def __init__(self):
        self._logfile = None
        self._logfilename = None
        self._verbose = False
        self._attrs = None
        self._verbose_attrs = None

    @staticmethod
    def _open_if_needed(filename):
        if isinstance(filename, (str, bytes)):
            return open(filename, 'w')
        else:
            # Assume is already file-like
            return filename

    def configure(self, **kwargs):
        '''Configure what assertion logging is done.

        Settings configured with this method are overridden by
        environment variables.

        Parameters
        ----------
        logfile : str or bytes or file object
            If a string or bytes object, we write to that filename.
            If an open file object, we just write to it. If None,
            disable logging. If we open the file, we open it in
            ``'w'`` mode, so any contents will be overwritten.
        attrs : list of str
            Capture these attributes on the TestCase being run when
            logging an assertion. For example, if you are testing
            multiple resources, make sure the resource name is a
            member of your TestCase, and configure marbles logging
            with that name. These are only captured on failure.
        verbose_attrs : list of str
            Similar to attrs, but these attrs are captured even on
            success.
        verbose : bool or list of str
            Fields (within the set {msg, note, locals}) to capture
            even when the test is successful. By default, those three
            fields are only captured on failure.
        '''
        if 'logfile' in kwargs:
            # Note that kwargs['logfile'] might be an open file
            # object, not a string. We deal with this in
            # _open_if_needed, but refactoring it so that in that case
            # it gets set on another attribute would be tricky to
            # handle the lazy opening semantics that let us override
            # it with MARBLES_LOGFILE, so instead we choose to let
            # self._logfilename do double-duty: sometimes it's a name,
            # sometimes it's sneakily a file object.
            self._logfilename = kwargs['logfile']

        if 'attrs' in kwargs:
            self._attrs = kwargs['attrs']

        if 'verbose_attrs' in kwargs:
            self._verbose_attrs = kwargs['verbose_attrs']

        if 'verbose' in kwargs:
            self._verbose = kwargs['verbose']

    @property
    def log_enabled(self):
        return self.logfile is not None

    @property
    def logfile(self):
        if self._logfile:
            return self._logfile
        if self.logfilename:
            self._logfile = self._open_if_needed(self.logfilename)
        return self._logfile

    @property
    def logfilename(self):
        return os.environ.get('MARBLES_LOGFILE', self._logfilename)

    @property
    def attrs(self):
        try:
            return os.environ['MARBLES_TEST_CASE_ATTRS'].split(',')
        except KeyError:
            return self._attrs or ()

    @property
    def verbose_attrs(self):
        try:
            return os.environ['MARBLES_TEST_CASE_ATTRS_VERBOSE'].split(',')
        except KeyError:
            return self._verbose_attrs or ()

    @property
    def verbose(self):
        verbose = os.environ.get('MARBLES_LOG_VERBOSE', self._verbose)

        verbose_attrs = ('msg', 'note', 'locals')
        if isinstance(verbose, str):
            if verbose.lower() == 'false':
                return ()
            elif verbose.lower() == 'true':
                return verbose_attrs
            else:
                return verbose.split(',')
        elif verbose is True:
            return verbose_attrs
        else:
            return verbose or ()

    def _log_assertion(self, case, assertion, args, kwargs, msg, note,
                       *exc_info):
        if not self.log_enabled:
            return

        now = datetime.datetime.now()
        locals_, module, filename, lineno = _stack.get_stack_info()
        passed = exc_info[0] is None

        doc = {
            'case': str(case),
            'test_case': case.__class__.__name__,
            'test_method': case._testMethodName,
            'module': module,
            'file': filename,
            'line': lineno,
            'assertion': assertion.__name__,
            'args': [str(a) for a in args],
            'kwargs': [{'key': k, 'value': str(v)} for k, v in kwargs.items()],
            'assertion_class': _class_defining_method(assertion),
            'marbles_version': __version__,
            '@timestamp': now.strftime('%Y-%m-%dT%H:%M:%S.%f')
        }

        verbose_elements = {
            'msg': msg,
            'note': note.format(**locals_) if note else None,
            'locals': [{'key': k, 'value': str(v)} for k, v in locals_.items()
                       if (k not in ('msg', 'note', 'self')
                           and not k.startswith('_'))]
        }
        if not passed:
            doc.update(verbose_elements)
        elif self.verbose:
            doc.update({k: v for k, v in verbose_elements.items()
                        if k in self.verbose})

        doc.update({attr: str(getattr(case, attr, None))
                    for attr in self.verbose_attrs})
        if not passed:
            doc.update({attr: str(getattr(case, attr, None))
                        for attr in self.attrs})

        if passed:
            doc['result'] = 'pass'
        else:
            doc['result'] = 'fail'

        json.dump(doc, self.logfile)
        self.logfile.write('\n')


logger = AssertionLogger()
