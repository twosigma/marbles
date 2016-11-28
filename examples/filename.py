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

        message = 'Expected a {expected} file but received a {actual} file.'
        advice = 'Contact the ingestion owner: Jane Doe'

        self.assertEqual(expected, actual, (message, advice))

    def test_filename_pattern(self):
        '''Verifies filename pattern.'''
        expected = '^file_[0-9]{8}$'
        actual = os.path.splitext(self.filename)[0]

        message = 'Filename {actual} does not match the pattern {expected}.'
        advice = ('Determine if this is a one-off error or if the file naming '
                  'pattern has changed. If the file naming pattern has '
                  'changed, consider updating this test.')

        self.assertIsNotNone(re.search(expected, actual), (message, advice))


if __name__ == '__main__':
    unittest.main()
