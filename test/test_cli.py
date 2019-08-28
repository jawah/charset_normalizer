import unittest
from charset_normalizer.cli.normalizer import cli_detect


class TestCommandLineInterface(unittest.TestCase):

    def test_single_file(self):

        self.assertEqual(
            0,
            cli_detect(
                ['./data/sample.1.ar.srt']
            )
        )

    def test_multiple_file(self):
        self.assertEqual(
            0,
            cli_detect(
                [
                    './data/sample.1.ar.srt',
                    './data/sample.1.he.srt',
                    './data/sample-chinese.txt'
                ]
            )
        )

    def test_non_existent_file(self):

        with self.assertRaises(SystemExit) as cm:
            cli_detect(
                ['./data/not_found_data.txt']
            )

        self.assertEqual(cm.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
