import pytest
from charset_normalizer import normalize
from os.path import exists
from os import unlink


def test_normalize_fp_creation():
    guesses = normalize(
        "./data/sample.1.ar.srt"
    )

    predicted_path = "./data/sample.1.ar-{}.srt".format(guesses.best().encoding)
    path_exist = exists(
        "./data/sample.1.ar-{}.srt".format(guesses.best().encoding)
    )

    assert path_exist is True

    if path_exist:
        unlink(predicted_path)
