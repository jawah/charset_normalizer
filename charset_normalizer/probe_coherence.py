# coding: utf-8
import statistics
from collections import Counter

from cached_property import cached_property

import json
from os.path import dirname, realpath, exists

from functools import lru_cache


class HashableCounter(Counter):

    def __hash__(self):
        return hash(tuple(self.items()))


@lru_cache(maxsize=8192)
class ProbeCoherence:

    FREQUENCIES = None
    CACHED = dict()
    ASSETS_PATH = '{}/assets'.format(dirname(realpath(__file__)))

    def __init__(self, character_occurrences):
        """
        :param HashableCounter character_occurrences:
        """
        if not isinstance(character_occurrences, Counter):
            raise TypeError('Cannot probe coherence from type <{}>, expected <collections.Counter>'.format(
                type(character_occurrences)))

        if ProbeCoherence.FREQUENCIES is None:
            with open('{}/frequencies.json'.format(ProbeCoherence.ASSETS_PATH) if exists('{}/frequencies.json'.format(
                    ProbeCoherence.ASSETS_PATH)) else './charset_normalizer/assets/frequencies.json', 'r') as fp:
                ProbeCoherence.FREQUENCIES = json.load(fp)

        self._character_occurrences = character_occurrences
        self.most_common = character_occurrences.most_common()
        self._most_common_dict = dict(self.most_common)
        self.nb_count_occurrence = sum(character_occurrences.values())

        self.rank_per_lang = dict()
        self.available_letter_per_lang = dict()

        self.index_of_rates = dict()

        self._probe()

    @cached_property
    def most_likely(self):
        p_ = [(float(el), float(sorted(self.index_of_rates[str(el)].keys())[0])) for el in
         sorted([float(el) for el in list(self.index_of_rates.keys())])[:10]]

        k_ = [self.index_of_rates[str(el[0])][str(el[1])] for el in sorted(p_, key=lambda tup: sum(tup))]
        return [item for sublist in k_ for item in sublist][:3]

    @cached_property
    def ratio(self):
        """
        Return a value between 0. and 1.
        Closest to 0. means that the initial string is considered coherent,
        Closest to 1. means that the initial string SEEMS NOT coherent.
        :return: Ratio as floating number
        :rtype: float
        """
        p_ = [(float(el), float(sorted(self.index_of_rates[str(el)].keys())[0])) for el in
              sorted([float(el) for el in list(self.index_of_rates.keys())])]

        return statistics.mean([sum(el) for el in p_[:2]]) if len(
            self.rank_per_lang.keys()) > 0 else 1.

    def _probe(self):

        self.index_of_rates = dict()

        for language, letters in ProbeCoherence.FREQUENCIES.items():

            most_common_cpy = list()
            n_letter_not_available = 0

            for o_l in letters:
                if not o_l.isalpha():
                    continue
                if o_l not in self._most_common_dict.keys():
                    n_letter_not_available += 1
                elif self._most_common_dict[o_l] / self.nb_count_occurrence >= 0.003:
                    most_common_cpy.append(
                        (o_l.lower(), self._most_common_dict[o_l])
                    )

            # Todo: !! Create more constant in constant.py !!
            if len(most_common_cpy) < 10:
                continue

            ratio_unavailable_letters = n_letter_not_available / len(letters)

            if ratio_unavailable_letters < 0.4:

                most_common_cpy = sorted(most_common_cpy, key=lambda x: x[1], reverse=True)

                not_respected_rank_coeff, n_tested_on, n_tested_verified_on = self._verify_order_on(
                    letters,
                    most_common_cpy,
                    distance_margin=3
                )

                if not_respected_rank_coeff < 0.5 and n_tested_verified_on >= 10:

                    if str(ratio_unavailable_letters) not in self.index_of_rates.keys():
                        self.index_of_rates[str(ratio_unavailable_letters)] = dict()

                    if str(not_respected_rank_coeff) not in self.index_of_rates[str(ratio_unavailable_letters)].keys():
                        self.index_of_rates[str(ratio_unavailable_letters)][str(not_respected_rank_coeff)] = list()

                    self.index_of_rates[str(ratio_unavailable_letters)][str(not_respected_rank_coeff)].append(language)

                    self.rank_per_lang[language] = not_respected_rank_coeff
                    self.available_letter_per_lang[language] = n_tested_verified_on

    @staticmethod
    def _verify_order_on(target_alphabet_ordered, character_occurrences, distance_margin=4):
        """
        Verify if a particular ordered set of character correspond more or less to our list of character occurrences
        :param list[str] target_alphabet_ordered:
        :param list[tuple[str, int]] character_occurrences:
        :return: Compute a ratio, Closest to 1. means our occurrences does not respect at all our ordered alphabet and closest to 0. means the opposite
        """
        n_not_rightfully_ranked = 0
        n_tested = 0
        n_tested_verified = 0

        n_letter_alphabet = len(target_alphabet_ordered)

        letters_failed = list()

        for w_index, (w_l, w_r) in zip(range(0, len(character_occurrences)), character_occurrences):
            if w_l not in target_alphabet_ordered:
                continue

            n_tested += 1

            r_index = target_alphabet_ordered.index(w_l)

            r_min_s, r_max_s = w_index - distance_margin, w_index + distance_margin

            if r_min_s < 0:
                r_min_s = 0
            if r_max_s > n_letter_alphabet - 1:
                r_max_s = n_letter_alphabet - 1

            if not r_min_s <= r_index <= r_max_s:
                letters_failed.append((w_l, w_r))
                n_not_rightfully_ranked += 1
                continue

            distance = r_index - w_index

            if 0 < distance < distance_margin:
                n_not_rightfully_ranked -= 1
            if distance == 0:
                n_not_rightfully_ranked -= 2

            if n_not_rightfully_ranked < 0:
                n_not_rightfully_ranked = 0

            n_tested_verified += 1

        if n_tested == 0 or n_tested_verified == 0:
            return 1., n_tested, n_tested_verified

        return (n_not_rightfully_ranked / n_tested) if n_tested >= 22 else 1., n_tested, n_tested_verified

    @staticmethod
    def frequencies_json(minimum_char_count=45000000, save_to_file=True, proxies=None):
        """
        This method refresh or create frequencies.json at will.
        Don't abuse it as it perform HTTP GET query
        Data scrapped from and (c) simia.net,

        To invoke, use trickery: ProbeCoherence.frequencies_json.__func__()

        :param int minimum_char_count:
        :param bool save_to_file:
        :param dict proxies: Proxies to use as used by requests if needed
        :return:
        """

        try:
            from requests import get
            from requests_html import HTML
        except ImportError:
            raise ImportError('You need to install requests and requests_html in order to invoke frequencies_json static method.')

        r = get(
            'http://simia.net/letters/',
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0'},
            proxies=proxies
        )

        if r.ok is False:
            raise IOError('Unable to perform HTTP GET on "http://simia.net/letters/". Got HTTP/{}.'.format(r.status_code))

        d = HTML(html=r.content)
        ProbeCoherence.FREQUENCIES = dict()

        for _row in d.find('tr'):
            td_language, td_letters = tuple(_row.find('td'))

            language = td_language.find('a')[0].text
            n_char = int(td_language.find('span')[0].text.replace('characters', '').replace(',', ''))

            if n_char < minimum_char_count and 'Chinese' not in language:
                continue

            letters = list()

            for span in td_letters.find('span'):
                letter = span.text  # type: str

                if letter.isalpha():
                    letters.append(letter)

                if len(letters) > 25:
                    break

            print(language, n_char, letters)

            ProbeCoherence.FREQUENCIES[language] = letters

        if save_to_file:
            with open('{}/frequencies.json'.format(ProbeCoherence.ASSETS_PATH) if exists('{}/frequencies.json'.format(
                    ProbeCoherence.ASSETS_PATH)) else './charset_normalizer/assets/frequencies.json', 'w', encoding='utf-8') as fp:
                json.dump(ProbeCoherence.FREQUENCIES, fp)

