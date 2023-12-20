#
#  Copyright (c) 2018-2023 Two Sigma Open Source, LLC
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

'''Test that python -m marbles works properly.'''

import os
import os.path
import subprocess
import sys
import tempfile
import unittest
import unittest.util
from distutils import sysconfig

import marbles.core


class CommandRunningTestCase(unittest.TestCase):

    def __init__(
            self,
            methodName='runTest',
            *,
            cmd=None,
            cwd=None
            ):  # noqa: D102
        super().__init__(methodName=methodName)
        self.cmd = cmd
        self.cwd = cwd

    def setUp(self):  # noqa: D102
        stdout, stderr = self.__run_cmd()
        setattr(self, 'stdout', stdout)
        setattr(self, 'stderr', stderr)

    def __run_cmd(self):
        '''Run the command provided and return stdout and stderr.'''
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
        core_dir = os.path.dirname(os.path.dirname(__file__))
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

            coverage_config = os.path.join(core_dir, '.coveragerc')
            env = {'COVERAGE_PROCESS_START': coverage_config, **os.environ}
            to_remove = pth.name
        else:
            env = None
            to_remove = None
        try:
            cwd = core_dir if self.cwd is None else self.cwd
            proc = subprocess.run(
                self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=env, cwd=cwd)
        finally:
            if to_remove:
                os.remove(to_remove)
        return proc.stdout.decode(), proc.stderr.decode()


class TestScriptRunningTestCase(CommandRunningTestCase):
    '''A TestCase which runs another test suite in a few ways.

    Can use ``python -m marbles``, ``python -m unittest``, and just
    ``python path/to/test_file.py``.

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
        if not (runner and test_file):
            # unittest's loader tries to instantiate this class
            # without calling our load_tests, so all our variables
            # will be None. Though it won't run that object, it needs
            # to create it without raising an exception, and
            # os.path.join raises if test_file is None. So, in that
            # case, just return something, it will be discarded and
            # our load_tests will construct real versions of this
            # TestCase later.
            super().__init__(methodName=methodName)
        else:
            self.runner = runner
            self.verbose = verbose
            self.test_file = test_file
            test_dir = os.path.dirname(__file__)
            test_path = os.path.join(test_dir, 'examples', self.test_file)
            if self.runner == 'script':
                cmd = [sys.executable, test_path]
            else:
                cmd = [sys.executable, '-m', self.runner, test_path]
            if self.verbose:
                cmd.append('-v')
            super().__init__(methodName=methodName, cmd=cmd)

    def __str__(self):  # noqa: D102
        params = ', '.join('{}={!r}'.format(name, getattr(self, name))
                           for name in ('runner', 'verbose', 'test_file'))
        return '{} ({}) ({})'.format(
            self._testMethodName,
            unittest.util.strclass(self.__class__),
            params)

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
            self.assertIn('requests.put(', self.stderr)
        else:
            self.assertNotIn('requests.put(', self.stderr)

    def test_show_msg(self):
        '''The failure message should always appear.'''
        self.assertIn('409 != 201', self.stderr)

    def test_show_locals(self):
        '''Locals should be printed.'''
        if self.has_marbles:
            self.assertIn('data', self.stderr)
            self.assertIn('Little Bobby Tables', self.stderr)
            self.assertIn('endpoint', self.stderr)
            self.assertIn('example.com', self.stderr)
        else:
            self.assertNotIn('data', self.stderr)
            self.assertNotIn('Little Bobby Tables', self.stderr)
            self.assertNotIn('endpoint', self.stderr)
            self.assertNotIn('example.com', self.stderr)


class MainWithErrorTestCase(TestScriptRunningTestCase):
    '''Test how marbles.core.main and unittest.main handle test errors.'''

    def test_traceback(self):
        '''The traceback should be shown for all errors.'''
        self.assertIn('Traceback', self.stderr)


class VersionTestCase(CommandRunningTestCase):
    '''Test that marbles --version works.'''

    def __init__(self, methodName='runTest'):  # noqa: D102
        super().__init__(methodName=methodName,
                         cmd=[sys.executable, '-m', 'marbles', '--version'])

    def test_stdout(self):
        '''The version output should contain marbles.core's version.'''
        expected = 'marbles.core version: {}'.format(marbles.core.__version__)
        self.assertIn(expected, self.stdout)

    def test_stderr(self):
        '''The error output should be empty.'''
        self.assertEqual('', self.stderr)


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

    suite.addTests(VersionTestCase(methodName=test_name)
                   for test_name in loader.getTestCaseNames(VersionTestCase))

    return suite


if __name__ == '__main__':
    unittest.main()
