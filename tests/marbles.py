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

'''Tests about marbles assertions.

Generally, we set up a fake AnnotatedTestCase, run its tests, and
check whether it responds by raising the right AnnotatedAssertionError
with fields filled in.
'''

import datetime
import io
import linecache
import logging
import os
import unittest

from marbles import (
    AnnotatedTestCase,
    AnnotatedAssertionError,
    AnnotationError
)
from marbles import log


class ReversingTestCaseMixin(object):

    def assertReverseEqual(self, left, right, *args, **kwargs):
        self.assertEqual(left, reversed(right), *args, **kwargs)


class OddArgumentOrderTestCaseMixin(object):

    def assertEqualWithMessageInOddPlace(self, left, msg=None, right=None):
        self.assertEqual(left, right, msg=msg)


@unittest.skip('This is the TestCase being tested')
class ExampleAnnotatedTestCase(
        ReversingTestCaseMixin,
        OddArgumentOrderTestCaseMixin,
        AnnotatedTestCase):

    longMessage = 'This is a long message'

    def test_success(self):
        self.assertTrue(True, advice='some advice')

    def test_failure(self):
        self.assertTrue(False, advice='some advice')

    def test_fail_without_msg_without_advice(self):
        self.fail()

    def test_fail_without_msg_kwargs_advice(self):
        self.fail(advice='some advice')

    def test_fail_positional_msg_kwargs_advice(self):
        self.fail('some message', advice='some advice')

    def test_fail_kwargs_msg_kwargs_advice(self):
        self.fail(msg='some message', advice='some advice')

    def test_fail_after_calling_formatMessage(self):
        self.assertIsNotNone(None, advice='some advice')

    def test_long_advice(self):
        advice = '''
Onionskins - Although this cane-cut swirl usually has at its center a
clear glass core, it appears solidly colored because the clear core is
covered by a thin layer of opaque color and then covered again by a
thin layer of clear glass. Extremely popular and highly prized,
onionskins take their name from the layering of glass, like layers of
an onion. In contrast to end of day marbles, onion skins have two
pontils. The base color, usually white or yellow, was applied by
rolling clear glass marble in powdered glass. Accent colors were added
by rolling the heated piece over fragments of crashed glass, creating
the speckled effect. There are various types of onionskins: single
color, speckled, and segmented. Sometimes mica was added to the glass,
thus increasing its value. Onionskins were known to exist from the
beginning of the cane-cut marble industry. An early example, dated
between 1850 and 1860 was unearthed in the excavation of an old privy
in New Orleans.'''
        self.assertTrue(False, advice=advice)

    def test_long_line_in_advice(self):
        advice = '''
OnionskinsAlthoughthiscanecutswirlusuallyhasatitscenteraclearglasscoreitappears
solidly colored because the clear core is covered by a thin layer of
opaque color and then covered again by a thin layer of clear
glass. Extremely popular and highly prized, onionskins take their name
from the layering of glass, like layers of an onion. In contrast to
end of day marbles, onion skins have two pontils. The base color,
usually white or yellow, was applied by rolling clear glass marble in
powdered glass. Accent colors were added by rolling the heated piece
over fragments of crashed glass, creating the speckled effect. There
are various types of onionskins: single color, speckled, and
segmented. Sometimes mica was added to the glass, thus increasing its
value. Onionskins were known to exist from the beginning of the
cane-cut marble industry. An early example, dated between 1850 and
1860 was unearthed in the excavation of an old privy in New
Orleans.'''
        self.assertTrue(False, advice=advice)

    def test_multi_paragraphs_in_advice(self):
        advice = '''
Onionskins - Although this cane-cut swirl usually has at its center a
clear glass core, it appears solidly colored because the clear core is
covered by a thin layer of opaque color and then covered again by a
thin layer of clear glass. Extremely popular and highly prized,
onionskins take their name from the layering of glass, like layers of
an onion.

In contrast to end of day marbles, onion skins have two pontils. The
base color, usually white or yellow, was applied by rolling clear glass
marble in powdered glass. Accent colors were added by rolling the
heated piece over fragments of crashed glass, creating the speckled
effect.

There are various types of onionskins: single color, speckled, and
segmented. Sometimes mica was added to the glass, thus increasing its
value. Onionskins were known to exist from the beginning of the
cane-cut marble industry. An early example, dated between 1850 and 1860
was unearthed in the excavation of an old privy in New Orleans.'''
        self.assertTrue(False, advice=advice)

    def test_list_in_advice(self):
        advice = '''
There are various types of onionskins:

    1. single color,

    2. speckled,

    3. and segmented.

    42. Sometimes mica was added to the glass, thus increasing its
value. Onionskins were known to exist from the beginning of the cane-
cut marble industry. An early example, dated between 1850 and 1860 was
unearthed in the excavation of an old privy in New Orleans.

There are various types of onionskins:

    a) single color,

    b) speckled,

    c) and segmented.

    d) Sometimes mica was added to the glass, thus increasing its
value. Onionskins were known to exist from the beginning of the cane-
cut marble industry. An early example, dated between 1850 and 1860 was
unearthed in the excavation of an old privy in New Orleans.'''
        self.assertTrue(False, advice=advice)

    def test_assert_raises_success(self):
        with self.assertRaises(Exception, advice='undead advice'):
            raise Exception()

    def test_assert_raises_failure(self):
        with self.assertRaises(Exception, advice='undead advice'):
            pass

    def test_assert_raises_missing_advice(self):
        with self.assertRaises(Exception):
            raise Exception()

    def test_assert_raises_kwargs_msg(self):
        with self.assertRaises(Exception, msg='undead message',
                               advice='undead advice'):
            pass

    def test_locals(self):
        foo = 'bar'  # noqa: F841
        self.assertTrue(False, advice='some advice about {foo!r}')

    def test_string_equality(self):
        s = ''
        self.assertEqual(s, s, advice='some advice')

    def test_missing_annotation_pass(self):
        self.assertTrue(True)

    def test_missing_annotation_fail(self):
        self.assertTrue(False)

    def test_missing_advice_dict(self):
        self.assertTrue(True, {'msg': 'message'})

    def test_missing_msg_dict(self):
        self.assertTrue(False, {'advice': 'advice'})

    def test_kwargs(self):
        self.assertTrue(False, msg='kwargs message', advice='kwargs advice')

    def test_kwargs_advice_missing(self):
        self.assertTrue(True, msg='kwargs message')

    def test_positional_msg_kwargs_advice(self):
        self.assertTrue(False, 'positional message', advice='kwargs advice')

    def test_missing_msg_kwargs_advice_success(self):
        self.assertTrue(True, advice='kwargs advice')

    def test_missing_msg_kwargs_advice_failure(self):
        self.assertTrue(False, advice='kwargs advice')

    def test_reverse_equality_positional_msg(self):
        s = 'leif'
        self.assertReverseEqual(s, s, 'some message', advice='some advice')

    def test_reverse_equality_kwargs(self):
        s = 'leif'
        self.assertReverseEqual(s, s,
                                msg='some message', advice='some advice')

    def test_odd_argument_order_success(self):
        s = 'leif'
        self.assertEqualWithMessageInOddPlace(s, 'message', s, advice='advice')

    def test_odd_argument_order_failure(self):
        s = 'leif'
        self.assertEqualWithMessageInOddPlace(s, 'message', reversed(s),
                                              advice='advice')

    def test_internal_mangled_locals(self):
        _foo = 'bar'  # noqa: F841
        __bar = 'baz'  # noqa: F841
        self.assertTrue(False, advice='some advice about {_foo!r}')

    def test_positional_assert_args(self):
        self.assertAlmostEqual(1, 2, 1, 'some message', advice='some advice')

    def test_named_assert_args(self):
        self.assertAlmostEqual(1, 2, places=1, msg='some message',
                               advice='some advice')

    def test_advice_format_strings_list_getitem(self):
        l = [1, 42, 2]
        advice = 'the answer is {l[1]}'
        self.assertTrue(False, advice=advice)

    def test_advice_format_strings_dict_getitem(self):
        l = {'answer': 42,
             'query': 'the answer to life, the universe, and everything'}
        advice = 'the answer is {l[answer]}'
        self.assertTrue(False, advice=advice)

    def test_advice_format_strings_attribute_access(self):
        class Foo(object):
            answer = 42
        obj = Foo()
        advice = 'the answer is {obj.answer}'
        self.assertTrue(False, advice=advice)

    def test_advice_format_strings_custom_format(self):
        date = datetime.date(2017, 8, 12)
        advice = 'the date is {date:%Y%m%d}'
        self.assertTrue(False, advice=advice)


class TestAnnotatedTestCase(unittest.TestCase):

    def setUp(self):
        self.case = ExampleAnnotatedTestCase()

    def tearDown(self):
        delattr(self, 'case')

    def test_annotated_assertion_error_not_raised(self):
        '''Is no error raised if a test succeeds?'''
        self.case.test_success()

    def test_annotated_assertion_error_raised(self):
        '''Is an AnnotatedAssertionError raised if a test fails?'''
        with self.assertRaises(AnnotatedAssertionError):
            self.case.test_failure()

    def test_fail_handles_advice_properly(self):
        '''Does TestCase.fail() deal with advice the right way?'''
        with self.assertRaises(AnnotationError):
            self.case.test_fail_without_msg_without_advice()
        with self.assertRaises(AnnotatedAssertionError):
            self.case.test_fail_without_msg_kwargs_advice()
        with self.assertRaises(AnnotatedAssertionError):
            self.case.test_fail_positional_msg_kwargs_advice()
        with self.assertRaises(AnnotatedAssertionError):
            self.case.test_fail_kwargs_msg_kwargs_advice()

    def test_fail_works_when_invoked_by_builtin_assertions(self):
        with self.assertRaises(AnnotatedAssertionError):
            self.case.test_fail_after_calling_formatMessage()

    def test_assert_raises_success(self):
        '''Does assertRaises work correctly when the test passes?'''
        self.case.test_assert_raises_success()

    def test_assert_raises_failure(self):
        '''Does assertRaises work correctly when the test fails?'''
        with self.assertRaises(AnnotatedAssertionError):
            self.case.test_assert_raises_failure()

    def test_assert_raises_missing_advice(self):
        '''Do we notice missing advice for assertRaises?'''
        with self.assertRaises(AnnotationError):
            self.case.test_assert_raises_missing_advice()

    def test_string_equality(self):
        '''Can we use assertEqual on strings?

        That calls down to assertMultiLineEqual which itself makes
        some calls to other assertions, but passes its own msg, which
        has caused problems for marbles in the past.
        '''
        self.case.test_string_equality()

    def test_missing_advice_dict(self):
        '''When passing a dict as msg, do we still check for advice?'''
        with self.assertRaises(AnnotationError):
            self.case.test_missing_advice_dict()

    def test_missing_msg_ok(self):
        '''Is it ok to provide only advice?'''
        self.case.test_missing_msg_kwargs_advice_success()
        with self.assertRaises(AnnotatedAssertionError):
            self.case.test_missing_msg_kwargs_advice_failure()

    def test_odd_argument_order_ok(self):
        '''Does marbles handle a msg argument before the last position?'''
        self.case.test_odd_argument_order_success()
        with self.assertRaises(AnnotatedAssertionError):
            self.case.test_odd_argument_order_failure()

    def test_missing_annotation(self):
        '''Does marbles check for missing annotations?'''
        with self.assertRaises(AnnotationError, msg='for a passing test'):
            self.case.test_missing_annotation_pass()
        with self.assertRaises(AnnotationError, msg='for a failing test'):
            self.case.test_missing_annotation_fail()


class TestAssertionLoggingFailure(unittest.TestCase):

    def setUp(self):
        self.case = ExampleAnnotatedTestCase()
        self.file_handle = object()
        self.old_logger = log.logger
        log.logger = log.AssertionLogger()
        log.logger.configure(logfile=self.file_handle)
        self.log_buffer = io.StringIO()
        self.handler = logging.StreamHandler(self.log_buffer)
        self.logger = logging.getLogger('marbles.marbles')
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
        delattr(self, 'case')

    def test_success(self):
        '''When logging fails, do we allow the test to proceed?'''
        self.case.test_success()
        self.assertIn("'object' object has no attribute 'write'",
                      self.log_buffer.getvalue())


class TestAnnotatedAssertionError(unittest.TestCase):

    def setUp(self):
        self.case = ExampleAnnotatedTestCase()

    def tearDown(self):
        delattr(self, 'case')

    def test_verify_annotation_dict_missing_keys(self):
        '''Is an Exception raised if annotation is missing expected keys?'''
        with self.assertRaises(Exception):
            AnnotatedAssertionError(({'foo': 'bar'}, 'standard message'))

    def test_verify_annotation_none(self):
        '''Is an Exception raised if no annotation is provided?'''
        with self.assertRaises(Exception):
            AnnotatedAssertionError(())

    def test_verify_annotation_locals(self):
        '''Are locals in the test definition formatted into annotations?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_locals()
        e = ar.exception
        self.assertEqual(e.advice.strip(), "some advice about 'bar'")

    def test_assert_raises_without_msg(self):
        '''Do we capture annotations properly for assertRaises?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_assert_raises_failure()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'Exception not raised')
        self.assertEqual(e.advice.strip(), 'undead advice')

    def test_assert_raises_kwargs_msg(self):
        '''Do we capture kwargs annotations properly for assertRaises?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_assert_raises_kwargs_msg()
        e = ar.exception
        expected_msg = 'undead message'
        self.assertEqual(e.standardMsg, expected_msg)
        self.assertEqual(e.advice.strip(), 'undead advice')

    def test_get_stack(self):
        '''Does _get_stack() find the stack level with the test definition?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_failure()
        e = ar.exception
        self.assertCountEqual(list(e._locals.keys()), ['self'])
        self.assertEqual(e.filename, os.path.abspath(__file__))
        # This isn't great because I have to change it every time I
        # add/remove imports but oh well
        self.assertEqual(e.linenumber, 58)

        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_locals()
        e = ar.exception
        self.assertCountEqual(list(e._locals.keys()), ['foo', 'self'])
        self.assertEqual(e.filename, os.path.abspath(__file__))
        # This isn't great because I have to change it every time I
        # add/remove imports but oh well
        self.assertEqual(e.linenumber, 183)

    def test_assert_stmt_indicates_line(self):
        '''Does e.assert_stmt indicate the line from the source code?'''
        test_linenumber = 58
        test_filename = os.path.abspath(__file__)
        with self.assertRaises(AnnotatedAssertionError) as ar:
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
        test_linenumber = 58
        test_filename = os.path.abspath(__file__)
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_failure()
        e = ar.exception
        lines = e._find_assert_stmt(test_filename, test_linenumber)[0]
        self.assertEqual(len(lines), 3)
        more_lines = e._find_assert_stmt(
            test_filename, test_linenumber, 2, 5)[0]
        self.assertEqual(len(more_lines), 7)

    def test_advice_wrapping(self):
        '''Do we wrap the advice properly?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_long_advice()
        e = ar.exception
        lines = e.advice.split('\n')
        for line in lines:
            self.assertLess(len(line), 75)
            self.assertTrue(line.startswith('\t'))

        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_long_line_in_advice()
        e = ar.exception
        lines = e.advice.split('\n')
        self.assertTrue(any(len(line) > 75 for line in lines))

        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_multi_paragraphs_in_advice()
        e = ar.exception
        paragraphs = e.advice.split('\n\n')
        self.assertGreater(len(paragraphs), 1)
        for paragraph in paragraphs:
            for line in paragraph.split('\n'):
                self.assertLess(len(line), 75)
                self.assertTrue(line.startswith('\t'))

        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_list_in_advice()
        e = ar.exception
        lines = e.advice.split('\n')
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
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_positional_assert_args()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'some message')
        self.assertEqual(e.advice.strip(), 'some advice')

    def test_named_assert_args(self):
        '''Is annotation captured correctly if named arguments are provided?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_named_assert_args()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'some message')
        self.assertEqual(e.advice.strip(), 'some advice')

    def test_use_kwargs_form(self):
        '''Does the kwargs form of an assertion work?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_kwargs()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'kwargs message')
        self.assertEqual(e.advice.strip(), 'kwargs advice')

    def test_kwargs_stick_together(self):
        '''Does the kwargs form of an assertion enforce that message and
        advice must both be present?
        '''
        with self.assertRaises(AnnotationError):
            self.case.test_kwargs_advice_missing()

    def test_positional_msg_kwargs_advice(self):
        '''Is annotation captured correctly when using a positional msg?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_positional_msg_kwargs_advice()
        e = ar.exception
        expected_msg = 'positional message'
        self.assertEqual(e.standardMsg, expected_msg)
        self.assertEqual(e.advice.strip(), 'kwargs advice')

    def test_missing_msg_kwargs_advice(self):
        '''Is the default msg properly displayed?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_missing_msg_kwargs_advice_failure()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'False is not true')
        self.assertEqual(e.advice.strip(), 'kwargs advice')

    def test_missing_msg_dict(self):
        '''Is the default msg properly displayed when advice is in a dict?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_missing_msg_dict()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'False is not true')
        self.assertEqual(e.advice.strip(), 'advice')

    def test_custom_assertions(self):
        '''Does the marbles advice work with custom-defined assertions?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_reverse_equality_positional_msg()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'some message')
        self.assertEqual(e.advice.strip(), 'some advice')

    def test_custom_assertions_kwargs(self):
        '''Does the marbles kwargs advice work with custom assertions?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_reverse_equality_kwargs()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'some message')
        self.assertEqual(e.advice.strip(), 'some advice')

    def test_odd_argument_order(self):
        '''Does marbles handle a msg argument before the last position?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_odd_argument_order_failure()
        e = ar.exception
        self.assertEqual(e.standardMsg, 'message')
        self.assertEqual(e.advice.strip(), 'advice')

    def test_exclude_ignored_locals(self):
        '''Are ignored variables excluded from output?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_locals()
        e = ar.exception
        locals_section = e._format_locals(e.locals).split('\n')
        locals_ = [local.split('=')[0] for local in locals_section]
        for local in locals_:
            self.assertTrue(local.startswith('\t'))
            local = local.strip()
            self.assertNotIn(local, e._IGNORE_LOCALS)

    def test_exclude_internal_mangled_locals(self):
        '''Are internal/mangled variables excluded from the "Locals"?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_internal_mangled_locals()
        e = ar.exception
        locals_section = e._format_locals(e.locals).split('\n')
        locals_ = [local.split('=')[0] for local in locals_section if local]
        for local in locals_:
            self.assertTrue(local.startswith('\t'))
            local = local.strip()
            self.assertNotIn(local, ['_foo', '__bar'])
            self.assertFalse(local.startswith('_'))
        self.assertEqual(e.advice.strip(), "some advice about 'bar'")

    def test_advice_rich_format_strings(self):
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_advice_format_strings_attribute_access()
        e = ar.exception
        self.assertEqual('the answer is 42', e.advice.strip())

        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_advice_format_strings_list_getitem()
        e = ar.exception
        self.assertEqual('the answer is 42', e.advice.strip())

        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_advice_format_strings_dict_getitem()
        e = ar.exception
        self.assertEqual('the answer is 42', e.advice.strip())

        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_advice_format_strings_custom_format()
        e = ar.exception
        self.assertEqual('the date is 20170812', e.advice.strip())


if __name__ == '__main__':
    unittest.main()
