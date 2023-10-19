from charset_normalizer import from_bytes
import pytest
import platform

@pytest.mark.xfail(platform.python_version_tuple()[0] == "3" and platform.python_version_tuple()[1] == "7", reason="Unicode database is too old for this case (Python 3.7)")
def test_unicode_edge_case():
    payload = b'\xef\xbb\xbf\xf0\x9f\xa9\xb3'

    best_guess = from_bytes(payload).best()

    assert best_guess is not None, "Payload should have given something, detection failure"
    assert best_guess.encoding == "utf_8", "UTF-8 payload wrongly detected"
