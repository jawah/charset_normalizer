from __future__ import annotations

import pytest

import charset_normalizer.api as api
from charset_normalizer import from_bytes
from charset_normalizer.constant import TOO_BIG_SEQUENCE


def test_large_payload_u8_sig_basic_entry():
    payload = ("0" * TOO_BIG_SEQUENCE).encode("utf_8_sig")
    best_guess = from_bytes(payload).best()

    assert best_guess is not None, "Large U8 payload case detection completely failed"
    assert (
        best_guess.encoding == "utf_8"
    ), "Large U8 payload case detection wrongly detected!"
    assert best_guess.bom is True, "SIG/BOM property should be True"
    assert len(best_guess.raw) == len(
        payload
    ), "Large payload should remain untouched when accessed through .raw"
    assert (
        best_guess._string is not None
    ), "str should be decoded before direct access (sig available)"


def test_large_payload_ascii_basic_entry():
    payload = ("0" * TOO_BIG_SEQUENCE).encode("utf_8")
    best_guess = from_bytes(payload).best()

    assert (
        best_guess is not None
    ), "Large ASCII payload case detection completely failed"
    assert (
        best_guess.encoding == "ascii"
    ), "Large ASCII payload case detection wrongly detected!"
    assert best_guess.bom is False, "SIG/BOM property should be False"
    assert len(best_guess.raw) == len(
        payload
    ), "Large payload should remain untouched when accessed through .raw"
    assert best_guess._string is None, "str should not be decoded until direct access"


def test_misleading_large_sequence():
    content = (
        ("hello simple ascii " * TOO_BIG_SEQUENCE) + ("我没有埋怨，磋砣的只是一些时间。 磋砣的只是一些时间。")
    ).encode("utf_8")

    guesses = from_bytes(content)

    assert len(guesses) > 0
    match = guesses.best()
    assert match is not None
    assert match._string is not None, "str should be cached as only match"
    assert match.encoding == "utf_8"
    assert str(match) is not None


@pytest.mark.parametrize("boundary_offset", [-1, 0, 1])
def test_large_gb18030_signature_is_stripped(boundary_offset):
    content = "a" * (TOO_BIG_SEQUENCE - 4 + boundary_offset)
    payload = ("\ufeff" + content).encode("gb18030")

    best_guess = from_bytes(payload).best()

    assert best_guess is not None
    assert best_guess.encoding == "gb18030"
    assert best_guess.bom is True
    assert best_guess.raw == payload
    decoded = str(best_guess)
    assert decoded[0] == "a"
    assert decoded == content


@pytest.mark.parametrize(
    "encoding",
    ["gb18030", "utf_7", "utf_8", "utf_16_le", "utf_16_be", "utf_32_le", "utf_32_be"],
)
@pytest.mark.parametrize("leading_bom_character", ["", "\ufeff"])
def test_lazy_decoding_strips_only_signature(monkeypatch, encoding, leading_bom_character):
    monkeypatch.setattr(api, "TOO_BIG_SEQUENCE", 32)
    content = leading_bom_character + "Hello world!\n" * 3
    payload = ("\ufeff" + content).encode(encoding)
    expected_encoding = encoding
    if encoding.startswith(("utf_16", "utf_32")):
        expected_encoding = encoding[:-3]

    best_guess = from_bytes(payload).best()

    assert best_guess is not None
    assert best_guess.encoding == expected_encoding
    assert best_guess.bom is True
    assert best_guess.raw == payload
    assert str(best_guess) == content
    assert best_guess.output() == content.encode("utf_8")
