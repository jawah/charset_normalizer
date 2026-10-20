from __future__ import annotations

import json
from io import BytesIO
from os.path import abspath

import pytest

import charset_normalizer.cli.__main__ as cli_module
from charset_normalizer.models import CharsetMatch, CharsetMatches


class NamedBytesIO(BytesIO):
    def __init__(self, payload, name):
        super().__init__(payload)
        self.name = name


def run_cli(monkeypatch, capsys, payloads, *args):
    streams = []

    def open_memory_file(file_type, name):
        stream = NamedBytesIO(payloads[name], name)
        streams.append(stream)
        return stream

    monkeypatch.setattr(cli_module.FileType, "__call__", open_memory_file)
    result = cli_module.cli_detect([*args, *payloads])
    captured = capsys.readouterr()
    assert all(stream.closed for stream in streams)
    return result, captured


@pytest.mark.parametrize("alternatives", [False, True])
def test_single_match_json_shape(monkeypatch, capsys, alternatives):
    payload = "Le café est une boisson délicieuse. ".encode("utf-16")
    args = ["--with-alternative"] if alternatives else []

    result, captured = run_cli(monkeypatch, capsys, {"sample.txt": payload}, *args)
    output = json.loads(captured.out)

    assert result == 0
    assert captured.err == ""
    assert isinstance(output, list if alternatives else dict)
    if alternatives:
        assert len(output) == 1
        output = output[0]
    assert output["path"] == abspath("sample.txt")
    assert output["encoding"] == "utf_16"
    assert output["is_preferred"] is True


@pytest.mark.parametrize("alternatives", [False, True])
def test_no_match_json_shape(monkeypatch, capsys, alternatives):
    args = ["-a"] if alternatives else []

    _, captured = run_cli(monkeypatch, capsys, {"binary.bin": bytes(range(256))}, *args)
    output = json.loads(captured.out)

    assert "Unable to identify originating encoding" in captured.err
    assert isinstance(output, list if alternatives else dict)
    if alternatives:
        assert len(output) == 1
        output = output[0]
    assert output["path"] == abspath("binary.bin")
    assert output["encoding"] is None
    assert output["chaos"] == 1.0
    assert output["coherence"] == 0.0


@pytest.mark.parametrize("alternatives", [False, True])
@pytest.mark.parametrize("binary_files", [0, 1, 2])
def test_multiple_files_json_shape(monkeypatch, capsys, alternatives, binary_files):
    text = "Le café est une boisson délicieuse. ".encode("utf-16")
    payloads = {
        "first.txt": bytes(range(256)) if binary_files == 2 else text,
        "second.txt": bytes(range(256)) if binary_files else text,
    }
    args = ["-a"] if alternatives else []

    _, captured = run_cli(monkeypatch, capsys, payloads, *args)
    output = json.loads(captured.out)

    assert isinstance(output, list)
    assert len(output) == 2
    assert [entry["path"] for entry in output] == [abspath(name) for name in payloads]
    assert [entry["encoding"] for entry in output] == (
        ["utf_16"] * (2 - binary_files) + [None] * binary_files
    )


def test_multiple_alternatives_json_shape(monkeypatch, capsys):
    best = CharsetMatch(b"x", "utf_8", 0.1, False, [("French", 0.9)])
    alternative = CharsetMatch(b"y", "cp1252", 0.2, False, [("English", 0.5)])
    monkeypatch.setattr(
        cli_module,
        "from_fp",
        lambda *args, **kwargs: CharsetMatches([best, alternative]),
    )

    result, captured = run_cli(monkeypatch, capsys, {"sample.txt": b"x"}, "-a")
    output = json.loads(captured.out)

    assert result == 0
    assert captured.err == ""
    assert isinstance(output, list)
    assert [entry["encoding"] for entry in output] == ["utf_8", "cp1252"]
    assert [entry["is_preferred"] for entry in output] == [True, False]
    assert [entry["chaos"] for entry in output] == [10.0, 20.0]
    assert [entry["coherence"] for entry in output] == [90.0, 50.0]


@pytest.mark.parametrize("alternatives", [False, True])
def test_minimal_output_remains_plain_text(monkeypatch, capsys, alternatives):
    payloads = {
        "sample.txt": "Le café est une boisson délicieuse. ".encode("utf-16"),
        "binary.bin": bytes(range(256)),
    }
    args = ["-a", "-m"] if alternatives else ["-m"]

    _, captured = run_cli(monkeypatch, capsys, payloads, *args)

    assert captured.out == "utf_16\nundefined\n"
