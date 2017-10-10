import unittest

import marbles
import numpy as np


class TestCase(marbles.AnnotatedTestCase):

    def setUp(self):
        setattr(self, 'current', 10)
        setattr(self, 'historic', -10)

    def tearDown(self):
        delattr(self, 'current')
        delattr(self, 'historic')

    def test_month_to_month_changes(self):
        mtm_change = ((self.current - self.historic) / self.historic) * 100
        expectation = 10.

        # A descending list ensures that the most severe failure is
        # tested first; this could also be accomplished outside of
        # a for loop.
        _params = [
            (10, 'Stop all processes using these data.'),
            (2, 'File a JIRA with the data provider.'),
            (1, 'Continue to monitor this test over the next month.')
        ]

        for severity, advice in _params:
            self.assertLessEqual(np.abs(mtm_change),
                                 expectation * severity,
                                 advice=advice)


if __name__ == '__main__':
    unittest.main()
