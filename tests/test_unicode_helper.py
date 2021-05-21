# coding: utf-8
import unittest
import charset_normalizer.unicode as unicode_utils


class TestUnicodeHelper(unittest.TestCase):

    def test_list_by_range(self):

        self.assertEqual(
            {'Basic Latin': ['a', 'b', 'c', 'd', 'e', 'é', 'ù'], 'Hangul Syllables': ['역', '사'],
             'Greek and Coptic': ['π', 'ο', 'υ']},
            unicode_utils.list_by_range(['a', 'b', 'c', 'd', 'e', 'é', 'ù', '역', '사', 'π', 'ο', 'υ'])
        )

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

    def test_should_throw(self):
        with self.assertRaises(IOError):
            unicode_utils.is_accentuated('àé')
        with self.assertRaises(IOError):
            unicode_utils.is_accentuated('aé')
        with self.assertRaises(IOError):
            unicode_utils.is_accentuated('aa')


if __name__ == '__main__':
    unittest.main()
