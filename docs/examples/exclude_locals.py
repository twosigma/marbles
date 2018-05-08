import marbles.core


class IntermediateStateTestCase(marbles.core.TestCase):

    def test_foo(self):
        start_str = 'foo'

        # Capitalize our string one character at a time
        _intermediate_state_1 = start_str.replace('f', 'F')
        __intermediate_state_2 = _intermediate_state_1.replace('o', 'O')

        stop_str = __intermediate_state_2.lower()

        self.assertNotEqual(start_str, stop_str)


if __name__ == '__main__':
    marbles.core.main()
