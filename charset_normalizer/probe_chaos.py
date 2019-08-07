import re

from charset_normalizer.unicode import UnicodeRangeIdentify

from dragonmapper.hanzi import identify as s_identify
from dragonmapper.hanzi import MIXED, BOTH, UNKNOWN
from zhon.hanzi import sentence as cjc_sentence_re

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

    def __dict__(self):
        return {
            'successive_upper_lower': self.successive_upper_lower,
            'successive_accent': self.successive_accent,
            'successive_different_unicode_range': self.successive_different_unicode_range,
            'encountered_unicode_range': self.encountered_unicode_range,
            'unprintable': self.unprintable,
            'encountered_white_space': self.encountered_white_space,
            'not_encountered_white_space': self.not_encountered_white_space,
            'encountered_unicode_range_occurrences': self.encountered_unicode_range_occurrences,
            'not_encountered_white_space_reset': self.not_encountered_white_space_reset,
            'total_letter_encountered': self.total_letter_encountered,
            '_unravel_suspicious_ranges': self._unravel_suspicious_ranges(),
            'total_lower_letter_encountered': self.total_lower_letter_encountered,
            'total_upper_accent_encountered': self.total_upper_accent_encountered,
            'total_upper_accent_encountered_inner': self.total_upper_accent_encountered_inner,
            'total_unaccented_letter_encountered': self.total_unaccented_letter_encountered,
            'cjc_id': s_identify(self._string) if 'Idéogrammes unifiés CJC' in self.encountered_unicode_range else 0,
            'f(x)': '({} + {} + {} + {} + {} + {}) / {}'.format(self.successive_upper_lower, self.successive_accent, self.successive_different_unicode_range, self.not_encountered_white_space, self.unprintable, self._unravel_suspicious_ranges(), len(self._string))
        }

    def _unravel_suspicious_ranges(self):
        len_ = len(self._string)
        s_ = 0

        for k, v in self.encountered_unicode_range_occurrences.items():
            k_ = k.lower()
            if ('latin' not in k_ and 'ponctuation générale' not in k_ and 'formes de demi et pleine chasse' not in k_ and 'symboles et ponct.' not in k_ and 'cjc' not in k_) or 'latin étendu' in k_ or 'supplément latin' in k_:
                if v / len_ < 0.09:
                    if len(self.encountered_unicode_range_occurrences.keys()) <= 2 and 'supplément latin' in k_:
                        continue
                    # print('Suspicous ranges added', k, v)
                    s_ += v if 'formes géométriques' not in k_ else v*10

        return s_

    def _probe(self):

        c__ = False

        # Todo: Gain 200ms by doing this : list(zip(self._string, self._string[1:]))[::2]
        # OR zip(self._string[::2], self._string[1::2])
        for c, i_ in zip(self._string, range(0, len(self._string))):

            if not c__ and (i_ / len(self._string)) > 0.2 and self.ratio >= 0.3:
                self.gave_up = True
                break
            elif c__ is False and (i_ / len(self._string)) > 0.2:
                c__ = True

            self.total_letter_encountered += 1

            if not c.isprintable():
                if c not in ['\n', '\t', '\r']:
                    u_name = UnicodeRangeIdentify.find_letter_type(c)
                    if 'CJC' not in u_name and 'Ponctuation générale' not in u_name and ord(c) != 160:  # CJC have there own space char
                        self.unprintable += 2
                else:
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

            if u_name is not None and u_name not in self.encountered_unicode_range:
                self.encountered_unicode_range_occurrences[u_name] = 0
                self.encountered_unicode_range.add(u_name)

            if is_accent and UnicodeRangeIdentify.is_accentuated(self.previous_printable_letter):
                self.successive_accent += 2

            if c.islower():
                self.total_lower_letter_encountered += 1

            if c.isupper() and is_accent:
                self.total_upper_accent_encountered += 1

                if self.previous_printable_letter.isalpha():
                    self.total_upper_accent_encountered_inner += 1
            elif not is_accent and c.isalpha():
                self.total_unaccented_letter_encountered += 1

            if u_name is not None:
                self.encountered_unicode_range_occurrences[u_name] += 1

                if 'symboles et ponct.' in u_name_lower or 'ponctuation générale' in u_name_lower:
                    self.encountered_white_space += 1
                    self.not_encountered_white_space = 0
                    self.not_encountered_white_space_reset += 1

                if 'latin' in u_name_lower or 'formes de demi et pleine chasse' in u_name_lower or 'symboles et ponct.' in u_name_lower or 'ponctuation générale' in u_name_lower or u_name is None:
                    self.previous_printable_letter = c
                    continue
                elif (self.previous_printable_letter.isupper() and c.islower()) or (
                        self.previous_printable_letter.islower() and c.isupper()):
                    self.successive_upper_lower += 1

                if u_name != self.previous_encountered_unicode_range and self.previous_encountered_unicode_range is not None:
                    if 'latin' not in self.previous_encountered_unicode_range.lower() and \
                            'formes de demi et pleine chasse' not in self.previous_encountered_unicode_range.lower() and \
                            'symboles et ponct.' not in self.previous_encountered_unicode_range.lower() and \
                            'ponctuation générale' not in self.previous_encountered_unicode_range.lower():
                        # print('successive unicode range', u_name, 'with', previous_encountered_unicode_range)
                        self.successive_different_unicode_range += 1

            self.previous_encountered_unicode_range = u_name
            self.previous_printable_letter = c

    def _unravel_cjc_suspicious(self):
        if 'Idéogrammes unifiés CJC' in self.encountered_unicode_range:
            if s_identify(self._string) in [MIXED, BOTH]:
                return self.encountered_unicode_range_occurrences['Idéogrammes unifiés CJC']
            elif len(re.findall(cjc_sentence_re, self._string)) == 0:
                return self.encountered_unicode_range_occurrences['Idéogrammes unifiés CJC']

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
        return (r_ + self.successive_upper_lower + self.successive_accent + self.successive_different_unicode_range + self.not_encountered_white_space + self.unprintable + self._unravel_suspicious_ranges() + self._unravel_cjc_suspicious()) / len(self._string)  # + len(self.encountered_unicode_range)-1

