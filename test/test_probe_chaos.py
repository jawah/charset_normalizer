import unittest
from charset_normalizer.probe_chaos import ProbeChaos


class TestProbeChaos(unittest.TestCase):

    def test_not_gibberish(self):

        self.assertEqual(
            ProbeChaos('[試下今日用中文打日記先… 打得差唔好怪我! 唔識睇o個d就… hahaha 幫你地唔到~ 學下中文啦.').ratio,
            0.
        )

        self.assertEqual(
            ProbeChaos('العقلية , التنويم المغناطيسي و / أو الاقتراح').ratio,
            0.
        )

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
            0.5
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
        self.assertGreater(
            ProbeChaos("""ØĢØŠØģØ§ØĶŲ ŲŲ ØĢŲ Ø§ŲŲØ§Øģ ŲŲŲ ŲØ§ ØģŲŲŲØŠØģØ§ØĶŲŲŲØ ØŊØđŲØ§ ŲØģŲØđ ØđŲ (ŲØąŲØŊŲ) ŲØ§ŲØŪØ§ØŠŲ""").ratio,
            1.
        )

        self.assertGreater(
            ProbeChaos(
                """ÇáÚŞáíÉ , ÇáÊäæíã ÇáãÛäÇØíÓí æ / Ãæ ÇáÇŞÊÑÇÍ""").ratio,
            1.
        )

    def test_part_gibberish(self):

        self.assertGreater(
            ProbeChaos(
                """hishamkoc@yahoo.com ุชุฑุฌูููุฉ ููุดูููุงู ุงููููููููุงูRadoZ ุชูููุนููููุฏูููู ุงููููุชูููููููููููููุช ููููู ูููุจููู""").ratio,
            0.5
        )

        self.assertGreater(
            ProbeChaos("锌褉械锌芯写邪胁邪褌械谢褟屑懈 锌芯褝褌芯 ").ratio,
            0.5
        )


if __name__ == '__main__':
    unittest.main()
