from charset_normalizer.api import from_bytes
from typing import Dict, Optional, Union


def detect(byte_str: bytes) -> Dict[str, Optional[Union[str, float]]]:
    """
    chardet legacy method
    Detect the encoding of the given byte string. It should be mostly backward-compatible.

    :param byte_str:     The byte sequence to examine.
    :type byte_str:      ``bytes`` or ``bytearray``
    :rtype: dict
    """
    if not isinstance(byte_str, (bytearray, bytes)):
        raise TypeError('Expected object of type bytes or bytearray, got: '
                        '{0}'.format(type(byte_str)))

    if isinstance(byte_str, bytearray):
        byte_str = bytes(byte_str)

    r = from_bytes(byte_str).best()

    encoding = r.encoding if r is not None else None
    language = r.language if r is not None and r.language != 'Unknown' else ''
    confidence = 1. - r.chaos if r is not None else None

    # Note: CharsetNormalizer does not return 'UTF-8-SIG' as the sig get stripped in the detection/normalization process
    # but chardet does return 'utf-8-sig' and it is a valid codec name.
    if r is not None and encoding == 'utf_8' and r.bom:
        encoding += '_sig'

    return {
        'encoding': encoding,
        'language': language,
        'confidence': confidence
    }
