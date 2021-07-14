import unittest

from charset_normalizer.api import from_bytes
from charset_normalizer.constant import TOO_BIG_SEQUENCE


class TestBytes(unittest.TestCase):

    def test_too_short_none(self):
        self.assertIsNotNone(
            from_bytes(b'\xfe\xff').best().first()
        )

    def test_empty_bytes(self):
        r = from_bytes(b'').best().first()

        self.assertIsNotNone(
            r
        )

        self.assertEqual(
            'utf_8',
            r.encoding
        )

        self.assertEqual(
            0,
            len(r.alphabets)
        )

    def test_empty_str_with_sig_gb18030(self):
        r = from_bytes('\uFEFF'.encode('gb18030')).best()

        self.assertIsNotNone(r)
        self.assertEqual(
            "",
            str(r)
        )
        self.assertEqual(
            "gb18030",
            r.encoding
        )
        self.assertEqual(
            4,
            len(r.raw)
        )

    def test_empty_str_with_sig_utf8(self):
        r = from_bytes(b'\xef\xbb\xbf').best()

        self.assertIsNotNone(r)
        self.assertEqual(
            "",
            str(r)
        )
        self.assertEqual(
            "utf_8",
            r.encoding
        )
        self.assertEqual(
            3,
            len(r.raw)
        )

    def test_empty_str_with_large_sig_utf8(self):
        r = from_bytes(b'\xef\xbb\xbf' + (b'0' * TOO_BIG_SEQUENCE)).best()

        self.assertIsNotNone(r)
        self.assertEqual(
            '0' * TOO_BIG_SEQUENCE,
            str(r)
        )
        self.assertEqual(
            "utf_8",
            r.encoding
        )
        self.assertEqual(
            TOO_BIG_SEQUENCE + 3,
            len(r.raw)
        )

    def test_on_empty_json(self):

        with self.subTest("Detecting empty JSON as ASCII"):
            results = from_bytes(b"{}").best()
            self.assertIsNotNone(
                results.best()
            )
            self.assertEqual(
                results.best().encoding,
                "ascii"
            )

    def test_bom_detection(self):
        with self.subTest('GB18030 UNAVAILABLE SIG'):
            self.assertFalse(
                from_bytes(
                    '我没有埋怨，磋砣的只是一些时间。。今觀俗士之論也，以族舉德，以位命賢，茲可謂得論之一體矣，而未獲至論之淑真也。'.encode('gb18030')
                ).best().first().byte_order_mark
            )

        with self.subTest('GB18030 AVAILABLE SIG'):
            self.assertTrue(
                from_bytes(
                    (u'\uFEFF' + '我没有埋怨，磋砣的只是一些时间。').encode('gb18030')
                ).best().first().byte_order_mark
            )

        with self.subTest('UTF-32 AVAILABLE BOM'):
            self.assertTrue(
                from_bytes(
                   '我没有埋怨，磋砣的只是一些时间。'.encode('utf_32')
                ).best().first().byte_order_mark
            )

        with self.subTest('UTF-8 AVAILABLE BOM'):
            self.assertTrue(
                from_bytes(
                    b'\xef\xbb\xbf' + '我没有埋怨，磋砣的只是一些时间。'.encode('utf_8')
                ).best().first().byte_order_mark
            )

    def test_encode_decode(self):

        with self.subTest('Encode & Detect UTF-8 WITHOUT SIG SMALL CONTENT'):
            self.assertEqual(
                from_bytes(
                    'h\xe9llo world!\n'.encode('utf_8')
                ).best().first().encoding,
                'utf_8'
            )

        with self.subTest('Encode & Detect GB18030 WITHOUT SIG'):
            self.assertEqual(
                from_bytes(
                    '我没有埋怨，磋砣的只是一些时间。夫令譽從我興，而二命自天降之。'.encode('gb18030')
                ).best().first().encoding,
                'gb18030'
            )

        with self.subTest('Encode & Detect GB18030 WITH SIG (CJK)'):
            self.assertEqual(
                from_bytes(
                    (u'\uFEFF' + '我没有埋怨，磋砣的只是一些时间。').encode('gb18030')
                ).best().first().encoding,
                'gb18030'
            )

        with self.subTest('Encode & Detect UTF-8 WITHOUT SIG (CJK)'):
            self.assertEqual(
                from_bytes(
                    '我没有埋怨，磋砣的只是一些时间。'.encode('utf_8')
                ).best().first().encoding,
                'utf_8'
            )

        with self.subTest('Encode & Detect UTF-32 WITH BOM (CJK)'):
            self.assertEqual(
                from_bytes(
                    '我没有埋怨，磋砣的只是一些时间。'.encode('utf_32')
                ).best().first().encoding,
                'utf_32'
            )

        with self.subTest('Encode & Detect UTF-8 WITH SIG (CJK)'):
            self.assertEqual(
                from_bytes(
                   b'\xef\xbb\xbf' + '我没有埋怨，磋砣的只是一些时间。'.encode('utf_8')
                ).best().first().encoding,
                'utf_8'
            )

        with self.subTest('Encode & Detect UTF-8 WITHOUT SIG (CYRILLIC)'):
            self.assertEqual(
                from_bytes(
                    'Bсеки човек има право на образование. Oбразованието трябва да бъде безплатно, '
                    'поне що се отнася до началното и основното образование.'.encode('utf_8')
                ).best().first().encoding,
                'utf_8'
            )

        with self.subTest('Encode & Detect UTF-8 WITHOUT SIG (CYRILLIC)'):
            self.assertEqual(
                from_bytes(
                    'Bсеки човек има право на образование.'.encode(
                        'utf_8')
                ).best().first().encoding,
                'utf_8'
            )
