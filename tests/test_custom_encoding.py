from __future__ import annotations

import codecs
import sys
import types
from encodings.aliases import aliases

from charset_normalizer import api, from_bytes, utils
from charset_normalizer.constant import _IANA_NAMES


def test_registered_custom_multibyte_codec_survives_chunk_boundaries(monkeypatch):
    name = "x_charset_normalizer_test_multibyte"

    def decode(data: bytes, errors: str = "strict") -> tuple[str, int]:
        output: list[str] = []
        index = 0
        while index < len(data):
            value = data[index]
            if value == 0x81:
                if index + 1 == len(data):
                    if errors == "ignore":
                        break
                    raise UnicodeDecodeError(
                        name, data, index, index + 1, "incomplete two-byte character"
                    )
                output.append(chr(data[index + 1]))
                index += 2
            else:
                output.append(chr(value))
                index += 1
        return "".join(output), len(data)

    def encode(text: str, errors: str = "strict") -> tuple[bytes, int]:
        output = bytearray()
        for character in text:
            if character == " ":
                output.append(0x20)
            elif ord(character) < 0x80:
                output.extend((0x81, ord(character)))
            else:
                raise UnicodeEncodeError(name, text, 0, 1, "ASCII only")
        return bytes(output), len(text)

    class IncrementalDecoder(codecs.IncrementalDecoder):
        def __init__(self, errors: str = "strict") -> None:
            super().__init__(errors)
            self.pending = b""

        def getstate(self) -> tuple[bytes, int]:
            return self.pending, 0

        def setstate(self, state: tuple[bytes, int]) -> None:
            self.pending = state[0]

        def decode(self, data: bytes, final: bool = False) -> str:
            pending, state = self.getstate()
            combined = pending + data
            if not final and combined.endswith(b"\x81"):
                self.setstate((b"\x81", state))
                combined = combined[:-1]
            else:
                self.setstate((b"", state))
            return decode(combined, self.errors)[0]

    class IncrementalEncoder(codecs.IncrementalEncoder):
        def encode(self, text: str, final: bool = False) -> bytes:
            return encode(text, self.errors)[0]

    def codec_info() -> codecs.CodecInfo:
        return codecs.CodecInfo(
            name=name,
            encode=encode,
            decode=decode,
            incrementalencoder=IncrementalEncoder,
            incrementaldecoder=IncrementalDecoder,
        )

    def search(encoding: str) -> codecs.CodecInfo | None:
        return codec_info() if encoding == name else None

    codecs.register(search)
    module = types.ModuleType(f"encodings.{name}")
    module.IncrementalDecoder = IncrementalDecoder
    module.getregentry = codec_info
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setitem(aliases, name, name)
    monkeypatch.setitem(_IANA_NAMES, name, name)
    monkeypatch.setattr(
        api, "IANA_SUPPORTED_MB_FIRST", [name, *api.IANA_SUPPORTED_MB_FIRST]
    )

    text = " " + ("The quick brown fox jumps over the lazy dog. " * 200)
    payload = encode(text)[0]

    assert payload.decode(name) == text
    incremental = codecs.getincrementaldecoder(name)()
    assert incremental.decode(b"\x81") == ""
    assert incremental.getstate() == (b"\x81", 0)
    assert incremental.decode(b"T", final=True) == "T"
    assert incremental.getstate() == (b"", 0)
    assert utils.is_multi_byte_encoding(name) is False
    assert utils.is_custom_encoding(name) is True

    matches = from_bytes(payload, cp_isolation=[name], chunk_size=512, steps=5)
    best = matches.best()

    assert best is not None
    assert best.encoding == name
    assert str(best) == text

    monkeypatch.setattr(api, "TOO_BIG_SEQUENCE", len(payload))
    large_path_matches = from_bytes(
        payload, cp_isolation=[name], chunk_size=512, steps=5
    )
    large_path_best = large_path_matches.best()
    assert large_path_best is not None
    assert str(large_path_best) == text

    invalid_matches = from_bytes(
        payload + b"\x81", cp_isolation=[name], chunk_size=512, steps=5
    )
    assert invalid_matches.best() is None
