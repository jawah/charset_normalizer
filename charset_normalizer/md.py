from functools import lru_cache
from typing import Optional, List

from charset_normalizer.constant import UNICODE_SECONDARY_RANGE_KEYWORD
from charset_normalizer.utils import is_punctuation, is_symbol, unicode_range, is_accentuated, is_latin, \
    remove_accent, is_separator


class MessDetectorPlugin:

    def eligible(self, character: str) -> bool:
        raise NotImplementedError

    def feed(self, character: str) -> None:
        raise NotImplementedError

    def reset(self) -> None:
        raise NotImplementedError

    @property
    def ratio(self) -> float:
        raise NotImplementedError


class TooManySymbolOrPunctuationPlugin(MessDetectorPlugin):

    def __init__(self):
        self._punctuation_count: int = 0
        self._symbol_count: int = 0
        self._character_count: int = 0

        self._last_printable_char: Optional[str] = None
        self._frenzy_symbol_in_word: bool = False

    def eligible(self, character: str) -> bool:
        return character.isprintable()

    def feed(self, character: str) -> None:
        self._character_count += 1

        if character != self._last_printable_char and character not in ["<", ">", "=", ":", "/", "&", ";"]:
            if is_punctuation(character):
                self._punctuation_count += 1
            elif character.isdigit() is False and is_symbol(character):
                self._symbol_count += 2

        self._last_printable_char = character

    def reset(self) -> None:
        self._punctuation_count = 0
        self._character_count = 0
        self._symbol_count = 0

    @property
    def ratio(self) -> float:
        if self._character_count == 0:
            return 0.

        ratio_of_punctuation: float = (self._punctuation_count + self._symbol_count) / self._character_count

        return ratio_of_punctuation if ratio_of_punctuation >= 0.3 else 0.


class TooManyAccentuatedPlugin(MessDetectorPlugin):

    def __init__(self):
        self._character_count: int = 0
        self._accentuated_count: int = 0

    def eligible(self, character: str) -> bool:
        return character.isalpha()

    def feed(self, character: str) -> None:
        self._character_count += 1

        if is_accentuated(character):
            self._accentuated_count += 1

    def reset(self) -> None:
        self._character_count = 0
        self._accentuated_count = 0

    @property
    def ratio(self) -> float:
        if self._character_count == 0:
            return 0.
        ratio_of_accentuation: float = self._accentuated_count / self._character_count
        return ratio_of_accentuation if ratio_of_accentuation >= 0.35 else 0.


class UnprintablePlugin(MessDetectorPlugin):

    def __init__(self):
        self._unprintable_count: int = 0
        self._character_count: int = 0

    def eligible(self, character: str) -> bool:
        return True

    def feed(self, character: str) -> None:
        if character not in {'\n', '\t', '\r'} and character.isprintable() is False:
            self._unprintable_count += 1
        self._character_count += 1

    def reset(self) -> None:
        self._unprintable_count = 0

    @property
    def ratio(self) -> float:
        if self._character_count == 0:
            return 0.

        ratio_of_unprintable: float = (self._unprintable_count * 8) / self._character_count

        return ratio_of_unprintable


class SuspiciousDuplicateAccentPlugin(MessDetectorPlugin):

    def __init__(self):
        self._successive_count: int = 0
        self._character_count: int = 0

        self._last_latin_character: Optional[str] = None

    def eligible(self, character: str) -> bool:
        return is_latin(character)

    def feed(self, character: str) -> None:
        if self._last_latin_character is not None:
            if is_accentuated(character) and is_accentuated(self._last_latin_character):
                if remove_accent(character) == remove_accent(self._last_latin_character):
                    self._successive_count += 1
        self._last_latin_character = character

    def reset(self) -> None:
        self._successive_count = 0
        self._character_count = 0
        self._last_latin_character = 0

    @property
    def ratio(self) -> float:
        if self._character_count == 0:
            return 0.
        ratio_of_successive_accent_same_char: float = (self._successive_count * 2) / self._character_count

        return ratio_of_successive_accent_same_char


class SuspiciousRange(MessDetectorPlugin):

    def __init__(self):
        self._suspicious_successive_range_count: int = 0
        self._character_count: int = 0
        self._last_printable_seen: Optional[str] = None

    def eligible(self, character: str) -> bool:
        return character.isprintable()

    def feed(self, character: str) -> None:
        self._character_count += 1

        if self._last_printable_seen is None:
            self._last_printable_seen = character
            return

        if character.isspace() or is_punctuation(character):
            self._last_printable_seen = None
            return

        unicode_range_a: str = unicode_range(self._last_printable_seen)
        unicode_range_b: str = unicode_range(character)

        if is_suspiciously_successive_range(unicode_range_a, unicode_range_b):
            self._suspicious_successive_range_count += 1

        self._last_printable_seen = character

    def reset(self) -> None:
        self._character_count = 0
        self._suspicious_successive_range_count = 0
        self._last_printable_seen = None

    @property
    def ratio(self) -> float:
        if self._character_count == 0:
            return 0.

        ratio_of_suspicious_range_usage: float = (self._suspicious_successive_range_count * 2) / self._character_count

        if ratio_of_suspicious_range_usage < 0.1:
            return 0.

        return ratio_of_suspicious_range_usage


class SuperWeirdWordPlugin(MessDetectorPlugin):

    def __init__(self):
        self._word_count: int = 0
        self._bad_word_count: int = 0
        self._is_current_word_bad: bool = False

        self._character_count: int = 0
        self._bad_character_count: int = 0

        self._buffer: str = ""
        self._buffer_accent_count: int = 0

    def eligible(self, character: str) -> bool:
        return True

    def feed(self, character: str) -> None:
        if character.isalpha():
            self._buffer = "".join([self._buffer, character])
            if is_accentuated(character):
                self._buffer_accent_count += 1
            return
        if not self._buffer:
            return
        if (character.isspace() or is_punctuation(character) or is_separator(character)) and self._buffer:
            self._word_count += 1
            buffer_length: int = len(self._buffer)

            self._character_count += buffer_length

            if buffer_length >= 4 and self._buffer_accent_count / buffer_length >= 0.3:
                self._is_current_word_bad = True

            if self._is_current_word_bad:
                self._bad_word_count += 1
                self._bad_character_count += len(self._buffer)
                self._is_current_word_bad = False

            self._buffer = ""
            self._buffer_accent_count = 0
        elif character not in {"<", ">", "-", "="} and character.isdigit() is False and is_symbol(character):
            self._is_current_word_bad = True
            self._buffer += character

    def reset(self) -> None:
        self._buffer = ""
        self._is_current_word_bad = False
        self._bad_word_count = 0
        self._word_count = 0
        self._character_count = 0
        self._bad_character_count = 0

    @property
    def ratio(self) -> float:
        if self._word_count <= 16:
            return 0.
        return self._bad_character_count / self._character_count


class ArchaicUpperLowerPlugin(MessDetectorPlugin):

    def __init__(self):
        self._buf: bool = False
        self._successive_upper_lower_count: int = 0
        self._character_count: int = 0

        self._last_alpha_seen: Optional[str] = None

    def eligible(self, character: str) -> bool:
        return character.isspace() or character.isalpha()

    def feed(self, character: str) -> None:
        if self._last_alpha_seen is not None:
            if (character.isupper() and self._last_alpha_seen.islower()) or (character.islower() and self._last_alpha_seen.isupper()):
                if self._buf is True:
                    self._successive_upper_lower_count += 1
                else:
                    self._buf = True
            else:
                self._buf = False

        self._character_count += 1
        self._last_alpha_seen = character

    def reset(self) -> None:
        self._character_count = 0
        self._successive_upper_lower_count = 0
        self._last_alpha_seen = None

    @property
    def ratio(self) -> float:
        if self._character_count == 0:
            return 0.

        ratio_of_archaic_upper_lower: float = (self._successive_upper_lower_count * 2) / self._character_count

        return ratio_of_archaic_upper_lower


def is_suspiciously_successive_range(unicode_range_a: Optional[str], unicode_range_b: Optional[str]) -> bool:
    """
    Determine if two Unicode range seen next to each other can be considered as suspicious.
    """
    if unicode_range_a is None or unicode_range_b is None:
        return True

    if unicode_range_a == unicode_range_b:
        return False

    if "Latin" in unicode_range_a and "Latin" in unicode_range_b:
        return False

    if "Emoticons" in unicode_range_a or "Emoticons" in unicode_range_b:
        return False

    keywords_range_a: List[str]
    keywords_range_b: List[str]

    keywords_range_a, keywords_range_b = unicode_range_a.split(" "), unicode_range_b.split(" ")

    for el in keywords_range_a:
        if el in UNICODE_SECONDARY_RANGE_KEYWORD:
            continue
        if el in keywords_range_b:
            return False

    # Japanese Exception
    if unicode_range_a in ['Katakana', 'Hiragana'] and unicode_range_b in ['Katakana', 'Hiragana']:
        return False

    if unicode_range_a in ['Katakana', 'Hiragana'] or unicode_range_b in ['Katakana', 'Hiragana']:
        if "CJK" in unicode_range_a or "CJK" in unicode_range_b:
            return False

    if "Hangul" in unicode_range_a or "Hangul" in unicode_range_b:
        if "CJK" in unicode_range_a or "CJK" in unicode_range_b:
            return False
        if unicode_range_a == "Basic Latin" or unicode_range_b == "Basic Latin":
            return False

    # Chinese/Japanese use dedicated range for punctuation and/or separators.
    if ('CJK' in unicode_range_a or 'CJK' in unicode_range_b) or (unicode_range_a in ['Katakana', 'Hiragana'] and unicode_range_b in ['Katakana', 'Hiragana']):
        if 'Punctuation' in unicode_range_a or 'Punctuation' in unicode_range_b:
            return False
        if 'Forms' in unicode_range_a or 'Forms' in unicode_range_b:
            return False

    return True


@lru_cache(maxsize=2048)
def mess_ratio(decoded_sequence: str, maximum_threshold: float = 0.2, debug: bool = False) -> float:
    """
    Compute a mess ratio given a decoded bytes sequence.
    """
    detectors: List[MessDetectorPlugin] = []

    for md_class in MessDetectorPlugin.__subclasses__():
        detectors.append(
            md_class()
        )

    length: int = len(decoded_sequence)

    intermediary_mean_mess_ratio_calc: int
    mean_mess_ratio: float = 0.

    if length < 512:
        intermediary_mean_mess_ratio_calc = 32
    elif length <= 1024:
        intermediary_mean_mess_ratio_calc = 64
    else:
        intermediary_mean_mess_ratio_calc = 128

    for character, index in zip(decoded_sequence, range(0, length)):
        for detector in detectors:
            if detector.eligible(character):
                detector.feed(character)

        if (index > 0 and index % intermediary_mean_mess_ratio_calc == 0) or index == length-1:
            mean_mess_ratio = sum(
                [
                    dt.ratio for dt in detectors
                ]
            )

            if mean_mess_ratio >= maximum_threshold:
                break

    if debug:
        for dt in detectors:
            print(
                dt.__class__,
                dt.ratio
            )

    return round(
        mean_mess_ratio,
        3
    )

