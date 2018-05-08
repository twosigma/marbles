import os
import marbles.core


class FileTestCase(marbles.core.TestCase):

    def test_file_size(self):
        file_name = __file__  # noqa: F841

        self.assertEqual(os.path.getsize(__file__), 0)


if __name__ == '__main__':
    marbles.core.main()
