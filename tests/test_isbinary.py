import pytest
import typing
from io import BytesIO
from base64 import b64decode
from charset_normalizer import is_binary
from os import path, pardir

DIR_PATH = path.join(
    path.dirname(path.realpath(__file__)),
    pardir
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        (b'\x00\x5f\x2f\xff'*50, True),
        (b64decode("R0lGODlhAQABAAAAACw="), True),
        (BytesIO(b64decode("R0lGODlhAQABAAAAACw=")), True),
        ('sample-polish.txt', False),
        ('sample-arabic.txt', False)
    ]
)
def test_isbinary(raw: typing.Union[bytes, typing.BinaryIO, str], expected: bool) -> None:
    if isinstance(raw, str):
        raw = DIR_PATH + "/data/{}".format(raw)

    assert is_binary(raw) is expected
