import unittest

from charset_normalizer import CharsetNormalizerMatches as CnM


class TestBytes(unittest.TestCase):

    def test_too_short_none(self):
        self.assertIsNotNone(
            CnM.from_bytes(b'\xfe\xff').best().first()
        )

    def test_empty_bytes(self):
        r = CnM.from_bytes(b'').best().first()

        self.assertIsNotNone(
            r
        )

        self.assertEqual(
            'utf-8',
            r.encoding
        )

        self.assertEqual(
            0,
            len(r.alphabets)
        )

    def test_bom_detection(self):
        with self.subTest('GB18030 UNAVAILABLE SIG'):
            self.assertFalse(
                CnM.from_bytes(
                    '我没有埋怨，磋砣的只是一些时间。'.encode('gb18030')
                ).best().first().byte_order_mark
            )

        with self.subTest('GB18030 AVAILABLE SIG'):
            self.assertTrue(
                CnM.from_bytes(
                    (u'\uFEFF' + '我没有埋怨，磋砣的只是一些时间。').encode('gb18030')
                ).best().first().byte_order_mark
            )

        with self.subTest('UTF-7 AVAILABLE BOM'):
            self.assertTrue(
                CnM.from_bytes(
                    b'\x2b\x2f\x76\x38' + '我没有埋怨，磋砣的只是一些时间。'.encode('utf_7')
                ).best().first().byte_order_mark
            )

        with self.subTest('UTF-8 AVAILABLE BOM'):
            self.assertTrue(
                CnM.from_bytes(
                    b'\xef\xbb\xbf' + '我没有埋怨，磋砣的只是一些时间。'.encode('utf_8')
                ).best().first().byte_order_mark
            )

    def test_encode_decode(self):

        with self.subTest('Encode & Detect UTF-8 WITHOUT SIG SMALL CONTENT'):
            self.assertEqual(
                CnM.from_bytes(
                    'h\xe9llo world!\n'.encode('utf_8')
                ).best().first().encoding,
                'utf_8'
            )

        with self.subTest('Encode & Detect GB18030 WITHOUT SIG'):
            self.assertEqual(
                CnM.from_bytes(
                    '我没有埋怨，磋砣的只是一些时间。'.encode('gb18030')
                ).best().first().encoding,
                'gb18030'
            )

        with self.subTest('Encode & Detect GB18030 WITH SIG (CJK)'):
            self.assertEqual(
                CnM.from_bytes(
                    (u'\uFEFF' + '我没有埋怨，磋砣的只是一些时间。').encode('gb18030')
                ).best().first().encoding,
                'gb18030'
            )

        with self.subTest('Encode & Detect UTF-8 WITHOUT SIG (CJK)'):
            self.assertEqual(
                CnM.from_bytes(
                    '我没有埋怨，磋砣的只是一些时间。'.encode('utf_8')
                ).best().first().encoding,
                'utf_8'
            )

        with self.subTest('Encode & Detect UTF-7 WITHOUT BOM (CJK)'):
            self.assertEqual(
                CnM.from_bytes(
                    '我没有埋怨,蹉跎的只是一些时间。'.encode('utf_7')
                ).best().first().encoding,
                'utf_7'
            )

        with self.subTest('Encode & Detect UTF-7 WITH BOM (CJK)'):
            self.assertEqual(
                CnM.from_bytes(
                    b'\x2b\x2f\x76\x38'+'我没有埋怨，磋砣的只是一些时间。'.encode('utf_7')
                ).best().first().encoding,
                'utf_7'
            )

        with self.subTest('Encode & Detect UTF-7 WITHOUT BOM (CYRILLIC)'):
            self.assertEqual(
                CnM.from_bytes(
                    'Bсеки човек има право на образование. Oбразованието трябва да бъде безплатно,'.encode('utf_7')
                ).best().first().encoding,
                'utf_7'
            )

        with self.subTest('Encode & Detect UTF-8 WITH SIG (CJK)'):
            self.assertEqual(
                CnM.from_bytes(
                   b'\xef\xbb\xbf' + '我没有埋怨，磋砣的只是一些时间。'.encode('utf_8')
                ).best().first().encoding,
                'utf_8'
            )

        with self.subTest('Encode & Detect UTF-8 WITHOUT SIG (CYRILLIC)'):
            self.assertEqual(
                CnM.from_bytes(
                    'Bсеки човек има право на образование. Oбразованието трябва да бъде безплатно, '
                    'поне що се отнася до началното и основното образование.'.encode('utf_8')
                ).best().first().encoding,
                'utf_8'
            )

        with self.subTest('Encode & Detect UTF-8 WITHOUT SIG (CYRILLIC)'):
            self.assertEqual(
                CnM.from_bytes(
                    'Bсеки човек има право на образование.'.encode(
                        'utf_8')
                ).best().first().encoding,
                'utf_8'
            )
