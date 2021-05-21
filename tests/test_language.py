import unittest
from charset_normalizer.normalizer import CharsetNormalizerMatches as CnM
from glob import glob
from os.path import basename


class TestLanguageDetection(unittest.TestCase):
    SHOULD_BE = {
        'sample.1.ar.srt': 'Arabic',
        'sample.1.fr.srt': 'French',
        'sample.1.gr.srt': 'Greek',
        'sample.1.he.srt': 'Hebrew',
        'sample.1.hi.srt': 'English',
        'sample.1.ru.srt': 'Russian',
        'sample.1.tu.srt': 'Turkish',
        'sample.2.ar.srt': 'Arabic',
        'sample.3.ar.srt': 'Arabic',
        'sample.4.ar.srt': 'Arabic',
        'sample.5.ar.srt': 'Arabic',
        'sample-chinese.txt': 'Classical Chinese',
        'sample-greek.txt': 'Greek',
        'sample-greek-2.txt': 'Greek',
        'sample-hebrew.txt': 'English',
        'sample-hebrew-2.txt': 'Hebrew',
        'sample-hebrew-3.txt': 'Hebrew',
        'sample-russian.txt': 'Russian',
        'sample-russian-2.txt': 'Russian',
        'sample-turkish.txt': 'Turkish',
        'sample-korean.txt': 'Korean',
        'sample-spanish.txt': 'Spanish',
        'sample-bulgarian.txt': 'Bulgarian',
        'sample-english.bom.txt': 'English'
    }

    def test_language_detection(self):

        for path_name in glob('./data/*.srt') + glob('./data/*.txt'):
            with self.subTest(path_name+' WRITTEN IN '+TestLanguageDetection.SHOULD_BE[basename(path_name)]):
                r_ = CnM.from_path(path_name).best().first()

                self.assertEqual(
                    TestLanguageDetection.SHOULD_BE[basename(path_name)],
                    r_.language
                )


if __name__ == '__main__':
    unittest.main()
