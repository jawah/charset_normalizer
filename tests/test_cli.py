import unittest
from charset_normalizer.cli.normalizer import cli_detect, query_yes_no
from unittest.mock import patch
from os.path import exists
from os import remove


class TestCommandLineInterface(unittest.TestCase):

    @patch('builtins.input', lambda *args: 'y')
    def test_simple_yes_input(self):
        self.assertTrue(
            query_yes_no('Are u willing to chill a little bit ?')
        )

    @patch('builtins.input', lambda *args: 'N')
    def test_simple_no_input(self):
        self.assertFalse(
            query_yes_no('Are u willing to chill a little bit ?')
        )

    def test_single_file(self):

        self.assertEqual(
            0,
            cli_detect(
                ['./data/sample.1.ar.srt']
            )
        )

    def test_single_file_normalize(self):
        self.assertEqual(
            0,
            cli_detect(
                ['./data/sample.1.ar.srt', '--normalize']
            )
        )

        self.assertTrue(
            exists('./data/sample.1.ar.cp1256.srt')
        )

        try:
            remove('./data/sample.1.ar.cp1256.srt')
        except:
            pass

    def test_single_verbose_file(self):
        self.assertEqual(
            0,
            cli_detect(
                ['./data/sample.1.ar.srt', '--verbose']
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
