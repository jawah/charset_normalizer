import warnings
from encodings.aliases import aliases
from hashlib import sha256
from json import dumps
from typing import Optional, List, Tuple
from collections import Counter
from re import sub, compile

from charset_normalizer.md import mess_ratio


class CharsetMatch:
    def __init__(
            self,
            payload: bytes,
            guessed_encoding: str,
            mean_mess_ratio: float,
            has_sig_or_bom: bool,
            languages: "CoherenceMatches",
            unicode_ranges: List[str],
            decoded_payload: Optional[str] = None
    ):
        self._payload = payload  # type: bytes

        self._encoding = guessed_encoding  # type: str
        self._mean_mess_ratio = mean_mess_ratio  # type: float
        self._languages = languages  # type: CoherenceMatches
        self._has_sig_or_bom = has_sig_or_bom  # type: bool
        self._unicode_ranges = unicode_ranges  # type: List[str]

        self._leaves = []  # type: List[CharsetMatch]
        self._mean_coherence_ratio = 0.  # type: float

        self._output_payload = None  # type: Optional[bytes]
        self._output_encoding = None  # type: Optional[str]

        self._string = str(self._payload, self._encoding, "strict") if decoded_payload is None else decoded_payload  # type: str

    def __eq__(self, other) -> bool:
        if not isinstance(other, CharsetMatch):
            raise TypeError('__eq__ cannot be invoked on {} and {}.'.format(str(other.__class__), str(self.__class__)))
        return self.encoding == other.encoding and self.fingerprint == other.fingerprint

    def __lt__(self, other) -> bool:
        """
        Implemented to make sorted available upon CharsetMatches items.
        """
        if not isinstance(other, CharsetMatch):
            raise ValueError

        chaos_difference = abs(self.chaos - other.chaos)  # type: float

        # Bellow 1% difference --> Use Coherence
        if chaos_difference < 0.01:
            return self.coherence > other.coherence

        return self.chaos < other.chaos

    @property
    def chaos_secondary_pass(self) -> float:
        """
        Check once again chaos in decoded text, except this time, with full content.
        Use with caution, this can be very slow.
        Notice: Will be removed in 3.0
        """
        warnings.warn("chaos_secondary_pass is deprecated and will be removed in 3.0", DeprecationWarning)
        return mess_ratio(
            self._string,
            1.
        )

    @property
    def coherence_non_latin(self) -> float:
        """
        Coherence ratio on the first non-latin language detected if ANY.
        Notice: Will be removed in 3.0
        """
        warnings.warn("coherence_non_latin is deprecated and will be removed in 3.0", DeprecationWarning)
        return 0.

    @property
    def w_counter(self) -> Counter:
        """
        Word counter instance on decoded text.
        Notice: Will be removed in 3.0
        """
        warnings.warn("w_counter is deprecated and will be removed in 3.0", DeprecationWarning)
        not_printable_pattern = compile(r'[0-9\W\n\r\t]+')
        string_printable_only = sub(not_printable_pattern, ' ', self._string.lower())

        return Counter(string_printable_only.split())

    def __str__(self) -> str:
        return self._string

    def __repr__(self) -> str:
        return "<CharsetMatch '{}' bytes({})>".format(self.encoding, self.fingerprint)

    def add_submatch(self, other: "CharsetMatch") -> None:
        if not isinstance(other, CharsetMatch) or other == self:
            raise ValueError("Unable to add instance <{}> as a submatch of a CharsetMatch".format(other.__class__))

        self._leaves.append(other)

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def encoding_aliases(self) -> List[str]:
        """
        Encoding name are known by many name, using this could help when searching for IBM855 when it's listed as CP855.
        """
        also_known_as = []  # type: List[str]
        for u, p in aliases.items():
            if self.encoding == u:
                also_known_as.append(p)
            elif self.encoding == p:
                also_known_as.append(u)
        return also_known_as

    @property
    def bom(self) -> bool:
        return self._has_sig_or_bom

    @property
    def byte_order_mark(self) -> bool:
        return self._has_sig_or_bom

    @property
    def languages(self) -> List[str]:
        """
        Return the complete list of possible languages found in decoded sequence.
        Usually not really useful.
        """
        return [e[0] for e in self._languages]

    @property
    def language(self) -> str:
        """
        Most probable language found in decoded sequence. If none were detected or inferred, the property will return
        "Unknown".
        """
        if not self._languages:
            return "Unknown"
        return self._languages[0][0]

    @property
    def chaos(self) -> float:
        return self._mean_mess_ratio

    @property
    def coherence(self) -> float:
        if not self._languages:
            return 0.
        return self._languages[0][1]

    @property
    def percent_chaos(self) -> float:
        return round(self.chaos * 100, ndigits=3)

    @property
    def percent_coherence(self) -> float:
        return round(self.coherence * 100, ndigits=3)

    @property
    def raw(self) -> bytes:
        """
        Original untouched bytes.
        """
        return self._payload

    @property
    def submatch(self) -> List["CharsetMatch"]:
        return self._leaves

    @property
    def has_submatch(self) -> bool:
        return len(self._leaves) > 0

    @property
    def alphabets(self) -> List[str]:
        return self._unicode_ranges

    @property
    def could_be_from_charset(self) -> List[str]:
        """
        The complete list of encoding that output the exact SAME str result and therefore could be the originating
        encoding.
        This list does include the encoding available in property 'encoding'.
        """
        return [self._encoding] + [m.encoding for m in self._leaves]

    def first(self) -> "CharsetMatch":
        """
        Kept for BC reasons. Will be removed in 3.0.
        """
        return self

    def best(self) -> "CharsetMatch":
        """
        Kept for BC reasons. Will be removed in 3.0.
        """
        return self

    def output(self, encoding: str = "utf_8") -> bytes:
        """
        Method to get re-encoded bytes payload using given target encoding. Default to UTF-8.
        Any errors will be simply ignored by the encoder NOT replaced.
        """
        if self._output_encoding is None or self._output_encoding != encoding:
            self._output_encoding = encoding
            self._output_payload = str(self).encode(encoding, "replace")

        return self._output_payload

    @property
    def fingerprint(self) -> str:
        """
        Retrieve the unique SHA256 computed using the transformed (re-encoded) payload. Not the original one.
        """
        return sha256(self.output()).hexdigest()


class CharsetMatches:
    """
    Container with every CharsetMatch items ordered by default from most probable to the less one.
    Act like a list(iterable)
    """
    def __init__(self, results: List[CharsetMatch] = None):
        self._results = sorted(results) if results else []  # type: List[CharsetMatch]

    def __iter__(self):
        for result in self._results:
            yield result

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._results[item]
        if isinstance(item, str):
            for result in self._results:
                if item == result.encoding:
                    return result
        raise KeyError

    def __len__(self) -> int:
        return len(self._results)

    def __contains__(self, item):
        if not isinstance(item, str):
            raise TypeError
        for result in self._results:
            if item in result.could_be_from_charset:
                return True
        return False

    def add(self, item: CharsetMatch) -> None:
        """
        Insert a single match. Will be inserted accordingly to preserve sort.
        Can be inserted as a submatch.
        """
        if not isinstance(item, CharsetMatch):
            raise ValueError
        for match in self._results:
            if match.fingerprint == item.fingerprint:
                match.add_submatch(item)
                return
        self._results.append(item)
        self._results = sorted(self._results)

    def best(self) -> Optional["CharsetMatch"]:
        """
        Simply return the first match. Strict equivalent to matches[0].
        """
        if not self._results:
            return None
        return self._results[0]

    def first(self) -> Optional["CharsetMatch"]:
        """
        Redundant method, call the method best(). Kept for BC reasons.
        """
        return self.best()


CoherenceMatch = Tuple[str, float]
CoherenceMatches = List[CoherenceMatch]


class CliDetectionResult:

    def __init__(self, path: str, encoding: str, encoding_aliases: List[str], alternative_encodings: List[str], language: str, alphabets: List[str], has_sig_or_bom: bool, chaos: float, coherence: float, unicode_path: Optional[str], is_preferred: bool):
        self.path = path
        self.unicode_path = unicode_path
        self.encoding = encoding
        self.encoding_aliases = encoding_aliases
        self.alternative_encodings = alternative_encodings
        self.language = language
        self.alphabets = alphabets
        self.has_sig_or_bom = has_sig_or_bom
        self.chaos = chaos
        self.coherence = coherence
        self.is_preferred = is_preferred

    @property
    def __dict__(self):
        return {
            'path': self.path,
            'encoding': self.encoding,
            'encoding_aliases': self.encoding_aliases,
            'alternative_encodings': self.alternative_encodings,
            'language': self.language,
            'alphabets': self.alphabets,
            'has_sig_or_bom': self.has_sig_or_bom,
            'chaos': self.chaos,
            'coherence': self.coherence,
            'unicode_path': self.unicode_path,
            'is_preferred': self.is_preferred
        }

    def to_json(self):
        return dumps(
            self.__dict__,
            ensure_ascii=True,
            indent=4
        )


CharsetNormalizerMatch = CharsetMatch
