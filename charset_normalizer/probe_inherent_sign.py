from re import findall, compile, IGNORECASE
from encodings.aliases import aliases

RE_POSSIBLE_ENCODING_INDICATION = compile(
    r'(?:(?:encoding)|(?:charset)|(?:coding))(?:[\:= ]{1,10})(?:[\"\']?)([a-zA-Z0-9\-_]+)(?:[\"\']?)',
    IGNORECASE
)


def any_specified_encoding(sequence):
    """
    Search in sequence (ASCII-mode) if there is any sign of declared encoding.
    :param bytes sequence:
    :return: Declared encoding if any else None
    :rtype: str
    """
    if not isinstance(sequence, bytes) and not isinstance(sequence, bytearray):
        raise TypeError

    seq_len = len(sequence)

    results = findall(
        RE_POSSIBLE_ENCODING_INDICATION,
        sequence[:seq_len if seq_len <= 2048 else int(seq_len*0.3)].decode('ascii', errors='ignore')
    )  # type: list[str]

    if len(results) == 0:
        return None

    for specified_encoding in results:
        specified_encoding = specified_encoding.lower().replace('-', '_')

        for a, b in aliases.items():
            if a == specified_encoding:
                return b
            if b == specified_encoding:
                return b

    return None
