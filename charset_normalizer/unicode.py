# coding: utf-8
from functools import lru_cache

from charset_normalizer.constant import UNICODE_RANGES_ZIP, UNICODE_RANGES_NAMES, UNICODE_SECONDARY_RANGE_KEYWORD


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
        return 'Latin' in (UnicodeRangeIdentify.find_letter_type(letter) or '')

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
        return r_name is not None and \
               ("Punctuation" in r_name or
               'Forms' in r_name or
               letter in set('º¯—–‒‐⁃«‹?!;.:^$¥*»£¹¿~ª؟©±¡{}[]|½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅐⅛⅜⅝⅞⅑⅒™℠¬‼⁇❝❞¶⁋√↑↓�¤©`¨'))

    @staticmethod
    @lru_cache(maxsize=8192)
    def is_cjk(letter):
        """
        Verify if a letter is part of a CJK unicode range
        :param str letter:
        :return:
        """
        return 'CJK' in (UnicodeRangeIdentify.find_letter_type(letter) or '')

    @staticmethod
    def unravel_suspicious_ranges(str_len, encountered_unicode_range_occurrences):
        """
        :param int str_len:
        :param dict encountered_unicode_range_occurrences:
        :return:
        """

        items = encountered_unicode_range_occurrences.items()
        s_ = 0

        # print(encountered_unicode_range_occurrences)

        for k, v in items:
            k_ = k.lower()
            if (
                    'latin' not in k_ and 'general punctuation' not in k_ and 'symbols and punctuation' not in k_ and 'cjk' not in k_) or 'latin extended' in k_ or 'latin-1 supplement' in k_:
                if v / str_len < 0.09:
                    if len(encountered_unicode_range_occurrences.keys()) <= 2 and 'latin-1 supplement' in k_:
                        continue
                    if 'halfwidth and fullwidth forms' in k_ and any(['CJK' in el for el in encountered_unicode_range_occurrences.keys()]):
                        continue
                    if 'hiragana' in k_ or 'katakana' in k_:
                        continue
                    # print('suspicious', k_, 'with', v)
                    s_ += v

        return s_

    @staticmethod
    @lru_cache(maxsize=8192)
    def is_suspiciously_successive_range(range_name_a, range_name_b):
        """
        Verify if range B encountered just after range A is considered suspicious
        :param str range_name_a: Unicode range A
        :param str range_name_b: Unicode range B
        :return: True if suspicious else False
        :rtype: bool
        """
        if range_name_a is None or range_name_b is None:
            return True

        dec_range_name_a, dec_range_name_b = range_name_a.split(), range_name_b.split()

        if range_name_a == range_name_b:
            return False

        if 'Latin' in range_name_a and 'Latin' in range_name_b:
            return False

        for el in dec_range_name_a:
            if el in dec_range_name_b:
                return False

        if range_name_a in ['Katakana', 'Hiragana'] and 'CJK' in range_name_b:
            return False

        if 'CJK' in range_name_a and range_name_b in ['Katakana', 'Hiragana']:
            return False

        if range_name_a in ['Katakana', 'Hiragana'] and range_name_b in ['Katakana', 'Hiragana']:
            return False

        return True

    @staticmethod
    def classification(word):
        """
        :param str word:
        :return:
        """
        cla_ = dict()

        for el in word:
            if el.isspace():
                raise IOError('Classification should not be invoked with sentences !')
            u_name = UnicodeRangeIdentify.find_letter_type(el)
            if u_name is None:
                u_name = 'Unknown'
            if u_name not in cla_:
                cla_[u_name] = 0
            cla_[u_name] += 1

        return cla_

    @staticmethod
    @lru_cache(maxsize=512)
    def is_range_secondary(u_range):
        """
        Determine if a unicode range name is not a primary range by search specific keyword in range name
        :param str u_range: Unicode range name
        :return: True if secondary else False
        :rtype: bool
        """
        try:
            UnicodeRangeIdentify.get_range_id(u_range)
        except ValueError:
            return True

        for keyword in UNICODE_SECONDARY_RANGE_KEYWORD:
            if keyword in u_range:
                return True

        return False

    @staticmethod
    def part_punc(word):
        """
        Determine how much of the word is composed of punc sign
        :param str word:
        :return: Ratio special letter VS len of the word
        :rtype: float
        """
        return [UnicodeRangeIdentify.is_punc(el) for el in word].count(True) / len(word)

    @staticmethod
    def part_accent(word):
        """
        Determine how much of the word is composed of accentuated letter
        :param word:
        :return: Ratio accentuated letter VS len of the word
        :rtype: float
        """
        return [UnicodeRangeIdentify.is_accentuated(el) for el in word].count(True) / len(word)

    @staticmethod
    def word_to_range_list(word):
        """
        :param str word:
        :return: Produce a list containing for each letter in word it's unicode range name
        :rtype: list[str]
        """
        return [UnicodeRangeIdentify.find_letter_type(el) for el in word]

    @staticmethod
    def word_to_range_continue(word):
        """
        :param str word:
        :return: List of tuple (unicode range with occ) continuously encountered in a word
        :rtype: list[tuple[str, int]]
        """
        l_ = list()

        for el in word:
            u_name = UnicodeRangeIdentify.find_letter_type(el)
            if len(l_) == 0:
                l_.append(
                    (
                        u_name,
                        1
                    )
                )
            else:
                if UnicodeRangeIdentify.is_suspiciously_successive_range(u_name, l_[-1][0]) is True:
                    l_.append(
                        (
                            u_name,
                            1
                        )
                    )
                else:
                    l_[-1] = (
                        u_name,
                        l_[-1][1]+1
                    )

        return l_

    @staticmethod
    def part_lonely_range(word):
        """
        :param str word:
        :return:
        """
        return [u_occ_cont == 1 for u_name, u_occ_cont in UnicodeRangeIdentify.word_to_range_continue(word)].count(True) / len(word)

    @staticmethod
    def list_by_range(letters):
        """
        Sort letters by unicode range in a dict
        :param list[str] letters:
        :return: Letters by unicode range
        :rtype: dict
        """
        by_ranges = dict()

        for l in letters:
            u_range = UnicodeRangeIdentify.find_letter_type(l)

            s_ = False

            for range_name, letters in by_ranges.items():
                if UnicodeRangeIdentify.is_suspiciously_successive_range(range_name, u_range) is False:
                    by_ranges[range_name].append(l)
                    s_ = True
                    break

            if s_ is False:
                if u_range not in by_ranges.keys():
                    by_ranges[u_range] = list()
                by_ranges[u_range].append(l)

        return by_ranges
