from __future__ import annotations

import platform

import pytest

from charset_normalizer import from_bytes


@pytest.mark.xfail(
    platform.python_version_tuple()[0] == "3"
    and platform.python_version_tuple()[1] == "7",
    reason="Unicode database is too old for this case (Python 3.7)",
)
def test_unicode_edge_case():
    payload = b"\xef\xbb\xbf\xf0\x9f\xa9\xb3"

    best_guess = from_bytes(payload).best()

    assert best_guess is not None, (
        "Payload should have given something, detection failure"
    )
    assert best_guess.encoding == "utf_8", "UTF-8 payload wrongly detected"


def test_issue_gh520():
    """Verify that minorities does not strip basic latin characters!"""
    payload = b"/includes/webform.compon\xd2\xaants.inc/"

    best_guess = from_bytes(payload).best()

    assert best_guess is not None, (
        "Payload should have given something, detection failure"
    )
    assert "Basic Latin" in best_guess.alphabets


def test_issue_gh509():
    """Two common ASCII punctuations should render as-is."""
    payload = b");"

    best_guess = from_bytes(payload).best()

    assert best_guess is not None, (
        "Payload should have given something, detection failure"
    )
    assert "ascii" == best_guess.encoding


def test_issue_gh498():
    """This case was mistaken for utf-16-le, this should never happen again."""
    payload = b"\x84\xae\xaa\xe3\xac\xa5\xad\xe2 Microsoft Word.docx"

    best_guess = from_bytes(payload).best()

    assert best_guess is not None, (
        "Payload should have given something, detection failure"
    )
    assert "Cyrillic" in best_guess.alphabets


def test_regression_gh771_fallback_entry_on_undecodable_payload():
    chaos = b'=][;:!?*&^%$#@ (){}<>~|_+ "quoted" ' * 90
    gap_position = 512 + (len(chaos) // 5 - 512) // 2
    payload = chaos[:gap_position] + "\u00e9".encode() + chaos[gap_position:]

    results = from_bytes(payload)  # must not raise
    best_guess = results.best()

    assert best_guess is not None, "fallback machinery gave no result at all"
    assert best_guess.encoding == "utf_8", (
        f"expected the utf_8 fallback, got {best_guess.encoding}"
    )
    assert str(best_guess), "best match must decode without error"


def test_from_bytes_rejects_non_positive_chunk_size():
    garbage = bytes([(i * 37) % 256 for i in range(5000)])
    with pytest.raises(ValueError, match="chunk_size must be a positive integer"):
        from_bytes(garbage, chunk_size=0)
    with pytest.raises(ValueError, match="chunk_size must be a positive integer"):
        from_bytes(garbage, chunk_size=-1)
    assert from_bytes(garbage, chunk_size=1).best() is None
    text_best = from_bytes(b"hello world", chunk_size=1).best()
    assert text_best is not None
    assert text_best.encoding == "ascii"
