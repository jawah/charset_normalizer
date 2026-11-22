from __future__ import annotations

import codecs

import pytest

from charset_normalizer import api


@pytest.fixture
def tilde_codec(monkeypatch, request):
    name = "x_tilde_escape"
    decoded_inputs = []
    table = {i: i for i in range(256) if i != ord("~")}

    def decode(data, errors="strict"):
        raw = bytes(data)
        decoded_inputs.append((len(raw), errors))
        text, _ = codecs.charmap_decode(raw.replace(b"~n", b"\xf1"), errors, table)
        return text, len(raw)

    codec = codecs.CodecInfo(name=name, encode=None, decode=decode)
    if hasattr(codecs, "unregister"):
        search = {name: codec}.get
        codecs.register(search)
        request.addfinalizer(lambda: codecs.unregister(search))
    else:
        # Python 3.7–3.9 can evict a cached codec but cannot unregister a search hook.
        import _codecs
        import encodings

        monkeypatch.setitem(encodings._cache, name, codec)
        codecs.lookup(name)
        request.addfinalizer(lambda: _codecs._forget_codec(name))

    # Simulate the candidate list captured when a codec is registered before import.
    monkeypatch.setattr(
        api, "IANA_SUPPORTED_MB_FIRST", [*api.IANA_SUPPORTED_MB_FIRST, name]
    )
    return name, decoded_inputs


def test_custom_multibyte_encoding(tilde_codec):
    name, decoded_inputs = tilde_codec
    prefix = b"the tree " * 56 + b"beside "
    suffix = b" under the tree." * 256
    assert len(prefix) == 511
    raw = prefix + b"~n" + suffix
    best = api.from_bytes(raw, cp_isolation=[name]).best()
    assert best is not None and best.encoding == name
    assert str(best) == prefix.decode("ascii") + "ñ" + suffix.decode("ascii")
    assert decoded_inputs == [(len(raw), "strict")]


def test_custom_multibyte_encoding_rejects_invalid_escape_between_samples(tilde_codec):
    name, decoded_inputs = tilde_codec
    # The first sample ends at byte 511 and the second starts at byte 940.
    raw = b"a" * 700 + b"~x" + b"b" * 4000
    assert api.from_bytes(raw, cp_isolation=[name]).best() is None
    assert decoded_inputs == [(len(raw), "strict")]
