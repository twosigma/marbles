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

'''Tests about marbles assertion logging.

Here, we are checking that all the configuration entry-points (env
vars and marbles.log.logger.configure) work properly.
'''

import collections
import io
import json
import os
import sys
import tempfile
import unittest
import unittest.util

from marbles.core import ContextualAssertionError
from marbles.core import log
from marbles.core import __version__
import tests.test_marbles as marbles_tests


class LoggingConfigureTestCase(unittest.TestCase):
    '''Configures assertion logging during a test.

    Assumes the subclass has a dict attr named 'log_config'.

    During a test, one can get the results of logging so far with
    ``self.assertion_logs()``.
    '''

    env_var_mapping = {
        'logfile': 'MARBLES_LOGFILE',
        'verbose': 'MARBLES_LOG_VERBOSE',
        'attrs': 'MARBLES_TEST_CASE_ATTRS',
        'verbose_attrs': 'MARBLES_TEST_CASE_ATTRS_VERBOSE',
    }

    def __init__(self, methodName='runTest', *, use_env=False, use_file=False,
                 use_annotated_test_case=False, **kwargs):
        super().__init__(methodName=methodName, **kwargs)
        self._use_env = use_env
        self._use_file = use_file
        self._use_annotated_test_case = use_annotated_test_case

    def __str__(self):
        params = ', '.join(
            '{}={!r}'.format(name, getattr(self, '_{}'.format(name)))
            for name in ('use_env', 'use_file', 'use_annotated_test_case'))
        return '{} ({}) ({})'.format(
            self._testMethodName,
            unittest.util.strclass(self.__class__),
            params)

    def setUpEnv(self):
        if not isinstance(self.__config['logfile'], str):
            raise unittest.SkipTest('can only use env vars to pass '
                                    'filenames, not file objects')
        self.new_env = {self.env_var_mapping[k]: v
                        for k, v in self.__config.items()}
        self.old_env = {k: os.environ.get(k)
                        for k in self.new_env.keys()}
        for k, v in self.new_env.items():
            if isinstance(v, str):
                os.environ[k] = v
            elif isinstance(v, collections.Sequence):
                os.environ[k] = ','.join(str(x) for x in v)
            else:
                os.environ[k] = str(v)

    def tearDownEnv(self):
        # If we skipped the test in setUpEnv, we wouldn't have this,
        # but we also don't need to do anything.
        if hasattr(self, 'old_env'):
            for k, v in self.old_env.items():
                if v is None:
                    del os.environ[k]
                else:
                    os.environ[k] = v

    def setUpConfigure(self):
        log.logger.configure(**self.__config)

    def tearDownConfigure(self):
        pass

    def setUp(self):
        super().setUp()
        if self._use_annotated_test_case:
            self.case = marbles_tests.ExampleAnnotatedTestCase()
        else:
            self.case = marbles_tests.ExampleTestCase()
        self.__old_logger = log.logger
        log.logger = log.AssertionLogger()
        log.logger.configure()
        self.__config = self.log_config.copy()
        if self._use_file:
            _, self._tmpfilename = tempfile.mkstemp()
            self.__config['logfile'] = self._tmpfilename
        else:
            self.__file_handle = io.StringIO()
            self.__config['logfile'] = self.__file_handle

        if self._use_env:
            self.setUpEnv()
        else:
            self.setUpConfigure()

    def tearDown(self):
        super().tearDown()
        delattr(self, 'case')
        if self._use_env:
            self.tearDownEnv()
        else:
            self.tearDownConfigure()
        if self._use_file:
            log.logger.logfile.close()
            os.remove(self._tmpfilename)
        log.logger = self.__old_logger

    def assertion_logs(self):
        if self._use_file:
            log.logger.logfile.flush()
            with open(self._tmpfilename, 'r') as f:
                lines = list(f.readlines())
        else:
            lines = self.__file_handle.getvalue().split('\n')
        return [json.loads(line) for line in lines if line]


class TestAssertionLogging(LoggingConfigureTestCase):

    log_config = {}

    def test_success(self):
        '''On a successful assertion, do we log information?'''
        self.case.test_success()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'file': marbles_tests.__file__,
            'assertion': 'assertTrue',
            'marbles_version': __version__,
            'args': ['True'],
            'kwargs': [],
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)
        for unexpected_key in ('locals', 'msg', 'advice'):
            self.assertNotIn(unexpected_key, logs[0])


class TestAssertionLoggingVerboseTrue(LoggingConfigureTestCase):

    log_config = {'verbose': True}

    def test_success(self):
        '''On a successful assertion, do we respect verbose=True?'''
        self.case.test_success()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'file': marbles_tests.__file__,
            'assertion': 'assertTrue',
            'marbles_version': __version__,
            'args': ['True'],
            'kwargs': [],
            'locals': [],
            'msg': None,
            'advice': 'some advice',
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)

    def test_failure(self):
        '''On a failed assertion, do we log information?'''
        with self.assertRaises(ContextualAssertionError):
            self.case.test_reverse_equality_positional_msg()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'file': marbles_tests.__file__,
            'assertion': 'assertReverseEqual',
            'assertion_class': 'tests.test_marbles.ReversingTestCaseMixin',
            'marbles_version': __version__,
            'args': ['leif', 'leif'],
            'kwargs': [],
            'locals': [{'key': 's', 'value': 'leif'}],
            'msg': 'some message',
            'advice': 'some advice',
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)


class TestAssertionLoggingVerboseFalse(LoggingConfigureTestCase):

    log_config = {'verbose': False}

    def test_success(self):
        '''On a successful assertion, do we respect verbose=False?'''
        self.case.test_success()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'file': marbles_tests.__file__,
            'assertion': 'assertTrue',
            'marbles_version': __version__,
            'args': ['True'],
            'kwargs': [],
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)
        for unexpected_key in ('locals', 'msg', 'advice'):
            self.assertNotIn(unexpected_key, logs[0])

    def test_failure(self):
        '''On a failed assertion, do we log information?'''
        with self.assertRaises(ContextualAssertionError):
            self.case.test_reverse_equality_positional_msg()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'file': marbles_tests.__file__,
            'assertion': 'assertReverseEqual',
            'assertion_class': 'tests.test_marbles.ReversingTestCaseMixin',
            'marbles_version': __version__,
            'args': ['leif', 'leif'],
            'kwargs': [],
            'locals': [{'key': 's', 'value': 'leif'}],
            'msg': 'some message',
            'advice': 'some advice',
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)


class TestAssertionLoggingVerboseList(LoggingConfigureTestCase):

    log_config = {'verbose': ['msg', 'advice']}

    def test_success(self):
        '''On a successful assertion, do we respect a verbose list?'''
        self.case.test_success()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'file': marbles_tests.__file__,
            'assertion': 'assertTrue',
            'marbles_version': __version__,
            'args': ['True'],
            'kwargs': [],
            'msg': None,
            'advice': 'some advice',
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)
        for unexpected_key in ('locals',):
            self.assertNotIn(unexpected_key, logs[0])

    def test_failure(self):
        '''On a failed assertion, do we log information?'''
        with self.assertRaises(ContextualAssertionError):
            self.case.test_reverse_equality_positional_msg()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'file': marbles_tests.__file__,
            'assertion': 'assertReverseEqual',
            'assertion_class': 'tests.test_marbles.ReversingTestCaseMixin',
            'marbles_version': __version__,
            'args': ['leif', 'leif'],
            'kwargs': [],
            'locals': [{'key': 's', 'value': 'leif'}],
            'msg': 'some message',
            'advice': 'some advice',
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)


class TestAssertionLoggingAttributeCapture(LoggingConfigureTestCase):

    log_config = {'attrs': ['longMessage']}

    def test_capture_test_case_attributes(self):
        '''Can we capture other attributes of a TestCase?'''
        self.case.test_success()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'assertion': 'assertTrue'
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)
        self.assertNotIn('longMessage', logs[0])

    def test_capture_test_case_attributes_on_failure(self):
        '''Can we capture other attributes of a TestCase on failure?'''
        with self.assertRaises(ContextualAssertionError):
            self.case.test_failure()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'assertion': 'assertTrue',
            'longMessage': 'This is a long message'
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)


class TestAssertionLoggingVerboseAttributeCapture(LoggingConfigureTestCase):

    log_config = {'verbose_attrs': ['longMessage']}

    def test_capture_test_case_attributes(self):
        '''Can we capture other attributes of a TestCase?'''
        self.case.test_success()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'assertion': 'assertTrue',
            'longMessage': 'This is a long message'
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)

    def test_capture_test_case_attributes_on_failure(self):
        '''Can we capture other attributes of a TestCase on failure?'''
        with self.assertRaises(ContextualAssertionError):
            self.case.test_failure()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'assertion': 'assertTrue',
            'longMessage': 'This is a long message'
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)


class TestAssertionLoggingRespectsEnvOverrides(LoggingConfigureTestCase):
    '''Tests that we can override log.logger.configure() with env vars.'''

    log_config = {'logfile': '/path/does/not/exist',
                  'verbose': False,
                  'attrs': ['longMessage']}

    def setUp(self):
        if self._use_env:
            raise unittest.SkipTest(
                'Only testing when the base class sets up with configure()')
        self._use_file = True
        super().setUp()
        self.old_logfile = os.environ.get('MARBLES_LOGFILE')
        _, self._tmpfilename = tempfile.mkstemp()
        os.environ['MARBLES_LOGFILE'] = self._tmpfilename

    def tearDown(self):
        super().tearDown()
        if self.old_logfile is None:
            del os.environ['MARBLES_LOGFILE']
        else:
            os.environ['MARBLES_LOGFILE'] = self.old_logfile
        delattr(self, 'old_logfile')
        if hasattr(self, 'old_verbose'):
            if self.old_verbose is None:
                del os.environ['MARBLES_LOG_VERBOSE']
            else:
                os.environ['MARBLES_LOG_VERBOSE'] = self.old_verbose

    def test_success(self):
        '''On a successful assertion, do we log information?'''
        self.case.test_success()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'file': marbles_tests.__file__,
            'assertion': 'assertTrue',
            'marbles_version': __version__,
            'args': ['True'],
            'kwargs': [],
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)
        for unexpected_key in ('locals', 'msg', 'advice'):
            self.assertNotIn(unexpected_key, logs[0])

    def test_verbose_override(self):
        '''On a successful assertion, do we log information?'''
        self.old_verbose = os.environ.get('MARBLES_LOG_VERBOSE')
        os.environ['MARBLES_LOG_VERBOSE'] = 'true'
        self.case.test_success()
        logs = self.assertion_logs()
        self.assertEqual(len(logs), 1)
        expected = {
            'file': marbles_tests.__file__,
            'assertion': 'assertTrue',
            'marbles_version': __version__,
            'args': ['True'],
            'kwargs': [],
            'locals': [],
            'msg': None,
            'advice': 'some advice',
        }
        self.assertEqual({k: v for k, v in logs[0].items() if k in expected},
                         expected)


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    module = sys.modules[__name__]
    objs = [getattr(module, name) for name in dir(module)]
    test_classes = [obj for obj in objs
                    if (isinstance(obj, type)
                        and issubclass(obj, unittest.TestCase))]

    for use_annotated_test_case in (True, False):
        for cls in test_classes:
            for name in loader.getTestCaseNames(cls):
                suite.addTest(
                    cls(
                        methodName=name,
                        use_env=False,
                        use_file=False,
                        use_annotated_test_case=use_annotated_test_case
                    )
                )
        for cls in test_classes:
            for name in loader.getTestCaseNames(cls):
                suite.addTest(
                    cls(
                        methodName=name,
                        use_env=False,
                        use_file=True,
                        use_annotated_test_case=use_annotated_test_case
                    )
                )
        for cls in test_classes:
            for name in loader.getTestCaseNames(cls):
                suite.addTest(
                    cls(
                        methodName=name,
                        use_env=True,
                        use_file=True,
                        use_annotated_test_case=use_annotated_test_case
                    )
                )

    return suite
