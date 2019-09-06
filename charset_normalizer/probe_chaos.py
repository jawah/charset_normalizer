# coding: utf-8
import re

from dragonmapper.hanzi import MIXED, BOTH, UNKNOWN
from dragonmapper.hanzi import identify as s_identify
from zhon.hanzi import sentence as cjc_sentence_re

from charset_normalizer.unicode import UnicodeRangeIdentify

from functools import lru_cache


@lru_cache(maxsize=8192)
class ProbeChaos:

    def __init__(self, string, giveup_threshold=0.09):
        """
        :param str string:
        """

        if not isinstance(string, str):
            raise TypeError('Cannot probe chaos from type <{}>, expected <str>'.format(type(string)))

        self._string = string
        self._threshold = giveup_threshold

        self.successive_upper_lower = 0
        self.successive_accent = 0
        self.successive_different_unicode_range = 0
        self.encountered_unicode_range = set()
        self.encountered_punc_sign = 0
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

            if not c__:
                state_ = (i_ / len(self._string) >= 0.5)

            # If we already have measured 10 % or more of chaos after reading 50 %, give up.
            if not c__ and state_ and self.ratio >= self._threshold:
                self.gave_up = True
                break
            elif c__ is False and state_:
                c__ = True

            self.total_letter_encountered += 1

            if not c.isprintable():
                if c not in ['\n', '\t', '\r']:
                    if not UnicodeRangeIdentify.is_cjk(c) and not UnicodeRangeIdentify.is_punc(c):
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

            is_upper = c.isupper()
            is_lower = c.islower() if not is_upper else False
            is_alpha = c.isalpha()
            is_latin = UnicodeRangeIdentify.is_latin(c)

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

                is_punc = UnicodeRangeIdentify.is_punc(c)

                if is_punc is True:
                    self.encountered_punc_sign += 1
                    self.encountered_white_space += 1
                    self.not_encountered_white_space = 0
                    self.not_encountered_white_space_reset += 1
                    continue

                if (is_lower and self.previous_printable_letter.isupper()) or (is_upper and self.previous_printable_letter.islower()):
                    self.successive_upper_lower += 1

                if is_latin:
                    self.previous_encountered_unicode_range = u_name
                    self.previous_printable_letter = c

                if self.previous_encountered_unicode_range is not None and UnicodeRangeIdentify.is_suspiciously_successive_range(u_name, self.previous_encountered_unicode_range) is True:

                    if not UnicodeRangeIdentify.is_punc(self.previous_printable_letter):
                        self.successive_different_unicode_range += 1

            self.previous_encountered_unicode_range = u_name
            self.previous_printable_letter = c

        if len(self._string) < 50:
            self.not_encountered_white_space = 0
        if self.successive_upper_lower < 3:
            self.successive_upper_lower = 0

    @staticmethod
    def _unravel_cjk_suspicious_chinese(string, encountered_unicode_range_occurrences):

        encountered_unicode_range = encountered_unicode_range_occurrences.keys()

        if 'CJK Unified Ideographs' in encountered_unicode_range and ('Hiragana' not in encountered_unicode_range and 'Katakana' not in encountered_unicode_range):
            i_ = s_identify(string)
            if i_ in [MIXED, BOTH]:
                return encountered_unicode_range_occurrences['CJK Unified Ideographs']
            elif i_ != UNKNOWN and len(re.findall(cjc_sentence_re, string)) == 0:
                return encountered_unicode_range_occurrences['CJK Unified Ideographs']

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
        p_ = self.encountered_punc_sign if self.encountered_punc_sign / len(self._string) > 0.2 else 0
        return (r_ + p_ + self.successive_upper_lower + self.successive_accent + self.successive_different_unicode_range + self.not_encountered_white_space + self.unprintable + z_ + ProbeChaos._unravel_cjk_suspicious_chinese.__func__(self._string, self.encountered_unicode_range_occurrences)) / len(self._string)  # + len(self.encountered_unicode_range)-1
