import setuptools.command.test
from distutils import log
from distutils.errors import DistutilsError

from marbles.core.main import main  # noqa: E402


# In order to mirror the functionality of python setup.py test
# this command inherits from the setuptools.Command for test
# and overrides functions that reference unittest to instead
# use marbles.
# Hopefully you can find a better way to achieve the same goal.
class MarblesTestCommand(setuptools.command.test.test):
    description = 'Run tests using Marbles'

    def run_tests(self):
        test = main(
            module=None,
            defaultTest=None,
            argv=self._argv,
            testLoader=self._resolve_as_ep(self.test_loader),
            testRunner=self._resolve_as_ep(self.test_runner),
            exit=False,
        )

        if not test.result.wasSuccessful():
            msg = 'Test failed: %s' % test.result
            self.announce(msg, log.ERROR)
            raise DistutilsError(msg)

    @property
    def _argv(self):
        return ['marbles'] + self.test_args
