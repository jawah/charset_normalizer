import pytest
from charset_normalizer.cd import encoding_languages, mb_encoding_languages, is_multi_byte_encoding


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
        ("iso2022_jp", ["Japanese"])
    ]
)
def test_infer_language_from_cp(iana_encoding, expected_languages):
    languages = mb_encoding_languages(iana_encoding) if is_multi_byte_encoding(iana_encoding) else encoding_languages(iana_encoding)

    for expected_language in expected_languages:
        assert expected_language in languages, "Wrongly detected language for given code page"
