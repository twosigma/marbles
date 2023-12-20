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

'''Tests about marbles assertions.

Generally, we set up a fake AnnotatedTestCase, run its tests, and
check whether it responds by raising the right ContextualAssertionError
with fields filled in.
'''

import datetime
import io
import linecache
import logging
import os
import sys
import unittest

from marbles.core import (
    AnnotatedTestCase,
    AnnotationError,
    ContextualAssertionError,
    TestCase
)
from marbles.core import log


class ReversingTestCaseMixin(object):

    def assertReverseEqual(self, left, right, *args, **kwargs):
        self.assertEqual(left, reversed(right), *args, **kwargs)


class OddArgumentOrderTestCaseMixin(object):

    def assertEqualWithMessageInOddPlace(self, left, msg=None, right=None):
        self.assertEqual(left, right, msg=msg)


# We write our example test case as a mixin, then mix it into both
# AnnotatedTestCase and TestCase below.  We inherit from
# unittest.TestCase here so that editors and tools that check for
# member existence don't get confused, we enforce that the marbles
# TestCase subclasses are earlier in the method resolution order than
# unittest.TestCase.

# This test case uses material from the Wikipedia article
# https://en.wikipedia.org/wiki/Marble_(toy) which is
# released under the Creative Commons Attribution-Share-Alike
# License 3.0 https://creativecommons.org/licenses/by-sa/3.0

@unittest.skip('This is the TestCase being tested')
class ExampleTestCaseMixin(
        ReversingTestCaseMixin,
        OddArgumentOrderTestCaseMixin,
        unittest.TestCase):

    longMessage = 'This is a long message'

    def test_success(self):
        self.assertTrue(True, note='some note')

    def test_failure(self):
        self.assertTrue(False, note='some note')

    def test_fail_without_msg_without_note(self):
        self.fail()

    def test_fail_without_msg_kwargs_note(self):
        self.fail(note='some note')

    def test_fail_positional_msg_kwargs_note(self):
        self.fail('some message', note='some note')

    def test_fail_kwargs_msg_kwargs_note(self):
        self.fail(msg='some message', note='some note')

    def test_fail_extra_arg_positional_msg_kwargs_note(self):
        self.fail('some message', 'foo', note='some note')

    def test_fail_after_calling_formatMessage(self):
        self.assertIsNotNone(None, note='some note')

    def test_long_note(self):
        note = '''
        Onionskins - Although this cane-cut swirl usually has at its
        center a clear glass core, it appears solidly colored because
        the clear core is covered by a thin layer of opaque color and
        then covered again by a thin layer of clear glass. Extremely
        popular and highly prized, onionskins take their name from the
        layering of glass, like layers of an onion. In contrast to end
        of day marbles, onion skins have two pontils. The base color,
        usually white or yellow, was applied by rolling clear glass
        marble in powdered glass. Accent colors were added by rolling
        the heated piece over fragments of crashed glass, creating the
        speckled effect. There are various types of onionskins: single
        color, speckled, and segmented. Sometimes mica was added to the
        glass, thus increasing its value. Onionskins were known to exist
        from the beginning of the cane-cut marble industry. An early
        example, dated between 1850 and 1860 was unearthed in the
        excavation of an old privy in New Orleans.'''
        self.assertTrue(False, note=note)

    def test_long_line_in_note(self):
        note = '''
        OnionskinsAlthoughthiscanecutswirlusuallyhasatitscenteraclearglasscoreitappears
        solidly colored because the clear core is covered by a thin
        layer of opaque color and then covered again by a thin layer of
        clear glass. Extremely popular and highly prized, onionskins
        take their name from the layering of glass, like layers of an
        onion. In contrast to end of day marbles, onion skins have two
        pontils. The base color, usually white or yellow, was applied by
        rolling clear glass marble in powdered glass. Accent colors were
        added by rolling the heated piece over fragments of crashed
        glass, creating the speckled effect. There are various types of
        onionskins: single color, speckled, and segmented. Sometimes
        mica was added to the glass, thus increasing its value.
        Onionskins were known to exist from the beginning of the
        cane-cut marble industry. An early example, dated between 1850
        and 1860 was unearthed in the excavation of an old privy in New
        Orleans.'''
        self.assertTrue(False, note=note)

    def test_multi_paragraphs_in_note(self):
        note = '''
        Onionskins - Although this cane-cut swirl usually has at its
        center a clear glass core, it appears solidly colored because
        the clear core is covered by a thin layer of opaque color and
        then covered again by a thin layer of clear glass. Extremely
        popular and highly prized, onionskins take their name from the
        layering of glass, like layers of an onion.

        In contrast to end of day marbles, onion skins have two pontils.
        The base color, usually white or yellow, was applied by rolling
        clear glass marble in powdered glass. Accent colors were added
        by rolling the heated piece over fragments of crashed glass,
        creating the speckled effect.

        There are various types of onionskins: single color, speckled,
        and segmented. Sometimes mica was added to the glass, thus
        increasing its value. Onionskins were known to exist from the
        beginning of the cane-cut marble industry. An early example,
        dated between 1850 and 1860 was unearthed in the excavation of
        an old privy in New Orleans.'''
        self.assertTrue(False, note=note)

    def test_list_in_note(self):
        note = '''
        There are various types of onionskins:

            1. single color,

            2. speckled,

            3. and segmented.

            42. Sometimes mica was added to the glass, thus increasing
            its value. Onionskins were known to exist from the beginning
            of the cane- cut marble industry. An early example, dated
            between 1850 and 1860 was unearthed in the excavation of an
            old privy in New Orleans.

        There are various types of onionskins:

            a) single color,

            b) speckled,

            c) and segmented.

            d) Sometimes mica was added to the glass, thus increasing
            its value. Onionskins were known to exist from the beginning
            of the cane- cut marble industry. An early example, dated
            between 1850 and 1860 was unearthed in the excavation of an
            old privy in New Orleans.'''
        self.assertTrue(False, note=note)

    def test_assert_raises_success(self):
        with self.assertRaises(Exception, note='undead note'):
            raise Exception()

    def test_assert_raises_failure(self):
        with self.assertRaises(Exception, note='undead note'):
            pass

    def test_assert_raises_missing_note(self):
        with self.assertRaises(Exception):
            raise Exception()

    def test_assert_raises_kwargs_msg(self):
        with self.assertRaises(Exception, msg='undead message',
                               note='undead note'):
            pass

    def test_locals(self):
        foo = 'bar'  # noqa: F841
        self.assertTrue(False, note='some note about {foo!r}')

    def test_multiline_locals(self):
        class Record(object):
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def __repr__(self):
                return 'Record(\n{}\n)'.format('\n'.join(
                    '  {key} = {value!r},'.format(key=key, value=value)
                    for key, value in self.kwargs.items()
                ))
        foo = Record(a=1, b=2)  # noqa: F841
        self.assertTrue(False, note='some note')

    def test_string_equality(self):
        s = ''
        self.assertEqual(s, s, note='some note')

    def test_missing_annotation_pass(self):
        self.assertTrue(True)

    def test_missing_annotation_fail(self):
        self.assertTrue(False)

    def test_missing_note_dict(self):
        self.assertTrue(True, {'msg': 'message'})

    def test_missing_msg_dict(self):
        self.assertTrue(False, {'note': 'note'})

    def test_kwargs(self):
        self.assertTrue(False, msg='kwargs message', note='kwargs note')

    def test_kwargs_note_missing(self):
        self.assertTrue(True, msg='kwargs message')

    def test_positional_msg_kwargs_note(self):
        self.assertTrue(False, 'positional message', note='kwargs note')

    def test_missing_msg_kwargs_note_success(self):
        self.assertTrue(True, note='kwargs note')

    def test_missing_msg_kwargs_note_failure(self):
        self.assertTrue(False, note='kwargs note')

    def test_reverse_equality_positional_msg(self):
        s = 'leif'
        self.assertReverseEqual(s, s, 'some message', note='some note')

    def test_reverse_equality_kwargs(self):
        s = 'leif'
        self.assertReverseEqual(s, s,
                                msg='some message', note='some note')

    def test_odd_argument_order_success(self):
        s = 'leif'
        self.assertEqualWithMessageInOddPlace(s, 'message', s, note='note')

    def test_odd_argument_order_failure(self):
        s = 'leif'
        self.assertEqualWithMessageInOddPlace(s, 'message', reversed(s),
                                              note='note')

    def test_internal_mangled_locals(self):
        _foo = 'bar'  # noqa: F841
        __bar = 'baz'  # noqa: F841
        self.assertTrue(False, note='some note about {_foo!r}')

    def test_positional_assert_args(self):
        self.assertAlmostEqual(1, 2, 1, 'some message', note='some note')

    def test_named_assert_args(self):
        self.assertAlmostEqual(1, 2, places=1, msg='some message',
                               note='some note')

    def test_note_format_strings_list_getitem(self):
        ls = [1, 42, 2]  # noqa: F841
        note = 'the answer is {ls[1]}'
        self.assertTrue(False, note=note)

    def test_note_format_strings_dict_getitem(self):
        ls = {'answer': 42,  # noqa: F841
              'query': 'the answer to life, the universe, and everything'}
        note = 'the answer is {ls[answer]}'
        self.assertTrue(False, note=note)

    def test_note_format_strings_attribute_access(self):
        class Foo(object):
            answer = 42
        obj = Foo()  # noqa: F841
        note = 'the answer is {obj.answer}'
        self.assertTrue(False, note=note)

    def test_note_format_strings_custom_format(self):
        dt = datetime.date(2017, 8, 12)  # noqa: F841
        note = 'the date is {dt:%Y%m%d}'
        self.assertTrue(False, note=note)


@unittest.skip('This is the TestCase being tested')
class ExampleTestCase(TestCase, ExampleTestCaseMixin):
    pass


@unittest.skip('This is the TestCase being tested')
class ExampleAnnotatedTestCase(AnnotatedTestCase, ExampleTestCaseMixin):
    pass


class MarblesTestCase(unittest.TestCase):
    '''Common setUp/tearDown for tests that should run against both
    TestCase and AnnotatedTestCase.
    '''

    def __init__(self, methodName='runTest', *, use_annotated_test_case=False,
                 **kwargs):
        super().__init__(methodName=methodName, **kwargs)
        self._use_annotated_test_case = use_annotated_test_case

    def __str__(self):
        params = ', '.join(
            '{}={!r}'.format(name, getattr(self, '_{}'.format(name)))
            for name in ('use_annotated_test_case',))
        return '{} ({}) ({})'.format(
            self._testMethodName,
            unittest.util.strclass(self.__class__),
            params)

    def setUp(self):
        if self._use_annotated_test_case:
            self.case = ExampleAnnotatedTestCase()
        else:
            self.case = ExampleTestCase()

    def tearDown(self):
        delattr(self, 'case')


class InterfaceTestCase(MarblesTestCase):

    def test_annotated_assertion_error_not_raised(self):
        '''Is no error raised if a test succeeds?'''
        self.case.test_success()

    def test_annotated_assertion_error_raised(self):
        '''Is an ContextualAssertionError raised if a test fails?'''
        with self.assertRaises(ContextualAssertionError):
            self.case.test_failure()

    def test_fail_handles_note_properly(self):
        '''Does TestCase.fail() deal with note the right way?'''
        if self._use_annotated_test_case:
            with self.assertRaises(AnnotationError):
                self.case.test_fail_without_msg_without_note()
        else:
            with self.assertRaises(ContextualAssertionError):
                self.case.test_fail_without_msg_without_note()
        with self.assertRaises(ContextualAssertionError):
            self.case.test_fail_without_msg_kwargs_note()
        with self.assertRaises(ContextualAssertionError):
            self.case.test_fail_positional_msg_kwargs_note()
        with self.assertRaises(ContextualAssertionError):
            self.case.test_fail_kwargs_msg_kwargs_note()

    def test_fail_rejects_extra_args(self):
        '''Does TestCase.fail() reject extra arguments?'''
        with self.assertRaises(TypeError):
            self.case.test_fail_extra_arg_positional_msg_kwargs_note()

    def test_fail_works_when_invoked_by_builtin_assertions(self):
        with self.assertRaises(ContextualAssertionError):
            self.case.test_fail_after_calling_formatMessage()

    def test_assert_raises_success(self):
        '''Does assertRaises work correctly when the test passes?'''
        self.case.test_assert_raises_success()

    def test_assert_raises_failure(self):
        '''Does assertRaises work correctly when the test fails?'''
        with self.assertRaises(ContextualAssertionError):
            self.case.test_assert_raises_failure()

    def test_assert_raises_missing_note(self):
        '''Do we notice missing note for assertRaises?'''
        if self._use_annotated_test_case:
            with self.assertRaises(AnnotationError):
                self.case.test_assert_raises_missing_note()
        else:
            self.case.test_assert_raises_missing_note()

    def test_string_equality(self):
        '''Can we use assertEqual on strings?

        That calls down to assertMultiLineEqual which itself makes
        some calls to other assertions, but passes its own msg, which
        has caused problems for marbles in the past.
        '''
        self.case.test_string_equality()

    def test_missing_note_dict(self):
        '''When passing a dict as msg, do we still check for note?'''
        if self._use_annotated_test_case:
            with self.assertRaises(AnnotationError):
                self.case.test_missing_note_dict()
        else:
            self.case.test_missing_note_dict()

    def test_missing_msg_ok(self):
        '''Is it ok to provide only note?'''
        self.case.test_missing_msg_kwargs_note_success()
        with self.assertRaises(ContextualAssertionError):
            self.case.test_missing_msg_kwargs_note_failure()

    def test_odd_argument_order_ok(self):
        '''Does marbles handle a msg argument before the last position?'''
        self.case.test_odd_argument_order_success()
        with self.assertRaises(ContextualAssertionError):
            self.case.test_odd_argument_order_failure()

    def test_missing_annotation(self):
        '''Does marbles check for missing annotations?'''
        if self._use_annotated_test_case:
            with self.assertRaises(AnnotationError, msg='for a passing test'):
                self.case.test_missing_annotation_pass()
            with self.assertRaises(AnnotationError, msg='for a failing test'):
                self.case.test_missing_annotation_fail()
        else:
            self.case.test_missing_annotation_pass()
            with self.assertRaises(AssertionError):
                self.case.test_missing_annotation_fail()


class TestAssertionLoggingFailure(MarblesTestCase):

    def setUp(self):
        super().setUp()
        self.file_handle = object()
        self.old_logger = log.logger
        log.logger = log.AssertionLogger()
        log.logger.configure(logfile=self.file_handle)
        self.log_buffer = io.StringIO()
        self.handler = logging.StreamHandler(self.log_buffer)
        self.logger = logging.getLogger('marbles.core.marbles')
        self.logger.addHandler(self.handler)
        self.logger.propagate = False

    def tearDown(self):
        self.logger.propagate = True
        self.logger.removeHandler(self.handler)
        log.logger = self.old_logger
        delattr(self, 'old_logger')
        delattr(self, 'logger')
        delattr(self, 'handler')
        delattr(self, 'log_buffer')
        log.logger.configure(logfile=None)
        delattr(self, 'file_handle')
        super().tearDown()

    def test_success(self):
        '''When logging fails, do we allow the test to proceed?'''
        self.case.test_success()
        self.assertIn("'object' object has no attribute 'write'",
                      self.log_buffer.getvalue())


class TestContextualAssertionError(MarblesTestCase):

    def test_verify_annotation_dict_missing_keys(self):
        '''Is an Exception raised if annotation is missing expected keys?'''
        with self.assertRaises(Exception):
            ContextualAssertionError(({'foo': 'bar'}, 'standard message'))

    def test_verify_annotation_none(self):
        '''Is an Exception raised if no annotation is provided?'''
        with self.assertRaises(Exception):
            ContextualAssertionError(())

    def test_verify_annotation_locals(self):
        '''Are locals in the test definition formatted into annotations?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_locals()
        e = ar.exception
        self.assertEqual(e.note.strip(), "some note about 'bar'")

    def test_multiline_locals_indentation(self):
        '''Are locals with multiline reprs indented correctly?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_multiline_locals()
        e = ar.exception
        self.assertIn("\n\t\t  a = 1,\n",
                      e._format_locals(e.public_test_locals))

    def test_assert_raises_without_msg(self):
        '''Do we capture annotations properly for assertRaises?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_assert_raises_failure()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'Exception not raised')
        self.assertEqual(e.note.strip(), 'undead note')

    def test_assert_raises_kwargs_msg(self):
        '''Do we capture kwargs annotations properly for assertRaises?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_assert_raises_kwargs_msg()
        e = ar.exception
        expected_msg = 'undead message'
        self.assertEqual(e.standardMsg, expected_msg)
        self.assertEqual(e.note.strip(), 'undead note')

    def test_get_stack(self):
        '''Does _get_stack() find the stack level with the test definition?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_failure()
        e = ar.exception
        self.assertCountEqual(list(e._locals.keys()), ['self'])
        self.assertEqual(e.filename, os.path.abspath(__file__))
        # This isn't great because I have to change it every time I
        # add/remove imports but oh well
        self.assertEqual(e.linenumber, 83)

        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_locals()
        e = ar.exception
        self.assertCountEqual(list(e._locals.keys()), ['foo', 'self'])
        self.assertEqual(e.filename, os.path.abspath(__file__))
        # This isn't great because I have to change it every time I
        # add/remove imports but oh well
        self.assertEqual(e.linenumber, 216)

    def test_assert_stmt_indicates_line(self):
        '''Does e.assert_stmt indicate the line from the source code?'''
        test_linenumber = 83
        test_filename = os.path.abspath(__file__)
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_failure()
        e = ar.exception
        lines = e.assert_stmt.split('\n')
        for i, line in enumerate(lines):
            # Is the linenumber provided indicated with a '>'?
            if i == 1:
                self.assertTrue(lines[i].startswith(' >'))
            else:
                self.assertFalse(lines[i].startswith(' >'))
        # Is the line represented correctly after the line number?
        self.assertEqual(
            lines[1].split('{0} '.format(test_linenumber))[-1].strip(),
            linecache.getline(test_filename, test_linenumber).strip())

    def test_assert_stmt_surrounding_lines(self):
        '''Does _find_assert_stmt read surrounding lines from the file?'''
        test_linenumber = 83
        test_filename = os.path.abspath(__file__)
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_failure()
        e = ar.exception
        lines = e._find_assert_stmt(test_filename, test_linenumber)[0]
        self.assertEqual(len(lines), 3)
        more_lines = e._find_assert_stmt(
            test_filename, test_linenumber, 2, 5)[0]
        self.assertEqual(len(more_lines), 7)

    def test_note_wrapping(self):
        '''Do we wrap the note properly?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_long_note()
        e = ar.exception
        lines = e.note.split('\n')
        for line in lines:
            self.assertLess(len(line), 75)
            self.assertTrue(line.startswith('\t'))

        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_long_line_in_note()
        e = ar.exception
        lines = e.note.split('\n')
        self.assertTrue(any(len(line) > 75 for line in lines))

        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_multi_paragraphs_in_note()
        e = ar.exception
        paragraphs = e.note.split('\n\n')
        self.assertGreater(len(paragraphs), 1)
        for paragraph in paragraphs:
            for line in paragraph.split('\n'):
                self.assertLess(len(line), 75)
                self.assertTrue(line.startswith('\t'))

        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_list_in_note()
        e = ar.exception
        lines = e.note.split('\n')
        for line in lines:
            self.assertLess(len(line), 75)
        list_lines = [2, 4, 6, 8, 16, 18, 20, 22]
        for list_line in list_lines:
            self.assertTrue(lines[list_line].startswith('\t    '))
        #  Hanging indent for both numbered and lettered lists
        #  with period or parenthesis
        self.assertTrue(lines[9].startswith('\t       '))
        self.assertTrue(lines[23].startswith('\t       '))

    def test_positional_assert_args(self):
        '''Is annotation captured correctly when using positional arguments?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_positional_assert_args()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'some message')
        self.assertEqual(e.note.strip(), 'some note')

    def test_named_assert_args(self):
        '''Is annotation captured correctly if named arguments are provided?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_named_assert_args()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'some message')
        self.assertEqual(e.note.strip(), 'some note')

    def test_use_kwargs_form(self):
        '''Does the kwargs form of an assertion work?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_kwargs()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'kwargs message')
        self.assertEqual(e.note.strip(), 'kwargs note')

    def test_kwargs_stick_together(self):
        '''Does the kwargs form of an assertion enforce that message and
        note must both be present?
        '''
        if self._use_annotated_test_case:
            with self.assertRaises(AnnotationError):
                self.case.test_kwargs_note_missing()
        else:
            self.case.test_kwargs_note_missing()

    def test_positional_msg_kwargs_note(self):
        '''Is annotation captured correctly when using a positional msg?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_positional_msg_kwargs_note()
        e = ar.exception
        expected_msg = 'positional message'
        self.assertEqual(e.standardMsg, expected_msg)
        self.assertEqual(e.note.strip(), 'kwargs note')

    def test_missing_msg_kwargs_note(self):
        '''Is the default msg properly displayed?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_missing_msg_kwargs_note_failure()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'False is not true')
        self.assertEqual(e.note.strip(), 'kwargs note')

    def test_missing_msg_dict(self):
        '''Is the default msg properly displayed when note is in a dict?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_missing_msg_dict()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'False is not true')
        self.assertEqual(e.note.strip(), 'note')

    def test_custom_assertions(self):
        '''Does the marbles note work with custom-defined assertions?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_reverse_equality_positional_msg()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'some message')
        self.assertEqual(e.note.strip(), 'some note')

    def test_custom_assertions_kwargs(self):
        '''Does the marbles kwargs note work with custom assertions?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_reverse_equality_kwargs()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'some message')
        self.assertEqual(e.note.strip(), 'some note')

    def test_odd_argument_order(self):
        '''Does marbles handle a msg argument before the last position?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_odd_argument_order_failure()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'message')
        self.assertEqual(e.note.strip(), 'note')

    def test_exclude_ignored_locals(self):
        '''Are ignored variables excluded from output?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_locals()
        e = ar.exception
        locals_section = e._format_locals(e.public_test_locals).split('\n')
        locals_ = [local.split('=')[0] for local in locals_section]
        for local in locals_:
            self.assertTrue(local.startswith('\t'))
            local = local.strip()
            self.assertNotIn(local, e._IGNORE_LOCALS)

    def test_exclude_internal_mangled_locals(self):
        '''Are internal/mangled variables excluded from the "Locals"?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_internal_mangled_locals()
        e = ar.exception
        locals_section = e._format_locals(e.public_test_locals).split('\n')
        locals_ = [local.split('=')[0] for local in locals_section if local]
        for local in locals_:
            self.assertTrue(local.startswith('\t'))
            local = local.strip()
            self.assertNotIn(local, ['_foo', '__bar'])
            self.assertFalse(local.startswith('_'))
        self.assertEqual(e.note.strip(), "some note about 'bar'")

    def test_note_rich_format_strings(self):
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_note_format_strings_attribute_access()
        e = ar.exception
        self.assertEqual('the answer is 42', e.note.strip())

        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_note_format_strings_list_getitem()
        e = ar.exception
        self.assertEqual('the answer is 42', e.note.strip())

        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_note_format_strings_dict_getitem()
        e = ar.exception
        self.assertEqual('the answer is 42', e.note.strip())

        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_note_format_strings_custom_format()
        e = ar.exception
        self.assertEqual('the date is 20170812', e.note.strip())

    def test_locals_hidden_when_missing(self):
        '''Does marbles hide the Locals section if there are none?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_failure()
        e = ar.exception
        self.assertNotIn('Locals:', str(e))

    def test_locals_hidden_when_all_private(self):
        '''Does marbles hide the Locals section if all are private?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_internal_mangled_locals()
        e = ar.exception
        self.assertNotIn('Locals:', str(e))

    def test_locals_shown_when_present(self):
        '''Does marbles show the Locals section if there are some?'''
        with self.assertRaises(ContextualAssertionError) as ar:
            self.case.test_locals()
        e = ar.exception
        self.assertIn('Locals:', str(e))


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    module = sys.modules[__name__]
    objs = [getattr(module, name) for name in dir(module)]
    test_classes = [obj for obj in objs
                    if (isinstance(obj, type)
                        and issubclass(obj, unittest.TestCase)
                        and not getattr(obj, '__unittest_skip__', False))]

    for use_annotated_test_case in (True, False):
        for cls in test_classes:
            for name in loader.getTestCaseNames(cls):
                suite.addTest(
                    cls(
                        methodName=name,
                        use_annotated_test_case=use_annotated_test_case
                    )
                )

    return suite


if __name__ == '__main__':
    unittest.main()
