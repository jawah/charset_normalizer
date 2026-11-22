from __future__ import annotations

import codecs
import logging

import pytest

from charset_normalizer.constant import IANA_SUPPORTED, _SINGLE_BYTE_DECODERS
from charset_normalizer.utils import (
    cp_similarity,
    iana_name,
    is_accentuated,
    is_multi_byte_encoding,
    set_logging_handler,
)


@pytest.mark.parametrize(
    "character, expected_is_accentuated",
    [
        ("é", True),
        ("è", True),
        ("à", True),
        ("À", True),
        ("Ù", True),
        ("ç", True),
        ("a", False),
        ("€", False),
        ("&", False),
        ("Ö", True),
        ("ü", True),
        ("ê", True),
        ("Ñ", True),
        ("Ý", True),
        ("Ω", False),
        ("ø", False),
        ("Ё", False),
    ],
)
def test_is_accentuated(character, expected_is_accentuated):
    assert (
        is_accentuated(character) is expected_is_accentuated
    ), "is_accentuated behavior incomplete"


@pytest.mark.parametrize(
    "cp_name_a, cp_name_b, expected_is_similar",
    [
        ("cp1026", "cp1140", True),
        ("cp1140", "cp1026", True),
        ("latin_1", "cp1252", True),
        ("latin_1", "iso8859_4", True),
        ("latin_1", "cp1251", False),
        ("cp1251", "mac_turkish", False),
    ],
)
def test_cp_similarity(cp_name_a, cp_name_b, expected_is_similar):
    is_similar = cp_similarity(cp_name_a, cp_name_b) >= 0.8

    assert is_similar is expected_is_similar, "cp_similarity is broken"


@pytest.mark.parametrize("cp_name", IANA_SUPPORTED)
def test_iana_name_resolves_every_supported_encoding(cp_name):
    assert iana_name(cp_name) == cp_name, "IANA_SUPPORTED entry is unresolvable"


@pytest.mark.parametrize("cp_name", IANA_SUPPORTED)
def test_every_supported_encoding_decodes_with_errors_ignore(cp_name):
    # Detection decodes with errors="ignore", which utf_7_imap (Python 3.16+) rejects.
    decoder = codecs.getincrementaldecoder(cp_name)(errors="ignore")
    assert isinstance(decoder.decode(b"@"), str)


@pytest.mark.parametrize("encoding", sorted(_SINGLE_BYTE_DECODERS))
def test_single_byte_decoders_can_decode_each_byte_independently(encoding):
    payload = bytes(range(256))
    characters = [bytes([b]).decode(encoding, errors="replace") for b in payload]
    assert all(len(character) == 1 for character in characters)
    assert "".join(characters) == payload.decode(encoding, errors="replace")


def test_single_byte_classification_resolves_known_aliases():
    assert not is_multi_byte_encoding("ISO-8859-1")
    assert not is_multi_byte_encoding("windows-1252")
    assert is_multi_byte_encoding("utf8")
    assert is_multi_byte_encoding("cp1252_custom")
