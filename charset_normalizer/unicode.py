# coding: utf-8
from charset_normalizer.constant import UNICODE_RANGES_ZIP, UNICODE_RANGES_NAMES
from functools import lru_cache


class UnicodeRangeIdentify:

    SUSPICIOUS_RANGES_CACHE = dict()

    @staticmethod
    @lru_cache(maxsize=8192)
    def find_letter_type(letter):
        """
        This method is intended to associate a single character with a range name from the unicode table
        :param str letter: Shall be a unique char
        :return: Associated unicode range designation
        :rtype: Union[str, None]
        """
        if len(letter) != 1:
            raise IOError('Trying to associate multiple char <{}> to a single unicode range'.format(letter))

        for u_name, u_range in UNICODE_RANGES_ZIP.items():

            if ord(letter) in u_range:
                return u_name

        return None

    @staticmethod
    @lru_cache(maxsize=8192)
    def is_accentuated(letter):
        """
        Verify if a latin letter is accentuated, unicode point of view.
        :param str letter: Letter to check
        :return: True if accentuated, else False
        :rtype: bool
        """
        if len(letter) != 1:
            raise IOError('Trying to determine accentuated state of multiple char <{}>'.format(letter))
        return 192 <= ord(letter) <= 383

    @staticmethod
    @lru_cache(maxsize=512)
    def get_range_id(range_name):
        return UNICODE_RANGES_NAMES.index(range_name)

    @staticmethod
    @lru_cache(maxsize=8192)
    def is_latin(letter):
        """
        Verify if a letter is Latin based
        :param str letter:
        :return:
        """
        return 'Latin' in UnicodeRangeIdentify.find_letter_type(letter)

    @staticmethod
    @lru_cache(maxsize=8192)
    def is_punc(letter):
        """
        Verify if a letter is a sort of punctuation sign
        :param str letter:
        :return:
        """
        if letter.isspace():
            return True
        r_name = UnicodeRangeIdentify.find_letter_type(letter)
        return "Punctuation" in r_name or \
               'Forms' in r_name or \
               letter in 'º¯—–‒‐⁃«‹?!;.:^$*»£¹¿~ª؟©±¡{}[]|¼½¾⅕⅙⅛™℠‼⁇❝❞¶⁋√↑↓�'

    @staticmethod
    @lru_cache(maxsize=8192)
    def is_cjk(letter):
        """
        Verify if a letter is part of a CJK unicode range
        :param str letter:
        :return:
        """
        return 'CJK' in UnicodeRangeIdentify.find_letter_type(letter)

    @staticmethod
    def unravel_suspicious_ranges(str_len, encountered_unicode_range_occurrences):
        """
        :param dict encountered_unicode_range_occurrences:
        :return:
        """

        items = encountered_unicode_range_occurrences.items()
        s_ = 0

        for k, v in items:
            k_ = k.lower()
            if (
                    'latin' not in k_ and 'general punctuation' not in k_ and 'symbols and punctuation' not in k_ and 'cjk' not in k_) or 'latin extended' in k_ or 'latin-1 supplement' in k_:
                if v / str_len < 0.09:
                    if len(encountered_unicode_range_occurrences.keys()) <= 2 and 'latin-1 supplement' in k_:
                        continue
                    if 'halfwidth and fullwidth forms' in k_ and any(['CJK' in el for el in encountered_unicode_range_occurrences.keys()]):
                        continue
                    s_ += v if 'geometric shapes' not in k_ else v * 10

        return s_

    @staticmethod
    @lru_cache(maxsize=8192)
    def is_suspiciously_successive_range(range_name_a, range_name_b):
        """
        :param str range_name_a:
        :param str range_name_b:
        :return:
        """

        dec_range_name_a, dec_range_name_b = range_name_a.split(), range_name_b.split()

        if range_name_a == range_name_b:
            return False

        if 'Latin' in range_name_a or 'Latin' in range_name_b:
            return False

        for el in dec_range_name_a:
            if el in dec_range_name_b:
                return False

        if range_name_a in ['Katakana', 'Hiragana'] and 'CJK' in range_name_b:
            return False

        if 'CJK' in range_name_a and range_name_b in ['Katakana', 'Hiragana']:
            return False

        return True
