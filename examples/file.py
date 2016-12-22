import os
import unittest

import marbles
from marbles import mixins


class FileTestCase(marbles.AnnotatedTestCase,
                   mixins.BetweenMixins,
                   mixins.FileMixins):
    '''FileTestCase makes assertions about a file, namely this file.'''

    def setUp(self):
        setattr(self, 'fname', __file__)

    def tearDown(self):
        delattr(self, 'fname')

    def test_that_file_exists(self):
        advice = '''{self.fname} doesn't exist, which is wild because
the string you're reading right now is written in that file.'''

        self.assertFileExists(self.fname, advice=advice)

    def test_that_file_name_matches_regex(self):
        advice = '''Determine if the file naming pattern has changed
or if this is a one-off thing. If it's a one-off, copy (or move)
{self.fname} to a file that matches the expected naming pattern
{expected}. If it's not a one-off, update this test to reflect the
new naming pattern.'''

        expected = '^[a-z]{4}.xlsx$'
        self.assertFileNameRegex(self.fname, expected, advice=advice)

    def test_for_file_type(self):
        advice = '''Email the vendor to ask if they can provide a
{expected} file, or if we should expect a different type of file
going forward.'''

        expected = '.xlsx'
        self.assertFileTypeEqual(self.fname, extension=expected, advice=advice)

    def test_for_file_size(self):
        advice = '''We're not prepared for files of this size. Email
the data engineering team to discuss.'''

        with open(self.fname) as f:
            f.seek(0, os.SEEK_END)
            filesize = f.tell()

        self.assertBetween(
                filesize, lower=1000, upper=2000, strict=False, advice=advice)


if __name__ == '__main__':
    unittest.main()
