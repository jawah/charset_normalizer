# coding: utf-8
import re

from dragonmapper.hanzi import MIXED, BOTH, UNKNOWN
from dragonmapper.hanzi import identify as s_identify
from zhon.hanzi import sentence as cjc_sentence_re

from charset_normalizer.unicode import UnicodeRangeIdentify

from functools import lru_cache


@lru_cache(maxsize=8192)
class ProbeChaos:

    def __init__(self, string):
        """
        :param str string:
        """

        if not isinstance(string, str):
            raise TypeError('Cannot probe chaos from type <{}>, expected <str>'.format(type(string)))

        self._string = string

        self.successive_upper_lower = 0
        self.successive_accent = 0
        self.successive_different_unicode_range = 0
        self.encountered_unicode_range = set()
        self.unprintable = 0
        self.encountered_white_space = 0
        self.not_encountered_white_space = 0

        self.encountered_unicode_range_occurrences = dict()

        self.not_encountered_white_space_reset = 0

        self.previous_printable_letter = None

        self.previous_encountered_unicode_range = None

        self.total_letter_encountered = 0

        self.total_lower_letter_encountered = 0
        self.total_upper_accent_encountered = 0
        self.total_upper_accent_encountered_inner = 0
        self.total_unaccented_letter_encountered = 0

        self.gave_up = False

        if len(self._string) >= 10:
            self._probe()

    def _probe(self):

        c__ = False

        for c, i_ in zip(self._string, range(0, len(self._string))):
            state_ = (i_ / len(self._string) >= 0.5)
            if not c__ and state_ > 0.2 and self.ratio >= 0.3:
                self.gave_up = True
                break
            elif c__ is False and state_ > 0.2:
                c__ = True

            self.total_letter_encountered += 1

            if not c.isprintable():
                if c not in ['\n', '\t', '\r']:
                    u_name = UnicodeRangeIdentify.find_letter_type(c)
                    if 'CJK' not in u_name and 'General Punctuation' not in u_name and ord(c) != 160:  # CJC have there own white spaces
                        self.unprintable += 2

                self.encountered_white_space += 1
                self.not_encountered_white_space = 0
                self.not_encountered_white_space_reset += 1
                continue

            if c.isspace():
                self.encountered_white_space += 1
                self.not_encountered_white_space = 0
                self.not_encountered_white_space_reset += 1
                self.previous_printable_letter = c
                continue

            if self.not_encountered_white_space_reset < 2:
                self.not_encountered_white_space += 1

            if self.previous_printable_letter is None:
                self.previous_printable_letter = c
                continue

            is_accent = UnicodeRangeIdentify.is_accentuated(c)
            u_name = UnicodeRangeIdentify.find_letter_type(c)
            u_name_lower = u_name.lower() if u_name is not None else None

            is_upper = c.isupper()
            is_lower = c.islower() if not is_upper else False
            is_alpha = c.isalpha()

            if u_name is not None and u_name not in self.encountered_unicode_range:
                self.encountered_unicode_range_occurrences[u_name] = 0
                self.encountered_unicode_range.add(u_name)

            if is_accent and UnicodeRangeIdentify.is_accentuated(self.previous_printable_letter):
                self.successive_accent += 2

            if is_lower:
                self.total_lower_letter_encountered += 1

            if is_upper and is_accent:
                self.total_upper_accent_encountered += 1
                if self.previous_printable_letter.isalpha():
                    self.total_upper_accent_encountered_inner += 1
            elif not is_accent and is_alpha:
                self.total_unaccented_letter_encountered += 1

            if u_name is not None:
                self.encountered_unicode_range_occurrences[u_name] += 1

                if 'symbols and punctuation' in u_name_lower or 'general punctuation' in u_name_lower or 'halfwidth and fullwidth forms' in u_name_lower:
                    self.encountered_white_space += 1
                    self.not_encountered_white_space = 0
                    self.not_encountered_white_space_reset += 1

                if 'latin' in u_name_lower or 'halfwidth and fullwidth forms' in u_name_lower or 'symbols and punctuation' in u_name_lower or 'general punctuation' in u_name_lower:
                    self.previous_printable_letter = c
                    continue
                elif (self.previous_printable_letter.isupper() and c.islower()) or (
                        self.previous_printable_letter.islower() and c.isupper()):
                    self.successive_upper_lower += 1

                if u_name != self.previous_encountered_unicode_range and self.previous_encountered_unicode_range is not None:
                    k__ = self.previous_encountered_unicode_range
                    if 'latin' not in k__ and \
                            'halfwidth and fullwidth forms' not in k__ and \
                            'symbols and punctuation' not in k__ and \
                            'general punctuation' not in k__:
                        self.successive_different_unicode_range += 1

            self.previous_encountered_unicode_range = u_name
            self.previous_printable_letter = c

    def _unravel_cjc_suspicious(self):
        if 'CJK Unified Ideographs' in self.encountered_unicode_range:
            if s_identify(self._string) in [MIXED, BOTH]:
                return self.encountered_unicode_range_occurrences['CJK Unified Ideographs']
            elif len(re.findall(cjc_sentence_re, self._string)) == 0:
                return self.encountered_unicode_range_occurrences['CJK Unified Ideographs']

        return UNKNOWN

    @property
    def ratio(self):
        """
        Return a value between 0. and 1.
        Closest to 1. means that the initial string is considered as chaotic,
        Closest to 0. means that the initial string SEEMS NOT chaotic.
        :return: Ratio as floating number
        :rtype: float
        """
        r_ = self.total_upper_accent_encountered if self.total_letter_encountered > 0 and self.total_unaccented_letter_encountered / self.total_letter_encountered < 0.5 else 0
        z_ = UnicodeRangeIdentify.unravel_suspicious_ranges(len(self._string), self.encountered_unicode_range_occurrences)
        return (r_ + self.successive_upper_lower + self.successive_accent + self.successive_different_unicode_range + self.not_encountered_white_space + self.unprintable + z_ + self._unravel_cjc_suspicious()) / len(self._string)  # + len(self.encountered_unicode_range)-1
