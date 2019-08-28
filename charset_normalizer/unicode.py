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
                    'latin' not in k_ and 'general punctuation' not in k_ and 'halfwidth and fullwidth forms' not in k_ and 'symbols and punctuation' not in k_ and 'cjk' not in k_) or 'latin extended' in k_ or 'latin-1 supplement' in k_:
                if v / str_len < 0.09:
                    if len(encountered_unicode_range_occurrences.keys()) <= 2 and 'latin-1 supplement' in k_:
                        continue
                    # print('Suspicous ranges added', k, v)
                    s_ += v if 'geometric shapes' not in k_ else v * 10

        return s_
