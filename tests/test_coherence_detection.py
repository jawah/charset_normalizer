from __future__ import annotations

import pytest

from charset_normalizer import from_bytes
from charset_normalizer.cd import (
    characters_popularity_compare,
    coherence_ratio,
    encoding_languages,
    filter_alt_coherence_matches,
    get_target_features,
    is_multi_byte_encoding,
    mb_encoding_languages,
)


def test_characters_popularity_compare_with_duplicates():
    assert characters_popularity_compare("English", ["e", "e", "t", "a"]) == 0.25


@pytest.mark.parametrize(
    "iana_encoding, expected_languages",
    [
        ("cp864", ["Arabic", "Farsi"]),
        ("cp862", ["Hebrew"]),
        ("cp737", ["Greek"]),
        ("cp424", ["Hebrew"]),
        ("cp273", ["Latin Based"]),
        ("johab", ["Korean"]),
        ("shift_jis", ["Japanese"]),
        ("mac_greek", ["Greek"]),
        ("iso2022_jp", ["Japanese"]),
    ],
)
def test_infer_language_from_cp(iana_encoding, expected_languages):
    languages = (
        mb_encoding_languages(iana_encoding)
        if is_multi_byte_encoding(iana_encoding)
        else encoding_languages(iana_encoding)
    )

    for expected_language in expected_languages:
        assert expected_language in languages, (
            "Wrongly detected language for given code page"
        )


@pytest.mark.parametrize(
    "language, expected_have_accents, expected_pure_latin",
    [
        ("English", False, True),
        ("French", True, True),
        ("Hebrew", False, False),
        ("Arabic", False, False),
        ("Vietnamese", True, True),
        ("Turkish", True, True),
    ],
)
def test_target_features(language, expected_have_accents, expected_pure_latin):
    target_have_accents, target_pure_latin = get_target_features(language)

    assert target_have_accents is expected_have_accents
    assert target_pure_latin is expected_pure_latin


@pytest.mark.parametrize(
    "matches, expected_return",
    [
        ([], []),
        ([("English—", 0.5)], [("English", 0.5)]),
        ([("Japanese——", 0.5)], [("Japanese", 0.5)]),
        (
            [("English—", 0.5), ("French", 0.4), ("Japanese——", 0.3)],
            [("English", 0.5), ("French", 0.4), ("Japanese", 0.3)],
        ),
        (
            [("English—", 0.5), ("English", 0.8), ("French", 0.4)],
            [("English", 0.8), ("French", 0.4)],
        ),
        (
            [
                (
                    "English",
                    0.88,
                ),
                ("English—", 0.99),
            ],
            [("English", 0.99)],
        ),
        (
            [
                (
                    "English",
                    0.88,
                ),
                ("English—", 0.99),
                ("English——", 0.999),
            ],
            [("English", 0.999)],
        ),
        (
            [
                (
                    "English",
                    0.88,
                ),
                ("English—", 0.77),
            ],
            [("English", 0.88)],
        ),
        (
            [
                (
                    "English",
                    0.88,
                ),
                ("Italian", 0.77),
            ],
            [("English", 0.88), ("Italian", 0.77)],
        ),
    ],
)
def test_filter_alt_coherence_matches(matches, expected_return):
    results = filter_alt_coherence_matches(matches)

    assert results == expected_return


def test_alternative_language_above_threshold():
    # This README excerpt scores 0.7 for English and 0.75 for its alternative.
    text = (
        "Copyright © [Ahmed TAHRI @Ousret](https://github.com/Ousret).<br />\n"
        "This project is [MIT]"
        "(https://github.com/Ousret/charset_normalizer/blob/master/LICENSE) licensed."
    )

    assert coherence_ratio(text, threshold=0.75) == [("English", 0.75)]

    match = from_bytes(text.encode("utf-8"), language_threshold=0.75).best()

    assert match is not None
    assert match.encoding == "utf_8"
    assert match.language == "English"
    assert match.languages == ["English"]
    assert match.coherence == 0.75
