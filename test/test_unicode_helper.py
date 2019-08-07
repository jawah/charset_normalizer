import unittest
from charset_normalizer.unicode import UnicodeRangeIdentify


class TestUnicodeHelper(unittest.TestCase):
    def test_should_be_accented(self):

        self.assertTrue(
            UnicodeRangeIdentify.is_accentuated('é')
        )

        self.assertTrue(
            UnicodeRangeIdentify.is_accentuated('è')
        )

        self.assertTrue(
            UnicodeRangeIdentify.is_accentuated('è')
        )

        self.assertTrue(
            UnicodeRangeIdentify.is_accentuated('à')
        )

        self.assertTrue(
            UnicodeRangeIdentify.is_accentuated('À')
        )

        self.assertTrue(
            UnicodeRangeIdentify.is_accentuated('Ù')
        )

        self.assertTrue(
            UnicodeRangeIdentify.is_accentuated('ç')
        )

    def test_should_throw(self):
        with self.assertRaises(IOError):
            UnicodeRangeIdentify.is_accentuated('àé')
        with self.assertRaises(IOError):
            UnicodeRangeIdentify.is_accentuated('aé')
        with self.assertRaises(IOError):
            UnicodeRangeIdentify.is_accentuated('aa')


if __name__ == '__main__':
    unittest.main()
