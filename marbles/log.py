''':mod:`marbles` can log information about each assertion called.

If configured, the :data:`marbles.log.logger` will log a json object
for each assertion and its success or failure, as well as any other
attributes of interest specified by the test author.

The captured information includes the assertion's args and kwargs,
msg, advice, local variables, and the result of the assertion.

Configuration is handled via the environment variables
:envvar:`MARBLES_LOGFILE` and :envvar:`MARBLES_TEST_CASE_ATTRS`, or
via the :meth:`AssertionLogger.configure` method.

Note that :class:`AssertionLogger` should not be instantiated
directly; instead, test authors should import and configure the
:data:`marbles.log.logger` as needed.
'''

import datetime
import inspect
import json
import os

from . import _stack


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

    .. warning::

       If you are uploading these logs somewhere like Elasticsearch,
       be sure that the information in your locals and arguments is
       protected by securing the destination system.

    This module exposes a single :class:`AssertionLogger`,
    :data:`marbles.log.logger`, that is used during a marbles test
    run. It can be configured with :meth:`configure` before running
    the tests or via environment variables.

    Example:

    .. code-block:: py

       from marbles.log import logger

       if __name__ == '__main__':
           logger.configure(logfile='/path/to/marbles.log',
                            attrs=['filename', 'category'])
           unittest.main()
    '''

    def __init__(self):
        self._logfile = self._open_if_needed(os.environ.get('MARBLES_LOGFILE'))
        if 'MARBLES_TEST_CASE_ATTRS' in os.environ:
            self._attrs = os.environ['MARBLES_TEST_CASE_ATTRS'].split(',')
        else:
            self._attrs = []

    @staticmethod
    def _open_if_needed(filename):
        if isinstance(filename, (str, bytes)):
            return open(filename, 'w')
        else:
            # Assume is already file-like
            return filename

    def configure(self, **kwargs):
        '''Configure what assertion logging is done.

        Parameters
        ----------
        logfile : str or bytes or file object
            If a string or bytes object, we append to that filename.
            If an open file object, we just write to it. If None,
            disable logging.
        attrs : list of str
            Capture these attributes on the TestCase being run when
            logging an assertion. For example, if you are testing
            multiple resources, make sure the resource name is a
            member of your TestCase, and configure marbles logging
            with that name.
        '''
        if 'logfile' in kwargs:
            if self._logfile and hasattr(self._logfile, 'close'):
                self._logfile.close()
            self._logfile = self._open_if_needed(kwargs['logfile'])

        if 'attrs' in kwargs:
            self._attrs = kwargs['attrs']

    @property
    def log_enabled(self):
        return self._logfile is not None

    @property
    def logfile(self):
        return self._logfile

    @property
    def attrs(self):
        return self._attrs

    def _log_assertion(self, case, assertion, args, kwargs, msg, advice,
                       *exc_info):
        if not self.log_enabled:
            return

        now = datetime.datetime.now()
        locals_, filename, lineno = _stack.get_stack_info()
        doc = {
            'case': str(case),
            'file': filename,
            'line': lineno,
            'assertion': assertion.__name__,
            'args': [str(a) for a in args],
            'kwargs': [{'key': k, 'value': str(v)} for k, v in kwargs.items()],
            'locals': [{'key': k, 'value': str(v)} for k, v in locals_.items()
                       if (k not in ('msg', 'advice', 'self')
                           and not k.startswith('_'))],
            'assertion_class': _class_defining_method(assertion),
            'msg': msg,
            'advice': advice.format(**locals_) if advice else None,
            '@timestamp': now.strftime('%Y-%m-%dT%H:%M:%S.%f')
        }

        for attr in self.attrs:
            doc[attr] = str(getattr(case, attr, None))

        if exc_info[0] is None:
            doc['result'] = 'pass'
        else:
            doc['result'] = 'fail'
            doc['msg'] = exc_info[1].standardMsg

        json.dump(doc, self.logfile)
        self.logfile.write('\n')


logger = AssertionLogger()
