from __future__ import annotations

import pytest

from charset_normalizer import CharsetMatch, from_bytes
from charset_normalizer.utils import any_specified_encoding


@pytest.mark.parametrize(
    "payload, expected_encoding",
    [
        (b'<?xml version="1.0" encoding="EUC-JP"?>', "euc_jp"),
        (b'<html><head><meta charset="utf-8"></head></html>', "utf_8"),
        (b'<html><head><meta charset="utf-57"></head></html>', None),
        (b"# coding: utf-8", "utf_8"),
        (b'<?xml version="1.0" encoding="UTF-8"?>', "utf_8"),
        (b'<?xml version="1.0" encoding="US-ASCII"?>', "ascii"),
        (b'<?xml version="1.0" encoding="JohaB"?>', "johab"),
        (b'<?xml version="1.0" encoding="ibm037"?>', "cp037"),
        (b"<html><head><meta charset=WINDOWS-1252></head></html>", "cp1252"),
        (b'<html><head><meta charset="WINDOWS-1256"></head></html>', "cp1256"),
    ],
)
def test_detect_most_common_body_encoding(payload, expected_encoding):
    specified_encoding = any_specified_encoding(payload)

    assert (
        specified_encoding == expected_encoding
    ), "Unable to determine properly encoding from given body"


@pytest.mark.parametrize(
    "payload, expected_outcome",
    [
        (
            b'<?xml version="1.0" encoding="EUC-JP"?>',
            b'<?xml version="1.0" encoding="utf-8"?>',
        ),
        (
            b'<html><head><meta charset="utf-8"></head></html>',
            b'<html><head><meta charset="utf-8"></head></html>',
        ),
        (
            b'<html><head><meta charset="utf-57"></head></html>',
            b'<html><head><meta charset="utf-57"></head></html>',
        ),
        (b"# coding: utf-8", b"# coding: utf-8"),
        (
            b'<?xml version="1.0" encoding="UTF-8"?>',
            b'<?xml version="1.0" encoding="UTF-8"?>',
        ),
        (
            b'<?xml version="1.0" encoding="US-ASCII"?>',
            b'<?xml version="1.0" encoding="utf-8"?>',
        ),
        (
            b'<?xml version="1.0" encoding="JohaB"?>',
            b'<?xml version="1.0" encoding="utf-8"?>',
        ),
        (
            b"<html><head><meta charset=WINDOWS-1252></head></html>",
            b"<html><head><meta charset=utf-8></head></html>",
        ),
        (
            b'<html><head><meta charset="WINDOWS-1256"></head></html>',
            b'<html><head><meta charset="utf-8"></head></html>',
        ),
    ],
)
def test_preemptive_mark_replacement(payload, expected_outcome):
    """
    When generating (to Unicode converted) bytes, we want to change any potential declarative charset
    to utf-8. This test that.
    """
    specified_encoding = any_specified_encoding(payload)

    detected_encoding = (
        specified_encoding if specified_encoding is not None else "utf-8"
    )

    m = CharsetMatch(
        payload,
        detected_encoding,
        0.0,
        False,
        [],
        preemptive_declaration=specified_encoding,
    )

    transformed_output = m.output()

    assert transformed_output == expected_outcome


def test_output_preserves_encoding_of_prose_near_charset_declaration():
    """Prose like 'encoding of' must not be rewritten; only the real declaration."""
    payload = (
        b"The encoding of this file matters.\n"
        b'<meta charset="windows-1252">\n'
        b"Price: caf\xe9\n"
    )
    m = from_bytes(payload).best()
    assert m is not None
    out = m.output()
    assert b"The encoding of this file matters." in out
    assert b"The encoding utf-8 this" not in out
    assert b'charset="utf-8"' in out or b"charset=utf-8" in out


def test_output_rewrites_meta_when_prose_mentions_utf8():
    """Space-separated 'encoding utf-8' in prose must not steal the declaration."""
    payload = (
        b"Note: encoding utf-8 is unsupported here.\n"
        b'<meta charset="windows-1252">\n'
        b"Cafe price: caf\xe9\n"
    )
    assert any_specified_encoding(payload) == "cp1252"
    m = from_bytes(payload).best()
    assert m is not None
    out = m.output()
    assert b'charset="utf-8"' in out or b"charset=utf-8" in out
    assert b"windows-1252" not in out
