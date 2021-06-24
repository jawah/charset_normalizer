from hashlib import sha256
from json import dumps
from typing import Optional, List, Tuple


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
        self._payload: bytes = payload

        self._encoding: str = guessed_encoding
        self._mean_mess_ratio: float = mean_mess_ratio
        self._languages: "CoherenceMatches" = languages
        self._has_sig_or_bom: bool = has_sig_or_bom
        self._unicode_ranges: List[str] = unicode_ranges

        self._leaves: List["CharsetMatch"] = []
        self._mean_coherence_ratio: float = 0.

        self._output_payload: Optional[bytes] = None
        self._output_encoding: Optional[str] = None

        self._string: str = str(self._payload, self._encoding, "strict") if decoded_payload is None else decoded_payload

    def __eq__(self, other) -> bool:
        if not isinstance(other, CharsetMatch):
            raise TypeError('__eq__ cannot be invoked on {} and {}.'.format(str(other.__class__), str(self.__class__)))
        return self.encoding == other.encoding

    def __lt__(self, other) -> bool:
        if not isinstance(other, CharsetMatch):
            raise ValueError

        chaos_difference: float = abs(self.chaos - other.chaos)

        # Bellow 1% difference --> Use Coherence
        if chaos_difference < 0.01:
            return self.coherence > other.coherence

        return self.chaos < other.chaos

    def __str__(self) -> str:
        return self._string

    def add_submatch(self, other: "CharsetMatch") -> None:
        if not isinstance(other, CharsetMatch):
            raise ValueError

        self._leaves.append(other)

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def encoding_aliases(self) -> List[str]:
        pass

    @property
    def bom(self) -> bool:
        return self._has_sig_or_bom

    @property
    def byte_order_mark(self) -> bool:
        return self._has_sig_or_bom

    @property
    def languages(self) -> List[str]:
        return [e[0] for e in self._languages]

    @property
    def language(self) -> str:
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
        return [self._encoding] + [m.encoding for m in self._leaves]

    def first(self) -> "CharsetMatch":
        return self

    def best(self) -> "CharsetMatch":
        return self

    def output(self, encoding: str = "utf_8") -> bytes:
        if self._output_encoding is None or self._output_encoding != encoding:
            self._output_encoding = encoding
            self._output_payload = str(self).encode(encoding, "replace")

        return self._output_payload

    @property
    def fingerprint(self) -> str:
        return sha256(self.output()).hexdigest()


class CharsetMatches:
    def __init__(self, results: List[CharsetMatch] = None):
        self._results: List[CharsetMatch] = sorted(results) if results else []

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
        if not isinstance(item, CharsetMatch):
            raise ValueError
        for match in self._results:
            if match.fingerprint == item.fingerprint:
                match.add_submatch(item)
                return
        self._results.append(item)
        self._results = sorted(self._results)

    def best(self) -> Optional["CharsetMatch"]:
        if not self._results:
            return None
        return self._results[0]

    def first(self) -> Optional["CharsetMatch"]:
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
