import marbles.core


class ComplexTestCase(marbles.core.AnnotatedTestCase):

    def test_for_edge_case(self):
        self.assertTrue(False)


if __name__ == '__main__':
    marbles.core.main()
