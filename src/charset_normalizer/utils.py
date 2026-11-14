from __future__ import annotations

import importlib
import logging
import unicodedata
from bisect import bisect_right
from codecs import IncrementalDecoder
from collections import Counter
from functools import lru_cache
from re import compile as re_compile
from typing import Generator, Sequence

from .constant import (
    ENCODING_MARKS,
    IANA_SUPPORTED_SIMILAR,
    LATIN_NON_ASCII_LETTERS,
    RE_POSSIBLE_ENCODING_INDICATION,
    UNICODE_RANGES_COMBINED,
    _COMMON_NON_ASCII_PUNCT_SYM,
    _SECONDARY_RANGE_NAMES,
    COMMON_CJK_CHARACTERS,
    _LATIN,
    _CJK,
    _HANGUL,
    _KATAKANA,
    _HIRAGANA,
    _HALFWIDTH_KATAKANA,
    _THAI,
    _ARABIC,
    _ARABIC_ISOLATED_FORM,
    _LIGATURE,
    _SUPERSCRIPT,
    _SENTENCE_OPEN_PUNCTUATION,
    _ACCENT_KEYWORDS,
    _ACCENTUATED,
    _KNOWN_MB_DECODERS,
    _KNOWN_MB_CLASSES,
    _IANA_NAMES,
    _MULTIBYTE_SEARCH_RADIUS,
)


def _character_flags(character: str) -> int:
    """Compute all name-based classification flags with a single unicodedata.name() call."""
    try:
        desc: str = unicodedata.name(character)
    except ValueError:
        return 0

    flags: int = 0

    if "LATIN" in desc:
        flags |= _LATIN
    if "CJK" in desc:
        flags |= _CJK
    if "HANGUL" in desc:
        flags |= _HANGUL
    if "KATAKANA" in desc:
        flags |= _KATAKANA
        if "HALFWIDTH" in desc:
            flags |= _HALFWIDTH_KATAKANA
    if "HIRAGANA" in desc:
        flags |= _HIRAGANA
    if "THAI" in desc:
        flags |= _THAI
    if "ARABIC" in desc:
        flags |= _ARABIC
        if "ISOLATED FORM" in desc:
            flags |= _ARABIC_ISOLATED_FORM
    if "LIGATURE" in desc or desc.endswith("LETTER AE"):
        flags |= _LIGATURE
    if "SUPERSCRIPT" in desc:
        flags |= _SUPERSCRIPT
    if desc in {"INVERTED QUESTION MARK", "INVERTED EXCLAMATION MARK"}:
        flags |= _SENTENCE_OPEN_PUNCTUATION

    for kw in _ACCENT_KEYWORDS:
        if kw in desc:
            flags |= _ACCENTUATED
            break

    return flags


def is_accentuated(character: str) -> bool:
    return bool(_character_flags(character) & _ACCENTUATED)


def remove_accent(character: str) -> str:
    decomposed: str = unicodedata.decomposition(character)
    if not decomposed:
        return character

    codes: list[str] = decomposed.split(" ")

    return chr(int(codes[0], 16))


# Pre-built sorted lookup table for O(log n) binary search in unicode_range().
# Each entry is (range_start, range_end_exclusive, range_name).
_UNICODE_RANGES_SORTED: list[tuple[int, int, str]] = sorted(
    (ord_range.start, ord_range.stop, name)
    for name, ord_range in UNICODE_RANGES_COMBINED.items()
)
_UNICODE_RANGE_STARTS: list[int] = [e[0] for e in _UNICODE_RANGES_SORTED]


def unicode_range(character: str) -> str | None:
    """
    Retrieve the Unicode range official name from a single character.
    """
    character_ord: int = ord(character)

    if character_ord < 32:
        return "Control character"
    if character_ord < 128:
        return "Basic Latin"

    # Binary search: find the rightmost range whose start <= character_ord
    idx = bisect_right(_UNICODE_RANGE_STARTS, character_ord) - 1
    if idx >= 0:
        start, stop, name = _UNICODE_RANGES_SORTED[idx]
        if character_ord < stop:
            return name

    return None


def is_latin(character: str) -> bool:
    return bool(_character_flags(character) & _LATIN)


def is_punctuation(character: str) -> bool:
    character_category: str = unicodedata.category(character)

    if "P" in character_category:
        return True

    character_range: str | None = unicode_range(character)

    if character_range is None:
        return False

    return "Punctuation" in character_range


def is_symbol(character: str) -> bool:
    character_category: str = unicodedata.category(character)

    if "S" in character_category or "N" in character_category:
        return True

    character_range: str | None = unicode_range(character)

    if character_range is None:
        return False

    return "Forms" in character_range and character_category != "Lo"


def is_emoticon(character: str) -> bool:
    character_range: str | None = unicode_range(character)

    if character_range is None:
        return False

    return "Emoticons" in character_range or "Pictographs" in character_range


def is_separator(character: str) -> bool:
    if character.isspace() or character in {"｜", "+", "<", ">"}:
        return True

    character_category: str = unicodedata.category(character)

    return "Z" in character_category or character_category in {"Po", "Pd", "Pc"}


def is_case_variable(character: str) -> bool:
    return character.islower() != character.isupper()


def is_cjk(character: str) -> bool:
    return bool(_character_flags(character) & _CJK)


def is_hiragana(character: str) -> bool:
    return bool(_character_flags(character) & _HIRAGANA)


def is_katakana(character: str) -> bool:
    return bool(_character_flags(character) & _KATAKANA)


def is_hangul(character: str) -> bool:
    return bool(_character_flags(character) & _HANGUL)


def is_thai(character: str) -> bool:
    return bool(_character_flags(character) & _THAI)


def is_arabic(character: str) -> bool:
    return bool(_character_flags(character) & _ARABIC)


def is_arabic_isolated_form(character: str) -> bool:
    return bool(_character_flags(character) & _ARABIC_ISOLATED_FORM)


def is_cjk_uncommon(character: str) -> bool:
    return character not in COMMON_CJK_CHARACTERS


def is_unicode_range_secondary(range_name: str) -> bool:
    return range_name in _SECONDARY_RANGE_NAMES


def is_unprintable(character: str) -> bool:
    return (
        not character.isspace()  # includes \n \t \r \v
        and not character.isprintable()
        and character != "\x1a"  # Why? Its the ASCII substitute character.
        and character != "\ufeff"  # bug discovered in Python,
        # Zero Width No-Break Space located in 	Arabic Presentation Forms-B, Unicode 1.1 not acknowledged as space.
    )


def any_specified_encoding(
    sequence: bytes | bytearray, search_zone: int = 8192
) -> str | None:
    """
    Extract using ASCII-only decoder any specified encoding in the first n-bytes.
    """
    if not isinstance(sequence, (bytes, bytearray)):
        raise TypeError

    seq_len: int = len(sequence)

    # Cheap literal pre-filter.
    search_bytes = sequence[: min(seq_len, search_zone)]
    lowered_bytes = search_bytes.lower()
    if b"coding" not in lowered_bytes and b"charset" not in lowered_bytes:
        return None

    decoded_zone: str = search_bytes.decode("ascii", errors="ignore")

    for match in RE_POSSIBLE_ENCODING_INDICATION.finditer(decoded_zone):
        specified_encoding = match.group(1).lower().replace("-", "_")
        encoding_iana = _IANA_NAMES.get(specified_encoding)
        if encoding_iana is not None:
            return encoding_iana

    return None


@lru_cache(maxsize=None)
def is_multi_byte_encoding(name: str) -> bool:
    """
    Verify is a specific encoding is a multi byte one based on it IANA name
    """
    if name in _KNOWN_MB_DECODERS:
        return True

    # Besides the Unicode family above, every multibyte codec shipped with
    # Python is implemented by _multibytecodec through exactly one of the six
    # cjkcodecs providers below. Probing those providers directly (getcodec)
    # classifies a name without importing its "encodings.<name>" module:
    # classifying the whole IANA_SUPPORTED list would otherwise import many
    # modules and dominate "import charset_normalizer" wall time.
    # see https://github.com/jawah/charset_normalizer/issues/742
    for provider in _KNOWN_MB_CLASSES:
        try:
            importlib.import_module(provider).getcodec(name)  # type: ignore[attr-defined]
        except (ImportError, AttributeError, LookupError):  # Defensive: edge cases
            continue
        return True

    return False


def identify_sig_or_bom(sequence: bytes | bytearray) -> tuple[str | None, bytes]:
    """
    Identify and extract SIG/BOM in given sequence.
    """

    for iana_encoding in ENCODING_MARKS:
        marks: bytes | list[bytes] = ENCODING_MARKS[iana_encoding]

        if isinstance(marks, bytes):
            marks = [marks]

        for mark in marks:
            if sequence.startswith(mark):
                return iana_encoding, mark

    return None, b""


def should_strip_sig_or_bom(iana_encoding: str) -> bool:
    return iana_encoding not in {"utf_16", "utf_32"}


def iana_name(cp_name: str, strict: bool = True) -> str:
    """Returns the Python normalized encoding name (Not the IANA official name)."""
    cp_name = cp_name.lower().replace("-", "_")

    encoding_iana = _IANA_NAMES.get(cp_name)
    if encoding_iana is not None:
        return encoding_iana

    if strict:
        raise ValueError(f"Unable to retrieve IANA for '{cp_name}'")

    return cp_name


def cp_similarity(iana_name_a: str, iana_name_b: str) -> float:
    if is_multi_byte_encoding(iana_name_a) or is_multi_byte_encoding(iana_name_b):
        return 0.0

    decoder_a = importlib.import_module(f"encodings.{iana_name_a}").IncrementalDecoder
    decoder_b = importlib.import_module(f"encodings.{iana_name_b}").IncrementalDecoder

    id_a: IncrementalDecoder = decoder_a(errors="ignore")
    id_b: IncrementalDecoder = decoder_b(errors="ignore")

    character_match_count: int = 0

    for i in range(256):
        to_be_decoded: bytes = bytes([i])
        if id_a.decode(to_be_decoded) == id_b.decode(to_be_decoded):
            character_match_count += 1

    return character_match_count / 256


def is_cp_similar(iana_name_a: str, iana_name_b: str) -> bool:
    """
    Determine if two code page are at least 80% similar. IANA_SUPPORTED_SIMILAR dict was generated using
    the function cp_similarity.
    """
    return (
        iana_name_a in IANA_SUPPORTED_SIMILAR
        and iana_name_b in IANA_SUPPORTED_SIMILAR[iana_name_a]
    )


def set_logging_handler(
    name: str = "charset_normalizer",
    level: int = logging.INFO,
    format_string: str = "%(asctime)s | %(levelname)s | %(message)s",
) -> None:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(handler)


def cut_sequence_chunks(
    sequences: bytes | bytearray,
    encoding_iana: str,
    offsets: range,
    chunk_size: int,
    bom_or_sig_available: bool,
    strip_sig_or_bom: bool,
    sig_payload: bytes,
    is_multi_byte_decoder: bool,
    decoded_payload: str | None = None,
    deferred_decoding: bool = False,
) -> Generator[str, None, None]:
    # iso2022 codec is stateful, generic mb cuter isn't going to cut it!
    if decoded_payload and encoding_iana.startswith("iso2022_"):
        decoded_length = len(decoded_payload)
        sequence_length = len(sequences)
        for i in offsets:
            decoded_offset = i * decoded_length // sequence_length
            chunk = decoded_payload[decoded_offset : decoded_offset + chunk_size]
            if not chunk:
                break
            yield chunk
    elif decoded_payload and not is_multi_byte_decoder:
        for i in offsets:
            chunk = decoded_payload[i : i + chunk_size]
            if not chunk:
                break
            yield chunk
    elif deferred_decoding:
        # Deferred single-byte probing: the whole payload is not decoded
        # yet. Single-byte codecs are stateless (1 byte == 1 char), hence
        # decode(base)[i:j] == decode(base[i:j]): slicing the raw bytes
        # yields exactly the chunks the branch above would have produced,
        # short trailing chunks included, and raises UnicodeDecodeError on
        # invalid bytes just like the whole-payload decode would.
        base_bytes = (
            sequences if not strip_sig_or_bom else sequences[len(sig_payload) :]
        )
        for i in offsets:
            cut_sequence = base_bytes[i : i + chunk_size]
            if not cut_sequence:
                break
            yield str(cut_sequence, encoding_iana)
    else:
        for i in offsets:
            chunk_end = i + chunk_size
            if chunk_end > len(sequences) + 8:
                continue

            cut_sequence = sequences[i : i + chunk_size]

            if bom_or_sig_available and not strip_sig_or_bom:
                cut_sequence = sig_payload + cut_sequence

            chunk = cut_sequence.decode(
                encoding_iana,
                errors="ignore" if is_multi_byte_decoder else "strict",
            )

            # multi-byte bad cutting detector and adjustment
            # not the cleanest way to perform that fix but clever enough for now.
            if is_multi_byte_decoder and i > 0:
                chunk_partial_size_chk: int = min(chunk_size, 16)
                chunk_prefix = chunk[:chunk_partial_size_chk]
                found_nearby = False

                if decoded_payload:
                    decoded_length = len(decoded_payload)
                    expected_offset = i * decoded_length // len(sequences)
                    search_start = max(0, expected_offset - _MULTIBYTE_SEARCH_RADIUS)
                    search_end = min(
                        decoded_length, expected_offset + _MULTIBYTE_SEARCH_RADIUS
                    )
                    found_nearby = (
                        decoded_payload.find(chunk_prefix, search_start, search_end)
                        >= 0
                    )

                if (
                    decoded_payload
                    and not found_nearby
                    and chunk_prefix not in decoded_payload
                ):
                    for j in range(i, i - 4, -1):
                        cut_sequence = sequences[j:chunk_end]

                        if bom_or_sig_available and not strip_sig_or_bom:
                            cut_sequence = sig_payload + cut_sequence

                        chunk = cut_sequence.decode(encoding_iana, errors="ignore")

                        if chunk[:chunk_partial_size_chk] in decoded_payload:
                            break

            yield chunk


_ASCII_ALPHA_RE = re_compile(r"[A-Za-z]")
_ASCII_RE = re_compile(r"[\x00-\x7f]+")
_MIXED_SCRIPT_ADJ_RE = re_compile(r"[A-Za-z]([^\x00-\x7f])|([^\x00-\x7f])[A-Za-z]")


def latin_orthography_profile(
    texts: Sequence[str],
    detected_languages: Sequence[tuple[str, float]],
) -> tuple[float, float, int]:
    """
    Score script cohesion and orthographic fit of decoded Latin-script text
    across supported Latin alphabets for transitive match tie-breaking.
    """
    raw_counts: Counter[str] = Counter()
    has_ascii_alpha: bool = False

    for text in texts:
        if not text:
            continue
        if not has_ascii_alpha and _ASCII_ALPHA_RE.search(text) is not None:
            has_ascii_alpha = True
        if not text.isascii():
            raw_counts.update(_ASCII_RE.sub("", text))

    if not raw_counts:
        return (1.0, 1.0, 0)

    counts: dict[str, int] = {}
    ranges: set[str] = set()
    weird_non_alpha: int = 0

    for ch, freq in raw_counts.items():
        rng: str | None = unicode_range(ch)
        if ch.isalpha():
            if ch == "İ":
                counts["\u0307"] = counts.get("\u0307", 0) + freq
            else:
                low: str = ch.lower()
                if len(low) == 1:
                    counts[low] = counts.get(low, 0) + freq
                elif low == "i\u0307":
                    counts["\u0307"] = counts.get("\u0307", 0) + freq
            if rng is not None:
                ranges.add(rng)
        elif (
            not ch.isspace()
            and ch not in _COMMON_NON_ASCII_PUNCT_SYM
            and (rng is None or "Punctuation" not in rng)
        ):
            weird_non_alpha += freq

    if not counts:
        if has_ascii_alpha and weird_non_alpha:
            return (0.0, 0.0, -99)
        return (1.0, 1.0, 0)

    non_latin_ranges: set[str] = {r for r in ranges if "Latin" not in r}
    latin_ranges: set[str] = {r for r in ranges if "Latin" in r}

    if non_latin_ranges:
        if not latin_ranges and not has_ascii_alpha:
            return (1.0, 1.0, 0)
        if not latin_ranges and len(non_latin_ranges) == 1 and weird_non_alpha == 0:
            mixed_word: bool = False
            for text in texts:
                for match in _MIXED_SCRIPT_ADJ_RE.finditer(text):
                    adj_ch: str | None = match.group(1) or match.group(2)
                    if adj_ch is not None and adj_ch.isalpha():
                        mixed_word = True
                        break
                if mixed_word:
                    break
            if not mixed_word:
                return (1.0, 1.0, 0)
        return (0.0, 0.0, -99)

    total: int = sum(counts.values()) + weird_non_alpha
    unique: set[str] = set(counts)
    detected_set: set[str] = {lang for lang, _ in detected_languages[:3]}

    best_score: tuple[float, float, int] = (-1.0, -1.0, -1)
    for lang, alphabet in LATIN_NON_ASCII_LETTERS.items():
        if not alphabet:
            continue
        unique_fit: float = len(unique & alphabet) / len(unique)
        occ_fit: float = sum(n for c, n in counts.items() if c in alphabet) / total
        candidate: tuple[float, float, int] = (
            round(unique_fit, 4),
            round(occ_fit, 4),
            1 if lang in detected_set else 0,
        )
        best_score = max(best_score, candidate)

    block_count: int = len(latin_ranges) if latin_ranges else 99
    return (best_score[0], best_score[1], -block_count)
