# coding: utf-8
import json
import statistics
from collections import Counter
from functools import lru_cache
from os.path import dirname, realpath, exists

from charset_normalizer.unicode import UnicodeRangeIdentify
from charset_normalizer.constant import COHERENCE_ACCEPTED_MARGIN_LETTER_RANK, COHERENCE_ALPHABET_COVERED_IF, COHERENCE_PICKING_LETTER_MIN_APPEARANCE, COHERENCE_MIN_LETTER_NEEDED, COHERENCE_MAXIMUM_UNAVAILABLE_LETTER, COHERENCE_MAXIMUM_NOT_RESPECTED_RANK

from cached_property import cached_property


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
        self.letters = list(character_occurrences.keys())
        self.covered_letters = set()

        self.nb_used_occurrence = 0

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

    def ratio_of(self, language):
        """
        :param str language:
        :return:
        """
        if language.capitalize() not in self.rank_per_lang:
            return 1.
        return self.rank_per_lang[language.capitalize()]

    @cached_property
    def ratio(self):
        """
        Return a value between 0. and 1.
        Closest to 0. means that the initial string is considered coherent,
        Closest to 1. means that the initial string SEEMS NOT coherent.
        :return: Ratio as floating number
        :rtype: float
        """
        languages = self.most_likely

        if len(languages) == 0:
            return 1.

        ratios = [self.rank_per_lang[lg] for lg in languages]

        return statistics.mean(ratios) / 2 if self.non_latin_covered_any is True else statistics.mean(ratios)

    @property
    def coverage(self):
        return self.nb_used_occurrence / self.nb_count_occurrence

    @cached_property
    def alphabet_coverage(self):
        list_by_range = UnicodeRangeIdentify.list_by_range(self.letters)
        coverages = dict()

        for u_range, letters in list_by_range.items():
            n_covered = 0
            for l in letters:
                if l in self.covered_letters:
                    n_covered += 1

            coverages[u_range] = n_covered / len(letters) >= COHERENCE_ALPHABET_COVERED_IF

        return coverages

    @property
    def non_latin_covered_any(self):
        """
        :return:
        """
        for alphabet, covered in self.alphabet_coverage.items():
            if 'Latin' not in alphabet and covered is True:
                return True
        return False

    def _probe(self):

        self.index_of_rates = dict()

        for language, letters in ProbeCoherence.FREQUENCIES.items():

            most_common_cpy = list()
            n_letter_not_available = 0

            used_occ = 0

            for o_l in letters:
                if not o_l.isalpha():
                    continue
                if o_l not in self._most_common_dict.keys():
                    n_letter_not_available += 1
                elif self._most_common_dict[o_l] / self.nb_count_occurrence >= COHERENCE_PICKING_LETTER_MIN_APPEARANCE:
                    most_common_cpy.append(
                        (o_l.lower(), self._most_common_dict[o_l])
                    )
                    used_occ += self._most_common_dict[o_l]

            if len(most_common_cpy) < COHERENCE_MIN_LETTER_NEEDED:
                continue

            ratio_unavailable_letters = n_letter_not_available / len(letters)

            if ratio_unavailable_letters < COHERENCE_MAXIMUM_UNAVAILABLE_LETTER:

                most_common_cpy = sorted(most_common_cpy, key=lambda x: x[1], reverse=True)

                not_respected_rank_coeff, n_tested_on, n_tested_verified_on = self._verify_order_on(
                    letters,
                    most_common_cpy,
                    distance_margin=COHERENCE_ACCEPTED_MARGIN_LETTER_RANK
                )

                if not_respected_rank_coeff < COHERENCE_MAXIMUM_NOT_RESPECTED_RANK and n_tested_verified_on >= COHERENCE_MIN_LETTER_NEEDED:

                    if str(ratio_unavailable_letters) not in self.index_of_rates.keys():
                        self.index_of_rates[str(ratio_unavailable_letters)] = dict()

                    if str(not_respected_rank_coeff) not in self.index_of_rates[str(ratio_unavailable_letters)].keys():
                        self.index_of_rates[str(ratio_unavailable_letters)][str(not_respected_rank_coeff)] = list()

                    self.index_of_rates[str(ratio_unavailable_letters)][str(not_respected_rank_coeff)].append(language)

                    self.rank_per_lang[language] = not_respected_rank_coeff
                    self.available_letter_per_lang[language] = n_tested_verified_on

                    self.nb_used_occurrence += used_occ

                    for l, o in most_common_cpy:
                        self.covered_letters.add(l)

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

        if n_tested < 15:
            return 1., n_tested, n_tested_verified
        elif 15 <= n_tested < 22:
            if n_tested_verified/n_tested < COHERENCE_MAXIMUM_NOT_RESPECTED_RANK:
                return 1., n_tested, n_tested_verified

        return n_not_rightfully_ranked / n_tested, n_tested, n_tested_verified

    @staticmethod
    def frequencies_json(minimum_char_count=45000000, save_to_file=True, proxies=None):  # pragma: no cover
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

            print('ADDED', language, '|Computed WITH|', n_char, '|WITH Letters|', letters)

            ProbeCoherence.FREQUENCIES[language] = letters

        if save_to_file:
            with open('{}/frequencies.json'.format(ProbeCoherence.ASSETS_PATH) if exists('{}/frequencies.json'.format(
                    ProbeCoherence.ASSETS_PATH)) else './charset_normalizer/assets/frequencies.json', 'w', encoding='utf-8') as fp:
                json.dump(ProbeCoherence.FREQUENCIES, fp)
