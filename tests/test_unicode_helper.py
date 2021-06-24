# coding: utf-8
import unittest
import charset_normalizer.utils as unicode_utils


class TestUnicodeHelper(unittest.TestCase):

    def test_should_be_accented(self):

        self.assertTrue(
            unicode_utils.is_accentuated('é')
        )

        self.assertTrue(
            unicode_utils.is_accentuated('è')
        )

        self.assertTrue(
            unicode_utils.is_accentuated('è')
        )

        self.assertTrue(
            unicode_utils.is_accentuated('à')
        )

        self.assertTrue(
            unicode_utils.is_accentuated('À')
        )

        self.assertTrue(
            unicode_utils.is_accentuated('Ù')
        )

        self.assertTrue(
            unicode_utils.is_accentuated('ç')
        )


if __name__ == '__main__':
    unittest.main()
