from __future__ import annotations

import logging

import pytest

from charset_normalizer.constant import IANA_SUPPORTED
from charset_normalizer.utils import (
    cp_similarity,
    iana_name,
    is_accentuated,
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
