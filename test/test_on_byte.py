import unittest

from charset_normalizer import CharsetNormalizerMatches as CnM


class TestBytes(unittest.TestCase):

    def test_bom_detection(self):
        self.assertFalse(
            CnM.from_bytes(
                '我没有埋怨，磋砣的只是一些时间。'.encode('gb18030')
            ).best().first().byte_order_mark
        )

        self.assertTrue(
            CnM.from_bytes(
                (u'\uFEFF' + '我没有埋怨，磋砣的只是一些时间。').encode('gb18030')
            ).best().first().byte_order_mark
        )

        self.assertTrue(
            CnM.from_bytes(
                b'\x2b\x2f\x76\x38' + '我没有埋怨，磋砣的只是一些时间。'.encode('utf_7')
            ).best().first().byte_order_mark
        )

        self.assertTrue(
            CnM.from_bytes(
                b'\xef\xbb\xbf' + '我没有埋怨，磋砣的只是一些时间。'.encode('utf_8')
            ).best().first().byte_order_mark
        )

    def test_encode_decode(self):

        self.assertEqual(
            CnM.from_bytes(
                '我没有埋怨，磋砣的只是一些时间。'.encode('gb18030')
            ).best().first().encoding,
            'gb18030'
        )

        self.assertEqual(
            CnM.from_bytes(
                (u'\uFEFF' + '我没有埋怨，磋砣的只是一些时间。').encode('gb18030')
            ).best().first().encoding,
            'gb18030'
        )

        self.assertEqual(
            CnM.from_bytes(
                '我没有埋怨，磋砣的只是一些时间。'.encode('utf_8')
            ).best().first().encoding,
            'utf_8'
        )

        self.assertEqual(
            CnM.from_bytes(
                '我没有埋怨,蹉跎的只是一些时间。'.encode('utf_7')
            ).best().first().encoding,
            'utf_7'
        )

        self.assertEqual(
            CnM.from_bytes(
                b'\x2b\x2f\x76\x38'+'我没有埋怨，磋砣的只是一些时间。'.encode('utf_7')
            ).best().first().encoding,
            'utf_7'
        )



        self.assertEqual(
            CnM.from_bytes(
                'Bсеки човек има право на образование. Oбразованието трябва да бъде безплатно,'.encode('utf_7')
            ).best().first().encoding,
            'utf_7'
        )

        self.assertEqual(
            CnM.from_bytes(
               b'\xef\xbb\xbf' + '我没有埋怨，磋砣的只是一些时间。'.encode('utf_8')
            ).best().first().encoding,
            'utf_8'
        )

        self.assertEqual(
            CnM.from_bytes(
                'Bсеки човек има право на образование. Oбразованието трябва да бъде безплатно, '
                'поне що се отнася до началното и основното образование.'.encode('utf_8')
            ).best().first().encoding,
            'utf_8'
        )

        self.assertEqual(
            CnM.from_bytes(
                'Bсеки човек има право на образование.'.encode(
                    'utf_8')
            ).best().first().encoding,
            'utf_8'
        )
