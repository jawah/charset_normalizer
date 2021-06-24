# coding: utf-8
import unittest
from charset_normalizer.md import mess_ratio


class TestProbeChaos(unittest.TestCase):

    def test_not_gibberish(self):

        with self.subTest('Chinese Not Gibberish'):
            self.assertLessEqual(
                mess_ratio(
                    '典肇乎庚辰年十二月廿一，及己丑年二月十九，收各方語言二百五十，合逾七百萬目；二十大卷佔八成，單英文卷亦過二百萬。悉文乃天下有志共筆而成；有意助之，幾網路、隨纂作，大典茁焉。'),
                0.
            )

        with self.subTest('Arabic Not Gibberish'):
            self.assertEqual(
                mess_ratio('العقلية , التنويم المغناطيسي و / أو الاقتراح'),
                0.
            )

        with self.subTest('Arabic Styled Not Gibberish'):
            self.assertEqual(
                mess_ratio("RadoZ تـــعــــديــل الـــتــــوقــيــــت مـــن قــبــل"),
                0.
            )

    def test_subtle_gibberish(self):

        self.assertLessEqual(
            mess_ratio("Cehennemin Sava■þ²s²'da kim?"),
            0.5
        )

        self.assertGreaterEqual(
            mess_ratio("Cehennemin Sava■þ²s²'da kim?"),
            0.
        )

        self.assertGreater(
            mess_ratio("´Á¥½³ø§i --  ±i®Ìºû, ³¯·Ø©v"),
            0.8
        )

        self.assertGreater(
            mess_ratio("ïstanbul, T■rkiye'nin en kalabal»k, iktisadi ve k■lt■rel aÓ»dan en —nemli"),
            0.
        )

        self.assertLessEqual(
            mess_ratio("ïstanbul, T■rkiye'nin en kalabal»k, iktisadi ve k■lt■rel aÓ»dan en —nemli"),
            0.5
        )

        self.assertLessEqual(
            mess_ratio("<i>Parce que Óa, c'est la vÕritable histoire de la rencontre avec votre Tante Robin.</i>"),
            0.5
        )

    def test_complete_gibberish(self):
        self.assertTrue(
            mess_ratio("""ØĢØŠØģØ§ØĶŲ ŲŲ ØĢŲ Ø§ŲŲØ§Øģ ŲŲŲ ŲØ§ ØģŲŲŲØŠØģØ§ØĶŲŲŲØ ØŊØđŲØ§ ŲØģŲØđ ØđŲ (ŲØąŲØŊŲ) ŲØ§ŲØŪØ§ØŠŲ""") >= 0.1,
        )

        self.assertTrue(
            mess_ratio("""ÇáÚŞáíÉ , ÇáÊäæíã ÇáãÛäÇØíÓí æ / Ãæ ÇáÇŞÊÑÇÍ""") >= 0.1,
        )

    def test_part_gibberish(self):

        self.assertGreater(
            mess_ratio(
                """hishamkoc@yahoo.com ุชุฑุฌูููุฉ ููุดูููุงู ุงููููููููุงูRadoZ ุชูููุนููููุฏูููู ุงููููุชูููููููููููููุช ููููู ูููุจููู""", 0.5),
            0.3
        )


if __name__ == '__main__':
    unittest.main()
