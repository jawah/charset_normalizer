"""
Compute the list of IANA-supported codecs, multibyte first, for charset_normalizer/constant.py.
"""

from charset_normalizer.constant import IANA_SUPPORTED
from charset_normalizer.utils import is_multi_byte_encoding

_mb_supported: list[str] = []
_sb_supported: list[str] = []

for _supported_enc in IANA_SUPPORTED:
    try:
        if is_multi_byte_encoding(_supported_enc):
            _mb_supported.append(_supported_enc)
        else:
            _sb_supported.append(_supported_enc)
    except ImportError:
        _sb_supported.append(_supported_enc)

print(f"IANA_SUPPORTED_MB_FIRST: list[str] = {_mb_supported + _sb_supported!r}")
