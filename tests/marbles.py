import linecache
import os
import unittest

from marbles import (
    AnnotatedTestCase,
    AnnotatedAssertionError,
    AnnotationError
)


class ReversingTestCaseMixin(object):

    def assertReverseEqual(self, left, right, *args, **kwargs):
        self.assertEqual(left, reversed(right), *args, **kwargs)


@unittest.skip('This is the TestCase being tested')
class ExampleAnnotatedTestCase(ReversingTestCaseMixin, AnnotatedTestCase):

    def test_succeed(self):
        self.assertTrue(True, ('some message', 'some advice'))

    def test_failure(self):
        self.assertTrue(False, ('some message', 'some advice'))

    def test_locals(self):
        foo = 'bar'  # noqa: F841
        self.assertTrue(False, ('some message', 'some advice about {foo}'))

    def test_missing_annotation_pass(self):
        self.assertTrue(True)

    def test_missing_annotation_fail(self):
        self.assertTrue(False)

    def test_missing_annotation_partial(self):
        self.assertTrue(True, ('message',))

    def test_kwargs(self):
        self.assertTrue(False, message='kwargs message',
                        advice='kwargs advice')

    def test_kwargs_advice_missing(self):
        self.assertTrue(True, message='kwargs message')

    def test_reverse_equality(self):
        s = 'leif'
        self.assertReverseEqual(s, s, ('some message', 'some advice'))

    def test_reverse_equality_kwargs(self):
        s = 'leif'
        self.assertReverseEqual(s, s,
                                message='some message',
                                advice='some advice')

    def test_internal_mangled_locals(self):
        _foo = 'bar'  # noqa: F841
        __bar = 'baz'  # noqa: F841
        self.assertTrue(False, ('some message', 'some advice about {_foo}'))

    def test_positional_assert_args(self):
        self.assertAlmostEqual(1, 2, 1, ('some message', 'some advice'))

    def test_named_assert_args(self):
        self.assertAlmostEqual(1, 2, places=1,
                               msg=('some message', 'some advice'))


class TestAnnotatedTestCase(unittest.TestCase):

    def setUp(self):
        self.case = ExampleAnnotatedTestCase()

    def tearDown(self):
        delattr(self, 'case')

    def test_annotated_assertion_error_not_raised(self):
        '''Is no error raised if a test succeeds?'''
        self.case.test_succeed()

    def test_annotated_assertion_error_raised(self):
        '''Is an AnnotatedAssertionError raised if a test fails?'''
        with self.assertRaises(AnnotatedAssertionError):
            self.case.test_failure()

    def test_missing_annotation(self):
        '''Does marbles check for missing annotations?'''
        with self.assertRaises(AnnotationError, msg='for a passing test'):
            self.case.test_missing_annotation_pass()
        with self.assertRaises(AnnotationError, msg='for a failing test'):
            self.case.test_missing_annotation_fail()
        with self.assertRaises(AnnotationError, msg='for a bad tuple'):
            self.case.test_missing_annotation_partial()


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
        self.assertEqual(e.annotation['advice'],
                         'some advice about \'bar\'')

    def test_get_stack(self):
        '''Does _get_stack() find the stack level with the test definition?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_failure()
        e = ar.exception
        self.assertCountEqual(list(e._locals.keys()), ['self'])
        self.assertEqual(e._filename, os.path.abspath(__file__))
        # This isn't great because I have to change it every time I
        # add/ remove imports but oh well
        self.assertEqual(e._linenumber, 25)

        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_locals()
        e = ar.exception
        self.assertCountEqual(list(e._locals.keys()), ['foo', 'self'])
        self.assertEqual(e._filename, os.path.abspath(__file__))
        # Ditto L72-73
        self.assertEqual(e._linenumber, 29)

    def test_get_source_indicate_line(self):
        '''Does _get_source() indicate the line from the file provided?'''
        test_linenumber = 5
        test_filename = os.path.abspath(__file__)
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_failure()
        e = ar.exception
        lines = e._get_source(test_filename, test_linenumber).split('\n')
        for i, line in enumerate(lines):
            # Is the linenumber provided indicated with a '>'?
            if i == 1:
                self.assertTrue(lines[i].startswith(' >'))
            else:
                self.assertFalse(lines[i].startswith(' >'))
        # Is the line represented correctly after the line number?
        self.assertEqual(
            lines[1].split('{0} '.format(test_linenumber))[-1],
            linecache.getline(test_filename, test_linenumber).strip())

    def test_get_source_surrounding_lines(self):
        '''Does _get_source() read surrounding lines from the file provided?'''
        test_linenumber = 5
        test_filename = os.path.abspath(__file__)
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_failure()
        e = ar.exception
        lines = e._get_source(test_filename, test_linenumber).split('\n')
        self.assertEqual(len(lines), 3)
        more_lines = e._get_source(
            test_filename, test_linenumber, 2, 5).split('\n')
        self.assertEqual(len(more_lines), 7)

    def test_positional_assert_args(self):
        '''Is annotation captured correctly when using positional arguments?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_positional_assert_args()
        e = ar.exception
        self.assertEqual(e.annotation['message'], 'some message')
        self.assertEqual(e.annotation['advice'], 'some advice')

    def test_named_assert_args(self):
        '''Is annotation captured correctly if named arguments are provided?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_named_assert_args()
        e = ar.exception
        self.assertEqual(e.annotation['message'], 'some message')
        self.assertEqual(e.annotation['advice'], 'some advice')

    def test_use_kwargs_form(self):
        '''Does the kwargs form of an assertion work?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_kwargs()
        e = ar.exception
        self.assertEqual(e.annotation['message'], 'kwargs message')
        self.assertEqual(e.annotation['advice'], 'kwargs advice')

    def test_kwargs_stick_together(self):
        '''Does the kwargs form of an assertion enforce that message and
        advice must both be present?
        '''
        with self.assertRaises(AnnotationError):
            self.case.test_kwargs_advice_missing()

    def test_custom_assertions(self):
        '''Does the marbles advice work with custom-defined assertions?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_reverse_equality()
        e = ar.exception
        self.assertEqual(e.annotation['message'], 'some message')
        self.assertEqual(e.annotation['advice'], 'some advice')

    def test_custom_assertions_kwargs(self):
        '''Does the marbles kwargs advice work with custom assertions?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_reverse_equality_kwargs()
        e = ar.exception
        self.assertEqual(e.annotation['message'], 'some message')
        self.assertEqual(e.annotation['advice'], 'some advice')

    def test_exclude_ignored_locals(self):
        '''Are ignored variables excluded from output?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_locals()
        e = ar.exception
        locals_section = e._format_locals().split('\n\t')
        locals_ = [local.split('=')[0] for local in locals_section]
        for local in locals_:
            self.assertNotIn(local, e._IGNORE_LOCALS)

    def test_exclude_internal_mangled_locals(self):
        '''Are internal/mangled variables excluded from the "Locals"?'''
        with self.assertRaises(AnnotatedAssertionError) as ar:
            self.case.test_internal_mangled_locals()
        e = ar.exception
        locals_section = e._format_locals().split('\n\t')
        locals_ = [local.split('=')[0] for local in locals_section]
        for local in locals_:
            self.assertNotIn(local, ['_foo', '__bar'])
            self.assertFalse(local.startswith('_'))
        self.assertEqual(e.annotation['advice'], "some advice about 'bar'")


if __name__ == '__main__':
    unittest.main()
