import unittest

import namespace.core.main as m


class TestCase(unittest.TestCase):
    def test_neg_nums(self):
        for i in range(-10, 0):
            self.assertEqual(i*2, m.double(i))

    def test_pos_nums(self):
        for i in range(10):
            self.assertEqual(i*2, m.double(i))
