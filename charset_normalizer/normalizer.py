# coding: utf-8
import collections
import re
import statistics
from encodings.aliases import aliases
from os.path import basename, splitext
from platform import python_version_tuple

from cached_property import cached_property

from charset_normalizer.constant import BYTE_ORDER_MARK
from charset_normalizer.probe_chaos import ProbeChaos
from charset_normalizer.probe_coherence import ProbeCoherence, HashableCounter


from hashlib import sha256


class CharsetNormalizerMatch:

    RE_NOT_PRINTABLE_LETTER = re.compile(r'[0-9\W\n\r\t]+')

    def __init__(self, b_content, guessed_source_encoding, chaos_ratio, ranges, has_bom=False, submatch=None):
        """
        :param bytes b_content: Raw binary content
        :param str guessed_source_encoding: Guessed source encoding accessible by Python
        :param float chaos_ratio: Coefficient of previously detected mess in decoded content
        :param list[CharsetNormalizerMatch] submatch: list of submatch that produce the EXACT same output as this one
        """

        self._raw = b_content
        self._encoding = guessed_source_encoding
        self._chaos_ratio = chaos_ratio

        self._bom = has_bom
        self._string = str(self._raw, encoding=self._encoding).replace('\r', '')

        self._string_printable_only = re.sub(CharsetNormalizerMatch.RE_NOT_PRINTABLE_LETTER, ' ', self._string.lower())
        self.char_counter = HashableCounter(self._string_printable_only.replace(' ', ''))

        self.ranges = ranges

        self._submatch = submatch or list()  # type: list[CharsetNormalizerMatch]

    @cached_property
    def w_counter(self):
        """
        By 'word' we consider output of split() method *with no args*
        :return: For each 'word' in string, associated occurrence as provided by collection.Counter
        :rtype: collections.Counter
        """
        return collections.Counter(self._string_printable_only.split())

    @property
    def submatch(self):
        """
        Return a list of submatch that produce the EXACT same output as this one.
        This return a list of CharsetNormalizerMatch and NOT a CharsetNormalizerMatches
        :return: list of submatch
        :rtype: list[CharsetNormalizerMatch]
        """
        return self._submatch

    @cached_property
    def alphabets(self):
        """
        Discover list of alphabet in decoded content
        :return: List of alphabet
        :rtype: list[str]
        """
        return list(self.ranges.keys())

    @cached_property
    def could_be_from_charset(self):
        """
        Return list of possible originating charset
        :return: list of encoding
        :rtype: list[str]
        """
        return [self.encoding] + [el.encoding for el in self._submatch]

    def __eq__(self, other):
        """
        :param CharsetNormalizerMatch other:
        :return:
        """
        return self.fingerprint == other.fingerprint and self.encoding == other.encoding

    @cached_property
    def coherence(self):
        """
        Return a value between 0. and 1.
        Closest to 0. means that the initial string is considered coherent,
        Closest to 1. means that the initial string SEEMS NOT coherent.
        :return: Ratio as floating number
        :rtype: float
        """
        return ProbeCoherence(self.char_counter).ratio

    @cached_property
    def coherence_non_latin(self):
        return ProbeCoherence(self.char_counter).non_latin_covered_any

    @cached_property
    def languages(self):
        """
        Return a list of probable language in text
        :return: List of language
        :rtype: list[str]
        """
        return ProbeCoherence(self.char_counter).most_likely

    @cached_property
    def language(self):
        """
        Return the most probable language found in text
        :return: Most used/probable language in text
        :rtype: str
        """
        probe_coherence = ProbeCoherence(self.char_counter)
        languages = probe_coherence.most_likely

        if len(languages) == 0:
            return 'English' if len(self.alphabets) == 1 and self.alphabets[0] == 'Basic Latin' else 'Unknown'

        return languages[0]

    @cached_property
    def chaos(self):
        """
        Return a value between 0. and 1.
        Closest to 1. means that the initial string is considered as chaotic,
        Closest to 0. means that the initial string SEEMS NOT chaotic.
        :return: Ratio as floating number
        :rtype: float
        """
        return self._chaos_ratio

    @cached_property
    def chaos_secondary_pass(self):
        """
        Check once again chaos in decoded text, except this time, with full content.
        :return: Same as chaos property expect it's about all content
        :rtype: float
        """
        return ProbeChaos(str(self)).ratio

    @property
    def encoding(self):
        """
        :return: Guessed possible/probable originating charset
        :rtype: str
        """
        return self._encoding

    @property
    def encoding_aliases(self):
        """
        Encoding name are known by many name, using this could help when searching for IBM855 when it's listed as CP855.
        :return: List of encoding aliases
        :rtype: list[str]
        """
        also_known_as = list()
        for u, p in aliases.items():
            if self.encoding == u:
                also_known_as.append(p)
            elif self.encoding == p:
                also_known_as.append(u)
        return also_known_as

    @property
    def bom(self):
        """
        Precise if file has a valid bom or sig associated with discovered encoding
        :return: True if a byte order mark or sig was discovered
        :rtype: bool
        """
        return self._bom

    @property
    def byte_order_mark(self):
        """
        Precise if file has a valid bom associated with discovered encoding
        :return: True if a byte order mark was discovered
        :rtype: bool
        """
        return self.bom

    @property
    def raw(self):
        """
        Get untouched bytes content
        :return: Original bytes sequence
        :rtype: bytes
        """
        return self._raw

    def first(self):
        """
        Just in case
        :return: himself
        :rtype: CharsetNormalizerMatch
        """
        return self

    def best(self):
        """
        Just in case
        :return: himself
        :rtype: CharsetNormalizerMatch
        """
        return self

    def __str__(self):
        return self._string

    @cached_property
    def fingerprint(self):
        """
        Generate sha256 checksum of encoded unicode self
        :return:
        """
        return sha256(self.output()).hexdigest()

    def output(self, encoding='utf-8'):
        """
        :param encoding:
        :return:
        :rtype: bytes
        """
        return str(self).encode(encoding)


class CharsetNormalizerMatches:

    def __init__(self, matches):
        """
        :param list[CharsetNormalizerMatch] matches:
        """
        self._matches = matches

    def __iter__(self):
        for elem in self._matches:
            yield elem

    def __getitem__(self, item):
        if not isinstance(item, int):
            raise KeyError
        return self._matches[item]

    def __len__(self):
        return len(self._matches)

    @staticmethod
    def normalize(path, steps=10, chunk_size=512, threshold=0.20):
        """
        :param str path:
        :param int steps:
        :param int chunk_size:
        :param float threshold:
        :return:
        """

        matches = CharsetNormalizerMatches.from_path(
            path,
            steps,
            chunk_size,
            threshold
        )

        b_name = basename(path)
        b_name_ext = list(splitext(b_name))

        if len(matches) == 0:
            raise IOError('Unable to normalize "{}", no encoding charset seems to fit.'.format(b_name))

        b_ = matches.best().first()

        b_name_ext[0] += '-' + b_.encoding

        with open('{}'.format(path.replace(b_name, ''.join(b_name_ext))), 'w', encoding='utf_8') as fp:
            fp.write(str(b_))

        return b_

    @staticmethod
    def from_bytes(sequences, steps=10, chunk_size=512, threshold=0.20):
        """
        Take a sequence of bytes that could potentially be decoded to str and discard all obvious non supported
        charset encoding.
        Will test input like this (with steps=4 & chunk_size=4) --> [####     ####     ####     ####]
        :param bytes sequences: Actual sequence of bytes to analyse
        :param float threshold: Maximum amount of chaos allowed on first pass
        :param int chunk_size: Size to extract and analyse in each step
        :param int steps: Number of steps
        :return: List of potential matches
        :rtype: CharsetNormalizerMatches
        """
        py_v = [int(el) for el in python_version_tuple()]
        py_need_sort = py_v[0] < 3 or (py_v[0] == 3 and py_v[1] < 6)

        supported = sorted(aliases.items()) if py_need_sort else aliases.items()

        tested = set()
        matches = list()

        maximum_length = len(sequences)

        if maximum_length <= chunk_size:
            chunk_size = maximum_length
            steps = 1

        for support in supported:

            k, p = support

            if p in tested:
                continue

            tested.add(p)

            bom_available = False
            bom_len = None

            try:
                if p in BYTE_ORDER_MARK.keys():

                    if isinstance(BYTE_ORDER_MARK[p], bytes) and sequences.startswith(BYTE_ORDER_MARK[p]):
                        bom_available = True
                        bom_len = len(BYTE_ORDER_MARK[p])
                    elif isinstance(BYTE_ORDER_MARK[p], list):
                        bom_c_list = [sequences.startswith(el) for el in BYTE_ORDER_MARK[p]]
                        if any(bom_c_list) is True:
                            bom_available = True
                            bom_len = len(BYTE_ORDER_MARK[p][bom_c_list.index(True)])

                str(
                    sequences if bom_available is False else sequences[bom_len:],
                    encoding=p
                )

            except UnicodeDecodeError:
                continue
            except LookupError:
                continue

            r_ = range(
                0 if bom_available is False else bom_len,
                maximum_length,
                int(maximum_length / steps)
            )

            measures = [ProbeChaos(str(sequences[i:i + chunk_size], encoding=p, errors='ignore'), giveup_threshold=threshold) for i in r_]
            ratios = [el.ratio for el in measures]
            nb_gave_up = [el.gave_up is True or el.ratio >= threshold for el in measures].count(True)

            chaos_means = statistics.mean(ratios)
            chaos_median = statistics.median(ratios)
            # chaos_min = min(ratios)
            # chaos_max = max(ratios)

            if (len(r_) >= 4 and nb_gave_up > len(r_) / 4) or chaos_median > threshold:
                # print(p, 'is too much chaos for decoded input !')
                continue

            encountered_unicode_range_occurrences = dict()

            for el in measures:
                for u_name, u_occ in el.encountered_unicode_range_occurrences.items():
                    if u_name not in encountered_unicode_range_occurrences.keys():
                        encountered_unicode_range_occurrences[u_name] = 0
                    encountered_unicode_range_occurrences[u_name] += u_occ

            # print(p, 'U RANGES', encountered_unicode_range_occurrences)

            cnm = CharsetNormalizerMatch(
                sequences if not bom_available else sequences[bom_len:],
                p,
                chaos_means,
                encountered_unicode_range_occurrences,
                bom_available
            )

            fingerprint_tests = [el.fingerprint == cnm.fingerprint for el in matches]

            if any(fingerprint_tests) is True:
                matches[fingerprint_tests.index(True)].submatch.append(cnm)
            else:
                matches.append(
                    CharsetNormalizerMatch(
                        sequences if not bom_available else sequences[bom_len:],
                        p,
                        chaos_means,
                        encountered_unicode_range_occurrences,
                        bom_available
                    )
                )

            # print(p, nb_gave_up, chaos_means, chaos_median, chaos_min, chaos_max, matches[-1].coherence, matches[-1].languages,)

            if (p == 'ascii' and chaos_median == 0.) or bom_available is True:
                return CharsetNormalizerMatches([matches[-1]])

        return CharsetNormalizerMatches(matches)

    @staticmethod
    def from_fp(fp, steps=10, chunk_size=512, threshold=0.20):
        """
        :param io.BinaryIO fp:
        :param int steps:
        :param int chunk_size:
        :param float threshold:
        :return:
        """
        return CharsetNormalizerMatches.from_bytes(
            bytearray(fp.read()),
            steps,
            chunk_size,
            threshold
        )

    @staticmethod
    def from_path(path, steps=10, chunk_size=512, threshold=0.20):
        """
        :param str path:
        :param int steps:
        :param int chunk_size:
        :param float threshold:
        :return:
        """
        with open(path, 'rb') as fp:
            return CharsetNormalizerMatches.from_fp(fp, steps, chunk_size, threshold)

    @cached_property
    def could_be_from_charset(self):
        """
        Return list of possible originating charset
        :return: list of encoding
        :rtype: list[str]
        """
        return [el.encoding for el in self._matches]

    def first(self):
        """
        Select first match available
        :return: first match available
        :rtype: CharsetNormalizerMatch or None
        """
        return self._matches[0] if len(self._matches) > 0 else None

    def best(self):
        """
        Keep only the matches with the lowest ratio of chaos and check eventually for coherence to keep the best of the
        best matches.
        :return: Single match or list of matches
        :rtype: CharsetNormalizerMatches | CharsetNormalizerMatch
        """

        lowest_ratio = None
        lowest_ratio_frequency = None

        match_per_ratio = dict()
        match_per_frequency_letter = dict()

        for match in self._matches:

            if match.chaos not in match_per_ratio.keys():
                match_per_ratio[match.chaos] = list()

            match_per_ratio[match.chaos].append(match)

            if lowest_ratio is None or lowest_ratio > match.chaos:
                lowest_ratio = match.chaos

        if lowest_ratio is None:
            return CharsetNormalizerMatches([])

        all_latin_basic = True

        for match in match_per_ratio[lowest_ratio]:  # type: CharsetNormalizerMatch
            secondary_ratio = match.coherence

            if lowest_ratio_frequency is None or lowest_ratio_frequency > secondary_ratio:
                lowest_ratio_frequency = secondary_ratio

            if secondary_ratio not in match_per_frequency_letter.keys():
                match_per_frequency_letter[secondary_ratio] = list()

            match_per_frequency_letter[secondary_ratio].append(match)

            if len(match.alphabets) != 1 or match.alphabets[0] != 'Basic Latin':
                all_latin_basic = False

        if all_latin_basic is True:
            return CharsetNormalizerMatches(match_per_frequency_letter[lowest_ratio_frequency]).first()

        return CharsetNormalizerMatches(match_per_frequency_letter[lowest_ratio_frequency]) if len(match_per_frequency_letter[lowest_ratio_frequency]) > 1 else CharsetNormalizerMatches(match_per_frequency_letter[lowest_ratio_frequency]).first()
