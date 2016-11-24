import os
import re
import unittest

from marbles import AnnotatedTestCase


filename = 'file_2016_01_01.py'


class FilenameTestCase(AnnotatedTestCase):
    '''FilenameTestCase makes assertions about a filename.'''

    def setUp(self):
        self.filename = filename

    def tearDown(self):
        delattr(self, 'filename')

    def test_filetype(self):
        '''Verifies file type.'''
        expected = '.py'
        actual = os.path.splitext(self.filename)[1]

        advice = ('Tell Jane Doe that we expected a {expected} file but '
                  'received a {actual} file. If we should expect {expected} '
                  'files moving forward, please update this test.')

        self.assertEqual(expected, actual, advice=advice)

    def test_filename_pattern(self):
        '''Verifies filename pattern.'''
        expected = '^file_[0-9]{8}$'
        actual = os.path.splitext(self.filename)[0]

        advice = ('Determine if this is a one-off error or if the file naming '
                  'pattern has changed to {actual}. If the file naming '
                  'pattern has changed, please update this test.')

        self.assertRegex(actual, expected, advice=advice)


if __name__ == '__main__':
    unittest.main()
