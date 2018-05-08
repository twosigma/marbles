import marbles.core
import marbles.mixins


def my_sort(i, reverse=False):
    '''Sort the elements in ``i``.'''
    # Purposefully sort in the wrong order so our unit test will fail
    return sorted(i, reverse=~reverse)


class SortTestCase(marbles.core.TestCase, marbles.mixins.MonotonicMixins):

    def test_sort(self):
        i = [1, 3, 4, 5, 2, 0, 8]

        self.assertMonotonicIncreasing(my_sort(i))
        self.assertMonotonicDecreasing(my_sort(i, reverse=True))


if __name__ == '__main__':
    marbles.core.main()
