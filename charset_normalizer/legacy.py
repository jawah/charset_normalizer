from charset_normalizer.normalizer import CharsetNormalizerMatches as CnM


def detect(byte_str):
    """
    chardet/cchardet legacy method
    Detect the encoding of the given byte string.

    :param byte_str:     The byte sequence to examine.
    :type byte_str:      ``bytes`` or ``bytearray``
    :rtype: dict
    """
    if not isinstance(byte_str, bytearray):
        if not isinstance(byte_str, bytes):
            raise TypeError('Expected object of type bytes or bytearray, got: '
                            '{0}'.format(type(byte_str)))
        else:
            byte_str = bytearray(byte_str)

    r = CnM.from_bytes(byte_str).best().first()

    return {
        'encoding': r.encoding if r is not None else None,
        'language': r.language if r is not None and r.language != 'Unknown' else '',
        'confidence': 1. - r.chaos if r is not None else None
    }
