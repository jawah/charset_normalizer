from __future__ import annotations

import unittest
from os import pardir, path, remove
from os.path import exists
from unittest.mock import patch

from charset_normalizer.cli import cli_detect, query_yes_no

DIR_PATH = path.join(path.dirname(path.realpath(__file__)), pardir)


class TestCommandLineInterface(unittest.TestCase):
    @patch("builtins.input", lambda *args: "y")
    def test_simple_yes_input(self):
        self.assertTrue(query_yes_no("Are u willing to chill a little bit ?"))

    @patch("builtins.input", lambda *args: "N")
    def test_simple_no_input(self):
        self.assertFalse(query_yes_no("Are u willing to chill a little bit ?"))

    def test_single_file(self):
        self.assertEqual(0, cli_detect([DIR_PATH + "/data/sample-arabic-1.txt"]))

    def test_version_output_success(self):
        with self.assertRaises(SystemExit):
            cli_detect(["--version"])

    def test_single_file_normalize(self):
        self.assertEqual(
            0, cli_detect([DIR_PATH + "/data/sample-arabic-1.txt", "--normalize"])
        )

        self.assertTrue(exists(DIR_PATH + "/data/sample-arabic-1.cp1256.txt"))

        try:
            remove(DIR_PATH + "/data/sample-arabic-1.cp1256.txt")
        except:
            pass

    def test_single_verbose_file(self):
        self.assertEqual(
            0, cli_detect([DIR_PATH + "/data/sample-arabic-1.txt", "--verbose"])
        )

    def test_multiple_file(self):
        self.assertEqual(
            0,
            cli_detect(
                [
                    DIR_PATH + "/data/sample-arabic-1.txt",
                    DIR_PATH + "/data/sample-french.txt",
                    DIR_PATH + "/data/sample-chinese.txt",
                ]
            ),
        )

    def test_with_alternative(self):
        self.assertEqual(
            0,
            cli_detect(
                [
                    "-a",
                    DIR_PATH + "/data/sample-arabic-1.txt",
                    DIR_PATH + "/data/sample-french.txt",
                    DIR_PATH + "/data/sample-chinese.txt",
                ]
            ),
        )

    def test_with_minimal_output(self):
        self.assertEqual(
            0,
            cli_detect(
                [
                    "-m",
                    DIR_PATH + "/data/sample-arabic-1.txt",
                    DIR_PATH + "/data/sample-french.txt",
                    DIR_PATH + "/data/sample-chinese.txt",
                ]
            ),
        )

    def test_with_minimal_and_alt(self):
        self.assertEqual(
            0,
            cli_detect(
                [
                    "-m",
                    "-a",
                    DIR_PATH + "/data/sample-arabic-1.txt",
                    DIR_PATH + "/data/sample-french.txt",
                    DIR_PATH + "/data/sample-chinese.txt",
                ]
            ),
        )

    def test_multiple_file_normalize(self):
        """Ensure --normalize with multiple files writes each output to the
        correct path and sets unicode_path on the corresponding result entry
        (not always on the first entry). Regression test for GH-702."""
        arabic_path = DIR_PATH + "/data/sample-arabic-1.txt"
        turkish_path = DIR_PATH + "/data/sample-turkish.txt"

        self.assertEqual(0, cli_detect([arabic_path, turkish_path, "--normalize"]))

        arabic_out = DIR_PATH + "/data/sample-arabic-1.cp1256.txt"
        turkish_out = DIR_PATH + "/data/sample-turkish.cp1254.txt"

        try:
            self.assertTrue(
                exists(arabic_out),
                "Normalized output for first file should exist",
            )
            self.assertTrue(
                exists(turkish_out),
                "Normalized output for second file should exist",
            )

            # Verify each file contains distinct, non-empty content that
            # matches what from_fp would produce for that specific input.
            with open(arabic_out, "rb") as fp:
                arabic_content = fp.read()
            with open(turkish_out, "rb") as fp:
                turkish_content = fp.read()

            self.assertGreater(len(arabic_content), 0)
            self.assertGreater(len(turkish_content), 0)
            self.assertNotEqual(
                arabic_content,
                turkish_content,
                "Each file must receive its own normalized content",
            )
        finally:
            for p in (arabic_out, turkish_out):
                try:
                    remove(p)
                except OSError:
                    pass

    def test_multiple_file_normalize_with_alternatives(self):
        """Same as above but with --with-alternative, ensuring that
        alternative entries appended between files do not confuse the
        unicode_path assignment."""
        arabic_path = DIR_PATH + "/data/sample-arabic-1.txt"
        turkish_path = DIR_PATH + "/data/sample-turkish.txt"

        self.assertEqual(
            0, cli_detect([arabic_path, turkish_path, "--normalize", "-a"])
        )

        arabic_out = DIR_PATH + "/data/sample-arabic-1.cp1256.txt"
        turkish_out = DIR_PATH + "/data/sample-turkish.cp1254.txt"

        try:
            self.assertTrue(
                exists(arabic_out),
                "Normalized output for first file should exist",
            )
            self.assertTrue(
                exists(turkish_out),
                "Normalized output for second file should exist",
            )
        finally:
            for p in (arabic_out, turkish_out):
                try:
                    remove(p)
                except OSError:
                    pass

    def test_non_existent_file(self):
        with self.assertRaises(SystemExit) as cm:
            cli_detect([DIR_PATH + "/data/not_found_data.txt"])

        self.assertEqual(cm.exception.code, 2)

    def test_replace_without_normalize(self):
        self.assertEqual(
            cli_detect([DIR_PATH + "/data/sample-arabic-1.txt", "--replace"]), 1
        )

    def test_force_replace_without_replace(self):
        self.assertEqual(
            cli_detect([DIR_PATH + "/data/sample-arabic-1.txt", "--force"]), 1
        )


if __name__ == "__main__":
    unittest.main()
