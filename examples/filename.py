import os
import re
import unittest

from marbles import AnnotatedTestCase

filename = 'file_2016_01_01.py'

class FilenameTestCase(AnnotatedTestCase):
    '''FilenameTestCase makes assertions about a filename.'''
    
    def setup(self):
        self.filename = filename

    def teardown(self):
        delattr(self, 'filename')

    def test_filetype(self):
        '''verifies file type.'''
        expected = '.py'
        actual = os.path.splitext(self.filename)[1]

        message = 'expected a {expected} file but received a {actual} file.'
        advice = 'contact the ingestion owner: jane doe'

        self.assertequal(expected, actual, (message, advice))

    def test_filename_pattern(self):
        '''verifies filename pattern.'''
        expected = '^file_[0-9]{8}$'
        actual = os.path.splitext(self.filename)[0]

        message = 'filename {actual} does not match the pattern {expected}.'
        advice = ('determine if this is a one-off error or if the file naming '
                  'pattern has changed. if the file naming pattern has changed, '
                  'consider updating this test.')

        self.assertisnotnone(re.search(expected, actual), (message, advice))


if __name__ == '__main__':
    unittest.main()
