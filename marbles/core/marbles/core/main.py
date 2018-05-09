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

    def _is_relevant_tb_level(self, tb):
        if self.showAll:
            # If verbose mode is on, print the traceback as normal.
            return super()._is_relevant_tb_level(tb)
        # I think the sense of the method name is swapped. Setting it
        # this way suppresses all frames of the traceback.
        return True


class MarblesTestRunner(unittest.TextTestRunner):
    '''A TestRunner which uses marbles-style assertion failure messages.'''

    resultclass = MarblesTestResult


unittest.TestCase = TestCase


def main(**kwargs):
    if 'testRunner' not in kwargs:
        kwargs['testRunner'] = MarblesTestRunner
    return unittest.main(**kwargs)
