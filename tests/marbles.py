import unittest

from marbles import AnnotatedTestCase, AnnotatedAssertionError


class ExampleAnnotatedTestCase(AnnotatedTestCase):

    def test_succeed(self):
        self.assertTrue(True, ('some message', 'some advice'))

    def test_failure(self):
        self.assertTrue(False, ('some message', 'some advice'))


class TestAnnotatedTestCase(unittest.TestCase):

    def setUp(self):
        self.case = ExampleAnnotatedTestCase()

    def tearDown(self):
        delattr(self, 'case')

    def test_annotated_assertion_error_not_raised(self):
        '''Assert that no error is raised if a test succeeds.'''
        self.case.test_succeed()

    def test_annotated_assertion_error_raised(self):
        '''Assert that an AnnotatedAssertionError is raised if a test fails.'''
        with self.assertRaises(AnnotatedAssertionError):
            self.case.test_failure()


class TestAnnotatedAssertionError(unittest.TestCase):

    def test_verify_annotation_dict_missing_keys(self):
        '''Is an Exception instead of an AnnotatedAssertionError raised if the
        annotation dict does not contain the expected keys?
        '''
        with self.assertRaises(Exception):
            AnnotatedAssertionError(({'foo': 'bar'}, 'standard message'))

    def test_verify_annotation_none(self):
        '''Is an Exception instead of an AnnotatedAssertionError raised if no
        annotation is provided?
        '''
        with self.assertRaises(Exception):
            AnnotatedAssertionError(())


if __name__ == '__main__':
    unittest.main()

