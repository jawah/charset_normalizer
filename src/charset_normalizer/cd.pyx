# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: nonecheck=False
# cython: freethreading_compatible=True

import importlib
import sys
from functools import lru_cache
from operator import itemgetter

from cpython.mem cimport PyMem_Free, PyMem_Malloc, PyMem_Realloc
from cpython.pyport cimport PY_SSIZE_T_MAX
from libc.stddef cimport size_t
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t
from libc.string cimport memcpy, memset

from charset_normalizer._cython_compat cimport (
    _unicode_data,
    _unicode_kind,
    _unicode_read,
)
from charset_normalizer.md cimport (
    NO_RANGE_ID,
    UNICODE_RANGE_CAPACITY,
    CharInfo,
    _char_info_from_codepoint,
    _is_suspicious_range_ids,
)

from charset_normalizer.constant import (
    FREQUENCIES,
    JP_NAMES,
    KO_NAMES,
    LANGUAGE_SUPPORTED_COUNT,
    TOO_SMALL_SEQUENCE,
    ZH_NAMES,
)
from charset_normalizer.md import (
    _ASCII_CHAR_INFO,
    _char_info,
    is_suspiciously_successive_range as _range_compatibility,
)
from charset_normalizer.utils import is_multi_byte_encoding, is_unicode_range_secondary

# Preserve the same module-level export as the Python implementation.
is_suspiciously_successive_range = _range_compatibility


cdef extern from "Python.h":
    # Part of the stable ABI, hence usable for the abi3 wheels as well.
    object PyUnicode_DecodeUTF32(
        const char* s, Py_ssize_t size, const char* errors, int* byteorder
    )


cdef enum:
    LANGUAGE_COUNT = 41
    BMP_CODEPOINT_COUNT = 65536
    STACK_RANK_CAPACITY = 512
    LANGUAGE_RANK_CAPACITY = 128
    STACK_LAYER_CAPACITY = 512
    INITIAL_LAYER_CAPACITY = 32

cdef uint8_t _LANGUAGE_RANKS[LANGUAGE_COUNT][BMP_CODEPOINT_COUNT]
cdef uint16_t _LANGUAGE_LENGTHS[LANGUAGE_COUNT]
cdef bint _LANGUAGE_HAS_ACCENTS[LANGUAGE_COUNT]
cdef bint _LANGUAGE_PURE_LATIN[LANGUAGE_COUNT]
cdef dict _LANGUAGE_INDEX = {}
cdef list _LANGUAGE_NAMES = []
cdef list _LANGUAGE_DISPLAY_NAMES = []
# PyUnicode_DecodeUTF32 byte order matching the in-memory uint32_t layout.
cdef int _NATIVE_BYTEORDER = -1 if sys.byteorder == "little" else 1


cdef void _initialize_language_ranks():
    cdef Py_ssize_t language_index = 0
    cdef Py_ssize_t rank
    cdef Py_UCS4 codepoint
    cdef object language
    cdef object characters
    cdef str character
    cdef CharInfo info

    if len(FREQUENCIES) != LANGUAGE_COUNT:
        raise RuntimeError(
            f"Expected {LANGUAGE_COUNT} language profiles, got {len(FREQUENCIES)}"
        )

    for language, characters in FREQUENCIES.items():
        if len(characters) > 255:
            raise RuntimeError(f"Language profile {language!r} exceeds 255 characters")
        if len(set(characters)) != len(characters):
            raise RuntimeError(f"Language profile {language!r} contains duplicates")
        _LANGUAGE_INDEX[language] = language_index
        _LANGUAGE_NAMES.append(language)
        _LANGUAGE_DISPLAY_NAMES.append(language.replace("—", ""))
        _LANGUAGE_LENGTHS[language_index] = len(characters)
        _LANGUAGE_PURE_LATIN[language_index] = True
        for rank, character in enumerate(characters):
            codepoint = ord(character)
            if codepoint >= BMP_CODEPOINT_COUNT:
                raise RuntimeError(
                    f"Language profile {language!r} contains a non-BMP character"
                )
            _LANGUAGE_RANKS[language_index][codepoint] = <uint8_t>(rank + 1)
            if codepoint < 128:
                info = _ASCII_CHAR_INFO[<Py_ssize_t>codepoint]
            else:
                info = _char_info(character)
            if info.accentuated:
                _LANGUAGE_HAS_ACCENTS[language_index] = True
            if not info.latin:
                _LANGUAGE_PURE_LATIN[language_index] = False
        language_index += 1


_initialize_language_ranks()


def encoding_unicode_range(str iana_name):
    """Return associated unicode ranges in a single byte code page."""
    cdef object decoder
    cdef object p
    cdef dict seen_ranges = {}
    cdef Py_ssize_t character_count = 0
    cdef Py_ssize_t i
    cdef Py_UCS4 chunk_codepoint
    cdef str chunk
    cdef object character_range
    cdef list selected_ranges = []

    if is_multi_byte_encoding(iana_name):
        raise OSError("Function not supported on multi-byte code page")

    decoder = importlib.import_module(f"encodings.{iana_name}").IncrementalDecoder
    p = decoder(errors="ignore")

    for i in range(0x40, 0xFF):
        chunk = p.decode(bytes([i]))
        if not chunk:
            continue

        chunk_codepoint = ord(chunk)
        if chunk_codepoint < 128:
            character_range = (
                <CharInfo>_ASCII_CHAR_INFO[<Py_ssize_t>chunk_codepoint]
            ).range
        else:
            character_range = (<CharInfo>_char_info(chunk)).range

        if character_range is None or is_unicode_range_secondary(character_range):
            continue

        if character_range not in seen_ranges:
            seen_ranges[character_range] = 0
        seen_ranges[character_range] += 1
        character_count += 1

    for character_range in seen_ranges:
        if seen_ranges[character_range] / character_count >= 0.15:
            selected_ranges.append(character_range)
    return sorted(selected_ranges)


cpdef list unicode_range_languages(str primary_range):
    """Return inferred languages used with a unicode range."""
    cdef list languages = []
    cdef object language
    cdef object characters
    cdef str character
    cdef Py_UCS4 codepoint
    cdef CharInfo info

    for language, characters in FREQUENCIES.items():
        for character in characters:
            codepoint = ord(character)
            if codepoint < 128:
                info = _ASCII_CHAR_INFO[<Py_ssize_t>codepoint]
            else:
                info = _char_info(character)
            if info.range == primary_range:
                languages.append(language)
                break
    return languages


@lru_cache()
def encoding_languages(str iana_name):
    """Return the language association for a single-byte encoding."""
    cdef list unicode_ranges
    cdef object primary_range = None
    cdef str specified_range

    try:
        unicode_ranges = encoding_unicode_range(iana_name)
    except ImportError:
        return []

    for specified_range in unicode_ranges:
        if "Latin" not in specified_range:
            primary_range = specified_range
            break

    if primary_range is None:
        return ["Latin Based"]
    return unicode_range_languages(primary_range)


@lru_cache()
def mb_encoding_languages(str iana_name):
    """Return the language association for a multi-byte encoding."""
    if iana_name in JP_NAMES:
        return ["Japanese"]
    if iana_name in ZH_NAMES:
        return ["Chinese"]
    if iana_name in KO_NAMES:
        return ["Korean"]
    return []


@lru_cache(maxsize=LANGUAGE_SUPPORTED_COUNT)
def get_target_features(str language):
    """Return whether a language has accents and is purely Latin."""
    cdef bint target_have_accents = False
    cdef bint target_pure_latin = True
    cdef str character
    cdef Py_UCS4 codepoint
    cdef CharInfo info

    for character in FREQUENCIES[language]:
        codepoint = ord(character)
        if codepoint < 128:
            info = _ASCII_CHAR_INFO[<Py_ssize_t>codepoint]
        else:
            info = _char_info(character)
        if not target_have_accents and info.accentuated:
            target_have_accents = True
        if target_pure_latin and not info.latin:
            target_pure_latin = False
    return target_have_accents, target_pure_latin


def alphabet_languages(list characters, bint ignore_non_latin=False):
    """Return languages associated with the supplied alphabet."""
    cdef list languages = []
    cdef list result = []
    cdef frozenset characters_set = frozenset(characters)
    cdef bint source_have_accents = False
    cdef Py_ssize_t character_count
    cdef Py_ssize_t character_match_count
    cdef Py_ssize_t language_index
    cdef double ratio
    cdef str character
    cdef Py_UCS4 codepoint
    cdef CharInfo info
    cdef object language
    cdef object compatible_language

    for character in characters:
        codepoint = ord(character)
        if codepoint < 128:
            info = _ASCII_CHAR_INFO[<Py_ssize_t>codepoint]
        else:
            info = _char_info(character)
        if info.accentuated:
            source_have_accents = True
            break

    for language_index in range(LANGUAGE_COUNT):
        if ignore_non_latin and not _LANGUAGE_PURE_LATIN[language_index]:
            continue
        if not _LANGUAGE_HAS_ACCENTS[language_index] and source_have_accents:
            continue

        language = _LANGUAGE_NAMES[language_index]
        character_count = _LANGUAGE_LENGTHS[language_index]
        character_match_count = 0
        for character in characters_set:
            codepoint = ord(character)
            if (
                codepoint < BMP_CODEPOINT_COUNT
                and _LANGUAGE_RANKS[language_index][codepoint]
            ):
                character_match_count += 1
        ratio = <double>character_match_count / character_count
        if ratio >= 0.2:
            languages.append((language, ratio))

    languages = sorted(languages, key=itemgetter(1), reverse=True)
    for compatible_language in languages:
        result.append(compatible_language[0])
    return result


cdef uint64_t _alphabet_language_ids(
    uint32_t* characters,
    Py_ssize_t character_count,
    bint ignore_non_latin,
    uint8_t* language_ids,
    Py_ssize_t* language_count,
) except -1:
    cdef uint16_t match_counts[LANGUAGE_COUNT]
    cdef double ratios[LANGUAGE_COUNT]
    cdef uint64_t result_mask = 0
    cdef Py_ssize_t character_index
    cdef Py_ssize_t language_index
    cdef Py_ssize_t insert_at
    cdef Py_UCS4 codepoint
    cdef CharInfo info
    cdef bint source_have_accents = False
    cdef double ratio

    memset(match_counts, 0, LANGUAGE_COUNT * sizeof(uint16_t))
    for character_index in range(character_count):
        codepoint = characters[character_index]
        if codepoint < 128:
            info = _ASCII_CHAR_INFO[<Py_ssize_t>codepoint]
        else:
            info = _char_info_from_codepoint(codepoint)
        if info.accentuated:
            source_have_accents = True
        if codepoint >= BMP_CODEPOINT_COUNT:
            continue
        for language_index in range(LANGUAGE_COUNT):
            if _LANGUAGE_RANKS[language_index][codepoint]:
                match_counts[language_index] += 1

    language_count[0] = 0
    for language_index in range(LANGUAGE_COUNT):
        if ignore_non_latin and not _LANGUAGE_PURE_LATIN[language_index]:
            continue
        if source_have_accents and not _LANGUAGE_HAS_ACCENTS[language_index]:
            continue
        ratio = <double>match_counts[language_index] / _LANGUAGE_LENGTHS[language_index]
        if ratio < 0.2:
            continue
        ratios[language_index] = ratio
        insert_at = language_count[0]
        while (
            insert_at > 0
            and ratios[language_ids[insert_at - 1]] < ratio
        ):
            language_ids[insert_at] = language_ids[insert_at - 1]
            insert_at -= 1
        language_ids[insert_at] = language_index
        language_count[0] += 1
        result_mask |= <uint64_t>1 << language_index

    return result_mask


cdef double _characters_popularity_compare_index(
    Py_ssize_t language_index,
    uint32_t* ordered_codepoints,
    Py_ssize_t ordered_characters_count,
) except -1:
    """Compare observed character popularity with a language profile."""
    cdef Py_ssize_t target_language_characters_count
    cdef Py_ssize_t character_approved_count = 0
    cdef Py_ssize_t popularity_rank
    cdef Py_ssize_t character_rank_in_language
    cdef Py_ssize_t character_rank
    cdef Py_ssize_t character_rank_projection
    cdef Py_ssize_t rank_distance
    cdef Py_ssize_t after_len
    cdef Py_ssize_t before_match_count
    cdef Py_ssize_t after_match_count
    cdef Py_ssize_t common_index
    cdef Py_ssize_t compare_index
    cdef Py_ssize_t common_count = 0
    cdef Py_ssize_t lr_i
    cdef Py_ssize_t orr_i
    cdef Py_ssize_t *common = NULL
    cdef Py_ssize_t *common_lr = NULL
    cdef Py_ssize_t *common_orr = NULL
    cdef Py_ssize_t stack_common[STACK_RANK_CAPACITY * 2]
    cdef Py_ssize_t before_counts[STACK_RANK_CAPACITY]
    cdef Py_ssize_t after_counts[STACK_RANK_CAPACITY]
    cdef Py_ssize_t rank_to_common[LANGUAGE_RANK_CAPACITY]
    cdef Py_ssize_t fenwick[STACK_RANK_CAPACITY + 1]
    cdef size_t allocation_count
    cdef bint heap_allocated = False
    cdef bint use_fenwick
    cdef bint large_alphabet
    cdef double large_alphabet_threshold
    cdef double expected_projection_ratio
    cdef Py_UCS4 codepoint
    cdef uint8_t rank_plus_one
    cdef Py_ssize_t fenwick_index
    cdef Py_ssize_t running_count
    cdef Py_ssize_t seen_count

    target_language_characters_count = _LANGUAGE_LENGTHS[language_index]
    large_alphabet = target_language_characters_count > 26
    large_alphabet_threshold = <double>target_language_characters_count / 3
    if ordered_characters_count == 0:
        raise ZeroDivisionError("division by zero")
    expected_projection_ratio = (
        <double>target_language_characters_count / ordered_characters_count
    )

    if ordered_characters_count <= STACK_RANK_CAPACITY:
        common = &stack_common[0]
    else:
        if <size_t>ordered_characters_count > (<size_t>-1) // (2 * sizeof(Py_ssize_t)):
            raise MemoryError()
        allocation_count = <size_t>ordered_characters_count * 2
        common = <Py_ssize_t *>PyMem_Malloc(allocation_count * sizeof(Py_ssize_t))
        if common == NULL:
            raise MemoryError()
        heap_allocated = True

    common_lr = common
    common_orr = common + ordered_characters_count
    try:
        for popularity_rank in range(ordered_characters_count):
            codepoint = ordered_codepoints[popularity_rank]
            if codepoint >= BMP_CODEPOINT_COUNT:
                continue
            rank_plus_one = _LANGUAGE_RANKS[language_index][codepoint]
            if rank_plus_one:
                common_lr[common_count] = rank_plus_one - 1
                common_orr[common_count] = popularity_rank
                common_count += 1

        # Direct counting avoids tree setup for small intersections. This
        # selects an equivalent counting algorithm, not a scoring threshold.
        use_fenwick = (
            common_count >= 32
            and ordered_characters_count <= STACK_RANK_CAPACITY
            and target_language_characters_count <= LANGUAGE_RANK_CAPACITY
        )
        if use_fenwick:
            memset(
                rank_to_common,
                0xFF,
                target_language_characters_count * sizeof(Py_ssize_t),
            )
            memset(
                fenwick,
                0,
                (ordered_characters_count + 1) * sizeof(Py_ssize_t),
            )
            for common_index in range(common_count):
                if rank_to_common[common_lr[common_index]] >= 0:
                    use_fenwick = False
                    break
                rank_to_common[common_lr[common_index]] = common_index

            if use_fenwick:
                # Count points strictly before each character in both rankings.
                for character_rank_in_language in range(
                    target_language_characters_count
                ):
                    common_index = rank_to_common[character_rank_in_language]
                    if common_index < 0:
                        continue
                    character_rank = common_orr[common_index]
                    running_count = 0
                    fenwick_index = character_rank
                    while fenwick_index > 0:
                        running_count += fenwick[fenwick_index]
                        fenwick_index -= fenwick_index & -fenwick_index
                    before_counts[common_index] = running_count
                    fenwick_index = character_rank + 1
                    while fenwick_index <= ordered_characters_count:
                        fenwick[fenwick_index] += 1
                        fenwick_index += fenwick_index & -fenwick_index

                memset(
                    fenwick,
                    0,
                    (ordered_characters_count + 1) * sizeof(Py_ssize_t),
                )
                seen_count = 0
                # Count the current point plus points at-or-after it in both rankings.
                for character_rank_in_language in range(
                    target_language_characters_count - 1, -1, -1
                ):
                    common_index = rank_to_common[character_rank_in_language]
                    if common_index < 0:
                        continue
                    character_rank = common_orr[common_index]
                    running_count = 0
                    fenwick_index = character_rank
                    while fenwick_index > 0:
                        running_count += fenwick[fenwick_index]
                        fenwick_index -= fenwick_index & -fenwick_index
                    after_counts[common_index] = 1 + seen_count - running_count
                    fenwick_index = character_rank + 1
                    while fenwick_index <= ordered_characters_count:
                        fenwick[fenwick_index] += 1
                        fenwick_index += fenwick_index & -fenwick_index
                    seen_count += 1

        for common_index in range(common_count):
            character_rank_in_language = common_lr[common_index]
            character_rank = common_orr[common_index]
            character_rank_projection = <Py_ssize_t>(
                character_rank * expected_projection_ratio
            )
            rank_distance = character_rank_projection - character_rank_in_language
            if rank_distance < 0:
                rank_distance = -rank_distance

            if not large_alphabet and rank_distance > 4:
                continue
            if large_alphabet and rank_distance < large_alphabet_threshold:
                character_approved_count += 1
                continue
            if character_rank_in_language == 0:
                character_approved_count += 1
                continue

            after_len = (
                target_language_characters_count - character_rank_in_language
            )
            if use_fenwick:
                before_match_count = before_counts[common_index]
                after_match_count = after_counts[common_index]
                if (
                    5 * before_match_count >= 2 * character_rank_in_language
                    or 5 * after_match_count >= 2 * after_len
                ):
                    character_approved_count += 1
            else:
                before_match_count = 0
                after_match_count = 0
                for compare_index in range(common_count):
                    lr_i = common_lr[compare_index]
                    orr_i = common_orr[compare_index]
                    if lr_i < character_rank_in_language:
                        if orr_i < character_rank:
                            before_match_count += 1
                            if 5 * before_match_count >= 2 * character_rank_in_language:
                                character_approved_count += 1
                                break
                    elif orr_i >= character_rank:
                        after_match_count += 1
                        if 5 * after_match_count >= 2 * after_len:
                            character_approved_count += 1
                            break

        return <double>character_approved_count / ordered_characters_count
    finally:
        if heap_allocated:
            PyMem_Free(common)


cpdef double characters_popularity_compare(str language, list ordered_characters):
    """Compare observed character popularity with a language profile."""
    cdef Py_ssize_t ordered_characters_count = len(ordered_characters)
    cdef Py_ssize_t index
    cdef Py_ssize_t language_index
    cdef size_t allocation_count
    cdef uint32_t stack_codepoints[STACK_RANK_CAPACITY]
    cdef uint32_t* codepoints = NULL
    cdef bint heap_allocated = False
    cdef object language_index_object = _LANGUAGE_INDEX.get(language)
    cdef object character

    if language_index_object is None:
        raise ValueError(f"{language} not available")
    language_index = language_index_object
    if ordered_characters_count <= STACK_RANK_CAPACITY:
        codepoints = &stack_codepoints[0]
    else:
        if <size_t>ordered_characters_count > (<size_t>-1) // sizeof(uint32_t):
            raise MemoryError()
        allocation_count = <size_t>ordered_characters_count
        codepoints = <uint32_t*>PyMem_Malloc(
            allocation_count * sizeof(uint32_t)
        )
        if codepoints == NULL:
            raise MemoryError()
        heap_allocated = True

    try:
        for index in range(ordered_characters_count):
            character = ordered_characters[index]
            if not isinstance(character, str) or len(character) != 1:
                codepoints[index] = <uint32_t>-1
            else:
                codepoints[index] = ord(character)
        return _characters_popularity_compare_index(
            language_index, codepoints, ordered_characters_count
        )
    finally:
        if heap_allocated:
            PyMem_Free(codepoints)


cdef struct _UnicodeLayer:
    uint32_t* codepoints
    Py_ssize_t length
    Py_ssize_t capacity
    int range_id


cdef int _grow_unicode_layer(
    _UnicodeLayer* layer, uint32_t* stack_codepoints
) except -1:
    cdef Py_ssize_t maximum_capacity = (
        PY_SSIZE_T_MAX // <Py_ssize_t>sizeof(uint32_t)
    )
    cdef Py_ssize_t new_capacity
    cdef uint32_t* new_codepoints
    if layer.capacity >= maximum_capacity:
        raise MemoryError()
    new_capacity = (
        layer.capacity * 2 if layer.capacity else INITIAL_LAYER_CAPACITY
    )
    if new_capacity > maximum_capacity:
        new_capacity = maximum_capacity
    if layer.codepoints == stack_codepoints:
        new_codepoints = <uint32_t*>PyMem_Malloc(
            <size_t>new_capacity * sizeof(uint32_t)
        )
        if new_codepoints == NULL:
            raise MemoryError()
        memcpy(
            new_codepoints, layer.codepoints,
            <size_t>layer.length * sizeof(uint32_t),
        )
    else:
        new_codepoints = <uint32_t*>PyMem_Realloc(
            layer.codepoints, <size_t>new_capacity * sizeof(uint32_t)
        )
        if new_codepoints == NULL:
            raise MemoryError()
    layer.codepoints = new_codepoints
    layer.capacity = new_capacity
    return 0


cpdef list alpha_unicode_split(str decoded_sequence):
    """Split alphabetic characters into compatible Unicode-range layers."""
    cdef list result = []
    cdef Py_ssize_t index
    cdef Py_ssize_t sequence_length = len(decoded_sequence)
    cdef Py_UCS4 codepoint
    cdef int unicode_kind = _unicode_kind(decoded_sequence)
    cdef void* unicode_data = _unicode_data(decoded_sequence)
    cdef Py_UCS4 last_codepoint = <Py_UCS4>-1
    cdef CharInfo info
    cdef CharInfo last_info = None
    cdef list ascii_char_info = _ASCII_CHAR_INFO
    cdef int character_range
    cdef int ascii_range = (<CharInfo>ascii_char_info[97]).range_id
    cdef int prev_character_range = NO_RANGE_ID
    # First-layer storage covers ordinary 512-character samples without a
    # heap allocation. Other layers grow only when characters are retained.
    cdef uint32_t stack_codepoints[STACK_LAYER_CAPACITY]
    cdef _UnicodeLayer layers[UNICODE_RANGE_CAPACITY]
    cdef _UnicodeLayer* current_layer = NULL
    cdef int layer_count = 0
    cdef int layer = 0
    cdef int byteorder

    if sequence_length == 0:
        return result

    try:
        for index in range(sequence_length):
            codepoint = _unicode_read(
                decoded_sequence, unicode_kind, unicode_data, index
            )
            if codepoint < 128:
                if not (65 <= codepoint <= 90 or 97 <= codepoint <= 122):
                    continue
                character_range = ascii_range
            else:
                if codepoint == last_codepoint:
                    info = last_info
                else:
                    info = _char_info_from_codepoint(codepoint)
                    last_codepoint = codepoint
                    last_info = info
                if not info.alpha:
                    continue
                character_range = info.range_id
                if character_range == NO_RANGE_ID:
                    continue

            if character_range != prev_character_range:
                for layer in range(layer_count):
                    if not _is_suspicious_range_ids(
                        layers[layer].range_id, character_range
                    ):
                        break
                else:
                    if layer_count == UNICODE_RANGE_CAPACITY:
                        raise RuntimeError("Too many Unicode layers")
                    layer = layer_count
                    layers[layer].range_id = character_range
                    layers[layer].length = 0
                    if layer == 0:
                        layers[layer].codepoints = stack_codepoints
                        layers[layer].capacity = STACK_LAYER_CAPACITY
                    else:
                        layers[layer].codepoints = NULL
                        layers[layer].capacity = 0
                    layer_count += 1
                current_layer = &layers[layer]
                prev_character_range = character_range

            if current_layer.length == current_layer.capacity:
                _grow_unicode_layer(current_layer, stack_codepoints)
            current_layer.codepoints[current_layer.length] = codepoint
            current_layer.length += 1

        for layer in range(layer_count):
            byteorder = _NATIVE_BYTEORDER
            result.append(
                PyUnicode_DecodeUTF32(
                    <char*>layers[layer].codepoints,
                    layers[layer].length * <Py_ssize_t>sizeof(uint32_t),
                    NULL,
                    &byteorder,
                ).lower()
            )
    finally:
        for layer in range(layer_count):
            if layers[layer].codepoints != stack_codepoints:
                PyMem_Free(layers[layer].codepoints)
    return result


cpdef list merge_coherence_ratios(list results):
    """Merge coherence ratios by language."""
    cdef dict per_language_ratios = {}
    cdef list merge = []
    cdef object result
    cdef object sub_result
    cdef object language
    cdef object ratio
    cdef list ratios

    for result in results:
        for sub_result in result:
            language, ratio = sub_result
            if language not in per_language_ratios:
                per_language_ratios[language] = [ratio]
            else:
                per_language_ratios[language].append(ratio)

    for language in per_language_ratios:
        ratios = per_language_ratios[language]
        merge.append((language, round(sum(ratios) / len(ratios), 4)))
    return sorted(merge, key=itemgetter(1), reverse=True)


cpdef list filter_alt_coherence_matches(list results):
    """Collapse alternative language names while retaining their best score."""
    cdef dict index_results = {}
    cdef list filtered_results
    cdef object result
    cdef object language
    cdef object ratio
    cdef str no_em_name

    for result in results:
        language, ratio = result
        no_em_name = language.replace("—", "")
        if no_em_name not in index_results:
            index_results[no_em_name] = []
        index_results[no_em_name].append(ratio)

    filtered_results = []
    for language in index_results:
        filtered_results.append((language, max(index_results[language])))
    return filtered_results


cdef Py_ssize_t _popular_codepoints(str layer, uint32_t* result) except -1:
    cdef Py_ssize_t length = len(layer)
    cdef Py_ssize_t capacity = 1
    cdef Py_ssize_t mask
    cdef Py_ssize_t index
    cdef Py_ssize_t slot
    cdef Py_ssize_t unique_count = 0
    cdef Py_ssize_t order_index
    cdef Py_ssize_t previous_index
    cdef Py_ssize_t moving_slot
    cdef Py_UCS4 codepoint
    cdef uint32_t* keys = NULL
    cdef uint32_t* counts = NULL
    cdef uint32_t* ordered_slots = NULL
    cdef int unicode_kind = _unicode_kind(layer)
    cdef void* unicode_data = _unicode_data(layer)

    while capacity < length * 2:
        capacity <<= 1
    mask = capacity - 1

    keys = <uint32_t*>PyMem_Malloc(capacity * sizeof(uint32_t))
    counts = <uint32_t*>PyMem_Malloc(capacity * sizeof(uint32_t))
    ordered_slots = <uint32_t*>PyMem_Malloc(length * sizeof(uint32_t))
    if keys == NULL or counts == NULL or ordered_slots == NULL:
        PyMem_Free(keys)
        PyMem_Free(counts)
        PyMem_Free(ordered_slots)
        raise MemoryError()

    memset(keys, 0xFF, capacity * sizeof(uint32_t))
    memset(counts, 0, capacity * sizeof(uint32_t))
    try:
        for index in range(length):
            codepoint = _unicode_read(layer, unicode_kind, unicode_data, index)
            slot = (<uint32_t>codepoint * <uint32_t>2654435761) & mask
            while keys[slot] != <uint32_t>0xFFFFFFFF and keys[slot] != codepoint:
                slot = (slot + 1) & mask
            if keys[slot] == <uint32_t>0xFFFFFFFF:
                keys[slot] = codepoint
                ordered_slots[unique_count] = slot
                unique_count += 1
            counts[slot] += 1

        # Stable insertion sort by descending count. Equal counts retain the
        # first-appearance order stored in ordered_slots.
        for order_index in range(1, unique_count):
            moving_slot = ordered_slots[order_index]
            previous_index = order_index - 1
            while (
                previous_index >= 0
                and counts[ordered_slots[previous_index]] < counts[moving_slot]
            ):
                ordered_slots[previous_index + 1] = ordered_slots[previous_index]
                previous_index -= 1
            ordered_slots[previous_index + 1] = moving_slot

        for order_index in range(unique_count):
            result[order_index] = keys[ordered_slots[order_index]]
        return unique_count
    finally:
        PyMem_Free(keys)
        PyMem_Free(counts)
        PyMem_Free(ordered_slots)


cpdef list coherence_ratio(
    str decoded_sequence, double threshold=0.1, str lg_inclusion=None
):
    """Detect languages represented in a decoded sequence."""
    cdef dict results = {}
    cdef bint ignore_non_latin = False
    cdef Py_ssize_t sufficient_match_count = 0
    cdef list lg_inclusion_list
    cdef Py_ssize_t character_count
    cdef Py_ssize_t popular_count
    cdef Py_ssize_t language_count = 0
    cdef Py_ssize_t language_position
    cdef Py_ssize_t language_index
    cdef Py_ssize_t requested_count
    cdef size_t allocation_count
    cdef double ratio
    cdef str layer
    cdef object language
    cdef object rounded_ratio
    cdef object language_index_object
    cdef uint64_t language_mask = 0
    cdef uint32_t stack_codepoints[STACK_RANK_CAPACITY]
    cdef uint32_t* popular_codepoints = NULL
    cdef uint8_t stack_language_ids[LANGUAGE_COUNT]
    cdef uint8_t* language_ids = &stack_language_ids[0]
    cdef bint codepoints_heap_allocated = False
    cdef bint language_ids_heap_allocated = False

    if lg_inclusion is not None:
        lg_inclusion_list = lg_inclusion.split(",")
    else:
        lg_inclusion_list = []
    if "Latin Based" in lg_inclusion_list:
        ignore_non_latin = True
        lg_inclusion_list.remove("Latin Based")

    requested_count = len(lg_inclusion_list)
    if requested_count > LANGUAGE_COUNT:
        language_ids = <uint8_t*>PyMem_Malloc(
            <size_t>requested_count * sizeof(uint8_t)
        )
        if language_ids == NULL:
            raise MemoryError()
        language_ids_heap_allocated = True

    try:
        if requested_count:
            language_mask = 0
            for language_position in range(requested_count):
                language = lg_inclusion_list[language_position]
                language_index_object = _LANGUAGE_INDEX.get(language)
                if language_index_object is None:
                    raise ValueError(f"{language} not available")
                language_index = language_index_object
                language_ids[language_position] = language_index
                language_mask |= <uint64_t>1 << language_index

        for layer in alpha_unicode_split(decoded_sequence):
            character_count = len(layer)
            if character_count <= TOO_SMALL_SEQUENCE:
                continue

            if character_count <= STACK_RANK_CAPACITY:
                popular_codepoints = &stack_codepoints[0]
            else:
                if <size_t>character_count > (<size_t>-1) // sizeof(uint32_t):
                    raise MemoryError()
                allocation_count = <size_t>character_count
                popular_codepoints = <uint32_t*>PyMem_Malloc(
                    allocation_count * sizeof(uint32_t)
                )
                if popular_codepoints == NULL:
                    raise MemoryError()
                codepoints_heap_allocated = True

            try:
                popular_count = _popular_codepoints(layer, popular_codepoints)
                if requested_count:
                    language_count = requested_count
                else:
                    language_mask = _alphabet_language_ids(
                        popular_codepoints,
                        popular_count,
                        ignore_non_latin,
                        language_ids,
                        &language_count,
                    )
                for language_position in range(language_count):
                    language_index = language_ids[language_position]
                    if not language_mask & (<uint64_t>1 << language_index):
                        continue
                    ratio = _characters_popularity_compare_index(
                        language_index, popular_codepoints, popular_count
                    )
                    if ratio < threshold:
                        continue
                    if ratio >= 0.8:
                        sufficient_match_count += 1
                    language = _LANGUAGE_DISPLAY_NAMES[language_index]
                    rounded_ratio = round(ratio, 4)
                    if language not in results or rounded_ratio > results[language]:
                        results[language] = rounded_ratio
                    if sufficient_match_count >= 3:
                        break
            finally:
                if codepoints_heap_allocated:
                    PyMem_Free(popular_codepoints)
                    popular_codepoints = NULL
                    codepoints_heap_allocated = False
    finally:
        if language_ids_heap_allocated:
            PyMem_Free(language_ids)

    return sorted(results.items(), key=itemgetter(1), reverse=True)
