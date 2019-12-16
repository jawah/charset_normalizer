from functools import lru_cache

from charset_normalizer.probe_coherence import HashableCounter
from charset_normalizer.unicode import UnicodeRangeIdentify


@lru_cache(maxsize=8192)
class ProbeWords:

    def __init__(self, w_counter):
        """
        :param HashableCounter w_counter:
        """
        self._w_counter = w_counter

        self._words = list()
        self._nb_words = 0

        self._suspicious = list()

        if w_counter is not None:
            self._words = list(w_counter.keys())
            self._nb_words = len(self._words)

            self._probe()

    def __add__(self, other):
        """

        :param ProbeWords other:
        :return:
        """
        k_ = ProbeWords(None)

        k_._nb_words = self._nb_words + other._nb_words
        k_._suspicious = self._suspicious + other._suspicious

        return k_

    def _probe(self):

        for el in self._words:

            w_len = len(el)
            classification = UnicodeRangeIdentify.classification(el)

            c_ = 0

            is_latin_based = all(['Latin' in el for el in list(classification.keys())])

            if len(classification.keys()) > 1:
                for u_name, u_occ in classification.items():

                    if UnicodeRangeIdentify.is_range_secondary(u_name) is True:
                        c_ += u_occ

            c_el = HashableCounter(el)

            if (not is_latin_based and c_ > int(w_len / 4)) \
                    or (is_latin_based and len(el) >= 9 and c_el.most_common()[0][1] >= sum(c_el.values()) * 0.5) \
                    or (is_latin_based and c_ > int(w_len / 2)) \
                    or (UnicodeRangeIdentify.part_punc(el) > 0.4 and len(classification.keys()) > 1) \
                    or (not is_latin_based and UnicodeRangeIdentify.part_accent(el) > 0.4) \
                    or (not is_latin_based and len(el) > 10 and UnicodeRangeIdentify.part_lonely_range(el) > 0.3):
                self._suspicious.append(el)
            else:
                pass

    @property
    def ratio(self):
        return len(self._suspicious) / self._nb_words if self._nb_words >= 1 else 0.

