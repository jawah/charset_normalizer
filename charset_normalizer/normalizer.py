# coding: utf-8
import collections
import re
import statistics
from encodings.aliases import aliases
from os.path import basename, splitext
from sys import version_info
from warnings import warn

from cached_property import cached_property

from charset_normalizer.constant import BYTE_ORDER_MARK
from charset_normalizer.probe_chaos import ProbeChaos
from charset_normalizer.probe_coherence import ProbeCoherence, HashableCounter

from charset_normalizer.encoding import is_multi_byte_encoding

from charset_normalizer.probe_inherent_sign import any_specified_encoding

from loguru import logger

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

    @property
    def has_submatch(self):
        """
        Determine if current match has any other match linked to it.
        :return: True if any sub match available
        :rtype: bool
        """
        return len(self._submatch) > 0

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
        if not isinstance(other, CharsetNormalizerMatch):
            raise TypeError('__eq__ cannot be invoked on {} and {}.'.format(str(other.__class__), str(self.__class__)))
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

    @property
    def percent_chaos(self):
        """
        Convert chaos ratio to readable percentage with ndigits=3
        from 0.000 % to 100.000 %
        :return: float
        """
        return round(self._chaos_ratio * 100, ndigits=3)

    @property
    def percent_coherence(self):
        """
        Convert coherence ratio to readable percentage with ndigits=3
        from 0.000 % to 100.000 %
        :return: float
        :rtype: float
        """
        return round((1 - self.coherence) * 100, ndigits=3)

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
        return str(self).encode(encoding, 'replace')


class CharsetNormalizerMatches:

    def __init__(self, matches):
        """
        :param list[CharsetNormalizerMatch] matches:
        """
        self._matches = matches

        if len(self) > 1 and 'utf_8' in self.could_be_from_charset:

            u8_index = self.could_be_from_charset.index('utf_8')

            # Put UTF_8 at the beginning if not already the case
            if u8_index > 0:
                self._matches.insert(1, self._matches.pop(u8_index))

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
    def from_bytes(sequences, steps=10, chunk_size=512, threshold=0.20, cp_isolation=None, cp_exclusion=None, preemptive_behaviour=True, explain=False):
        """
        Take a sequence of bytes that could potentially be decoded to str and discard all obvious non supported
        charset encoding.
        Will test input like this (with steps=4 & chunk_size=4) --> [####     ####     ####     ####]
        :param bytes sequences: Actual sequence of bytes to analyse
        :param float threshold: Maximum amount of chaos allowed on first pass
        :param int chunk_size: Size to extract and analyse in each step
        :param int steps: Number of steps/block to extract from sequence
        :param bool preemptive_behaviour: Determine if we should look into sequence (ASCII-Mode) for pre-defined encoding
        :param bool explain: Print on screen what is happening when searching for a match
        :param list[str] cp_isolation: Finite list of encoding to use when searching for a match
        :param list[str] cp_exclusion: Finite list of encoding to avoid when searching for a match
        :return: List of potential matches
        :rtype: CharsetNormalizerMatches
        """
        if not explain:
            logger.disable('charset_normalizer')

        if len(sequences) == 0:
            return CharsetNormalizerMatch(
                sequences,
                'utf-8',
                0.,
                {}
            )

        too_small_sequence = len(sequences) < 24

        if too_small_sequence is True:
            warn('Trying to detect encoding from a tiny portion of ({}) bytes.'.format(len(sequences)))

        maximum_length = len(sequences)

        # Adjust steps and chunk_size when content is just too small for it
        if maximum_length <= (chunk_size * steps):
            logger.warning(
                'override steps and chunk_size as content does not fit parameters.',
                chunk_size=chunk_size, steps=steps, seq_len=maximum_length)
            steps = 1
            chunk_size = maximum_length

        if steps > 1 and maximum_length / steps < chunk_size:
            chunk_size = int(maximum_length / steps)

        if cp_isolation is not None and isinstance(cp_isolation, list) is False:
            raise TypeError('cp_isolation must be None or list')

        if cp_exclusion is not None and isinstance(cp_exclusion, list) is False:
            raise TypeError('cp_exclusion must be None or list')

        if cp_isolation is not None:
            logger.warning('cp_isolation is set. use this flag for debugging purpose. '
                           'limited list of encoding allowed : {allowed_list}.',
                           allowed_list=', '.join(cp_isolation))

        if cp_exclusion is not None:
            logger.warning(
                'cp_exclusion is set. use this flag for debugging purpose. '
                'limited list of encoding excluded : {excluded_list}.',
                excluded_list=', '.join(cp_exclusion))

        # Bellow Python 3.6, Expect dict to not behave the same.
        py_v = [int(el) for el in (version_info.major, version_info.minor, version_info.micro,)]
        py_need_sort = py_v[0] < 3 or (py_v[0] == 3 and py_v[1] < 6)

        supported = collections.OrderedDict(aliases).items() if py_need_sort else aliases.items()

        tested = set()
        matches = list()

        specified_encoding = any_specified_encoding(sequences) if preemptive_behaviour is True else None

        if specified_encoding is not None:
            warn(
                'Trying to detect encoding on a sequence that seems to declare a encoding ({}).'.format(specified_encoding)
            )

        for support in supported:

            k, p = support

            if cp_isolation is not None and p not in cp_isolation:
                continue

            if cp_exclusion is not None and p in cp_exclusion:
                continue

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
                    if bom_available is True:
                        logger.info('{encoding} has a SIG or BOM mark on first {n_byte} byte(s).  Adding chaos bonus.', encoding=p, n_byte=bom_len)

                str(
                    sequences if bom_available is False else sequences[bom_len:],
                    encoding=p
                )

            except UnicodeDecodeError as e:
                logger.debug('{encoding} does not fit given bytes sequence at ALL. {explanation}', encoding=p, explanation=str(e))
                continue
            except LookupError:
                continue

            is_multi_byte_enc = is_multi_byte_encoding(p)

            if is_multi_byte_enc is True:
                logger.info('{encoding} is a multi byte encoding table. '
                            'Should not be a coincidence. Adding chaos bonus.',
                            encoding=p)
            else:
                logger.debug('{encoding} is a single byte encoding table.', encoding=p)

            r_ = range(
                0 if bom_available is False else bom_len,
                maximum_length,
                int(maximum_length / steps)
            )

            measures = [ProbeChaos(str(sequences[i:i + chunk_size], encoding=p, errors='ignore'), giveup_threshold=threshold, bonus_bom_sig=bom_available, bonus_multi_byte=is_multi_byte_enc) for i in r_]
            ratios = [el.ratio for el in measures]
            nb_gave_up = [el.gave_up is True or el.ratio >= threshold for el in measures].count(True)

            if len(ratios) == 0:
                logger.warning('{encoding} was excluded because no measure can be done on sequence. ',
                               encoding=p)
                continue

            chaos_means = statistics.mean(ratios)
            chaos_median = statistics.median(ratios)
            # chaos_min = min(ratios)
            # chaos_max = max(ratios)

            if (len(r_) >= 4 and nb_gave_up > len(r_) / 4) or chaos_means > threshold:
                logger.warning('{encoding} was excluded because of initial chaos probing. '
                                      'Gave up {nb_gave_up} time(s). '
                                      'Computed median chaos is {chaos_median} %.',
                                      encoding=p,
                                      nb_gave_up=nb_gave_up,
                                      chaos_median=round(chaos_means*100, ndigits=3))
                continue

            encountered_unicode_range_occurrences = dict()

            for el in measures:
                for u_name, u_occ in el.encountered_unicode_range_occurrences.items():
                    if u_name not in encountered_unicode_range_occurrences.keys():
                        encountered_unicode_range_occurrences[u_name] = 0
                    encountered_unicode_range_occurrences[u_name] += u_occ

            cnm = CharsetNormalizerMatch(
                sequences if not bom_available else sequences[bom_len:],
                p,
                chaos_means,
                encountered_unicode_range_occurrences,
                bom_available
            )

            logger.info(
                '{encoding} passed initial chaos probing. '
                'Measured chaos is {chaos_means} % and coherence is {coherence} %. '
                'It seems to be written in {language}.',
                encoding=p,
                chaos_means=round(chaos_means*100, ndigits=3),
                coherence=cnm.percent_coherence,
                language=cnm.languages
            )

            fingerprint_tests = [el.fingerprint == cnm.fingerprint for el in matches]

            if any(fingerprint_tests) is True:
                matches[fingerprint_tests.index(True)].submatch.append(cnm)
                logger.debug('{encoding} is marked as a submatch of {primary_encoding}.', encoding=cnm.encoding, primary_encoding=matches[fingerprint_tests.index(True)].encoding)
            else:
                matches.append(
                    cnm
                )

            if specified_encoding is not None and p == specified_encoding:
                logger.info('{encoding} is most likely the one. '
                            'Because it is specified in analysed byte sequence and '
                            'initial test passed successfully. '
                            'Disable this behaviour by setting preemptive_behaviour '
                            'to False', encoding=specified_encoding)
                return CharsetNormalizerMatches([cnm]) if any(fingerprint_tests) is False else CharsetNormalizerMatches([matches[fingerprint_tests.index(True)]])

            if (p == 'ascii' and chaos_median == 0.) or bom_available is True:
                logger.info('{encoding} is most likely the one. {bom_available}',
                                   encoding=p,
                                   bom_available='BOM/SIG available' if bom_available else '')

                return CharsetNormalizerMatches([matches[-1]])

        return CharsetNormalizerMatches(matches)

    @staticmethod
    def from_fp(fp, steps=10, chunk_size=512, threshold=0.20, cp_isolation=None, cp_exclusion=None, preemptive_behaviour=True, explain=False):
        """
        :param io.BinaryIO fp:
        :param int steps:
        :param int chunk_size:
        :param float threshold:
        :param bool explain: Print on screen what is happening when searching for a match
        :param bool preemptive_behaviour: Determine if we should look into sequence (ASCII-Mode) for pre-defined encoding
        :param list[str] cp_isolation: Finite list of encoding to use when searching for a match
        :param list[str] cp_exclusion: Finite list of encoding to avoid when searching for a match
        :return: List of potential matches
        :rtype: CharsetNormalizerMatches
        """
        return CharsetNormalizerMatches.from_bytes(
            bytearray(fp.read()),
            steps,
            chunk_size,
            threshold,
            cp_isolation,
            cp_exclusion,
            preemptive_behaviour,
            explain
        )

    @staticmethod
    def from_path(path, steps=10, chunk_size=512, threshold=0.20, cp_isolation=None, cp_exclusion=None, preemptive_behaviour=True, explain=False):
        """
        :param str path:
        :param int steps:
        :param int chunk_size:
        :param float threshold:
        :param bool preemptive_behaviour: Determine if we should look into sequence (ASCII-Mode) for pre-defined encoding
        :param bool explain: Print on screen what is happening when searching for a match
        :param list[str] cp_isolation: Finite list of encoding to use when searching for a match
        :param list[str] cp_exclusion: Finite list of encoding to avoid when searching for a match
        :return: List of potential matches
        :rtype: CharsetNormalizerMatches
        """
        with open(path, 'rb') as fp:
            return CharsetNormalizerMatches.from_fp(fp, steps, chunk_size, threshold, cp_isolation, cp_exclusion, preemptive_behaviour, explain)

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

        if len(self) == 0:
            logger.error('Trying to call best() on empty CharsetNormalizerMatches, that is sad.')
            return CharsetNormalizerMatches(self._matches)
        elif len(self) == 1:
            logger.debug('best() is not required because there is only one match in it.')
            return CharsetNormalizerMatches(self._matches)

        logger.info('We need to choose between {nb_suitable_match} match. Order By Chaos Then Coherence.', nb_suitable_match=len(self))

        sorted_matches = sorted(self._matches, key=lambda x: x.chaos)

        nb_lowest_ratio = [el.chaos <= sorted_matches[0].chaos * 1.2 for el in sorted_matches[1:]].count(True)

        logger.info('Lowest Chaos found is {lowest_chaos} %. Reduced list to {nb_suitable_match} match.', lowest_chaos=sorted_matches[0].percent_chaos, nb_suitable_match=nb_lowest_ratio+1)

        if nb_lowest_ratio+1 > 1:
            logger.info('Order By Chaos is not enough, {nb_suitable_match} remaining. Next, ordering by Coherence.', nb_suitable_match=nb_lowest_ratio+1)

            sorted_matches_second_pass = sorted(sorted_matches[:nb_lowest_ratio+1], key=lambda x: x.coherence)
            nb_lowest_ratio = [el.coherence == sorted_matches_second_pass[0].coherence for el in sorted_matches_second_pass[1:]].count(True)

            logger.info('Highest Coherence found is {lowest_chaos} %. Reduced list to {nb_suitable_match} match.', lowest_chaos=sorted_matches_second_pass[0].percent_coherence, nb_suitable_match=nb_lowest_ratio+1)

            return CharsetNormalizerMatches(
                sorted_matches_second_pass[:nb_lowest_ratio+1]
            )

        return CharsetNormalizerMatches(
            sorted_matches[:nb_lowest_ratio+1]
        )


# Some aliases to CharsetNormalizerMatches, because it is too long for a class name.
CharsetDetector = CharsetNormalizerMatches
EncodingDetector = CharsetNormalizerMatches
CharsetDoctor = CharsetNormalizerMatches
