import linecache
import os
import unittest

from marbles import AnnotatedTestCase, AnnotatedAssertionError


@unittest.skip('This is the TestCase being tested')
class ExampleAnnotatedTestCase(AnnotatedTestCase):

    def test_succeed(self):
        self.assertTrue(True, ('some message', 'some advice'))

    def test_failure(self):
        self.assertTrue(False, ('some message', 'some advice'))

    def test_locals(self):
        foo = 'bar'
        self.assertTrue(False, ('some message', 'some advice about {foo}'))


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


class TestAnnotatedAssertionError(unittest.TestCase):

    def setUp(self):
        self.case = ExampleAnnotatedTestCase()

    def tearDown(self):
        delattr(self, 'case')

    def test_verify_annotation_dict_missing_keys(self):
        '''Is an Exception raised if annotation doesn't contain expected keys?'''
        with self.assertRaises(Exception):
            AnnotatedAssertionError(({'foo': 'bar'}, 'standard message'))

    def test_verify_annotation_none(self):
        '''Is an Exception raised if no annotation is provided?'''
        with self.assertRaises(Exception):
            AnnotatedAssertionError(())

    def test_verify_annotation_locals(self):
        '''Are locals defined in the test definition formatted into annotations?'''
        try:
            self.case.test_locals()
        except AnnotatedAssertionError as e:
            self.assertEqual(e.annotation['advice'], 'some advice about \'bar\'')

    def test_get_stack(self):
        '''Does _get_stack() find the stack level with the test definition?'''
        try:
            self.case.test_failure()
        except AnnotatedAssertionError as e:
            self.assertCountEqual(list(e._locals.keys()), ['self'])
            self.assertEqual(e._filename, os.path.abspath(__file__))
            # This isn't great because I have to change it every time I add/
            # remove imports but oh well
            self.assertEqual(e._linenumber, 15)

        try:
            self.case.test_locals()
        except AnnotatedAssertionError as e:
            self.assertCountEqual(list(e._locals.keys()), ['foo', 'self'])
            self.assertEqual(e._filename, os.path.abspath(__file__))
            # Ditto L72-73
            self.assertEqual(e._linenumber, 19)

    def test_get_source_indicate_line(self):
        '''Does _get_source() read and indicate the line from the file provided?'''
        test_linenumber = 5
        test_filename = os.path.abspath(__file__)
        try:
            self.case.test_failure()
        except AnnotatedAssertionError as e:
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
        try:
            self.case.test_failure()
        except AnnotatedAssertionError as e:
            lines = e._get_source(test_filename, test_linenumber).split('\n')
            self.assertEqual(len(lines), 3)
            more_lines = e._get_source(
                test_filename, test_linenumber, 2, 5).split('\n')
            self.assertEqual(len(more_lines), 7)


if __name__ == '__main__':
    unittest.main()

