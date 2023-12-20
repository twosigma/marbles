#
#  Copyright (c) 2018-2023 Two Sigma Open Source, LLC
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#

import operator
import os
import unittest
from unittest import mock
from datetime import date, datetime, timedelta, timezone

from marbles.mixins import mixins


class TestBetweenMixins(unittest.TestCase):

    def setUp(self):
        class TestBetween(unittest.TestCase, mixins.BetweenMixins): pass  # noqa: E701

        setattr(self, 'kls', TestBetween())

    def tearDown(self):
        delattr(self, 'kls')

    def test_assert_between(self):
        self.kls.assertBetween(10, 0, 20, strict=True)
        self.kls.assertBetween(10, 10, 20, strict=False)

        msg = '%s is not strictly between %s and %s' % (10, 10, 20)
        with self.assertRaises(AssertionError) as e:
            self.kls.assertBetween(10, 10, 20, strict=True)
        self.assertEqual(e.exception.args[0], msg)

        msg = '%s is not between %s and %s' % (0, 10, 20)
        with self.assertRaises(AssertionError) as e:
            self.kls.assertBetween(0, 10, 20, strict=False)
        self.assertEqual(e.exception.args[0], msg)

        # degenerate interval
        self.assertEqual(e.exception.args[0], msg)

        msg = '%s is not strictly between %s and %s' % (10, 10, 10)
        with self.assertRaises(AssertionError)as e:
            self.kls.assertBetween(10, 10, 10, strict=True)

        self.kls.assertNotBetween(0, 10, 20, strict=True)
        self.kls.assertNotBetween(10, 10, 20, strict=False)

        msg = '%s is strictly between %s and %s' % (10, 0, 20)
        with self.assertRaises(AssertionError) as e:
            self.kls.assertNotBetween(10, 0, 20, strict=False)
        self.assertEqual(e.exception.args[0], msg)

        msg = '%s is between %s and %s' % (10, 10, 20)
        with self.assertRaises(AssertionError) as e:
            self.kls.assertNotBetween(10, 10, 20, strict=True)
        self.assertEqual(e.exception.args[0], msg)

        # degenerate interval
        msg = 'cannot specify strict=False if lower == upper'
        with self.assertRaises(ValueError) as e:
            self.kls.assertNotBetween(10, 10, 10, strict=False)
        self.assertEqual(e.exception.args[0], msg)

        msg = '%s is between %s and %s' % (10, 10, 10)
        with self.assertRaises(AssertionError) as e:
            self.kls.assertNotBetween(10, 10, 10, strict=True)
        self.assertEqual(e.exception.args[0], msg)


class TestMonotonicMixins(unittest.TestCase):

    def setUp(self):
        class TestMonotonic(unittest.TestCase, mixins.MonotonicMixins): pass  # noqa: E701

        setattr(self, 'kls', TestMonotonic())
        setattr(self, 'seq', [1, 2, 3, 3, 4])
        setattr(self, 'seqstrict', (1, 2, 3, 4, 5))
        setattr(self, 'seqrev', 'zzy')
        setattr(self, 'seqrevstrict', 'zyx')

    def tearDown(self):
        delattr(self, 'kls')
        delattr(self, 'seq')
        delattr(self, 'seqstrict')
        delattr(self, 'seqrev')
        delattr(self, 'seqrevstrict')

    def test_type_checking(self):
        '''Is a TypeError raised if ``sequence`` is not iterable?'''
        typed_asserts = [
            self.kls.assertMonotonicIncreasing,
            self.kls.assertNotMonotonicIncreasing,
            self.kls.assertMonotonicDecreasing,
            self.kls.assertNotMonotonicDecreasing
        ]
        msg = 'First argument is not iterable'

        for tassert in typed_asserts:
            with self.subTest(tassert=tassert):
                with self.assertRaises(TypeError) as e:
                    tassert(10, strict=True)
                self.assertTrue(e.exception.args[0].endswith(msg))

                with self.assertRaises(TypeError) as e:
                    tassert(10, strict=False)
                self.assertTrue(e.exception.args[0].endswith(msg))

    def test_monotonic(self):
        self.assertTrue(self.kls._monotonic(operator.le, self.seq))
        self.assertFalse(self.kls._monotonic(operator.lt, self.seq))
        self.assertTrue(self.kls._monotonic(operator.le, self.seqstrict))
        self.assertTrue(self.kls._monotonic(operator.lt, self.seqstrict))

        self.assertTrue(self.kls._monotonic(operator.ge, self.seqrev))
        self.assertFalse(self.kls._monotonic(operator.gt, self.seqrev))
        self.assertTrue(self.kls._monotonic(operator.ge, self.seqrevstrict))
        self.assertTrue(self.kls._monotonic(operator.gt, self.seqrevstrict))

        self.assertFalse(self.kls._monotonic(operator.le, self.seqrev))
        self.assertFalse(self.kls._monotonic(operator.lt, self.seqrev))
        self.assertFalse(self.kls._monotonic(operator.le, self.seqrevstrict))
        self.assertFalse(self.kls._monotonic(operator.lt, self.seqrevstrict))

        self.assertFalse(self.kls._monotonic(operator.ge, self.seq))
        self.assertFalse(self.kls._monotonic(operator.gt, self.seq))
        self.assertFalse(self.kls._monotonic(operator.ge, self.seqstrict))
        self.assertFalse(self.kls._monotonic(operator.gt, self.seqstrict))

        # If there's only one element in the sequence it's monotonic
        self.assertTrue(self.kls._monotonic(operator.le, (0,)))
        # If there are no elements in the sequence it's monotonic
        self.assertTrue(self.kls._monotonic(operator.le, []))

    def test_assert_monotonic_increasing(self):
        self.kls.assertMonotonicIncreasing(self.seqstrict, strict=True)
        self.kls.assertMonotonicIncreasing(self.seq, strict=False)

        msg = ('Elements in %s are not strictly monotonically '
               'increasing' % (self.seq,))
        with self.assertRaises(AssertionError) as e:
            self.kls.assertMonotonicIncreasing(self.seq, strict=True)
        self.assertEqual(e.exception.args[0], msg)

        msg = ('Elements in %s are not monotonically '
               'increasing' % (self.seqrev,))
        with self.assertRaises(AssertionError) as e:
            self.kls.assertMonotonicIncreasing(self.seqrev, strict=False)
        self.assertEqual(e.exception.args[0], msg)

        self.kls.assertNotMonotonicIncreasing(self.seqrevstrict, strict=True)
        self.kls.assertNotMonotonicIncreasing(self.seqrev, strict=False)

        msg = ('Elements in %s are strictly monotonically '
               'increasing' % (self.seqstrict,))
        with self.assertRaises(AssertionError) as e:
            self.kls.assertNotMonotonicIncreasing(self.seqstrict, strict=True)
        self.assertEqual(e.exception.args[0], msg)

        msg = ('Elements in %s are monotonically increasing' % (self.seq,))
        with self.assertRaises(AssertionError) as e:
            self.kls.assertNotMonotonicIncreasing(self.seq, strict=False)
        self.assertEqual(e.exception.args[0], msg)

    def test_assert_monotonic_decreasing(self):
        self.kls.assertMonotonicDecreasing(self.seqrevstrict, strict=True)
        self.kls.assertMonotonicDecreasing(self.seqrev, strict=False)

        msg = ('Elements in %s are not strictly monotonically '
               'decreasing' % (self.seqrev,))
        with self.assertRaises(AssertionError) as e:
            self.kls.assertMonotonicDecreasing(self.seqrev, strict=True)
        self.assertEqual(e.exception.args[0], msg)

        msg = ('Elements in %s are not monotonically '
               'decreasing' % (self.seq,))
        with self.assertRaises(AssertionError) as e:
            self.kls.assertMonotonicDecreasing(self.seq, strict=False)
        self.assertEqual(e.exception.args[0], msg)

        self.kls.assertNotMonotonicDecreasing(self.seqstrict, strict=True)
        self.kls.assertNotMonotonicDecreasing(self.seq, strict=False)

        msg = ('Elements in %s are strictly monotonically '
               'decreasing' % (self.seqrevstrict,))
        with self.assertRaises(AssertionError) as e:
            self.kls.assertNotMonotonicDecreasing(self.seqrevstrict,
                                                  strict=True)
        self.assertEqual(e.exception.args[0], msg)

        msg = ('Elements in %s are monotonically decreasing' % (self.seqrev,))
        with self.assertRaises(AssertionError) as e:
            self.kls.assertNotMonotonicDecreasing(self.seqrev, strict=False)
        self.assertEqual(e.exception.args[0], msg)


class TestUniqueMixins(unittest.TestCase):

    def setUp(self):
        class TestUnique(unittest.TestCase, mixins.UniqueMixins): pass  # noqa: E701

        setattr(self, 'kls', TestUnique())
        setattr(self, 'seq', [1, 2, 3, 3, 4])
        setattr(self, 'sequnique', (1, 2, 3, 4, 5))

    def tearDown(self):
        delattr(self, 'kls')
        delattr(self, 'seq')
        delattr(self, 'sequnique')

    def test_type_checking(self):
        '''Is a TypeError raised if ``container`` is not iterable?'''
        msg = 'First argument is not iterable'

        with self.assertRaises(TypeError) as e:
            self.kls.assertUnique(10)
        self.assertTrue(e.exception.args[0].endswith(msg))

        with self.assertRaises(TypeError) as e:
            self.kls.assertNotUnique(10)
        self.assertTrue(e.exception.args[0].endswith(msg))

    def test_assert_unique(self):
        self.kls.assertUnique(self.sequnique)

        msg = 'Elements in %s are not unique' % (self.seq,)
        with self.assertRaises(AssertionError) as e:
            self.kls.assertUnique(self.seq)
        self.assertEqual(e.exception.args[0], msg)

        self.kls.assertNotUnique(self.seq)

        msg = 'Elements in %s are unique' % (self.sequnique,)
        with self.assertRaises(AssertionError) as e:
            self.kls.assertNotUnique(self.sequnique)
        self.assertEqual(e.exception.args[0], msg)

        # unhashable types
        self.kls.assertUnique([set([1, 2, 3]), set([2, 3, 4])])

        msg = 'Elements in %s are not unique' % ([set([1, 2, 3]),
                                                  set([1, 2, 3])],)
        with self.assertRaises(AssertionError) as e:
            self.kls.assertUnique([set([1, 2, 3]), set([1, 2, 3])])
        self.assertEqual(e.exception.args[0], msg)

        self.kls.assertNotUnique([set([1, 2, 3]), set([1, 2, 3])])

        msg = 'Elements in %s are unique' % ([set([1, 2, 3]), set([2, 3, 4])],)
        with self.assertRaises(AssertionError) as e:
            self.kls.assertNotUnique([set([1, 2, 3]), set([2, 3, 4])])
        self.assertEqual(e.exception.args[0], msg)


class TestFileMixins(unittest.TestCase):

    def setUp(self):
        class TestFile(unittest.TestCase, mixins.FileMixins): pass  # noqa: E701

        setattr(self, 'kls', TestFile())
        setattr(self, 'filename', 'fake-file-19910914.csv')
        setattr(self, 'filesize', 10)
        setattr(self, 'filetype', '.csv')
        setattr(self, 'encoding', 'utf-8')
        setattr(self, 'regex', '^[a-z]*-[a-z]*-[0-9]{8}.csv$')

    def tearDown(self):
        delattr(self, 'kls')
        delattr(self, 'filename')
        delattr(self, 'filesize')
        delattr(self, 'filetype')
        delattr(self, 'encoding')
        delattr(self, 'regex')

    def test_get_or_open_file(self):
        filemock = mock.MagicMock()
        filemock.name = self.filename

        # filename provided
        with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as m:
            m.return_value = filemock
            self.kls._get_or_open_file(self.filename)
            m.assert_called_once_with(self.filename)

        # file-like object provided
        with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as m:
            m.return_value = filemock
            self.kls._get_or_open_file(filemock)
            m.assert_not_called()

        # file-like object provided but has no read or write attributes
        with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as m:
            del filemock.read  # pretend there's no read attribute
            del filemock.write  # pretend there's no write attribute'
            m.return_value = filemock

            with self.assertRaises(TypeError) as e:
                self.kls._get_or_open_file(filemock)
            m.assert_not_called()
            self.assertEqual(e.exception.args[0],
                             'filename must be str or bytes, or a file')

        with self.assertRaises(TypeError) as e:
            self.kls._get_or_open_file(1)
        self.assertEqual(e.exception.args[0],
                         'filename must be str or bytes, or a file')

    def test_get_file_info(self):
        # The name of the method being tested, expected attributes,
        # and the expected return value
        # _get_file_size is tested separately (below) because it
        # relies on methods instead of attributes
        method_info = [
            (self.kls._get_file_name, ['name'], self.filename),
            (self.kls._get_file_type, ['name'], self.filetype),
            (self.kls._get_file_encoding, ['encoding'], self.encoding)
        ]

        for method, attrs, exp in method_info:
            with self.subTest(method=method, attrs=attrs, exp=exp):
                filemock = mock.MagicMock()

                # Set attributes for testing
                filemock.name = self.filename
                filemock.encoding = self.encoding

                # filename provided
                with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as m:
                    m.return_value = filemock
                    out = method(exp)
                    self.assertEqual(out, exp)
                    m.assert_called_once_with(exp)

                # filename provided but is missing attributes
                with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as m:
                    for attr in attrs:
                        delattr(filemock, attr)
                    m.return_value = filemock

                    with self.assertRaises(TypeError) as e:
                        method(exp)
                    self.assertEqual(e.exception.args[0],
                                     'Expected file-like object')
                    m.assert_called_once_with(exp)

                # file-like object provided
                filemock = mock.MagicMock()

                # Set attributes for testing
                filemock.name = self.filename
                filemock.encoding = self.encoding

                with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as m:
                    m.return_value = filemock
                    out = method(filemock)
                    self.assertEqual(out, exp)
                    m.assert_not_called()

                # missing attributes
                with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as m:
                    for attr in attrs:
                        delattr(filemock, attr)
                    m.return_value = filemock

                    with self.assertRaises(TypeError) as e:
                        method(filemock)
                    self.assertEqual(e.exception.args[0],
                                     'Expected file-like object')
                    m.assert_not_called()

        # _get_file_size is a little bit special in that it expects
        # methods instead of attributes, and methods are mocked
        # differently than attributes
        filemock = mock.MagicMock()
        filemock.tell.return_value = self.filesize

        # filename provided
        with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as m:
            m.return_value = filemock
            out = self.kls._get_file_size(self.filename)
            self.assertEqual(out, self.filesize)
            m.assert_called_once_with(self.filename)

        # filename provided but is missing attributes
        with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as m:
            del filemock.seek
            m.return_value = filemock

            with self.assertRaises(TypeError) as e:
                self.kls._get_file_size(self.filename)
            self.assertEqual(e.exception.args[0], 'Expected file-like object')
            m.assert_called_once_with(self.filename)

        # file-like object provided
        filemock = mock.MagicMock()
        filemock.tell.return_value = self.filesize

        with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as m:
            m.return_value = filemock
            out = self.kls._get_file_size(filemock)
            self.assertEqual(out, self.filesize)
            m.assert_not_called()

        # missing attributes
        with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as m:
            del filemock.seek
            m.return_value = filemock

            with self.assertRaises(TypeError) as e:
                self.kls._get_file_size(filemock)
            self.assertEqual(e.exception.args[0], 'Expected file-like object')
            m.assert_not_called()

    @mock.patch.object(os.path, 'isfile')
    def test_assert_file_exists(self, mock_exists):
        mock_exists.return_value = True
        self.kls.assertFileExists(self.filename)

        with self.assertRaises(AssertionError) as e:
            self.kls.assertFileNotExists(self.filename)
        self.assertEqual(e.exception.args[0], '%s exists' % self.filename)

        mock_exists.return_value = False
        self.kls.assertFileNotExists(self.filename)

        with self.assertRaises(AssertionError) as e:
            self.kls.assertFileExists(self.filename)
        self.assertEqual(
                e.exception.args[0], '%s does not exist' % self.filename)

    @mock.patch.object(mixins.FileMixins, '_get_file_name')
    def test_assert_file_name_equal(self, mock_get):
        mock_get.return_value = self.filename

        filemock = mock.MagicMock()
        filemock.name = self.filename

        with mock.patch.object(unittest.TestCase, 'assertEqual') as m:
            # filename provided
            self.kls.assertFileNameEqual(self.filename, self.filename)
            m.assert_called_with(self.filename, self.filename, msg=None)

            self.kls.assertFileNameEqual(
                    self.filename, self.filename, msg='override')
            m.assert_called_with(self.filename, self.filename, msg='override')

            # file-like object provided
            self.kls.assertFileNameEqual(filemock, name=self.filename)
            m.assert_called_with(self.filename, self.filename, msg=None)

            self.kls.assertFileNameEqual(
                    filemock, self.filename, msg='override')
            m.assert_called_with(self.filename, self.filename, msg='override')

        with mock.patch.object(unittest.TestCase, 'assertNotEqual') as m:
            # filename provided
            self.kls.assertFileNameNotEqual(self.filename, self.filename)
            m.assert_called_with(self.filename, self.filename, msg=None)

            self.kls.assertFileNameNotEqual(
                    self.filename, self.filename, msg='override')
            m.assert_called_with(self.filename, self.filename, msg='override')

            # file-like object provided
            self.kls.assertFileNameNotEqual(filemock, self.filename)
            m.assert_called_with(self.filename, self.filename, msg=None)

            self.kls.assertFileNameNotEqual(
                    filemock, self.filename, msg='override')
            m.assert_called_with(self.filename, self.filename, msg='override')

    @mock.patch.object(mixins.FileMixins, '_get_file_name')
    def test_assert_file_name_regex(self, mock_get):
        mock_get.return_value = self.filename

        filemock = mock.MagicMock()
        filemock.name = self.filename

        with mock.patch.object(unittest.TestCase, 'assertRegex') as m:
            # filename provided
            self.kls.assertFileNameRegex(self.filename, self.regex)
            m.assert_called_with(self.filename, self.regex, msg=None)

            self.kls.assertFileNameRegex(
                    self.filename, self.regex, msg='override')
            m.assert_called_with(self.filename, self.regex, msg='override')

            # file-like object provided
            self.kls.assertFileNameRegex(filemock, self.regex)
            m.assert_called_with(self.filename, self.regex, msg=None)

            self.kls.assertFileNameRegex(filemock, self.regex, msg='override')
            m.assert_called_with(self.filename, self.regex, msg='override')

        with mock.patch.object(unittest.TestCase, 'assertNotRegex') as m:
            # filename provided
            self.kls.assertFileNameNotRegex(self.filename, self.regex)
            m.assert_called_with(self.filename, self.regex, msg=None)

            self.kls.assertFileNameNotRegex(
                    self.filename, self.regex, msg='override')
            m.assert_called_with(self.filename, self.regex, msg='override')

            # file-like object provided
            self.kls.assertFileNameNotRegex(filemock, self.regex)
            m.assert_called_with(self.filename, self.regex, msg=None)

            self.kls.assertFileNameNotRegex(filemock, self.regex, msg='override')
            m.assert_called_with(self.filename, self.regex, msg='override')

    @mock.patch.object(mixins.FileMixins, '_get_file_type')
    def test_assert_file_type_equal(self, mock_get):
        mock_get.return_value = self.filetype

        filemock = mock.MagicMock()
        filemock.name = self.filename

        with mock.patch.object(unittest.TestCase, 'assertEqual') as m:
            # filename provided
            self.kls.assertFileTypeEqual(self.filename, '.csv')
            m.assert_called_with('.csv', '.csv', msg=None)

            self.kls.assertFileTypeEqual(self.filename, '.csv', msg='override')
            m.assert_called_with('.csv', '.csv', msg='override')

            # file-like object provided
            self.kls.assertFileTypeEqual(filemock, '.csv')
            m.assert_called_with('.csv', '.csv', msg=None)

            self.kls.assertFileTypeEqual(filemock, '.csv', msg='override')
            m.assert_called_with('.csv', '.csv', msg='override')

        with mock.patch.object(unittest.TestCase, 'assertNotEqual') as m:
            # filename argument provided
            self.kls.assertFileTypeNotEqual(self.filename, '.csv')
            m.assert_called_with('.csv', '.csv', msg=None)

            self.kls.assertFileTypeNotEqual(
                    self.filename, '.csv', msg='override')
            m.assert_called_with('.csv', '.csv', msg='override')

            # file-like object provided
            self.kls.assertFileTypeNotEqual(filemock, '.csv')
            m.assert_called_with('.csv', '.csv', msg=None)

            self.kls.assertFileTypeNotEqual(filemock, '.csv', msg='override')
            m.assert_called_with('.csv', '.csv', msg='override')

    @mock.patch.object(mixins.FileMixins, '_get_file_encoding')
    def test_assert_file_encoding_equal(self, mock_get):
        mock_get.return_value = self.encoding

        filemock = mock.MagicMock()
        filemock.name = self.filename
        filemock.encoding = self.encoding

        with mock.patch.object(unittest.TestCase, 'assertEqual') as m:
            # filename provided
            with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as mo:
                mo.return_value = filemock

                msg = '%s is not %s encoded' % (self.filename, self.encoding)
                self.kls.assertFileEncodingEqual(self.filename, self.encoding)
                mo.assert_called_with(self.filename)
                m.assert_called_with('utf-8', self.encoding, msg)

                over_msg = self._formatMessage('override', msg)
                self.kls.assertFileEncodingEqual(self.filename,
                                                 self.encoding,
                                                 msg='override')
                mo.assert_called_with(self.filename)
                m.assert_called_with('utf-8', self.encoding, over_msg)

            # file-like object provided
            self.kls.assertFileEncodingEqual(filemock, self.encoding)
            m.assert_called_with('utf-8', self.encoding, msg)

            self.kls.assertFileEncodingEqual(filemock,
                                             self.encoding,
                                             msg='override')
            m.assert_called_with('utf-8', self.encoding, over_msg)

        with mock.patch.object(unittest.TestCase, 'assertNotEqual') as m:
            # filename provided
            with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as mo:
                mo.return_value = filemock

                msg = '%s is %s encoded' % (self.filename, self.encoding)
                self.kls.assertFileEncodingNotEqual(self.filename,
                                                    self.encoding)
                mo.assert_called_with(self.filename)
                m.assert_called_with('utf-8', self.encoding, msg)

                over_msg = self._formatMessage('override', msg)
                self.kls.assertFileEncodingNotEqual(self.filename,
                                                    self.encoding,
                                                    msg='override')
                mo.assert_called_with(self.filename)
                m.assert_called_with('utf-8', self.encoding, over_msg)

            # file-like object provided
            self.kls.assertFileEncodingNotEqual(filemock, self.encoding)
            m.assert_called_with('utf-8', self.encoding, msg)

            self.kls.assertFileEncodingNotEqual(filemock,
                                                self.encoding,
                                                msg='override')
            m.assert_called_with('utf-8', self.encoding, over_msg)

    @mock.patch.object(mixins.FileMixins, '_get_file_encoding')
    def test_assert_file_size_equalities(self, mock_get):
        '''assertFileSize* equality assertions => unittest equality assertions'''
        mock_get.return_value = self.filesize

        filemock = mock.MagicMock()
        filemock.tell.return_value = self.filesize

        assert_map = {
            self.kls.assertFileSizeEqual: 'assertEqual',
            self.kls.assertFileSizeNotEqual: 'assertNotEqual',
            self.kls.assertFileSizeGreater: 'assertGreater',
            self.kls.assertFileSizeGreaterEqual: 'assertGreaterEqual',
            self.kls.assertFileSizeLess: 'assertLess',
            self.kls.assertFileSizeLessEqual: 'assertLessEqual'
        }

        for trivial, original in assert_map.items():
            with self.subTest(trivial=trivial, original=original):
                with mock.patch.object(unittest.TestCase, original) as m:
                    # filename provided
                    with mock.patch(
                            'marbles.mixins.mixins.open', mock.mock_open()) as mo:
                        mo.return_value = filemock

                        trivial(self.filename, 10)
                        mo.assert_called_with(self.filename)
                        m.assert_called_with(10, 10, msg=None)

                        trivial(self.filename, 10, msg='override')
                        mo.assert_called_with(self.filename)
                        m.assert_called_with(10, 10, msg='override')

                    # file-like object provided
                    trivial(filemock, 10)
                    m.assert_called_with(10, 10, msg=None)

                    trivial(filemock, 10, msg='override')
                    m.assert_called_with(10, 10, msg='override')

        with mock.patch.object(unittest.TestCase, 'assertAlmostEqual') as m:
            # filename provided
            with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as mo:
                mo.return_value = filemock

                self.kls.assertFileSizeAlmostEqual(self.filename, 10)
                mo.assert_called_with(self.filename)
                m.assert_called_with(10, 10, places=None, msg=None, delta=None)

                self.kls.assertFileSizeAlmostEqual(self.filename,
                                                   10,
                                                   msg='override')
                mo.assert_called_with(self.filename)
                m.assert_called_with(
                        10, 10, places=None, msg='override', delta=None)

                self.kls.assertFileSizeAlmostEqual(self.filename, 10, places=1)
                mo.assert_called_with(self.filename)
                m.assert_called_with(10, 10, places=1, msg=None, delta=None)

                self.kls.assertFileSizeAlmostEqual(
                        filename=self.filename, size=10, delta=1)
                mo.assert_called_with(self.filename)
                m.assert_called_with(
                        10, 10, places=None, msg=None, delta=1)

            # file-like object provided
            self.kls.assertFileSizeAlmostEqual(filemock, 10)
            m.assert_called_with(10, 10, places=None, msg=None, delta=None)

            self.kls.assertFileSizeAlmostEqual(filemock, 10, msg='override')
            m.assert_called_with(
                    10, 10, places=None, msg='override', delta=None)

            self.kls.assertFileSizeAlmostEqual(filemock, 10, places=1)
            m.assert_called_with(10, 10, places=1, msg=None, delta=None)

            self.kls.assertFileSizeAlmostEqual(filemock, 10, delta=1)
            m.assert_called_with(10, 10, places=None, msg=None, delta=1)

        with mock.patch.object(unittest.TestCase, 'assertNotAlmostEqual') as m:
            # filename provided
            with mock.patch('marbles.mixins.mixins.open', mock.mock_open()) as mo:
                mo.return_value = filemock

                self.kls.assertFileSizeNotAlmostEqual(self.filename, 10)
                mo.assert_called_with(self.filename)
                m.assert_called_with(10, 10, places=None, msg=None, delta=None)

                self.kls.assertFileSizeNotAlmostEqual(self.filename,
                                                      10,
                                                      msg='override')
                mo.assert_called_with(self.filename)
                m.assert_called_with(
                        10, 10, places=None, msg='override', delta=None)

                self.kls.assertFileSizeNotAlmostEqual(self.filename,
                                                      10,
                                                      places=1)
                mo.assert_called_with(self.filename)
                m.assert_called_with(10, 10, places=1, msg=None, delta=None)

                self.kls.assertFileSizeNotAlmostEqual(self.filename,
                                                      10,
                                                      delta=1)
                mo.assert_called_with(self.filename)
                m.assert_called_with(10, 10, places=None, msg=None, delta=1)

            # file-like object provided
            self.kls.assertFileSizeNotAlmostEqual(filemock, 10)
            m.assert_called_with(10, 10, places=None, msg=None, delta=None)

            self.kls.assertFileSizeNotAlmostEqual(filemock, 10, msg='override')
            m.assert_called_with(
                    10, 10, places=None, msg='override', delta=None)

            self.kls.assertFileSizeNotAlmostEqual(filemock, 10, places=1)
            m.assert_called_with(10, 10, places=1, msg=None, delta=None)

            self.kls.assertFileSizeNotAlmostEqual(filemock, 10, delta=1)
            m.assert_called_with(10, 10, places=None, msg=None, delta=1)


class TestCategoricalMixins(unittest.TestCase):

    def setUp(self):
        class TestCategorical(unittest.TestCase, mixins.CategoricalMixins): pass  # noqa: E701

        setattr(self, 'kls', TestCategorical())
        setattr(self, 'levels1', [1, 2, 3, 2, 1])
        setattr(self, 'levels2', [1, 1, 2, 2, 3])
        setattr(self, 'levels3', ['x', 'y', 'z'])

    def tearDown(self):
        delattr(self, 'kls')
        delattr(self, 'levels1')
        delattr(self, 'levels2')
        delattr(self, 'levels3')

    def test_type_checking(self):
        '''Is an AssertionError raised if either argument is not iterable?'''
        typed_asserts = [
            self.kls.assertCategoricalLevelsEqual,
            self.kls.assertCategoricalLevelsNotEqual
        ]
        msg = '%s argument is not iterable'

        for tassert in typed_asserts:
            with self.subTest(tassert=tassert):
                with self.assertRaises(TypeError) as e:
                    tassert(10, [1, 2, 3])
                self.assertTrue(e.exception.args[0].endswith(msg % 'First'))

                with self.assertRaises(TypeError) as e:
                    tassert([1, 2, 3], None)
                self.assertTrue(e.exception.args[0].endswith(msg % 'Second'))

        typed_asserts = [
            self.kls.assertCategoricalLevelIn,
            self.kls.assertCategoricalLevelNotIn
        ]

        for tassert in typed_asserts:
            with self.subTest(tassert=tassert):
                with self.assertRaises(TypeError) as e:
                    tassert(10, None)
                self.assertTrue(e.exception.args[0].endswith(msg % 'Second'))

    def test_assert_categorical_level_equalities(self):
        self.kls.assertCategoricalLevelsEqual(self.levels1, self.levels2)

        msg = '%s levels != %s levels' % (self.levels1, self.levels3)
        with self.assertRaises(AssertionError) as e:
            self.kls.assertCategoricalLevelsEqual(self.levels1, self.levels3)
        self.assertEqual(e.exception.args[0], msg)

        self.kls.assertCategoricalLevelsNotEqual(self.levels1, self.levels3)

        msg = '%s levels == %s levels' % (self.levels1, self.levels2)
        with self.assertRaises(AssertionError) as e:
            self.kls.assertCategoricalLevelsNotEqual(self.levels1, self.levels2)
        self.assertEqual(e.exception.args[0], msg)

        # unhashable types
        self.kls.assertCategoricalLevelsEqual([set([1, 2, 3])],
                                              [set([1, 2, 3])])

        msg = '%s levels != %s levels' % ([set([1, 2, 3])],
                                          [set([1, 2, 3]), set([2, 3, 4])])
        with self.assertRaises(AssertionError) as e:
            self.kls.assertCategoricalLevelsEqual([set([1, 2, 3])],
                                                  [set([1, 2, 3]),
                                                   set([2, 3, 4])])
        self.assertEqual(e.exception.args[0], msg)

        self.kls.assertCategoricalLevelsNotEqual([set([1, 2, 3])],
                                                 [set([1, 2, 3]),
                                                  set([2, 3, 4])])

        msg = '%s levels == %s levels' % ([set([1, 2, 3])], [set([1, 2, 3])])
        with self.assertRaises(AssertionError) as e:
            self.kls.assertCategoricalLevelsNotEqual([set([1, 2, 3])],
                                                     [set([1, 2, 3])])
        self.assertEqual(e.exception.args[0], msg)

    def test_trivial_asserts(self):
        assert_map = {
            self.kls.assertCategoricalLevelIn: 'assertIn',
            self.kls.assertCategoricalLevelNotIn: 'assertNotIn'
        }

        for trivial, original in assert_map.items():
            with self.subTest(trivial=trivial, original=original):
                with mock.patch.object(unittest.TestCase, original) as m:
                    trivial('foo', 'bar')
                    m.assert_called_with('foo', 'bar', msg=None)

                    trivial('foo', 'bar', msg='override')
                    m.assert_called_with('foo', 'bar', msg='override')


class TestDateTimeMixins(unittest.TestCase):

    def setUp(self):
        class TestDateTime(unittest.TestCase, mixins.DateTimeMixins): pass  # noqa: E701,E301

        setattr(self, 'kls', TestDateTime())
        setattr(self, 'tz', timezone.utc)
        setattr(self, 'dt', datetime(2016, 1, 1, 1, 9, 0, tzinfo=self.tz))
        setattr(self, 'pdates', [
            datetime.today() - timedelta(7),
            datetime.today() - timedelta(6),
            datetime.today() - timedelta(5),
            datetime.today() - timedelta(4),
            datetime.today() - timedelta(3),
            datetime.today() - timedelta(2),
            datetime.today() - timedelta(1)
        ])
        setattr(self, 'fdates', [
            datetime.today() + timedelta(7),
            datetime.today() + timedelta(6),
            datetime.today() + timedelta(5),
            datetime.today() + timedelta(4),
            datetime.today() + timedelta(3),
            datetime.today() + timedelta(2),
            datetime.today() + timedelta(1)
        ])

    def tearDown(self):
        delattr(self, 'kls')
        delattr(self, 'dt')
        delattr(self, 'pdates')
        delattr(self, 'fdates')

    def test_type_checking(self):
        msg = 'Expected iterable of datetime or date objects'
        with self.assertRaises(TypeError) as e:
            self.kls.assertDateTimesPast([1, 2, 3])
        self.assertEqual(e.exception.args[0], msg)

        with self.assertRaises(TypeError) as e:
            self.kls.assertDateTimesFuture([1, 2, 3])
        self.assertEqual(e.exception.args[0], msg)

        # assertions that require sequence to contain a date(time)
        methods = [
            self.kls.assertDateTimesLagEqual,
            self.kls.assertDateTimesLagLess,
            self.kls.assertDateTimesLagLessEqual
        ]

        msg = 'Expected iterable of datetime or date objects'
        for method in methods:
            with self.subTest(method=method):
                with self.assertRaises(TypeError) as e:
                    method([1, 2, 3], timedelta(2))
                self.assertEqual(e.exception.args[0], msg)

        msg = 'Second argument is not a datetime or date object or iterable'
        with self.assertRaises(TypeError) as e:
            self.kls.assertDateTimesBefore(self.pdates, 1)
        self.assertEqual(e.exception.args[0], msg)

        with self.assertRaises(TypeError) as e:
            self.kls.assertDateTimesAfter(self.pdates, 1)
        self.assertEqual(e.exception.args[0], msg)

        # assertions that require an iterable and a timedelta
        methods = [
            self.kls.assertDateTimesFrequencyEqual,
            self.kls.assertDateTimesLagEqual,
            self.kls.assertDateTimesLagLess,
            self.kls.assertDateTimesLagLessEqual
        ]

        for method in methods:
            with self.subTest(method=method):
                msg = ('First argument is not iterable',
                       'Second argument is not a timedelta object')
                with self.assertRaises(TypeError) as e:
                    method(1, timedelta(2))
                self.assertTrue(e.exception.args[0].endswith(msg[0]))

                with self.assertRaises(TypeError) as e:
                    method([1, 2, 3], 2)
                self.assertTrue(e.exception.args[0].endswith(msg[1]))

        with self.assertRaises(TypeError) as e:
            self.kls.assertDateTimesPast(1)
        self.assertTrue(e.exception.args[0].endswith(msg[0]))

        with self.assertRaises(TypeError) as e:
            self.kls.assertDateTimesFuture(1)
        self.assertTrue(e.exception.args[0].endswith(msg[0]))

        with self.assertRaises(TypeError) as e:
            self.kls.assertDateTimesBefore(1, [1])
        self.assertTrue(e.exception.args[0].endswith(msg[0]))

        with self.assertRaises(TypeError) as e:
            self.kls.assertDateTimesAfter(1, [1])
        self.assertTrue(e.exception.args[0].endswith(msg[0]))

        msg = 'First argument is not a datetime object'
        with self.assertRaises(TypeError) as e:
            self.kls.assertTimeZoneIsNone(10)
        self.assertTrue(e.exception.args[0].endswith(msg))

        with self.assertRaises(TypeError) as e:
            self.kls.assertTimeZoneIsNotNone(date.today())
        self.assertTrue(e.exception.args[0].endswith(msg))

        msg = ('First argument is not a datetime object',
               'Second argument is not a timezone object')
        with self.assertRaises(TypeError) as e:
            self.kls.assertTimeZoneEqual(10, timezone.utc)
        self.assertTrue(e.exception.args[0].endswith(msg[0]))

        with self.assertRaises(TypeError) as e:
            self.kls.assertTimeZoneEqual(datetime.now(), 'UTC')
        self.assertTrue(e.exception.args[0].endswith(msg[1]))

        with self.assertRaises(TypeError) as e:
            self.kls.assertTimeZoneNotEqual(10, timezone.utc)
        self.assertTrue(e.exception.args[0].endswith(msg[0]))

        with self.assertRaises(TypeError) as e:
            self.kls.assertTimeZoneNotEqual(datetime.now(), 'UTC')
        self.assertTrue(e.exception.args[0].endswith(msg[1]))

    def test_before(self):
        # sequence of targets provided
        self.kls.assertDateTimesBefore(self.pdates, self.fdates)

        self.kls.assertDateTimesBefore(self.pdates, self.pdates, strict=False)
        with self.assertRaises(AssertionError):
            self.kls.assertDateTimesBefore(self.pdates, self.pdates)

        msg = ('Length mismatch: '
               'first argument contains %s elements, '
               'second argument contains %s elements' % (len(self.pdates),
                                                         len(self.pdates) - 1))
        with self.assertRaises(ValueError) as e:
            self.kls.assertDateTimesBefore(self.pdates, self.fdates[:-1])
        self.assertTrue(e.exception.args[0].endswith(msg))

        msg = '%s is not less than %s'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesBefore(self.fdates, self.pdates)
        self.assertTrue(e.exception.args[0], msg % (self.fdates, self.pdates))

        msg = '%s is not strictly less than %s'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesBefore(
                    self.fdates, self.pdates, strict=True)
        self.assertTrue(e.exception.args[0], msg % (self.fdates, self.pdates))

        # datetimes provided
        target = datetime.now()
        self.kls.assertDateTimesBefore(self.pdates, target, strict=False)

        msg = '%s is not strictly less than'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesBefore(self.fdates, target, strict=True)
        self.assertTrue(e.exception.args[0].startswith(msg % self.fdates))

        msg = '%s is not less than'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesBefore(self.fdates, target, strict=False)
        self.assertTrue(e.exception.args[0].startswith(msg % self.fdates))

        # dates provided
        target = date.today()
        self.fdates = [x.date() for x in self.fdates]
        self.pdates = [x.date() for x in self.pdates]

        self.kls.assertDateTimesBefore(self.pdates, target, strict=False)

        msg = '%s is not strictly less than %s'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesBefore(self.fdates, target, strict=True)
        self.assertEqual(e.exception.args[0], msg % (self.fdates, target))

        msg = '%s is not less than %s'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesBefore(self.fdates, target, strict=False)
        self.assertEqual(e.exception.args[0], msg % (self.fdates, target))

    def test_after(self):
        # sequence of targets provided
        self.kls.assertDateTimesAfter(self.fdates, self.pdates)

        self.kls.assertDateTimesAfter(self.pdates, self.pdates, strict=False)
        with self.assertRaises(AssertionError):
            self.kls.assertDateTimesAfter(self.fdates, self.fdates)

        msg = ('Length mismatch: '
               'first argument contains %s elements, '
               'second argument contains %s elements' % (len(self.pdates),
                                                         len(self.pdates) - 1))
        with self.assertRaises(ValueError) as e:
            self.kls.assertDateTimesAfter(self.fdates, self.pdates[:-1])
        self.assertTrue(e.exception.args[0].endswith(msg))

        msg = '%s is not greater than %s'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesAfter(self.pdates, self.fdates)
        self.assertTrue(e.exception.args[0], msg % (self.pdates, self.fdates))

        msg = '%s is not strictly greater than %s'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesAfter(self.pdates, self.fdates, strict=True)
        self.assertTrue(e.exception.args[0], msg % (self.pdates, self.fdates))

        # datetimes provided
        target = datetime.now()
        self.kls.assertDateTimesAfter(self.fdates, target, strict=False)

        msg = '%s is not strictly greater than'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesAfter(self.pdates, target, strict=True)
        self.assertTrue(e.exception.args[0].startswith(msg % self.pdates))

        msg = '%s is not greater than'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesAfter(self.pdates, target, strict=False)
        self.assertTrue(e.exception.args[0].startswith(msg % self.pdates))

        # dates provided
        target = date.today()
        self.pdates = [x.date() for x in self.pdates]
        self.fdates = [x.date() for x in self.fdates]

        self.kls.assertDateTimesAfter(self.fdates, target, strict=False)

        msg = '%s is not strictly greater than %s'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesAfter(self.pdates, target, strict=True)
        self.assertEqual(e.exception.args[0], msg % (self.pdates, target))

        msg = '%s is not greater than %s'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesAfter(self.pdates, target, strict=False)
        self.assertEqual(e.exception.args[0], msg % (self.pdates, target))

    @mock.patch.object(mixins.DateTimeMixins, 'assertDateTimesBefore')
    def test_past(self, mock_assert_before):
        target = date.today()

        # datetimes provided
        self.kls.assertDateTimesPast(self.pdates)
        self.assertEqual(mock_assert_before.call_args[0][0], self.pdates)

        self.assertIsInstance(mock_assert_before.call_args[0][1], datetime)
        self.assertEqual(mock_assert_before.call_args[0][1].date(), target)

        # dates provided
        self.pdates = [x.date() for x in self.pdates]

        self.kls.assertDateTimesPast(self.pdates)
        self.assertEqual(mock_assert_before.call_args[0][0], self.pdates)

        self.assertIsInstance(mock_assert_before.call_args[0][1], date)
        self.assertEqual(mock_assert_before.call_args[0][1], target)

    @mock.patch.object(mixins.DateTimeMixins, 'assertDateTimesAfter')
    def test_future(self, mock_assert_after):
        target = date.today()

        # datetimes provided
        self.kls.assertDateTimesFuture(self.fdates)
        self.assertEqual(mock_assert_after.call_args[0][0], self.fdates)

        self.assertIsInstance(mock_assert_after.call_args[0][1], datetime)
        self.assertEqual(mock_assert_after.call_args[0][1].date(), target)

        # dates provided
        self.fdates = [x.date() for x in self.fdates]

        self.kls.assertDateTimesFuture(self.fdates)
        self.assertEqual(mock_assert_after.call_args[0][0], self.fdates)

        self.assertIsInstance(mock_assert_after.call_args[0][1], date)
        self.assertEqual(mock_assert_after.call_args[0][1], target)

    def test_frequency(self):
        self.pdates = [x.date() for x in self.pdates]
        self.fdates = [x.date() for x in self.fdates]

        self.kls.assertDateTimesFrequencyEqual(self.pdates, timedelta(1))
        self.kls.assertDateTimesFrequencyEqual(self.fdates, timedelta(-1))

        self.kls.assertDateTimesFrequencyEqual(self.pdates,
                                               timedelta(hours=24))
        self.kls.assertDateTimesFrequencyEqual(self.fdates,
                                               timedelta(hours=-24))

        msg = 'unexpected frequencies found in %s'
        with self.assertRaises(AssertionError) as e:
            self.kls.assertDateTimesFrequencyEqual(self.pdates, timedelta(2))
        self.assertEqual(e.exception.args[0], msg % (self.pdates,))

    def test_lag(self):
        with mock.patch.object(unittest.TestCase, 'assertEqual') as m:
            # datetimes provided
            diff = datetime.now() - max(self.pdates)
            self.kls.assertDateTimesLagEqual(self.pdates, diff)
            self.assertTrue(m.called)

        with mock.patch.object(unittest.TestCase, 'assertEqual') as m:
            # dates provided
            diff = date.today() - max(self.pdates).date()
            self.kls.assertDateTimesLagEqual(
                    [x.date() for x in self.pdates], diff)
            m.assert_called_once_with(diff, diff, msg=None)

        with self.assertRaises(AssertionError):
            self.kls.assertDateTimesLagEqual(self.pdates, timedelta(10))

        with mock.patch.object(unittest.TestCase, 'assertLess') as m:
            # datetimes provided
            self.kls.assertDateTimesLagLess(self.pdates, timedelta(2))
            self.assertTrue(m.called)

        with mock.patch.object(unittest.TestCase, 'assertLess') as m:
            # dates provided
            diff = date.today() - max(self.pdates).date()
            self.kls.assertDateTimesLagLess(
                    [x.date() for x in self.pdates], timedelta(2))
            m.assert_called_once_with(diff, timedelta(2), msg=None)

        with self.assertRaises(AssertionError):
            self.kls.assertDateTimesLagLess(self.pdates, timedelta(1))

        with mock.patch.object(unittest.TestCase, 'assertLessEqual') as m:
            # datetimes provided
            self.kls.assertDateTimesLagLessEqual(self.pdates, timedelta(2))
            self.assertTrue(m.called)

        with mock.patch.object(unittest.TestCase, 'assertLessEqual') as m:
            # dates provided
            diff = date.today() - max(self.pdates).date()
            self.kls.assertDateTimesLagLessEqual(
                    [x.date() for x in self.pdates], timedelta(2))
            m.assert_called_once_with(diff, timedelta(2), msg=None)

        with self.assertRaises(AssertionError):
            self.kls.assertDateTimesLagLess(self.pdates, timedelta(0))

    def test_assert_time_zone_equalities(self):
        with mock.patch.object(unittest.TestCase, 'assertIsNone') as m:
            self.kls.assertTimeZoneIsNone(self.dt)
            m.assert_called_with(self.dt.tzinfo, msg=None)

            self.kls.assertTimeZoneIsNone(self.dt, msg='override')
            m.assert_called_with(self.dt.tzinfo, msg='override')

        with mock.patch.object(unittest.TestCase, 'assertIsNotNone') as m:
            self.kls.assertTimeZoneIsNotNone(self.dt)
            m.assert_called_with(self.dt.tzinfo, msg=None)

            self.kls.assertTimeZoneIsNotNone(self.dt, msg='override')
            m.assert_called_with(self.dt.tzinfo, msg='override')

        with mock.patch.object(unittest.TestCase, 'assertEqual') as m:
            self.kls.assertTimeZoneEqual(self.dt, self.tz)
            m.assert_called_with(self.dt.tzinfo, self.tz, msg=None)

            self.kls.assertTimeZoneEqual(self.dt, self.tz, msg='override')
            m.assert_called_with(self.dt.tzinfo, self.tz, msg='override')

        with mock.patch.object(unittest.TestCase, 'assertNotEqual') as m:
            self.kls.assertTimeZoneNotEqual(self.dt, self.tz)
            m.assert_called_with(self.dt.tzinfo, self.tz, msg=None)

            self.kls.assertTimeZoneNotEqual(self.dt, self.tz, msg='override')
            m.assert_called_with(self.dt.tzinfo, self.tz, msg='override')


if __name__ == '__main__':
    unittest.main()
