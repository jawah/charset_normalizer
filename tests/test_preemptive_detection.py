from __future__ import annotations

from xml.etree import ElementTree

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
        (
            b'<meta charset="not-an-encoding"><meta charset="utf-8">',
            "utf_8",
        ),
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


@pytest.mark.parametrize("warm_cache", [False, True])
def test_failed_output_encoding_does_not_change_cache(warm_cache):
    payload = b'<?xml version="1.0" encoding="latin-1"?>caf\xe9'
    match = CharsetMatch(
        payload, "latin_1", 0.0, False, [], preemptive_declaration="latin-1"
    )
    expected = b'<?xml version="1.0" encoding="utf-8"?>caf\xc3\xa9'
    if warm_cache:
        assert match.output() == expected
    for _ in range(2):
        with pytest.raises(ValueError):
            match.output("no-such-encoding")
    assert match.output() == expected
    assert match.output("latin_1") == payload


@pytest.mark.parametrize(
    "template",
    [
        '<?xml version="1.0" encoding="{}"?><doc>caf\u00e9</doc>',
        '<html><head><meta charset="{}"></head><body>caf\u00e9</body></html>',
        '# coding: {}\ntext = "caf\u00e9"\n',
    ],
)
@pytest.mark.parametrize("encoding", ["latin_1", "utf_16"])
def test_utf8_declaration_follows_output_encoding(template, encoding):
    payload = template.format("UTF-8").encode("utf-8")
    match = from_bytes(payload).best()
    assert match is not None
    assert match.encoding == "utf_8"

    output = match.output(encoding)
    assert output.decode(encoding) == template.format(encoding.replace("_", "-"))
    assert match.output(encoding) == output
    assert match.output() == payload


@pytest.mark.parametrize("encoding", ["latin_1", "utf_16"])
@pytest.mark.parametrize("payload_type", [bytes, bytearray])
def test_transcoded_utf8_xml_is_parseable(encoding, payload_type):
    payload = payload_type(
        '<?xml version="1.0" encoding="UTF-8"?><doc>caf\u00e9</doc>'.encode("utf-8")
    )
    match = from_bytes(payload).best()
    assert match is not None

    assert ElementTree.fromstring(match.output(encoding)).text == "caf\u00e9"


@pytest.mark.parametrize("declaration", ["UTF-8", "utf8", "utf_8"])
@pytest.mark.parametrize("encoding", ["utf_8", "UTF-8", "utf8", "u8", "utf_8_sig"])
def test_utf8_output_preserves_utf8_declaration(declaration, encoding):
    text = '<?xml version="1.0" encoding="{}"?><doc>caf\u00e9</doc>'.format(declaration)
    match = from_bytes(text.encode("utf-8")).best()
    assert match is not None

    assert match.output(encoding) == text.encode(encoding)
