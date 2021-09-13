from charset_normalizer.api import from_path
import pytest


@pytest.mark.parametrize(
    "input_data_file, expected_charset, expected_language",
    [
        ('sample.1.ar.srt', 'cp1256', 'Arabic'),
        ('sample.1.fr.srt', 'cp1252', 'French'),
        ('sample.1.gr.srt', 'cp1253', 'Greek'),
        ('sample.1.he.srt', 'cp1255', 'Hebrew'),
        ('sample.1.hi.srt', 'ascii', 'English'),
        ('sample.1.ru.srt', 'cp1251', 'Russian'),
        ('sample.1.tu.srt', 'cp1254', 'Turkish'),
        ('sample.2.ar.srt', 'cp1256', 'Arabic'),
        ('sample.3.ar.srt', 'utf_8', 'Arabic'),
        ('sample.4.ar.srt', 'cp1256', 'Arabic'),
        ('sample.5.ar.srt', 'utf_8', 'Arabic'),
        ('sample-chinese.txt', 'big5', 'Classical Chinese'),
        ('sample-greek.txt', 'cp1253', 'Greek'),
        ('sample-greek-2.txt', 'cp1253', 'Greek'),
        ('sample-hebrew-2.txt', 'cp1255', 'Hebrew'),
        ('sample-hebrew-3.txt', 'cp1255', 'Hebrew'),
        ('sample-bulgarian.txt', 'utf_8', 'Bulgarian'),
        ('sample-english.bom.txt', 'utf_8', 'English'),
        ('sample-spanish.txt', 'utf_8', 'Spanish'),
        ('sample-korean.txt', 'cp949', 'Korean'),
        ('sample-turkish.txt', 'cp1254', 'Turkish'),
        ('sample-russian-2.txt', 'utf_8', 'Russian'),
        ('sample-russian.txt', 'mac_cyrillic', 'Russian'),
    ]
)
def test_elementary_detection(
    input_data_file: str,
    expected_charset: str,
    expected_language: str,
):
    best_guess = from_path("./data/{}".format(input_data_file)).best()

    assert best_guess is not None, "Elementary detection has failed upon '{}'".format(input_data_file)
    assert best_guess.encoding == expected_charset, "Elementary charset detection has failed upon '{}'".format(input_data_file)
    assert best_guess.language == expected_language, "Elementary language detection has failed upon '{}'".format(input_data_file)
