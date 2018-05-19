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

'''Test that python -m marbles works properly.'''

import os
import os.path
import subprocess
import sys
import tempfile
import unittest
import unittest.util
from distutils import sysconfig


class TestScriptRunningTestCase(unittest.TestCase):
    '''A TestCase which runs another test suite in a few ways.

    Can use ``python -m marbles``, ``python -m unittest``, and just
    ``python path/to/test_file.py``.

    Parameters
    ----------
    methodName : str
        Test method (within the subclass of this TestCase) to run,
        passed through to unittest.
    runner : str
        Either the name of a main module (marbles or unittest) to use
        with ``python -m``, or the word ``script``, to run the test
        file as a script.
    verbose : bool
        Whether to use verbose mode (``-v``).
    test_file : str
        Path to the test file to run.
    '''

    def __init__(self, methodName='runTest', *, runner=None, verbose=None,
                 test_file=None):  # noqa: D102
        super().__init__(methodName=methodName)
        self.runner = runner
        self.verbose = verbose
        self.test_file = test_file

    def __str__(self):  # noqa: D102
        params = ', '.join('{}={!r}'.format(name, getattr(self, name))
                           for name in ('runner', 'verbose', 'test_file'))
        return '{} ({}) ({})'.format(
            self._testMethodName,
            unittest.util.strclass(self.__class__),
            params)

    def setUp(self):  # noqa: D102
        stdout, stderr = self.__run_test()
        setattr(self, 'stdout', stdout)
        setattr(self, 'stderr', stderr)

    def __run_test(self):
        '''Run the test under either unittest or marbles.

        Since we're already running a unittest test (i.e. this class),
        and :mod:`marbles.core.main` rebinds
        :class:`unittest.TestCase`, it's risky to run those tests
        inside this process, they could modify (or have their behavior
        affected by) this process's modules and interpreter state.

        We use subprocess to make sure the tests we're running have a
        fresh Python interpreter and go through all the normal Python
        startup procedures, so we're testing as closely as possible to
        what users will see.

        It is possible to run these in-process using
        :func:`runpy.run_module` and :func:`runpy.run_path`, and that
        would be faster (and would not require the coverage hack
        below), but at the risk of exposing the problems described
        above.

        Returns
        -------
        (str, str)
            Standard output and error produced by the test.
        '''
        test_dir = os.path.dirname(__file__)
        test_path = os.path.join(test_dir, 'examples', self.test_file)
        if self.runner == 'script':
            cmd = [sys.executable, test_path]
        else:
            cmd = [sys.executable, '-m', self.runner, test_path]
        if self.verbose:
            cmd.append('-v')

        # In order to get coverage working for tests run through
        # subprocess, we need to set COVERAGE_PROCESS_START to point
        # to a .coveragerc, and trick the python interpreter into
        # calling coverage.process_startup() before doing anything
        # else.

        # This is documented here, though it doesn't say what
        # COVERAGE_PROCESS_START needs to contain:
        # http://coverage.readthedocs.io/en/coverage-4.2/subprocess.html

        # The way we're tricking python into running
        # coverage.process_startup() is by putting it in the .pth file
        # in site-packages. This may not work on all environments, for
        # example, if site-packages is read-only, but it should work
        # in the places we're using to test.

        # Also, due to https://github.com/pypa/virtualenv/issues/355,
        # we can't use site.getsitepackages(), but
        # distutils.sysconfig.get_python_lib() works.
        if sys.gettrace():
            # Only add this .pth file if we're running under the
            # coverage tool, which is the most likely reason that
            # sys.gettrace() would be set to anything.
            site_packages = sysconfig.get_python_lib()
            with tempfile.NamedTemporaryFile(
                    mode='w', dir=site_packages, suffix='.pth',
                    delete=False) as pth:
                pth.write('import coverage; coverage.process_startup()\n')
                pth.flush()

            coverage_config = os.path.join(test_dir, '..', '.coveragerc')
            env = {'COVERAGE_PROCESS_START': coverage_config}
            to_remove = pth.name
        else:
            env = {}
            to_remove = None
        try:
            proc = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=env)
        finally:
            if to_remove:
                os.remove(to_remove)
        return proc.stdout.decode(), proc.stderr.decode()

    @property
    def run_with_marbles(self):
        '''Are we using marbles to run the test?'''
        return (
            self.runner == 'marbles'
            or self.runner == 'script' and self.is_marbles_test
        )

    @property
    def is_marbles_test(self):
        '''Is the test a marbles test?'''
        return 'marbles' in self.test_file

    @property
    def has_marbles(self):
        '''Do we have marbles at all?'''
        return self.run_with_marbles or self.is_marbles_test

    def test_empty_stdout(self):
        '''Standard out should be empty in all cases.'''
        self.assertEqual(self.stdout, '')


class MainWithFailureTestCase(TestScriptRunningTestCase):
    '''Test how marbles.core.main and unittest.main handle test failures.'''

    def test_traceback(self):
        '''The traceback should only be shown in verbose mode.

        The traceback will be present when we're running under
        unittest, even if the test is a marbles test.
        '''
        if self.verbose or not self.run_with_marbles:
            self.assertIn('Traceback', self.stderr)
        else:
            self.assertNotIn('Traceback', self.stderr)

    def test_show_source(self):
        '''The source code should appear.'''
        if self.has_marbles:
            self.assertIn('Source', self.stderr)
            self.assertIn('self.assertEqual(', self.stderr)
        else:
            self.assertNotIn('self.assertEqual(', self.stderr)

    def test_show_msg(self):
        '''The failure message should always appear.'''
        self.assertIn('409 != 201', self.stderr)

    def test_show_locals(self):
        '''Locals should be printed.'''
        if self.has_marbles:
            self.assertIn('data', self.stderr)
            self.assertIn('Jane', self.stderr)
            self.assertIn('endpoint', self.stderr)
            self.assertIn('example.com', self.stderr)
        else:
            self.assertNotIn('data', self.stderr)
            self.assertNotIn('Jane', self.stderr)
            self.assertNotIn('endpoint', self.stderr)
            self.assertNotIn('example.com', self.stderr)


class MainWithErrorTestCase(TestScriptRunningTestCase):
    '''Test how marbles.core.main and unittest.main handle test errors.'''

    def test_traceback(self):
        '''The traceback should be shown for all errors.'''
        self.assertIn('Traceback', self.stderr)


def load_tests_from_testcase(loader, class_, test_files):
    '''Load and parametrize tests for ``class_``.'''
    runners = [
        'unittest',
        'marbles',
        'script'
    ]
    test_names = loader.getTestCaseNames(class_)
    return (
        class_(methodName=test_name, runner=runner, verbose=verbose,
               test_file=test_file)
        for runner in runners
        for verbose in (True, False)
        for test_file in test_files
        for test_name in test_names
    )


def load_tests(loader, tests, pattern):  # noqa: D103
    suite = unittest.TestSuite()

    failure_tests = ['example_unittest.py', 'example_marbles.py']
    suite.addTests(load_tests_from_testcase(
        loader, MainWithFailureTestCase, failure_tests))

    error_tests = ['example_error.py']
    suite.addTests(load_tests_from_testcase(
        loader, MainWithErrorTestCase, error_tests))

    return suite


if __name__ == '__main__':
    unittest.main()
