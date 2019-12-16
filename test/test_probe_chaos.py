# coding: utf-8
import unittest
from charset_normalizer.probe_chaos import ProbeChaos


class TestProbeChaos(unittest.TestCase):

    def test_not_gibberish(self):

        with self.subTest('Chinese Not Gibberish'):
            self.assertLessEqual(
                ProbeChaos(
                    '典肇乎庚辰年十二月廿一，及己丑年二月十九，收各方語言二百五十，合逾七百萬目；二十大卷佔八成，單英文卷亦過二百萬。悉文乃天下有志共筆而成；有意助之，幾網路、隨纂作，大典茁焉。').ratio,
                0.
            )

        with self.subTest('Arabic Not Gibberish'):
            self.assertEqual(
                ProbeChaos('العقلية , التنويم المغناطيسي و / أو الاقتراح').ratio,
                0.
            )

        with self.subTest('Arabic Styled Not Gibberish'):
            self.assertEqual(
                ProbeChaos("RadoZ تـــعــــديــل الـــتــــوقــيــــت مـــن قــبــل").ratio,
                0.
            )

    def test_subtle_gibberish(self):

        self.assertLessEqual(
            ProbeChaos("Cehennemin Sava■þ²s²'da kim?").ratio,
            0.5
        )

        self.assertGreaterEqual(
            ProbeChaos("Cehennemin Sava■þ²s²'da kim?").ratio,
            0.
        )

        self.assertGreater(
            ProbeChaos('´Á¥½³ø§i --  ±i®Ìºû, ³¯·Ø©v').ratio,
            0.
        )

        self.assertLessEqual(
            ProbeChaos("´Á¥½³ø§i --  ±i®Ìºû, ³¯·Ø©v").ratio,
            0.9
        )

        self.assertGreater(
            ProbeChaos("ïstanbul, T■rkiye'nin en kalabal»k, iktisadi ve k■lt■rel aÓ»dan en —nemli").ratio,
            0.
        )

        self.assertLessEqual(
            ProbeChaos("ïstanbul, T■rkiye'nin en kalabal»k, iktisadi ve k■lt■rel aÓ»dan en —nemli").ratio,
            0.5
        )

        self.assertLessEqual(
            ProbeChaos("<i>Parce que Óa, c'est la vÕritable histoire de la rencontre avec votre Tante Robin.</i>").ratio,
            0.5
        )

    def test_complete_gibberish(self):
        self.assertTrue(
            ProbeChaos("""ØĢØŠØģØ§ØĶŲ ŲŲ ØĢŲ Ø§ŲŲØ§Øģ ŲŲŲ ŲØ§ ØģŲŲŲØŠØģØ§ØĶŲŲŲØ ØŊØđŲØ§ ŲØģŲØđ ØđŲ (ŲØąŲØŊŲ) ŲØ§ŲØŪØ§ØŠŲ""").gave_up,
        )

        self.assertTrue(
            ProbeChaos("""ÇáÚŞáíÉ , ÇáÊäæíã ÇáãÛäÇØíÓí æ / Ãæ ÇáÇŞÊÑÇÍ""").gave_up,
        )

    def test_part_gibberish(self):

        self.assertGreater(
            ProbeChaos(
                """hishamkoc@yahoo.com ุชุฑุฌูููุฉ ููุดูููุงู ุงููููููููุงูRadoZ ุชูููุนููููุฏูููู ุงููููุชูููููููููููููุช ููููู ูููุจููู""", giveup_threshold=0.5).ratio,
            0.4
        )

        self.assertGreater(
            ProbeChaos("锌褉械锌芯写邪胁邪褌械谢褟屑懈 锌芯褝褌芯 ").ratio,
            0.4
        )


if __name__ == '__main__':
    unittest.main()
