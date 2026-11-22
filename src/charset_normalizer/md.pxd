from libc.stdint cimport uint32_t


cdef enum:
    UNICODE_RANGE_CAPACITY = 512
    # Identifier used for characters that do not belong to any known range.
    NO_RANGE_ID = UNICODE_RANGE_CAPACITY - 1


cdef class CharInfo:
    cdef readonly str character
    cdef readonly bint printable
    cdef readonly bint alpha
    cdef readonly bint upper
    cdef readonly bint lower
    cdef readonly bint space
    cdef readonly bint digit
    cdef readonly bint is_ascii
    cdef readonly bint case_variable
    cdef readonly int flags
    cdef readonly bint accentuated
    cdef readonly bint latin
    cdef readonly bint is_cjk
    cdef readonly bint is_katakana
    cdef readonly bint is_halfwidth_katakana
    cdef readonly bint is_arabic
    cdef readonly bint is_ligature
    cdef readonly bint is_superscript
    cdef readonly bint is_sentence_open_punctuation
    cdef readonly bint is_glyph
    cdef readonly bint punct
    cdef readonly bint sym
    cdef readonly object range
    cdef int range_id
    cdef readonly bint sep
    cdef readonly bint emoticon
    cdef readonly bint safe
    cdef readonly bint common_cjk
    cdef readonly str unaccented


cdef CharInfo _char_info_from_codepoint(Py_UCS4 codepoint)
cdef bint _is_suspicious_range_ids(int range_id_a, int range_id_b) noexcept


cdef class MessDetectorPlugin:
    cpdef void feed_info(self, str character, CharInfo info)
    cpdef void reset(self)


cdef class TooManySymbolOrPunctuationPlugin(MessDetectorPlugin):
    cdef int _punctuation_count
    cdef int _symbol_count
    cdef int _character_count
    cdef uint32_t _last_printable_char
    cpdef void feed_info(self, str character, CharInfo info)
    cpdef void reset(self)
    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept
    cdef double _ratio(self) noexcept


cdef class TooManyAccentuatedPlugin(MessDetectorPlugin):
    cdef int _character_count
    cdef int _accentuated_count
    cpdef void feed_info(self, str character, CharInfo info)
    cpdef void reset(self)
    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept
    cdef double _ratio(self) noexcept


cdef class UnprintablePlugin(MessDetectorPlugin):
    cdef int _unprintable_count
    cdef int _character_count
    cdef bint _has_escape
    cpdef void feed_info(self, str character, CharInfo info)
    cpdef void reset(self)
    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept
    cdef double _ratio(self) noexcept


cdef class SuspiciousDuplicateAccentPlugin(MessDetectorPlugin):
    cdef int _successive_count
    cdef int _character_count
    cdef object _last_latin_character
    cdef bint _last_was_accentuated
    cpdef void feed_info(self, str character, CharInfo info)
    cpdef void reset(self)
    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept
    cdef double _ratio(self) noexcept


cdef class SuspiciousRange(MessDetectorPlugin):
    cdef int _suspicious_successive_range_count
    cdef int _character_count
    cdef bint _has_last_printable
    cdef int _last_printable_range_id
    cpdef void feed_info(self, str character, CharInfo info)
    cpdef void reset(self)
    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept
    cdef double _ratio(self) noexcept


cdef class SuperWeirdWordPlugin(MessDetectorPlugin):
    cdef int _word_count
    cdef int _bad_word_count
    cdef int _foreign_long_count
    cdef bint _is_current_word_bad
    cdef bint _foreign_long_watch
    cdef int _character_count
    cdef int _bad_character_count
    cdef int _buffer_length
    cdef bint _buffer_last_char_upper
    cdef bint _buffer_last_char_accentuated
    cdef int _buffer_accent_count
    cdef int _buffer_glyph_count
    cdef int _buffer_upper_count
    cdef bint _buffer_first_lower
    cdef bint _buffer_has_non_ascii
    cdef bint _buffer_last_char_ligature
    cdef bint _buffer_has_internal_ligature
    cdef bint _is_current_word_invalid
    cdef int _invalid_word_count
    cpdef void feed_info(self, str character, CharInfo info)
    cpdef void reset(self)
    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept
    cdef double _ratio(self) noexcept


cdef class CjkUncommonPlugin(MessDetectorPlugin):
    cdef int _character_count
    cdef int _uncommon_count
    cpdef void feed_info(self, str character, CharInfo info)
    cpdef void reset(self)
    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept
    cdef double _ratio(self) noexcept


cdef class SuspiciousKatakanaPlugin(MessDetectorPlugin):
    cdef int _katakana_count
    cdef int _halfwidth_katakana_count
    cdef int _cjk_count
    cdef int _uncommon_cjk_count
    cpdef void feed_info(self, str character, CharInfo info)
    cpdef void reset(self)
    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept
    cdef double _ratio(self) noexcept


cdef class ArchaicUpperLowerPlugin(MessDetectorPlugin):
    cdef bint _buf
    cdef int _character_count_since_last_sep
    cdef int _successive_upper_lower_count
    cdef int _successive_upper_lower_count_final
    cdef int _character_count
    cdef bint _last_alpha_seen_upper
    cdef bint _last_alpha_seen_lower
    cdef bint _current_ascii_only
    cpdef void feed_info(self, str character, CharInfo info)
    cpdef void reset(self)
    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept
    cdef double _ratio(self) noexcept


cdef class ArabicIsolatedFormPlugin(MessDetectorPlugin):
    cdef int _character_count
    cdef int _isolated_form_count
    cpdef void feed_info(self, str character, CharInfo info)
    cpdef void reset(self)
    cdef inline void _feed(self, Py_UCS4 codepoint, CharInfo info) noexcept
    cdef double _ratio(self) noexcept


cpdef double mess_ratio(
    str decoded_sequence,
    double maximum_threshold=*,
    bint debug=*,
)
