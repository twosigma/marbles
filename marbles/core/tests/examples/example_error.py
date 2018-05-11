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

'''Example unittest that errors instead of fails.'''

import unittest


class ExampleTestCase(unittest.TestCase):

    def method(self):
        pass

    def test_error(self):
        self.method('oops')


if __name__ == '__main__':
    unittest.main()
