import unittest
from glob import glob
from charset_normalizer import CharsetNormalizerMatches as CnM
from os.path import basename


class TestFileCharsetNormalizer(unittest.TestCase):

    SHOULD_BE = {
        'sample.1.ar.srt': 'cp1256',
        'sample.1.fr.srt': 'cp1252',
        'sample.1.gr.srt': 'iso8859_7',
        'sample.1.he.srt': 'cp1255',
        'sample.1.hi.srt': 'ascii',
        'sample.1.ru.srt': 'cp1251',
        'sample.1.tu.srt': 'cp1256',  # Not actually the good one. But kinda readable.
        'sample.2.ar.srt': 'cp1256',
        'sample.3.ar.srt': 'utf_8',
        'sample.4.ar.srt': 'cp1256',
        'sample.5.ar.srt': 'utf_8',
        'sample-chinese.txt': 'big5',
        'sample-greek.txt': 'cp1253',
        'sample-hebrew.txt': 'utf_8',
        'sample-russian.txt': 'mac_cyrillic',
        'sample-russian-2.txt': 'utf_8',
        'sample-turkish.txt': 'cp1252',
    }

    def test_file_input(self):
        for path_name in glob('../data/*.srt') + glob('../data/*.txt'):

            matches = CnM.from_path(path_name)

            self.assertGreater(
                len(matches),
                0
            )

            r_ = matches.best().first()

            self.assertIsNotNone(
                r_
            )

            self.assertEqual(
                r_.encoding,
                TestFileCharsetNormalizer.SHOULD_BE[basename(path_name)]
            )


if __name__ == '__main__':
    unittest.main()
