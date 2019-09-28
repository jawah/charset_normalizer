from charset_normalizer.constant import MULTI_BYTE_DECODER
import importlib


def is_multi_byte_encoding(encoding_name):
    """
    Verify is a specific encoding is a multi byte one based on it IANA name
    :param str encoding_name: IANA encoding name
    :return: True if multi byte
    :rtype: bool
    """
    return issubclass(
        importlib.import_module('encodings.{encoding_name}'.format(encoding_name=encoding_name)).IncrementalDecoder,
        MULTI_BYTE_DECODER
    )
