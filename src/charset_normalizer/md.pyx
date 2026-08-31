# cython: boundscheck=False, wraparound=False, initializedcheck=False
# cython: nonecheck=False, cdivision=True, language_level=3
# cython: freethreading_compatible=True

cimport cython

from functools import lru_cache
from logging import getLogger

from libc.stdint cimport uint32_t

from charset_normalizer._cython_compat cimport (
    _unicode_data,
    _unicode_kind,
    _unicode_read,
)

from charset_normalizer.constant import (
    COMMON_CJK_CHARACTERS,
    COMMON_SAFE_ASCII_CHARACTERS,
    TRACE,
    CompatibleFamillyRange,
    _ACCENTUATED,
    _ARABIC,
    _ARABIC_ISOLATED_FORM,
    _BASIC_LATIN_COMPATIBLE_RANGE_FAMILIES,
    _CJK,
    _COMPATIBLE_RANGE_FAMILIES,
    _COMPATIBLE_WITH_ANY_RANGE_FAMILIES,
    _HANGUL,
    _HALFWIDTH_KATAKANA,
    _HIRAGANA,
    _KATAKANA,
    _LATIN,
    _LIGATURE,
    _RANGE_FAMILIES,
    _SENTENCE_OPEN_PUNCTUATION,
    _SUPERSCRIPT,
    _THAI,
)
from charset_normalizer.utils import (
    _character_flags,
    is_emoticon,
    is_punctuation,
    is_separator,
    is_symbol,
    remove_accent,
    unicode_range,
)


cdef int _GLYPH_MASK = _CJK | _HANGUL | _KATAKANA | _HIRAGANA | _THAI
cdef int _ACCENTUATED_MASK = _ACCENTUATED
cdef int _LATIN_MASK = _LATIN
cdef int _CJK_MASK = _CJK
cdef int _KATAKANA_MASK = _KATAKANA
cdef int _HALFWIDTH_KATAKANA_MASK = _HALFWIDTH_KATAKANA
cdef int _ARABIC_MASK = _ARABIC
cdef int _ARABIC_ISOLATED_FORM_MASK = _ARABIC_ISOLATED_FORM
cdef int _LIGATURE_MASK = _LIGATURE
cdef int _SUPERSCRIPT_MASK = _SUPERSCRIPT
cdef int _SENTENCE_OPEN_PUNCTUATION_MASK = _SENTENCE_OPEN_PUNCTUATION

cdef enum:
    UNICODE_PAGE_SHIFT = 8
    UNICODE_PAGE_SIZE = 256
    UNICODE_PAGE_MASK = 255
    UNICODE_PAGE_COUNT = 4352


cdef class CharInfo:
    """Pre-computed character properties shared across all detectors."""

    def __init__(self, str character):
        cdef Py_UCS4 codepoint = ord(character)
        cdef int flags

        self.character = character
        if codepoint < 128:
            self.is_ascii = True
            self.accentuated = False
            self.unaccented = character
            self.emoticon = False
            self.common_cjk = False
            self.safe = character in COMMON_SAFE_ASCII_CHARACTERS
            self.is_cjk = False
            self.is_katakana = False
            self.is_halfwidth_katakana = False
            self.is_arabic = False
            self.is_ligature = False
            self.is_superscript = False
            self.is_sentence_open_punctuation = False
            self.is_glyph = False
            if 65 <= codepoint <= 90:
                self.alpha = True
                self.upper = True
                self.lower = False
                self.space = False
                self.digit = False
                self.printable = True
                self.case_variable = True
                self.flags = _LATIN
                self.latin = True
                self.punct = False
                self.sym = False
            elif 97 <= codepoint <= 122:
                self.alpha = True
                self.upper = False
                self.lower = True
                self.space = False
                self.digit = False
                self.printable = True
                self.case_variable = True
                self.flags = _LATIN
                self.latin = True
                self.punct = False
                self.sym = False
            elif 48 <= codepoint <= 57:
                self.alpha = False
                self.upper = False
                self.lower = False
                self.space = False
                self.digit = True
                self.printable = True
                self.case_variable = False
                self.flags = 0
                self.latin = False
                self.punct = False
                self.sym = False
            elif codepoint == 32 or 9 <= codepoint <= 13:
                self.alpha = False
                self.upper = False
                self.lower = False
                self.space = True
                self.digit = False
                self.printable = codepoint == 32
                self.case_variable = False
                self.flags = 0
                self.latin = False
                self.punct = False
                self.sym = False
            else:
                self.printable = character.isprintable()
                self.alpha = False
                self.upper = False
                self.lower = False
                self.space = False
                self.digit = False
                self.case_variable = False
                self.flags = 0
                self.latin = False
                self.punct = is_punctuation(character) if self.printable else False
                self.sym = is_symbol(character) if self.printable else False
        else:
            self.is_ascii = False
            self.safe = False
            self.printable = character.isprintable()
            self.alpha = character.isalpha()
            self.upper = character.isupper()
            self.lower = character.islower()
            self.space = character.isspace()
            self.digit = character.isdigit()
            self.case_variable = self.lower != self.upper
            flags = _character_flags(character)
            if self.alpha:
                self.emoticon = False
            else:
                self.emoticon = is_emoticon(character)
            self.flags = flags
            self.accentuated = bool(flags & _ACCENTUATED_MASK)
            self.latin = bool(flags & _LATIN_MASK)
            self.is_cjk = bool(flags & _CJK_MASK)
            self.is_katakana = bool(flags & _KATAKANA_MASK)
            self.is_halfwidth_katakana = bool(flags & _HALFWIDTH_KATAKANA_MASK)
            self.is_arabic = bool(flags & _ARABIC_MASK)
            self.is_ligature = bool(flags & _LIGATURE_MASK)
            self.is_superscript = bool(flags & _SUPERSCRIPT_MASK)
            self.is_sentence_open_punctuation = bool(
                flags & _SENTENCE_OPEN_PUNCTUATION_MASK
            )
            self.is_glyph = bool(flags & _GLYPH_MASK)
            self.unaccented = (
                remove_accent(character)
                if self.latin and self.accentuated
                else character
            )
            self.common_cjk = self.is_cjk and character in COMMON_CJK_CHARACTERS
            if self.printable:
                self.punct = is_punctuation(character)
                self.sym = is_symbol(character)
            else:
                self.punct = False
                self.sym = False

        self.range = unicode_range(character)
        self.sep = is_separator(character)


def _char_info(str character):
    """Build and cache character information for the public string API."""
    return _char_info_from_codepoint(ord(character))


_ASCII_CHAR_INFO = [CharInfo(chr(codepoint)) for codepoint in range(128)]
_CHAR_INFO_PAGES = [None] * UNICODE_PAGE_COUNT


cdef CharInfo _char_info_from_codepoint(Py_UCS4 codepoint):
    cdef Py_ssize_t page_index = (<Py_ssize_t>codepoint) >> UNICODE_PAGE_SHIFT
    cdef Py_ssize_t slot_index = (<Py_ssize_t>codepoint) & UNICODE_PAGE_MASK
    cdef object page = _CHAR_INFO_PAGES[page_index]
    cdef object info

    if page is None:
        page = [None] * UNICODE_PAGE_SIZE
        _CHAR_INFO_PAGES[page_index] = page

    info = (<list>page)[slot_index]
    if info is None:
        info = CharInfo(chr(codepoint))
        (<list>page)[slot_index] = info
    return <CharInfo>info


cdef inline Py_UCS4 _public_codepoint(str character) except *:
    return ord(character)


cdef class MessDetectorPlugin:
    """Base class for mess-detection plugins."""

    cpdef void feed_info(self, str character, CharInfo info):
        raise NotImplementedError

    cpdef void reset(self):
        raise NotImplementedError

    @property
    def ratio(self):
        raise NotImplementedError


@cython.final
cdef class TooManySymbolOrPunctuationPlugin(MessDetectorPlugin):
    def __init__(self):
        self._punctuation_count = 0
        self._symbol_count = 0
        self._character_count = 0
        self._last_printable_char = <uint32_t>-1

    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept:
        self._character_count += 1
        if codepoint != self._last_printable_char and not info.safe:
            if info.punct:
                self._punctuation_count += 1
            elif not info.digit and info.sym and not info.emoticon:
                self._symbol_count += 2
        self._last_printable_char = codepoint

    cpdef void feed_info(self, str character, CharInfo info):
        self._feed(_public_codepoint(character), info)

    cpdef void reset(self):
        # Preserve the Python implementation's previous-character state.
        self._punctuation_count = 0
        self._character_count = 0
        self._symbol_count = 0

    cdef double _ratio(self) noexcept:
        cdef double value
        if self._character_count == 0:
            return 0.0
        value = (
            <double>(self._punctuation_count + self._symbol_count)
            / self._character_count
        )
        return value if value >= 0.3 else 0.0

    @property
    def ratio(self):
        return self._ratio()


@cython.final
cdef class TooManyAccentuatedPlugin(MessDetectorPlugin):
    def __init__(self):
        self._character_count = 0
        self._accentuated_count = 0

    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept:
        self._character_count += 1
        if info.accentuated:
            self._accentuated_count += 1

    cpdef void feed_info(self, str character, CharInfo info):
        self._feed(_public_codepoint(character), info)

    cpdef void reset(self):
        self._character_count = 0
        self._accentuated_count = 0

    cdef double _ratio(self) noexcept:
        cdef double value
        if self._character_count < 8:
            return 0.0
        value = <double>self._accentuated_count / self._character_count
        return value if value >= 0.35 else 0.0

    @property
    def ratio(self):
        return self._ratio()


@cython.final
cdef class UnprintablePlugin(MessDetectorPlugin):
    def __init__(self):
        self._unprintable_count = 0
        self._character_count = 0
        self._has_escape = False

    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept:
        if codepoint == 0x1B:
            self._has_escape = True

        if (
            not info.printable
            and not info.space
            and codepoint != 0x1A
            and codepoint != 0xFEFF
        ):
            self._unprintable_count += 1
        self._character_count += 1

    cpdef void feed_info(self, str character, CharInfo info):
        self._feed(_public_codepoint(character), info)

    cpdef void reset(self):
        # Preserve the Python implementation's cumulative denominator on reset.
        self._unprintable_count = 0
        self._has_escape = False

    cdef double _ratio(self) noexcept:
        if self._character_count == 0:
            return 0.0
        if self._has_escape:
            return 1.0
        return <double>(self._unprintable_count * 8) / self._character_count

    @property
    def ratio(self):
        return self._ratio()


@cython.final
cdef class SuspiciousDuplicateAccentPlugin(MessDetectorPlugin):
    def __init__(self):
        self._successive_count = 0
        self._character_count = 0
        self._last_latin_character = None
        self._last_was_accentuated = False

    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info):
        cdef CharInfo previous
        self._character_count += 1
        if (
            self._last_latin_character is not None
            and info.accentuated
            and self._last_was_accentuated
        ):
            previous = <CharInfo>self._last_latin_character
            if info.upper and previous.upper:
                self._successive_count += 1
            if info.unaccented == previous.unaccented:
                self._successive_count += 1
        self._last_latin_character = info
        self._last_was_accentuated = info.accentuated

    cpdef void feed_info(self, str character, CharInfo info):
        self._feed(_public_codepoint(character), info)

    cpdef void reset(self):
        self._successive_count = 0
        self._character_count = 0
        self._last_latin_character = None
        self._last_was_accentuated = False

    cdef double _ratio(self) noexcept:
        if self._character_count == 0:
            return 0.0
        return <double>(self._successive_count * 2) / self._character_count

    @property
    def ratio(self):
        return self._ratio()


@cython.final
cdef class SuspiciousRange(MessDetectorPlugin):
    def __init__(self):
        self._suspicious_successive_range_count = 0
        self._character_count = 0
        self._has_last_printable = False
        self._last_printable_range = None

    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info):
        cdef object range_a
        cdef object range_b
        self._character_count += 1
        if info.space or info.punct or info.safe:
            self._has_last_printable = False
            self._last_printable_range = None
            return
        if not self._has_last_printable:
            self._has_last_printable = True
            self._last_printable_range = info.range
            return
        range_a = self._last_printable_range
        range_b = info.range
        if (
            range_a != range_b or range_a is None
        ) and is_suspiciously_successive_range(range_a, range_b):
            self._suspicious_successive_range_count += 1
        self._last_printable_range = range_b

    cpdef void feed_info(self, str character, CharInfo info):
        self._feed(_public_codepoint(character), info)

    cpdef void reset(self):
        self._character_count = 0
        self._suspicious_successive_range_count = 0
        self._has_last_printable = False
        self._last_printable_range = None

    cdef double _ratio(self) noexcept:
        if self._character_count <= 13:
            return 0.0
        return (
            <double>(self._suspicious_successive_range_count * 2)
            / self._character_count
        )

    @property
    def ratio(self):
        return self._ratio()


@cython.final
cdef class SuperWeirdWordPlugin(MessDetectorPlugin):
    def __init__(self):
        self._word_count = 0
        self._bad_word_count = 0
        self._foreign_long_count = 0
        self._is_current_word_bad = False
        self._foreign_long_watch = False
        self._character_count = 0
        self._bad_character_count = 0
        self._buffer_length = 0
        self._buffer_last_char_upper = False
        self._buffer_last_char_accentuated = False
        self._buffer_accent_count = 0
        self._buffer_glyph_count = 0
        self._buffer_upper_count = 0
        self._buffer_first_lower = False
        self._buffer_has_non_ascii = False
        self._buffer_last_char_ligature = False
        self._buffer_has_internal_ligature = False
        self._is_current_word_invalid = False
        self._invalid_word_count = 0

    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept:
        cdef int buffer_length
        cdef bint probable_camel_cased

        if info.alpha:
            if self._buffer_last_char_ligature:
                self._buffer_has_internal_ligature = True
            self._buffer_last_char_ligature = info.is_ligature
            if self._buffer_length == 0:
                self._buffer_first_lower = info.lower
            self._buffer_length += 1
            # Only the previous character's uppercase state is needed.
            self._buffer_last_char_upper = info.upper
            if info.upper:
                self._buffer_upper_count += 1
            if not info.is_ascii:
                self._buffer_has_non_ascii = True
            self._buffer_last_char_accentuated = info.accentuated
            if info.accentuated:
                self._buffer_accent_count += 1
            if info.is_glyph:
                self._buffer_glyph_count += 1
            elif not self._foreign_long_watch and (not info.latin or info.accentuated):
                self._foreign_long_watch = True
            return

        if not self._buffer_length:
            return
        if info.is_sentence_open_punctuation or (
            info.is_superscript and self._buffer_has_internal_ligature
        ):
            self._is_current_word_bad = True
            self._is_current_word_invalid = True
        if info.space or info.punct or info.sep:
            self._word_count += 1
            buffer_length = self._buffer_length
            self._character_count += buffer_length
            if buffer_length >= 4:
                if <double>self._buffer_accent_count / buffer_length >= 0.5:
                    self._is_current_word_bad = True
                elif (
                    self._buffer_last_char_accentuated
                    and self._buffer_last_char_upper
                    and self._buffer_upper_count != buffer_length
                ):
                    self._foreign_long_count += 1
                    self._is_current_word_bad = True
                elif self._buffer_glyph_count == 1:
                    self._is_current_word_bad = True
                    self._foreign_long_count += 1
                elif (
                    self._buffer_has_non_ascii
                    and self._buffer_first_lower
                    and self._buffer_upper_count == buffer_length - 1
                ):
                    self._foreign_long_count += 1
                    self._is_current_word_bad = True
            if buffer_length >= 24 and self._foreign_long_watch:
                probable_camel_cased = (
                    self._buffer_upper_count > 0
                    and <double>self._buffer_upper_count / buffer_length <= 0.3
                )
                if not probable_camel_cased:
                    self._foreign_long_count += 1
                    self._is_current_word_bad = True
            if self._is_current_word_bad:
                self._bad_word_count += 1
                self._bad_character_count += buffer_length
                self._is_current_word_bad = False
            if self._is_current_word_invalid:
                self._invalid_word_count += 1
                self._is_current_word_invalid = False
            self._foreign_long_watch = False
            self._buffer_length = 0
            self._buffer_last_char_upper = False
            self._buffer_last_char_accentuated = False
            self._buffer_accent_count = 0
            self._buffer_glyph_count = 0
            self._buffer_upper_count = 0
            self._buffer_first_lower = False
            self._buffer_has_non_ascii = False
            self._buffer_last_char_ligature = False
            self._buffer_has_internal_ligature = False
        # Keep these comparisons at C level: <, >, -, =, ~, |, and _ are safe.
        elif (
            codepoint != 60
            and codepoint != 62
            and codepoint != 45
            and codepoint != 61
            and codepoint != 126
            and codepoint != 124
            and codepoint != 95
            and not info.digit
            and info.sym
        ):
            self._is_current_word_bad = True
            self._buffer_length += 1
            self._buffer_last_char_upper = False
            self._buffer_last_char_accentuated = False

    cpdef void feed_info(self, str character, CharInfo info):
        self._feed(_public_codepoint(character), info)

    cpdef void reset(self):
        self._buffer_length = 0
        self._buffer_last_char_upper = False
        self._buffer_last_char_accentuated = False
        self._is_current_word_bad = False
        self._foreign_long_watch = False
        self._bad_word_count = 0
        self._word_count = 0
        self._character_count = 0
        self._bad_character_count = 0
        self._foreign_long_count = 0
        self._buffer_accent_count = 0
        self._buffer_glyph_count = 0
        self._buffer_upper_count = 0
        self._buffer_first_lower = False
        self._buffer_has_non_ascii = False
        self._buffer_last_char_ligature = False
        self._buffer_has_internal_ligature = False
        self._is_current_word_invalid = False
        self._invalid_word_count = 0

    cdef double _ratio(self) noexcept:
        if self._invalid_word_count:
            return 1.0
        if self._word_count <= 10 and self._foreign_long_count == 0:
            return 0.0
        return <double>self._bad_character_count / self._character_count

    @property
    def ratio(self):
        return self._ratio()


@cython.final
cdef class CjkUncommonPlugin(MessDetectorPlugin):
    """Detect messy CJK text that probably means nothing."""

    def __init__(self):
        self._character_count = 0
        self._uncommon_count = 0

    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept:
        self._character_count += 1
        if not info.common_cjk:
            self._uncommon_count += 1

    cpdef void feed_info(self, str character, CharInfo info):
        self._feed(_public_codepoint(character), info)

    cpdef void reset(self):
        self._character_count = 0
        self._uncommon_count = 0

    cdef double _ratio(self) noexcept:
        cdef double value
        if self._character_count < 4:
            return 0.0
        value = <double>self._uncommon_count / self._character_count
        return value / 10.0 if value > 0.5 else 0.0

    @property
    def ratio(self):
        return self._ratio()


@cython.final
cdef class SuspiciousKatakanaPlugin(MessDetectorPlugin):
    """Detect implausible halfwidth Katakana and uncommon CJK combinations."""

    def __init__(self):
        self._katakana_count = 0
        self._halfwidth_katakana_count = 0
        self._cjk_count = 0
        self._uncommon_cjk_count = 0

    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept:
        if info.is_katakana:
            self._katakana_count += 1
            if info.is_halfwidth_katakana:
                self._halfwidth_katakana_count += 1
            return

        self._cjk_count += 1
        if not info.common_cjk:
            self._uncommon_cjk_count += 1

    cpdef void feed_info(self, str character, CharInfo info):
        self._feed(_public_codepoint(character), info)

    cpdef void reset(self):
        self._katakana_count = 0
        self._halfwidth_katakana_count = 0
        self._cjk_count = 0
        self._uncommon_cjk_count = 0

    cdef double _ratio(self) noexcept:
        if (
            self._halfwidth_katakana_count >= 4
            and self._halfwidth_katakana_count == self._katakana_count
            and self._cjk_count >= 3
            and self._uncommon_cjk_count == self._cjk_count
        ):
            return 1.0

        return 0.0

    @property
    def ratio(self):
        return self._ratio()


@cython.final
cdef class ArchaicUpperLowerPlugin(MessDetectorPlugin):
    def __init__(self):
        self._buf = False
        self._character_count_since_last_sep = 0
        self._successive_upper_lower_count = 0
        self._successive_upper_lower_count_final = 0
        self._character_count = 0
        self._last_alpha_seen_upper = False
        self._last_alpha_seen_lower = False
        self._current_ascii_only = True

    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept:
        cdef bint is_concerned = info.alpha and info.case_variable
        cdef bint chunk_sep = not is_concerned
        if chunk_sep and self._character_count_since_last_sep > 0:
            if (
                self._character_count_since_last_sep <= 64
                and not info.digit
                and not self._current_ascii_only
            ):
                self._successive_upper_lower_count_final += (
                    self._successive_upper_lower_count
                )
            self._successive_upper_lower_count = 0
            self._character_count_since_last_sep = 0
            self._buf = False
            self._character_count += 1
            self._current_ascii_only = True
            return
        if self._current_ascii_only and not info.is_ascii:
            self._current_ascii_only = False
        if self._character_count_since_last_sep > 0:
            if (info.upper and self._last_alpha_seen_lower) or (
                info.lower and self._last_alpha_seen_upper
            ):
                if self._buf:
                    self._successive_upper_lower_count += 2
                    self._buf = False
                else:
                    self._buf = True
            else:
                self._buf = False
        self._character_count += 1
        self._character_count_since_last_sep += 1
        self._last_alpha_seen_upper = info.upper
        self._last_alpha_seen_lower = info.lower

    cpdef void feed_info(self, str character, CharInfo info):
        self._feed(_public_codepoint(character), info)

    cpdef void reset(self):
        self._character_count = 0
        self._character_count_since_last_sep = 0
        self._successive_upper_lower_count = 0
        self._successive_upper_lower_count_final = 0
        self._last_alpha_seen_upper = False
        self._last_alpha_seen_lower = False
        self._buf = False
        self._current_ascii_only = True

    cdef double _ratio(self) noexcept:
        if self._character_count == 0:
            return 0.0
        return <double>self._successive_upper_lower_count_final / self._character_count

    @property
    def ratio(self):
        return self._ratio()


@cython.final
cdef class ArabicIsolatedFormPlugin(MessDetectorPlugin):
    def __init__(self):
        self._character_count = 0
        self._isolated_form_count = 0

    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept:
        self._character_count += 1
        if info.flags & _ARABIC_ISOLATED_FORM_MASK:
            self._isolated_form_count += 1

    cpdef void feed_info(self, str character, CharInfo info):
        self._feed(_public_codepoint(character), info)

    cpdef void reset(self):
        self._character_count = 0
        self._isolated_form_count = 0

    cdef double _ratio(self) noexcept:
        if self._character_count < 8:
            return 0.0
        return <double>self._isolated_form_count / self._character_count

    @property
    def ratio(self):
        return self._ratio()


@lru_cache(maxsize=None)
def is_suspiciously_successive_range(unicode_range_a, unicode_range_b):
    """Return whether two adjacent Unicode ranges are suspicious."""
    cdef str family_a
    cdef str family_b
    if unicode_range_a is None or unicode_range_b is None:
        return True
    family_a = _RANGE_FAMILIES[unicode_range_a]
    family_b = _RANGE_FAMILIES[unicode_range_b]
    if family_a == family_b:
        return False
    if (
        family_a in _COMPATIBLE_WITH_ANY_RANGE_FAMILIES
        or family_b in _COMPATIBLE_WITH_ANY_RANGE_FAMILIES
    ):
        return False
    if CompatibleFamillyRange(family_a, family_b) in _COMPATIBLE_RANGE_FAMILIES:
        return False
    if unicode_range_a == "Basic Latin":
        return family_b not in _BASIC_LATIN_COMPATIBLE_RANGE_FAMILIES
    if unicode_range_b == "Basic Latin":
        return family_a not in _BASIC_LATIN_COMPATIBLE_RANGE_FAMILIES
    return True


cdef inline double _mean_ratio(
    TooManySymbolOrPunctuationPlugin d_sp,
    TooManyAccentuatedPlugin d_ta,
    UnprintablePlugin d_up,
    SuspiciousDuplicateAccentPlugin d_sda,
    SuspiciousRange d_sr,
    SuperWeirdWordPlugin d_sw,
    CjkUncommonPlugin d_cu,
    SuspiciousKatakanaPlugin d_sk,
    ArchaicUpperLowerPlugin d_au,
    ArabicIsolatedFormPlugin d_ai,
) noexcept:
    return (
        d_sp._ratio() + d_ta._ratio() + d_up._ratio() + d_sda._ratio()
        + d_sr._ratio() + d_sw._ratio() + d_cu._ratio() + d_au._ratio()
        + d_sk._ratio() + d_ai._ratio()
    )


cpdef double mess_ratio(
    str decoded_sequence, double maximum_threshold=0.2, bint debug=False
):
    """Compute the mess ratio for a decoded string, with checkpoint early stop."""
    cdef Py_ssize_t seq_len = len(decoded_sequence)
    cdef Py_ssize_t step
    cdef Py_ssize_t block_start
    cdef Py_ssize_t block_end
    cdef Py_ssize_t index
    cdef Py_UCS4 codepoint
    cdef int unicode_kind = _unicode_kind(decoded_sequence)
    cdef void* unicode_data = _unicode_data(decoded_sequence)
    cdef CharInfo info
    cdef CharInfo nl_info
    cdef double mean_mess_ratio
    cdef bint is_pure_ascii = decoded_sequence.isascii()
    cdef list ascii_char_info = _ASCII_CHAR_INFO

    cdef TooManySymbolOrPunctuationPlugin d_sp = TooManySymbolOrPunctuationPlugin()
    cdef TooManyAccentuatedPlugin d_ta = TooManyAccentuatedPlugin()
    cdef UnprintablePlugin d_up = UnprintablePlugin()
    cdef SuspiciousDuplicateAccentPlugin d_sda = SuspiciousDuplicateAccentPlugin()
    cdef SuspiciousRange d_sr = SuspiciousRange()
    cdef SuperWeirdWordPlugin d_sw = SuperWeirdWordPlugin()
    cdef CjkUncommonPlugin d_cu = CjkUncommonPlugin()
    cdef SuspiciousKatakanaPlugin d_sk = SuspiciousKatakanaPlugin()
    cdef ArchaicUpperLowerPlugin d_au = ArchaicUpperLowerPlugin()
    cdef ArabicIsolatedFormPlugin d_ai = ArabicIsolatedFormPlugin()

    if seq_len < 511:
        step = 32
    elif seq_len < 1024:
        step = 64
    else:
        step = 128

    block_start = 0
    while block_start < seq_len:
        block_end = block_start + step
        if block_end > seq_len:
            block_end = seq_len
        for index in range(block_start, block_end):
            codepoint = _unicode_read(
                decoded_sequence, unicode_kind, unicode_data, index
            )
            if codepoint < 128:
                info = <CharInfo>ascii_char_info[<Py_ssize_t>codepoint]
            else:
                info = _char_info_from_codepoint(codepoint)

            d_up._feed(codepoint, info)
            d_sw._feed(codepoint, info)
            if is_pure_ascii:
                if info.printable:
                    d_sp._feed(codepoint, info)
                continue

            d_au._feed(codepoint, info)
            if info.printable:
                d_sp._feed(codepoint, info)
                d_sr._feed(codepoint, info)
            if info.alpha:
                d_ta._feed(codepoint, info)
                if info.latin:
                    d_sda._feed(codepoint, info)
                if info.is_cjk:
                    d_cu._feed(codepoint, info)
                    d_sk._feed(codepoint, info)
                elif info.is_katakana:
                    d_sk._feed(codepoint, info)
                if info.is_arabic:
                    d_ai._feed(codepoint, info)

        mean_mess_ratio = _mean_ratio(
            d_sp, d_ta, d_up, d_sda, d_sr, d_sw, d_cu, d_sk, d_au, d_ai
        )
        if mean_mess_ratio >= maximum_threshold:
            break
        block_start += step
    else:
        nl_info = <CharInfo>ascii_char_info[10]
        d_sw._feed(10, nl_info)
        if not is_pure_ascii:
            d_au._feed(10, nl_info)
        d_up._feed(10, nl_info)
        mean_mess_ratio = _mean_ratio(
            d_sp, d_ta, d_up, d_sda, d_sr, d_sw, d_cu, d_sk, d_au, d_ai
        )

    if debug:
        logger = getLogger("charset_normalizer")
        logger.log(
            TRACE,
            "Mess-detector extended-analysis start. "
            f"intermediary_mean_mess_ratio_calc={step} "
            f"mean_mess_ratio={mean_mess_ratio} "
            f"maximum_threshold={maximum_threshold}",
        )
        if seq_len > 16:
            logger.log(TRACE, f"Starting with: {decoded_sequence[:16]}")
            logger.log(TRACE, f"Ending with: {decoded_sequence[seq_len - 16:]}")
        for detector in [
            d_sp,
            d_ta,
            d_up,
            d_sda,
            d_sr,
            d_sw,
            d_cu,
            d_sk,
            d_au,
            d_ai,
        ]:
            logger.log(TRACE, f"{detector.__class__}: {detector.ratio}")

    return round(mean_mess_ratio, 3)
