import re
import statistics
from encodings.aliases import aliases
from os.path import basename, splitext
import collections

from cached_property import cached_property

from charset_normalizer.probe_coherence import ProbeCoherence
from charset_normalizer.probe_chaos import ProbeChaos


class CharsetNormalizerMatch:

    RE_PRINTABLE_LETTER = re.compile(r'[0-9\W\n\r\t]+')

    def __init__(self, b_content, guessed_source_encoding, chaos_ratio, ranges):
        """
        :param bytes b_content: Raw binary content
        :param str guessed_source_encoding: Guessed source encoding accessible by Python
        :param float chaos_ratio: Coefficient of previously detected mess in decoded content
        """

        self._raw = b_content
        self._encoding = guessed_source_encoding
        self._chaos_ratio = chaos_ratio

        self._string = str(self._raw, encoding=self._encoding).replace('\r', '')

        self.char_counter = collections.Counter(re.sub(CharsetNormalizerMatch.RE_PRINTABLE_LETTER, '', self._string.lower()))

        self.ranges = ranges

    @cached_property
    def w_counter(self):
        return collections.Counter(re.sub(CharsetNormalizerMatch.RE_PRINTABLE_LETTER, ' ', self._string.lower()).split())

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
        return [self.encoding]

    def __eq__(self, other):
        """
        :param CharsetNormalizerMatch other:
        :return:
        """
        return self.chaos == other.chaos and len(self.raw) == len(other.raw) and self.encoding == other.encoding

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
        :return:
        """
        return ProbeChaos(str(self))

    @property
    def encoding(self):
        """
        :return: Guessed possible/probable originating charset
        :rtype: str
        """
        return self._encoding

    @property
    def raw(self):
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
    def normalize(path, steps=10, chunk_size=512, threshold=0.09):
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
    def from_bytes(sequences, steps=10, chunk_size=512, threshold=0.09):
        """
        Take a sequence of bytes that could potentially be decoded to str and discard all obvious non supported
        charset encoding.
        :param bytearray sequences: Actual sequence of bytes to analyse
        :param float threshold: Maximum amount of chaos allowed on first pass
        :param int chunk_size: Size to extract and analyse in each step
        :param int steps: Number of steps
        :return: List of potential matches
        :rtype: CharsetNormalizerMatches
        """

        supported = aliases.items()
        tested = set()
        working = dict()

        maximum_length = len(sequences)

        for support in supported:
            k, p = support

            if p in tested:
                continue

            tested.add(p)

            try:
                str(sequences, encoding=p)
            except UnicodeDecodeError:
                continue
            except LookupError:
                continue

            chaos_measures = list()
            ranges_encountered_t = dict()
            decoded_len_t = 0

            for i in range(0, maximum_length, int(maximum_length / steps)):

                chunk = sequences[i:i + chunk_size]
                decoded = str(chunk, encoding=p, errors='ignore')

                probe_chaos = ProbeChaos(decoded)
                chaos_measure, ranges_encountered = probe_chaos.ratio, probe_chaos.encountered_unicode_range_occurrences

                for k, e in ranges_encountered.items():
                    if k not in ranges_encountered_t.keys():
                        ranges_encountered_t[k] = 0
                    ranges_encountered_t[k] += e

                if chaos_measure > threshold:
                    if p in working.keys():
                        del working[p]
                    break

                chaos_measures.append(chaos_measure)

                if p not in working.keys():
                    working[p] = dict()

            if p in working.keys():
                working[p]['ratio'] = statistics.mean(chaos_measures)
                working[p]['ranges'] = ranges_encountered_t
                working[p]['chaos'] = sum(chaos_measures)
                working[p]['len'] = decoded_len_t

            if p == 'ascii' and working[p]['ratio'] == 0.:
                break

        return CharsetNormalizerMatches(
            [CharsetNormalizerMatch(sequences, enc, working[enc]['ratio'], working[enc]['ranges']) for enc in
             working.keys() if working[enc]['ratio'] <= threshold])

    @staticmethod
    def from_fp(fp, steps=10, chunk_size=512, threshold=0.09):
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
    def from_path(path, steps=10, chunk_size=512, threshold=0.09):
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

            if len(match.alphabets) != 1 or match.alphabets[0] != 'Latin de base':
                all_latin_basic = False

        if all_latin_basic is True:
            return CharsetNormalizerMatches(match_per_frequency_letter[lowest_ratio_frequency]).first()

        return CharsetNormalizerMatches(match_per_frequency_letter[lowest_ratio_frequency]) if len(match_per_frequency_letter[lowest_ratio_frequency]) > 1 else CharsetNormalizerMatches(match_per_frequency_letter[lowest_ratio_frequency]).first()
