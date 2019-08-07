import statistics
from collections import Counter
from hashlib import sha256

from cached_property import cached_property

import json
from os.path import dirname, realpath, exists


class ProbeCoherence:

    FREQUENCIES = None
    CACHED = dict()
    ASSETS_PATH = '{}/assets'.format(dirname(realpath(__file__)))

    def __init__(self, character_occurrences):
        """
        :param collections.Counter character_occurrences:
        """
        if not isinstance(character_occurrences, Counter):
            raise TypeError('Cannot probe coherence from type <{}>, expected <collections.Counter>'.format(type(character_occurrences)))

        if ProbeCoherence.FREQUENCIES is None:
            with open('{}/frequencies.json'.format(ProbeCoherence.ASSETS_PATH) if exists('{}/frequencies.json'.format(ProbeCoherence.ASSETS_PATH)) else './charset_normalizer/assets/frequencies.json', 'r') as fp:
                ProbeCoherence.FREQUENCIES = json.load(fp)

        self._character_occurrences = character_occurrences
        self.most_common = character_occurrences.most_common()
        self.nb_count_occurrence = sum(character_occurrences.values())
        self.rank_per_lang = dict()

        if self.uuid not in ProbeCoherence.CACHED:
            self._probe()

    @cached_property
    def uuid(self):
        return sha256(''.join(list(self._character_occurrences.keys())).encode('utf-8')).hexdigest()

    @property
    def ratio(self):
        """
        Return a value between 0. and 1.
        Closest to 0. means that the initial string is considered coherent,
        Closest to 1. means that the initial string SEEMS NOT coherent.
        :return: Ratio as floating number
        :rtype: float
        """
        if self.uuid not in ProbeCoherence.CACHED:
            ProbeCoherence.CACHED[self.uuid] = statistics.mean([c for l, c in self.rank_per_lang.items()]) if len(self.rank_per_lang.keys()) > 0 else 1.
        return ProbeCoherence.CACHED[self.uuid]

    def _probe(self):
        for language, letters in ProbeCoherence.FREQUENCIES.items():

            most_common_cpy = list()
            n_letter_not_available = 0

            for o_letter, o_appearances in self.most_common:

                if o_letter.lower() not in letters and o_appearances/self.nb_count_occurrence >= 0.0009:
                    n_letter_not_available += 1
                elif o_appearances/self.nb_count_occurrence >= 0.0009:
                    most_common_cpy.append(
                        (o_letter.lower(), o_appearances)
                    )

            if len(most_common_cpy) == 0:
                continue

            ratio_unavailable_letters = n_letter_not_available/len(self.most_common)

            if ratio_unavailable_letters < 0.4:
                not_respected_rank_coeff, n_tested_on = self._verify_order_on(letters, most_common_cpy)

                if not_respected_rank_coeff < 0.7:
                    self.rank_per_lang[language] = not_respected_rank_coeff

    @staticmethod
    def _verify_order_on(target_alphabet_ordered, character_occurrences):
        """
        Verify if a particular ordered set of character correspond more or less to our list of character occurrences
        :param list[str] target_alphabet_ordered:
        :param list[tuple[str, int]] character_occurrences:
        :return: Compute a ratio, Closest to 1. means our occurrences does not respect at all our ordered alphabet and closest to 0. means the opposite
        """
        n_not_rightfully_ranked = 0
        n_tested = 0

        n_letter_alphabet = len(target_alphabet_ordered)

        letters_failed = list()

        for w_index, (w_l, w_r) in zip(range(0, len(character_occurrences)), character_occurrences):
            if w_l not in target_alphabet_ordered:
                continue

            n_tested += 1

            r_index = target_alphabet_ordered.index(w_l)

            r_min_s, r_max_s = w_index - int(0.15 * n_letter_alphabet), w_index + int(0.15 * n_letter_alphabet)

            if r_min_s < 0:
                r_min_s = 0
            if r_max_s > n_letter_alphabet - 1:
                r_max_s = n_letter_alphabet - 1

            if not r_min_s <= r_index <= r_max_s:
                letters_failed.append((w_l, w_r))
                n_not_rightfully_ranked += 1
            elif r_index == w_index and n_not_rightfully_ranked > 0:
                n_not_rightfully_ranked -= 1

        if n_tested == 0:
            return 1., 0

        return (n_not_rightfully_ranked / n_tested) if n_tested >= 22 else 1., n_tested
