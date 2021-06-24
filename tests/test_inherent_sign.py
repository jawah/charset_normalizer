import unittest
from charset_normalizer.utils import any_specified_encoding


class TestDetectLegacy(unittest.TestCase):

    def test_specified_encoding_xml(self):

        p = any_specified_encoding(
            b'<?xml version="1.0" encoding="EUC-JP"?>'
        )

        self.assertEqual(
            "euc_jp",
            p
        )

    def test_specified_encoding_html(self):

        p = any_specified_encoding(
            b'<html><head><meta charset="utf-8"></head></html>'
        )

        self.assertEqual(
            "utf_8",
            p
        )

    def test_specified_but_unknown(self):
        p = any_specified_encoding(
            b'<html><head><meta charset="utf-57"></head></html>'
        )

        self.assertIsNone(
            p
        )
