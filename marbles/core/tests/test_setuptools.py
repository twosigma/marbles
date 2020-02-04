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

import contextlib
import distutils.errors
import io
import json
import os
import setuptools.dist
import sys
import unittest

import marbles.setuptools
import tests.test_main

@contextlib.contextmanager
def working_directory(dir):
    try:
        cwd = os.getcwd()
        os.chdir(dir)
        yield
    finally:
        os.chdir(cwd)

class MarblesCommandTestCase(tests.test_main.CommandRunningTestCase):
    "Abstract test case to be run on a sample package directory"

    def __init__(self, methodName='runTest', package_dir=None):
        cmd = [sys.executable, 'setup.py', 'marbles']
        super().__init__(methodName=methodName, cmd=cmd, cwd=package_dir)
        self.package_dir = package_dir
        self.maxDiff = None


class TopLevelTestsTestCase(MarblesCommandTestCase):
    "Tests simple package structure where tests/ is top level and no namespace"

    def __init__(self, methodName='runTest'):
        super().__init__(methodName=methodName,
                         package_dir='example_packages/simple_package/')

    def test_locals(self):
        expected_lines = ['Locals:', 'e=2', 'a=1']
        for e in expected_lines:
            self.assertIn(e, self.stderr)

    def test_tests_run(self):
        expected_lines = [
                'test_test (tests.test_two.TestTest) ... ok',
                'test_test (tests.test.TestTest) ... FAIL',
                'Ran 2 tests in',
                ]
        for e in expected_lines:
            self.assertIn(e, self.stderr)

    def test_source(self):
        expected_lines = ['Source', 'e = 2', 'self.assertEqual(a,e)']
        for e in expected_lines:
            self.assertIn(e, self.stderr)

    
class NamespaceTestCase(MarblesCommandTestCase):
    "Test with namespace package"

    def __init__(self, methodName='runTest'):
        super().__init__(methodName=methodName,
                         package_dir='example_packages/namespace_package/')


    def test_locals(self):
        expected_lines = ['Locals:', 'i=6']
        for e in expected_lines:
            self.assertIn(e, self.stderr)

    
    def test_tests_run(self):
        expected_lines = [
                'test_neg_numbers (tests.namespace.core.test.TestCase) ... ok',
                'test_pos_numbers (tests.namespace.core.test.TestCase) ... FAIL',
                'Ran 2 tests in',
                ]
        for e in expected_lines:
            self.assertIn(e, self.stderr)

    def test_source(self):
        expected_lines = [
                'Source', 
                'for i in range(10)', 
                'self.assertEqual(i*2, m.double(i))'
                ]
        for e in expected_lines:
            self.assertIn(e, self.stderr)

class NoTestTestCase(MarblesCommandTestCase):
    "Test a package with no tests"

    def __init__(self, methodName='runTest'):
        super().__init__(methodName=methodName,
                         package_dir='example_packages/no_tests_package/')

    def test_tests_run(self):
        expected_lines = ['Ran 0 tests in']
        for e in expected_lines:
            self.assertIn(e, self.stderr)
