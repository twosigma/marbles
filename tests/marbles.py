import unittest

from marbles import AnnotatedTestCase, AnnotatedAssertionError


@unittest.skip('This is the TestCase being tested')
class ExampleAnnotatedTestCase(AnnotatedTestCase):
    # TODO (jsa): how do I get unittest not to run this test case?

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

    def test_verify_annotation_dict_missing_keys(self):
        '''Is an Exception raised if annotation dict doesn't contain expected keys?'''
        with self.assertRaises(Exception):
            AnnotatedAssertionError(({'foo': 'bar'}, 'standard message'))

    def test_verify_annotation_none(self):
        '''Is an Exception raised if no annotation is provided?'''
        with self.assertRaises(Exception):
            AnnotatedAssertionError(())

    def test_verify_annotation_locals(self):
        '''Are locals defined in the test definition formatted into annotations?'''
        case = ExampleAnnotatedTestCase()
        try:
            case.test_locals()
        except AnnotatedAssertionError as e:
            self.assertEqual(e.annotation['advice'], 'some advice about \'bar\'')


if __name__ == '__main__':
    unittest.main()

