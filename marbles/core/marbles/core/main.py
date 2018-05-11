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

'''Main method for marbles.

With :mod:`unittest`, you can run ``python -m unittest`` to discover
and run your tests.

With :mod:`marbles`, you can run ``python -m marbles`` to discover and
run them, but with :mod:`marbles` style assertion failure messages,
including local variables and additional source code scope.
'''

import contextlib
import os
import unittest

from marbles.core import TestCase


class MarblesTestResult(unittest.TextTestResult):
    '''A TestResult which omits the traceback.

    Because marbles failure messages contain all of the information
    included in a normal unit test traceback, we can hide the
    traceback to make failure messages easier to read without losing
    any information. Here, we remove the traceback from the failure
    message, unless the user has asked for verbose output.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__show_traceback = True

    @contextlib.contextmanager
    def __hide_traceback(self):
        '''Suppress the traceback while in this context.'''
        old_show_traceback = self.__show_traceback
        self.__show_traceback = False
        try:
            yield
        finally:
            self.__show_traceback = old_show_traceback

    def _exc_info_to_string(self, err, test):
        '''Convert the exception to a string.

        We use unittest's conversion, but if the propagating exception
        is a test failure, then suppress the traceback. If the
        propagating exception is an error, or if tests are running in
        verbose mode, we keep the traceback in the output.
        '''
        exctype, value, tb = err
        if isinstance(value, test.failureException):
            with self.__hide_traceback():
                return super()._exc_info_to_string(err, test)
        else:
            return super()._exc_info_to_string(err, test)

    def _is_relevant_tb_level(self, tb):
        if self.showAll or self.__show_traceback:
            # If verbose mode is on, or we're printing an error, not a
            # failure, print the traceback as normal.
            return super()._is_relevant_tb_level(tb)
        # I think what unittest means by 'relevant' here is that the
        # frame in tb is part of the unittest framework (either above
        # or below the user's test and library code), which means
        # returning True here will suppress output of this frame.
        return True


class MarblesTestRunner(unittest.TextTestRunner):
    '''A TestRunner which uses marbles-style assertion failure messages.'''

    resultclass = MarblesTestResult


def main(**kwargs):
    # Override this so that when unittest loads our test modules,
    # those test modules will actually subclass marbles.TestCase.
    #
    # But, we can't do this at the module level because
    # marbles.core.main is imported into marbles.core.__init__ so that
    # marbles users can run marbles.core.main(). Since our __init__
    # loads this module, it breaks marbles's own tests which need to
    # actually use unittest.TestCase. It's also cleaner to only do
    # this if we know we're using marbles's main method to run some
    # possibly marbles-naive unit tests.
    unittest.TestCase = TestCase

    if 'testRunner' not in kwargs:  # pragma: no branch
        kwargs['testRunner'] = MarblesTestRunner
    return unittest.main(**kwargs)
