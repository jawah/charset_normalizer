# coding: utf-8
import unittest
from glob import glob

from charset_normalizer import CharsetNormalizerMatches as CnM
from os.path import basename


class TestFileCharsetNormalizer(unittest.TestCase):

    SHOULD_BE = {
        'sample.1.ar.srt': 'cp1256',
        'sample.1.fr.srt': 'cp1252',
        'sample.1.gr.srt': 'cp1253',
        'sample.1.he.srt': 'cp1255',
        'sample.1.hi.srt': 'ascii',
        'sample.1.ru.srt': 'cp1251',
        'sample.1.tu.srt': 'cp1252',  # Not actually the good one. But kinda readable.
        'sample.2.ar.srt': 'cp1256',
        'sample.3.ar.srt': 'utf_8',
        'sample.4.ar.srt': 'cp1256',
        'sample.5.ar.srt': 'utf_8',
        'sample-chinese.txt': 'big5',
        'sample-greek.txt': 'cp1253',
        'sample-greek-2.txt': 'cp1253',
        'sample-hebrew.txt': 'utf_8',
        'sample-hebrew-2.txt': 'cp1255',
        'sample-hebrew-3.txt': 'cp1255',
        'sample-russian.txt': 'mac_cyrillic',
        'sample-russian-2.txt': 'utf_8',
        'sample-turkish.txt': 'cp1252',
        'sample-korean.txt': 'cp949',
        'sample-spanish.txt': 'utf_8',
        'sample-bulgarian.txt': 'utf_8',
        'sample-english.bom.txt': 'utf_8'
    }

    def test_file_input(self):
        for path_name in glob('./data/*.srt') + glob('./data/*.txt'):

            with self.subTest('test_file_input <{}>'.format(path_name)):

                matches = CnM.from_path(path_name)

                self.assertGreater(
                    len(matches),
                    0
                )

                r_ = matches.best().first()

                self.assertIsNotNone(
                    r_
                )

                if isinstance(TestFileCharsetNormalizer.SHOULD_BE[basename(path_name)], str):
                    self.assertEqual(
                        r_.encoding,
                        TestFileCharsetNormalizer.SHOULD_BE[basename(path_name)]
                    )
                else:
                    self.assertIn(
                        r_.encoding,
                        TestFileCharsetNormalizer.SHOULD_BE[basename(path_name)]
                    )


if __name__ == '__main__':
    unittest.main()
