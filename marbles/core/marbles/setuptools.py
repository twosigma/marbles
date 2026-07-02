import importlib

import setuptools
from setuptools.errors import BaseError

from marbles.core.main import main  # noqa: E402


# In order to mirror the functionality of python setup.py test, this
# command runs unittest discovery using marbles.
class MarblesTestCommand(setuptools.Command):
    description = 'Run tests using Marbles'
    user_options = [
        ('test-module=', 'm', "Run 'test_suite' in specified module"),
        ('test-suite=', 's', "Run single test, case or suite"),
        ('test-runner=', 'r', "Test runner to use"),
    ]

    def initialize_options(self):
        self.test_module = None
        self.test_suite = None
        self.test_runner = None

    def finalize_options(self):
        if self.test_suite is None:
            self.test_suite = getattr(self.distribution, 'test_suite', None)
        if self.test_runner is None:
            self.test_runner = getattr(self.distribution, 'test_runner', None)

    @staticmethod
    def _resolve_dotted_name(name):
        if name is None:
            return None
        module_name, _, attr_name = name.rpartition('.')
        if not module_name:
            return None
        return getattr(importlib.import_module(module_name), attr_name)

    def run(self):
        self.run_tests()

    def run_tests(self):
        kwargs = {
            'module': None,
            'defaultTest': None,
            'argv': self._argv,
            'exit': False,
        }
        test_runner = self._resolve_dotted_name(self.test_runner)
        if test_runner is not None:
            kwargs['testRunner'] = test_runner

        test = main(**kwargs)

        if not test.result.wasSuccessful():
            msg = 'Test failed: %s' % test.result
            self.announce(msg)
            raise BaseError(msg)

    @property
    def _argv(self):
        test_target = self.test_suite or self.test_module
        if test_target:
            return ['marbles', test_target, '-v']
        return ['marbles', 'discover', '-v']
