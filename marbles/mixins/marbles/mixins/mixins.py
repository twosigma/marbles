#
#  Copyright (c) 2018 Two Sigma Open Source, LLC
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

'''This module provides custom :mod:`unittest`-style assertions. For
the most part, :mod:`marbles.mixins` assertions trivially wrap
:mod:`unittest` assertions. For example, a call to
:meth:`CategoricalMixins.assertCategoricalLevelIn` will simply pass the
provided arguments to :meth:`~unittest.TestCase.assertIn`.

Custom assertions are provided via mixins so that they can use other
assertions as building blocks. Using mixins, instead of straight
inheritance, means that users can compose multiple mixins to create
a test case with all the assertions that they need.

.. warning::

    :mod:`marbles.mixins` can be mixed into a
    :class:`unittest.TestCase`, a :class:`marbles.core.TestCase`,
    a :class:`marbles.core.AnnotatedTestCase`, or any other class that
    implements a :class:`unittest.TestCase` interface. To enforce
    this, mixins define `abstract methods <abc>`_. This means that,
    when mixing them into your test case, they must come `after` the
    class(es) that implement those methods instead of appearing first
    in the inheritance list like normal mixins.

    .. _abc: https://docs.python.org/3.5/library/abc.html#abc.abstractmethod

Example:

.. code-block:: python

    import unittest

    from marbles.core import marbles
    from marbles.mixins import mixins


    class MyTestCase(unittest.TestCase, mixins.BetweenMixins):

        def test_me(self):
            self.assertBetween(5, lower=0, upper=10)


    class MyMarblesTestCase(marbles.TestCase, mixins.BetweenMixins):

        def test_me(self):
            self.assertBetween(5, lower=0, upper=10)
'''

import abc
import collections
import operator
import os
from datetime import date, datetime, timedelta, timezone

import pandas as pd

# TODO (jsa): override abc TypeError to inform user that they have to
# inherit from unittest.TestCase (I don't know if this is possible)


class BetweenMixins(abc.ABC):
    '''Built-in assertions about betweenness.'''

    @abc.abstractmethod
    def fail(self, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _formatMessage(self, msg, standardMsg):
        pass  # pragma: no cover

    def assertBetween(self, obj, lower, upper, strict=True, msg=None):
        '''Fail if ``obj`` is not between ``lower`` and ``upper``.

        If ``strict=True`` (default), fail unless
        ``lower < obj < upper``. If ``strict=False``, fail unless
        ``lower <= obj <= upper``.

        This is equivalent to ``self.assertTrue(lower < obj < upper)``
        or ``self.assertTrue(lower <= obj <= upper)``, but with a nicer
        default message.

        Parameters
        ----------
        obj
        lower
        upper
        strict : bool
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.
        '''
        if strict:
            standardMsg = '%s is not strictly between %s and %s' % (
                    obj, lower, upper)
            op = operator.lt
        else:
            standardMsg = '%s is not between %s and %s' % (obj, lower, upper)
            op = operator.le

        if not (op(lower, obj) and op(obj, upper)):
            self.fail(self._formatMessage(msg, standardMsg))

    def assertNotBetween(self, obj, lower, upper, strict=True, msg=None):
        '''Fail if ``obj`` is between ``lower`` and ``upper``.

        If ``strict=True`` (default), fail if ``lower <= obj <=
        upper``. If ``strict=False``, fail if ``lower < obj < upper``.

        This is equivalent to ``self.assertFalse(lower < obj < upper)``
        or ``self.assertFalse(lower <= obj <= upper)``, but with a
        nicer default message.

        Raises
        ------
        ValueError
            If ``lower`` equals ``upper`` and ``strict=True`` is
            specified.

        Parameters
        ----------
        obj
        lower
        upper
        strict : bool
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.
        '''
        if strict:
            standardMsg = '%s is between %s and %s' % (obj, lower, upper)
            op = operator.le
        else:
            standardMsg = '%s is strictly between %s and %s' % (
                    obj, lower, upper)
            op = operator.lt

        # Providing strict=False and a degenerate interval should raise
        # ValueError so the test will error instead of fail
        if (not strict) and (lower == upper):
            raise ValueError('cannot specify strict=False if lower == upper')

        if (op(lower, obj) and op(obj, upper)):
            self.fail(self._formatMessage(msg, standardMsg))


class MonotonicMixins(abc.ABC):
    '''Built-in assertions about monotonicity.'''

    @abc.abstractmethod
    def fail(self):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertIsInstance(self, obj, cls, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _formatMessage(self, msg, standardMsg):
        pass  # pragma: no cover

    @staticmethod
    def _monotonic(op, sequence):
        return all(op(i, j) for i, j in zip(sequence, sequence[1:]))

    def assertMonotonicIncreasing(self, sequence, strict=True, msg=None):
        '''Fail if ``sequence`` is not monotonically increasing.

        If ``strict=True`` (default), fail unless each element in
        ``sequence`` is less than the following element as determined
        by the ``<`` operator. If ``strict=False``, fail unless each
        element in ``sequence`` is less than or equal to the following
        element as determined by the ``<=`` operator.

        .. code-block:: python

            assert all((i < j) for i, j in zip(sequence, sequence[1:]))
            assert all((i <= j) for i, j in zip(sequence, sequence[1:]))

        Parameters
        ----------
        sequence : iterable
        strict : bool
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        '''
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')

        if strict:
            standardMsg = ('Elements in %s are not strictly monotonically '
                           'increasing') % (sequence,)
            op = operator.lt
        else:
            standardMsg = ('Elements in %s are not monotonically '
                           'increasing') % (sequence,)
            op = operator.le

        if not self._monotonic(op, sequence):
            self.fail(self._formatMessage(msg, standardMsg))

    def assertNotMonotonicIncreasing(self, sequence, strict=True, msg=None):
        '''Fail if ``sequence`` is monotonically increasing.

        If ``strict=True`` (default), fail if each element in
        ``sequence`` is less than the following element as determined
        by the ``<`` operator. If ``strict=False``, fail if each
        element in ``sequence`` is less than or equal to the following
        element as determined by the ``<=`` operator.

        .. code-block:: python

            assert not all((i < j) for i, j in zip(sequence, sequence[1:]))
            assert not all((i <= j) for i, j in zip(sequence, sequence[1:]))

        Parameters
        ----------
        sequence : iterable
        strict : bool
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        '''
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')

        if strict:
            standardMsg = ('Elements in %s are strictly monotonically '
                           'increasing') % (sequence,)
            op = operator.lt
        else:
            standardMsg = ('Elements in %s are monotonically '
                           'increasing') % (sequence,)
            op = operator.le

        if self._monotonic(op, sequence):
            self.fail(self._formatMessage(msg, standardMsg))

    def assertMonotonicDecreasing(self, sequence, strict=True, msg=None):
        '''Fail if ``sequence`` is not monotonically decreasing.

        If ``strict=True`` (default), fail unless each element in
        ``sequence`` is greater than the following element as
        determined by the ``>`` operator. If ``strict=False``, fail
        unless each element in ``sequence`` is greater than or equal
        to the following element as determined by the ``>=`` operator.

        .. code-block:: python

            assert all((i > j) for i, j in zip(sequence, sequence[1:]))
            assert all((i >= j) for i, j in zip(sequence, sequence[1:]))

        Parameters
        ----------
        sequence : iterable
        strict : bool
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        '''
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')

        if strict:
            standardMsg = ('Elements in %s are not strictly monotonically '
                           'decreasing') % (sequence,)
            op = operator.gt
        else:
            standardMsg = ('Elements in %s are not monotonically '
                           'decreasing') % (sequence,)
            op = operator.ge

        if not self._monotonic(op, sequence):
            self.fail(self._formatMessage(msg, standardMsg))

    def assertNotMonotonicDecreasing(self, sequence, strict=True, msg=None):
        '''Fail if ``sequence`` is monotonically decreasing.

        If ``strict=True`` (default), fail if each element in
        ``sequence`` is greater than the following element as
        determined by the ``>`` operator. If ``strict=False``, fail if
        each element in ``sequence`` is greater than or equal to the
        following element as determined by the ``>=`` operator.

        .. code-block:: python

            assert not all((i > j) for i, j in zip(sequence, sequence[1:]))
            assert not all((i >= j) for i, j in zip(sequence, sequence[1:]))

        Parameters
        ----------
        sequence : iterable
        strict : bool
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        '''
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')

        if strict:
            standardMsg = ('Elements in %s are strictly monotonically '
                           'decreasing') % (sequence,)
            op = operator.gt
        else:
            standardMsg = ('Elements in %s are monotonically '
                           'decreasing') % (sequence,)
            op = operator.ge

        if self._monotonic(op, sequence):
            self.fail(self._formatMessage(msg, standardMsg))


class UniqueMixins(abc.ABC):
    '''Built-in assertions about uniqueness.

    These assertions can handle containers that contain unhashable
    elements.
    '''

    @abc.abstractmethod
    def fail(self, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertIsInstance(self, obj, cls, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _formatMessage(self, msg, standardMsg):
        pass  # pragma: no cover

    def assertUnique(self, container, msg=None):
        '''Fail if elements in ``container`` are not unique.

        Parameters
        ----------
        container : iterable
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``container`` is not iterable.
        '''
        if not isinstance(container, collections.Iterable):
            raise TypeError('First argument is not iterable')

        standardMsg = 'Elements in %s are not unique' % (container,)

        # We iterate over each element in the container instead of
        # comparing len(container) == len(set(container)) to allow
        # for containers that contain unhashable types
        for idx, elem in enumerate(container):
            # If elem appears at an earlier or later index position
            # the elements are not unique
            if elem in container[:idx] or elem in container[idx+1:]:
                self.fail(self._formatMessage(msg, standardMsg))

    def assertNotUnique(self, container, msg=None):
        '''Fail if elements in ``container`` are unique.

        Parameters
        ----------
        container : iterable
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``container`` is not iterable.
        '''
        if not isinstance(container, collections.Iterable):
            raise TypeError('First argument is not iterable')

        standardMsg = 'Elements in %s are unique' % (container,)

        # We iterate over each element in the container instead of
        # comparing len(container) == len(set(container)) to allow
        # for containers that contain unhashable types
        for idx, elem in enumerate(container):
            # If elem appears at an earlier or later index position
            # the elements are not unique
            if elem in container[:idx] or elem in container[idx+1:]:
                return  # succeed fast

        self.fail(self._formatMessage(msg, standardMsg))


class FileMixins(abc.ABC):
    '''Built-in assertions for files.

    With the exception of :meth:`assertFileExists` and
    :meth:`assertFileNotExists`, all custom file assertions take a
    ``filename`` argument which can accept a file name as a
    :class:`str` or :py:class:`bytes` object, or a `file-like object`_.
    Accepting a file-like object is useful for testing files that are
    not present locally, e.g., files in HDFS.

    .. _file-like object: http://docs.python.org/3.5/glossary.html#term-file-like-object

    .. code-block:: python

        import unittest

        import hdfs3
        from marbles.mixins import mixins


        class MyFileTest(unittest.TestCase, mixins.FileMixins):

            def test_file_encoding(self):
                fname = 'myfile.csv'

                # You can pass fname directly to the assertion (if the
                # file exists locally)
                self.assertFileEncodingEqual(fname, 'utf-8')

                # Or open the file and pass a file descriptor to the
                # assertion
                with open(fname) as f:
                    self.assertFileEncodingEqual(f, 'utf-8')

            def test_hdfs_file_encoding(self):
                hdfspath = '/path/to/myfile.csv'

                client = hdfs3.HDFileSystem(host='host', port='port')
                with client.open(hdfspath) as f:
                    self.assertFileEncodingEqual(f, 'utf-8')

    Note that not all file-like objects implement the expected
    interface. These custom file assertions expect the following
    methods and attributes:

        + :meth:`read`
        + :meth:`write`
        + :meth:`seek`
        + :meth:`tell`
        + :attr:`name`
        + :attr:`encoding`
    '''

    @abc.abstractmethod
    def fail(self, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertEqual(self, first, second, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertNotEqual(self, first, second, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertAlmostEqual(self, first, second, places, msg, delta):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertNotAlmostEqual(self, first, second, places, msg, delta):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertGreater(self, a, b, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertGreaterEqual(self, a, b, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertLess(self, a, b, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertLessEqual(self, a, b, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertRegex(self, text, expected_regex, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertNotRegex(self, text, expected_regex, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _formatMessage(self, msg, standardMsg):
        pass  # pragma: no cover

    @staticmethod
    def _get_or_open_file(filename):
        '''If ``filename`` is a string or bytes object, open the
        ``filename`` and return the file object. If ``filename`` is
        file-like (i.e., it has 'read' and 'write' attributes, return
        ``filename``.

        Parameters
        ----------
        filename : str, bytes, file

        Raises
        ------
        TypeError
            If ``filename`` is not a string, bytes, or file-like
            object.

            File-likeness is determined by checking for 'read' and
            'write' attributes.
        '''
        if isinstance(filename, (str, bytes)):
            f = open(filename)
        elif hasattr(filename, 'read') and hasattr(filename, 'write'):
            f = filename
        else:
            raise TypeError('filename must be str or bytes, or a file')
        return f

    def _get_file_name(self, filename):
        f = self._get_or_open_file(filename)

        try:
            fname = f.name
        except AttributeError as e:
            # If f doesn't have an name attribute,
            # raise a TypeError
            if e.args == ('name',):
                raise TypeError('Expected file-like object')
            raise e  # pragma: no cover
        finally:
            f.close()

        return fname

    def _get_file_type(self, filename):
        f = self._get_or_open_file(filename)

        try:
            fname = f.name
        except AttributeError as e:
            # If f doesn't have an name attribute,
            # raise a TypeError
            if e.args == ('name',):
                raise TypeError('Expected file-like object')
            raise e  # pragma: no cover
        else:
            filetype = os.path.splitext(fname)[-1]
        finally:
            f.close()

        return filetype

    def _get_file_encoding(self, filename):
        f = self._get_or_open_file(filename)

        try:
            encoding = f.encoding
        except AttributeError as e:
            # If f doesn't have an encoding attribute,
            # raise a TypeError
            if e.args == ('encoding',):
                raise TypeError('Expected file-like object')
            raise e  # pragma: no cover
        finally:
            f.close()

        return encoding

    def _get_file_size(self, filename):
        f = self._get_or_open_file(filename)

        try:
            f.seek(0, os.SEEK_END)
        except AttributeError as e:
            # If f doesn't have a seek method,
            # raise a TypeError
            if e.args == ('seek',):
                raise TypeError('Expected file-like object')
            raise e  # pragma: no cover
        else:
            length = f.tell()
        finally:
            f.close()

        return length

    def assertFileExists(self, filename, msg=None):
        '''Fail if ``filename`` does not exist as determined by
        ``os.path.isfile(filename)``.

        Parameters
        ----------
        filename : str, bytes
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.
        '''
        standardMsg = '%s does not exist' % filename

        if not os.path.isfile(filename):
            self.fail(self._formatMessage(msg, standardMsg))

    def assertFileNotExists(self, filename, msg=None):
        '''Fail if ``filename`` exists as determined by
        ``~os.path.isfile(filename)``.

        Parameters
        ----------
        filename : str, bytes
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.
        '''
        standardMsg = '%s exists' % filename

        if os.path.isfile(filename):
            self.fail(self._formatMessage(msg, standardMsg))

    def assertFileNameEqual(self, filename, name, msg=None):
        '''Fail if ``filename`` does not have the given ``name`` as
        determined by the ``==`` operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        name : str, byes
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fname = self._get_file_name(filename)
        self.assertEqual(fname, name, msg=msg)

    def assertFileNameNotEqual(self, filename, name, msg=None):
        '''Fail if ``filename`` has the given ``name`` as determined
        by the ``!=`` operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        name : str, byes
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fname = self._get_file_name(filename)
        self.assertNotEqual(fname, name, msg=msg)

    def assertFileNameRegex(self, filename, expected_regex, msg=None):
        '''Fail unless ``filename`` matches ``expected_regex``.

        Parameters
        ----------
        filename : str, bytes, file-like
        expected_regex : str, bytes
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fname = self._get_file_name(filename)
        self.assertRegex(fname, expected_regex, msg=msg)

    def assertFileNameNotRegex(self, filename, expected_regex, msg=None):
        '''Fail if ``filename`` matches ``expected_regex``.

        Parameters
        ----------
        filename : str, bytes, file-like
        expected_regex : str, bytes
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fname = self._get_file_name(filename)
        self.assertNotRegex(fname, expected_regex, msg=msg)

    def assertFileTypeEqual(self, filename, extension, msg=None):
        '''Fail if ``filename`` does not have the given ``extension``
        as determined by the ``==`` operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        extension : str, bytes
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        ftype = self._get_file_type(filename)
        self.assertEqual(ftype, extension, msg=msg)

    def assertFileTypeNotEqual(self, filename, extension, msg=None):
        '''Fail if ``filename`` has the given ``extension`` as
        determined by the ``!=`` operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        extension : str, bytes
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        ftype = self._get_file_type(filename)
        self.assertNotEqual(ftype, extension, msg=msg)

    def assertFileEncodingEqual(self, filename, encoding, msg=None):
        '''Fail if ``filename`` is not encoded with the given
        ``encoding`` as determined by the '==' operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        encoding : str, bytes
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fencoding = self._get_file_encoding(filename)

        fname = self._get_file_name(filename)
        standardMsg = '%s is not %s encoded' % (fname, encoding)

        self.assertEqual(fencoding.lower(),
                         encoding.lower(),
                         self._formatMessage(msg, standardMsg))

    def assertFileEncodingNotEqual(self, filename, encoding, msg=None):
        '''Fail if ``filename`` is encoded with the given ``encoding``
        as determined by the '!=' operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        encoding : str, bytes
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fencoding = self._get_file_encoding(filename)

        fname = self._get_file_name(filename)
        standardMsg = '%s is %s encoded' % (fname, encoding)

        self.assertNotEqual(fencoding.lower(),
                            encoding.lower(),
                            self._formatMessage(msg, standardMsg))

    def assertFileSizeEqual(self, filename, size, msg=None):
        '''Fail if ``filename`` does not have the given ``size`` as
        determined by the '==' operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        size : int, float
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fsize = self._get_file_size(filename)
        self.assertEqual(fsize, size, msg=msg)

    def assertFileSizeNotEqual(self, filename, size, msg=None):
        '''Fail if ``filename`` has the given ``size`` as determined
        by the '!=' operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        size : int, float
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fsize = self._get_file_size(filename)
        self.assertNotEqual(fsize, size, msg=msg)

    def assertFileSizeAlmostEqual(
            self, filename, size, places=None, msg=None, delta=None):
        '''Fail if ``filename`` does not have the given ``size`` as
        determined by their difference rounded to the given number of
        decimal ``places`` (default 7) and comparing to zero, or if
        their difference is greater than a given ``delta``.

        Parameters
        ----------
        filename : str, bytes, file-like
        size : int, float
        places : int
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.
        delta : int, float

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fsize = self._get_file_size(filename)
        self.assertAlmostEqual(
                fsize, size, places=places, msg=msg, delta=delta)

    def assertFileSizeNotAlmostEqual(
            self, filename, size, places=None, msg=None, delta=None):
        '''Fail unless ``filename`` does not have the given ``size``
        as determined by their difference rounded to the given number
        ofdecimal ``places`` (default 7) and comparing to zero, or if
        their difference is greater than a given ``delta``.

        Parameters
        ----------
        filename : str, bytes, file-like
        size : int, float
        places : int
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.
        delta : int, float

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fsize = self._get_file_size(filename)
        self.assertNotAlmostEqual(
                fsize, size, places=places, msg=msg, delta=delta)

    def assertFileSizeGreater(self, filename, size, msg=None):
        '''Fail if ``filename``'s size is not greater than ``size`` as
        determined by the '>' operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        size : int, float
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fsize = self._get_file_size(filename)
        self.assertGreater(fsize, size, msg=msg)

    def assertFileSizeGreaterEqual(self, filename, size, msg=None):
        '''Fail if ``filename``'s size is not greater than or equal to
        ``size`` as determined by the '>=' operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        size : int, float
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fsize = self._get_file_size(filename)
        self.assertGreaterEqual(fsize, size, msg=msg)

    def assertFileSizeLess(self, filename, size, msg=None):
        '''Fail if ``filename``'s size is not less than ``size`` as
        determined by the '<' operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        size : int, float
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fsize = self._get_file_size(filename)
        self.assertLess(fsize, size, msg=msg)

    def assertFileSizeLessEqual(self, filename, size, msg=None):
        '''Fail if ``filename``'s size is not less than or equal to
        ``size`` as determined by the '<=' operator.

        Parameters
        ----------
        filename : str, bytes, file-like
        size : int, float
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``filename`` is not a str or bytes object and is not
            file-like.
        '''
        fsize = self._get_file_size(filename)
        self.assertLessEqual(fsize, size, msg=msg)


class CategoricalMixins(abc.ABC):
    '''Built-in assertions for categorical data.

    This mixin includes some common categorical variables (e.g.,
    weekdays, months, U.S. states, etc.) that test authors can use
    test resources against. For instance, if a dataset is supposed
    to contain data for all states in the U.S., test authors can
    test the state column in their dataset against the `US_STATES`
    attribute.

    .. code-block:: python

        import unittest
        from marbles.mixins import mixins


        class MyTestCase(unittest.TestCase, mixins.CategoricalMixins):

            def test_that_all_states_are_present(self):
                df = ...
                self.assertCategoricalLevelsEqual(df['STATE'], self.US_STATES)

    These categorical variables are provided as a convenience; test
    authors can and should manipulate these variables, or create
    their own, as needed. The idea is, for expectations that may
    apply across datasets, to ensure that the same expectation
    is being tested in the same way across different datasets.

    Attributes
    ----------
    WEEKDAYS : list
    WEEKDAYS_ABBR : list
        Weekdays abbreviated to three characters
    MONTHS : list
    MONTHS_ABBR : list
        Months abbreviated to three characters
    US_STATES : list
    US_STATES_ABBR : list
        U.S. state names abbreviated to two uppercase characters
    US_TERRITORIES : list
    US_TERRITORIES_ABBR : list
        U.S. territory names abbreviated to two uppercase characters
    CONTINENTS : list
        7-continent model names
    '''

    # TODO (jsa): providing these as pandas Series objects or numpy
    # arrays might make applying transformations (uppercase, lowercase)
    # easier
    WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                'Friday', 'Saturday', 'Sunday']
    WEEKDAYS_ABBR = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']
    MONTHS_ABBR = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    US_STATES = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
                 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
                 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas',
                 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts',
                 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana',
                 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
                 'New Mexico', 'New York', 'North Carolina', 'North Dakota',
                 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
                 'South Carolina', 'South Dakota', 'Tennessee', 'Texas',
                 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia',
                 'Wisconsin', 'Wyoming']
    US_STATES_ABBR = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL',
                      'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA',
                      'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE',
                      'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK',
                      'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT',
                      'VA', 'WA', 'WV', 'WI', 'WY']

    US_TERRITORIES = ['American Samoa', 'District of Columbia',
                      'Federated States of Micronesia', 'Guam',
                      'Marshall Islands', 'Northern Mariana Islands',
                      'Palau', 'Puerto Rico', 'Virgin Islands']
    US_TERRITORIES_ABBR = ['AS', 'DC', 'FM', 'GU', 'MH', 'MP', 'PW', 'PR', 'VI']

    # TODO (jsa): support 4 and/or 6 continent models?
    CONTINENTS = ['Africa', 'Antarctica', 'Asia', 'Australia',
                  'Europe', 'North America', 'South America']

    @abc.abstractmethod
    def fail(self, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertIsInstance(self, obj, cls, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertIn(self, member, container, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertNotIn(self, member, container, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def _formatMessage(self, msg, standardMsg):
        pass  # pragma: no cover

    def assertCategoricalLevelsEqual(self, levels1, levels2, msg=None):
        '''Fail if ``levels1`` and ``levels2`` do not have the same
        domain.

        Parameters
        ----------
        levels1 : iterable
        levels2 : iterable
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If either ``levels1`` or ``levels2`` is not iterable.
        '''
        if not isinstance(levels1, collections.Iterable):
            raise TypeError('First argument is not iterable')
        if not isinstance(levels2, collections.Iterable):
            raise TypeError('Second argument is not iterable')

        standardMsg = '%s levels != %s levels' % (levels1, levels2)

        if not all(level in levels2 for level in levels1):
            self.fail(self._formatMessage(msg, standardMsg))

        if not all(level in levels1 for level in levels2):
            self.fail(self._formatMessage(msg, standardMsg))

    def assertCategoricalLevelsNotEqual(self, levels1, levels2, msg=None):
        '''Fail if ``levels1`` and ``levels2`` have the same domain.

        Parameters
        ----------
        levels1 : iterable
        levels2 : iterable
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If either ``levels1`` or ``levels2`` is not iterable.
        '''
        if not isinstance(levels1, collections.Iterable):
            raise TypeError('First argument is not iterable')
        if not isinstance(levels2, collections.Iterable):
            raise TypeError('Second argument is not iterable')

        standardMsg = '%s levels == %s levels' % (levels1, levels2)

        unshared_levels = False
        if not all(level in levels2 for level in levels1):
            unshared_levels = True

        if not all(level in levels1 for level in levels2):
            unshared_levels = True

        if not unshared_levels:
            self.fail(self._formatMessage(msg, standardMsg))

    def assertCategoricalLevelIn(self, level, levels, msg=None):
        '''Fail if ``level`` is not in ``levels``.

        This is equivalent to ``self.assertIn(level, levels)``.

        Parameters
        ----------
        levels1
        levels2 : iterable
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``levels2`` is not iterable.
        '''
        if not isinstance(levels, collections.Iterable):
            raise TypeError('Second argument is not iterable')

        self.assertIn(level, levels, msg=msg)

    def assertCategoricalLevelNotIn(self, level, levels, msg=None):
        '''Fail if ``level`` is in ``levels``.

        This is equivalent to ``self.assertNotIn(level, levels)``.

        Parameters
        ----------
        levels1
        levels2 : iterable
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``levels2`` is not iterable.
        '''
        if not isinstance(levels, collections.Iterable):
            raise TypeError('Second argument is not iterable')

        self.assertNotIn(level, levels, msg=msg)


class DateTimeMixins(abc.ABC):
    '''Built-in assertions for :class:`date` s, :class:`datetime` s,
    and :class:`time` s.
    '''

    @abc.abstractmethod
    def fail(self, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertIsInstance(self, obj, cls, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertIsNone(self, obj, msg):
        pass  # pragma: no cover

    @abc.abstractmethod
    def assertIsNotNone(self, obj, msg):
        pass  # pragma: no cover

    def assertDateTimesBefore(self, sequence, target, strict=True, msg=None):
        '''Fail if any elements in ``sequence`` are not before
        ``target``.

        If ``target`` is iterable, it must have the same length as
        ``sequence``

        If ``strict=True``, fail unless all elements in ``sequence``
        are strictly less than ``target``. If ``strict=False``, fail
        unless all elements in ``sequence`` are less than or equal to
        ``target``.

        Parameters
        ----------
        sequence : iterable
        target : datetime, date, iterable
        strict : bool
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        ValueError
            If ``target`` is iterable but does not have the same length
            as ``sequence``.
        TypeError
            If ``target`` is not a datetime or date object and is not
            iterable.
        '''
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')

        if strict:
            standardMsg = '%s is not strictly less than %s' % (sequence,
                                                               target)
            op = operator.lt
        else:
            standardMsg = '%s is not less than %s' % (sequence, target)
            op = operator.le

        # Null date(time)s will always compare False, but
        # we want to know about null date(time)s
        if isinstance(target, collections.Iterable):
            if len(target) != len(sequence):
                raise ValueError(('Length mismatch: '
                                  'first argument contains %s elements, '
                                  'second argument contains %s elements' % (
                                      len(sequence), len(target))))
            if not all(op(i, j) for i, j in zip(sequence, target)):
                self.fail(self._formatMessage(msg, standardMsg))
        elif isinstance(target, (date, datetime)):
            if not all(op(element, target) for element in sequence):
                self.fail(self._formatMessage(msg, standardMsg))
        else:
            raise TypeError(
                'Second argument is not a datetime or date object or iterable')

    def assertDateTimesAfter(self, sequence, target, strict=True, msg=None):
        '''Fail if any elements in ``sequence`` are not after
        ``target``.

        If ``target`` is iterable, it must have the same length as
        ``sequence``

        If ``strict=True``, fail unless all elements in ``sequence``
        are strictly greater than ``target``. If ``strict=False``,
        fail unless all elements in ``sequence`` are greater than or
        equal to ``target``.

        Parameters
        ----------
        sequence : iterable
        target : datetime, date, iterable
        strict : bool
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        ValueError
            If ``target`` is iterable but does not have the same length
            as ``sequence``.
        TypeError
            If ``target`` is not a datetime or date object and is not
            iterable.
        '''
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')

        if strict:
            standardMsg = '%s is not strictly greater than %s' % (sequence,
                                                                  target)
            op = operator.gt
        else:
            standardMsg = '%s is not greater than %s' % (sequence,
                                                         target)
            op = operator.ge

        # Null date(time)s will always compare False, but
        # we want to know about null date(time)s
        if isinstance(target, collections.Iterable):
            if len(target) != len(sequence):
                raise ValueError(('Length mismatch: '
                                  'first argument contains %s elements, '
                                  'second argument contains %s elements' % (
                                      len(sequence), len(target))))
            if not all(op(i, j) for i, j in zip(sequence, target)):
                self.fail(self._formatMessage(msg, standardMsg))
        elif isinstance(target, (date, datetime)):
            if not all(op(element, target) for element in sequence):
                self.fail(self._formatMessage(msg, standardMsg))
        else:
            raise TypeError(
                'Second argument is not a datetime or date object or iterable')

    def assertDateTimesPast(self, sequence, strict=True, msg=None):
        '''Fail if any elements in ``sequence`` are not in the past.

        If the max element is a datetime, "past" is defined as anything
        prior to ``datetime.now()``; if the max element is a date,
        "past" is defined as anything prior to ``date.today()``.

        If ``strict=True``, fail unless all elements in ``sequence``
        are strictly less than ``date.today()`` (or ``datetime.now()``).
        If ``strict=False``, fail unless all elements in ``sequence``
        are less than or equal to ``date.today()`` (or
        ``datetime.now()``).

        Parameters
        ----------
        sequence : iterable
        strict : bool
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        TypeError
            If max element in ``sequence`` is not a datetime or date
            object.
        '''
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')

        # Cannot compare datetime to date, so if dates are provided use
        # date.today(), if datetimes are provided use datetime.today()
        if isinstance(max(sequence), datetime):
            target = datetime.today()
        elif isinstance(max(sequence), date):
            target = date.today()
        else:
            raise TypeError('Expected iterable of datetime or date objects')

        self.assertDateTimesBefore(sequence, target, strict=strict, msg=msg)

    def assertDateTimesFuture(self, sequence, strict=True, msg=None):
        '''Fail if any elements in ``sequence`` are not in the future.

        If the min element is a datetime, "future" is defined as
        anything after ``datetime.now()``; if the min element is a date,
        "future" is defined as anything after ``date.today()``.

        If ``strict=True``, fail unless all elements in ``sequence``
        are strictly greater than ``date.today()``
        (or ``datetime.now()``).  If ``strict=False``, fail all
        elements in ``sequence`` are greater than or equal to
        ``date.today()`` (or ``datetime.now()``).

        Parameters
        ----------
        sequence : iterable
        strict : bool
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        TypeError
            If min element in ``sequence`` is not a datetime or date
            object.
        '''
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')

        # Cannot compare datetime to date, so if dates are provided use
        # date.today(), if datetimes are provided use datetime.today()
        if isinstance(min(sequence), datetime):
            target = datetime.today()
        elif isinstance(min(sequence), date):
            target = date.today()
        else:
            raise TypeError('Expected iterable of datetime or date objects')

        self.assertDateTimesAfter(sequence, target, strict=strict, msg=msg)

    def assertDateTimesFrequencyEqual(self, sequence, frequency, msg=None):
        '''Fail if any elements in ``sequence`` aren't separated by
        the expected ``fequency``.

        Parameters
        ----------
        sequence : iterable
        frequency : timedelta
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        TypeError
            If ``frequency`` is not a timedelta object.
        '''
        # TODO (jsa): check that elements in sequence are dates or
        # datetimes, keeping in mind that sequence may contain null
        # values
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')
        if not isinstance(frequency, timedelta):
            raise TypeError('Second argument is not a timedelta object')

        standardMsg = 'unexpected frequencies found in %s' % sequence

        s1 = pd.Series(sequence)
        s2 = s1.shift(-1)

        freq = s2 - s1

        if not all(f == frequency for f in freq[:-1]):
            self.fail(self._formatMessage(msg, standardMsg))

    def assertDateTimesLagEqual(self, sequence, lag, msg=None):
        '''Fail unless max element in ``sequence`` is separated from
        the present by ``lag`` as determined by the '==' operator.

        If the max element is a datetime, "present" is defined as
        ``datetime.now()``; if the max element is a date, "present"
        is defined as ``date.today()``.

        This is equivalent to
        ``self.assertEqual(present - max(sequence), lag)``.

        Parameters
        ----------
        sequence : iterable
        lag : timedelta
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        TypeError
            If ``lag`` is not a timedelta object.
        TypeError
            If max element in ``sequence`` is not a datetime or date
            object.
        '''
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')
        if not isinstance(lag, timedelta):
            raise TypeError('Second argument is not a timedelta object')

        # Cannot compare datetime to date, so if dates are provided use
        # date.today(), if datetimes are provided use datetime.today()
        if isinstance(max(sequence), datetime):
            target = datetime.today()
        elif isinstance(max(sequence), date):
            target = date.today()
        else:
            raise TypeError('Expected iterable of datetime or date objects')

        self.assertEqual(target - max(sequence), lag, msg=msg)

    def assertDateTimesLagLess(self, sequence, lag, msg=None):
        '''Fail if max element in ``sequence`` is separated from
        the present by ``lag`` or more as determined by the '<'
        operator.

        If the max element is a datetime, "present" is defined as
        ``datetime.now()``; if the max element is a date, "present"
        is defined as ``date.today()``.

        This is equivalent to
        ``self.assertLess(present - max(sequence), lag)``.

        Parameters
        ----------
        sequence : iterable
        lag : timedelta
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        TypeError
            If ``lag`` is not a timedelta object.
        TypeError
            If max element in ``sequence`` is not a datetime or date
            object.
        '''
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')
        if not isinstance(lag, timedelta):
            raise TypeError('Second argument is not a timedelta object')

        # Cannot compare datetime to date, so if dates are provided use
        # date.today(), if datetimes are provided use datetime.today()
        if isinstance(max(sequence), datetime):
            target = datetime.today()
        elif isinstance(max(sequence), date):
            target = date.today()
        else:
            raise TypeError('Expected iterable of datetime or date objects')

        self.assertLess(target - max(sequence), lag, msg=msg)

    def assertDateTimesLagLessEqual(self, sequence, lag, msg=None):
        '''Fail if max element in ``sequence`` is separated from
        the present by more than ``lag`` as determined by the '<='
        operator.

        If the max element is a datetime, "present" is defined as
        ``datetime.now()``; if the max element is a date, "present"
        is defined as ``date.today()``.

        This is equivalent to
        ``self.assertLessEqual(present - max(sequence), lag)``.

        Parameters
        ----------
        sequence : iterable
        lag : timedelta
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``sequence`` is not iterable.
        TypeError
            If ``lag`` is not a timedelta object.
        TypeError
            If max element in ``sequence`` is not a datetime or date
            object.
        '''
        if not isinstance(sequence, collections.Iterable):
            raise TypeError('First argument is not iterable')
        if not isinstance(lag, timedelta):
            raise TypeError('Second argument is not a timedelta object')

        # Cannot compare datetime to date, so if dates are provided use
        # date.today(), if datetimes are provided use datetime.today()
        if isinstance(max(sequence), datetime):
            target = datetime.today()
        elif isinstance(max(sequence), date):
            target = date.today()
        else:
            raise TypeError('Expected iterable of datetime or date objects')

        self.assertLessEqual(target - max(sequence), lag, msg=msg)

    def assertTimeZoneIsNone(self, dt, msg=None):
        '''Fail if ``dt`` has a non-null ``tzinfo`` attribute.

        Parameters
        ----------
        dt : datetime
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``dt`` is not a datetime object.
        '''
        if not isinstance(dt, datetime):
            raise TypeError('First argument is not a datetime object')

        self.assertIsNone(dt.tzinfo, msg=msg)

    def assertTimeZoneIsNotNone(self, dt, msg=None):
        '''Fail unless ``dt`` has a non-null ``tzinfo`` attribute.

        Parameters
        ----------
        dt : datetime
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``dt`` is not a datetime object.
        '''
        if not isinstance(dt, datetime):
            raise TypeError('First argument is not a datetime object')

        self.assertIsNotNone(dt.tzinfo, msg=msg)

    def assertTimeZoneEqual(self, dt, tz, msg=None):
        '''Fail unless ``dt``'s ``tzinfo`` attribute equals ``tz`` as
        determined by the '==' operator.

        Parameters
        ----------
        dt : datetime
        tz : timezone
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``dt`` is not a datetime object.
        TypeError
            If ``tz`` is not a timezone object.
        '''
        if not isinstance(dt, datetime):
            raise TypeError('First argument is not a datetime object')
        if not isinstance(tz, timezone):
            raise TypeError('Second argument is not a timezone object')

        self.assertEqual(dt.tzinfo, tz, msg=msg)

    def assertTimeZoneNotEqual(self, dt, tz, msg=None):
        '''Fail if ``dt``'s ``tzinfo`` attribute equals ``tz`` as
        determined by the '!=' operator.

        Parameters
        ----------
        dt : datetime
        tz : timezone
        msg : str
            If not provided, the :mod:`marbles.mixins` or
            :mod:`unittest` standard message will be used.

        Raises
        ------
        TypeError
            If ``dt`` is not a datetime object.
        TypeError
            If ``tz`` is not a timezone object.
        '''
        if not isinstance(dt, datetime):
            raise TypeError('First argument is not a datetime object')
        if not isinstance(tz, timezone):
            raise TypeError('Second argument is not a timezone object')

        self.assertNotEqual(dt.tzinfo, tz, msg=msg)
