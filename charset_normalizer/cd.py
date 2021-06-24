from codecs import IncrementalDecoder
from functools import lru_cache
from typing import List, Set, Optional, Tuple, Dict
import importlib

from charset_normalizer.models import CoherenceMatches
from charset_normalizer.utils import unicode_range, is_unicode_range_secondary, is_multi_byte_encoding
from charset_normalizer.md import is_suspiciously_successive_range
from charset_normalizer.assets import FREQUENCIES
from collections import Counter


def encoding_unicode_range(iana_name: str) -> List[str]:
    if is_multi_byte_encoding(iana_name):
        raise IOError("Function not supported on multi-byte code page")

    decoder = importlib.import_module(f'encodings.{iana_name}').IncrementalDecoder

    p: IncrementalDecoder = decoder(errors="ignore")
    seen_ranges: Set[str] = set()

    for i in range(48, 255):
        chunk: str = p.decode(
            bytes([i])
        )

        if chunk:
            character_range: str = unicode_range(chunk)

            if is_unicode_range_secondary(character_range) is False:
                seen_ranges.add(character_range)

    return sorted(list(seen_ranges))


def unicode_range_languages(primary_range: str) -> List[str]:
    languages: List[str] = []

    for language, characters in FREQUENCIES.items():
        for character in characters:
            if unicode_range(character) == primary_range:
                languages.append(language)
                break

    return languages


@lru_cache()
def encoding_languages(iana_name: str) -> List[str]:
    """
    Single-byte encoding language association
    """
    unicode_ranges: List[str] = encoding_unicode_range(iana_name)
    primary_range: Optional[str] = None

    for specified_range in unicode_ranges:
        if "Latin" not in specified_range:
            primary_range = specified_range
            break

    if primary_range is None:
        return ["Latin Based"]

    return unicode_range_languages(primary_range)


def mb_encoding_languages(iana_name: str) -> List[str]:
    """
    Multi-byte encoding language association
    """
    if iana_name.startswith("shift_") or iana_name.startswith("iso2022_jp") or iana_name.startswith("euc_j") or iana_name in {"cp932"}:
        return ["Japanese"]
    if iana_name.startswith("gb") or iana_name in {"big5", "cp950", "big5hkscs"}:
        return ["Chinese", "Classical Chinese"]
    if iana_name.startswith("iso2022_kr") or iana_name in {"johab", "cp949", "euc_kr"}:
        return ["Korean"]

    return []


def alphabet_languages(characters: List[str]) -> List[str]:
    languages: List[str] = []

    for language, language_characters in FREQUENCIES.items():
        character_match_count: int = 0
        character_count: int = len(language_characters)

        for character in language_characters:
            if character in characters:
                character_match_count += 1

        if character_match_count / character_count >= 0.2:
            languages.append(language)

    return languages


def characters_popularity_compare(language: str, ordered_characters: List[str]) -> float:
    if language not in FREQUENCIES:
        raise ValueError("{} not available".format(language))

    character_approved_count: int = 0

    for character in ordered_characters:
        if character not in FREQUENCIES[language]:
            continue

        characters_before_source: List[str] = FREQUENCIES[language][0:FREQUENCIES[language].index(character)]
        characters_after_source: List[str] = FREQUENCIES[language][FREQUENCIES[language].index(character):]

        characters_before: List[str] = ordered_characters[0:ordered_characters.index(character)]
        characters_after: List[str] = ordered_characters[ordered_characters.index(character):]

        before_match_count: int = [e in characters_before for e in characters_before_source].count(True)
        after_match_count: int = [e in characters_after for e in characters_after_source].count(True)

        if len(characters_before_source) == 0 and before_match_count <= 4:
            character_approved_count += 1
            continue

        if len(characters_after_source) == 0 and after_match_count <= 4:
            character_approved_count += 1
            continue

        if before_match_count / len(characters_before_source) >= 0.4 or after_match_count / len(characters_after_source) >= 0.4:
            character_approved_count += 1
            continue

    return character_approved_count / len(ordered_characters)


def alpha_unicode_split(decoded_sequence: str) -> List[str]:
    layers: Dict[str, str] = {}

    for character in decoded_sequence:
        if character.isalpha() is False:
            continue

        character_range: str = unicode_range(character)

        layer_target_range: Optional[str] = None

        for discovered_range in layers:
            if is_suspiciously_successive_range(discovered_range, character_range) is False:
                layer_target_range = discovered_range
                break

        if layer_target_range is None:
            layer_target_range = character_range

        if layer_target_range not in layers:
            layers[layer_target_range] = character.lower()
            continue

        layers[layer_target_range] += character.lower()

    return list(layers.values())


def merge_coherence_ratios(results: List[CoherenceMatches]) -> CoherenceMatches:
    per_language_ratios: Dict[str, List[float]] = {}
    merge: CoherenceMatches = []

    for result in results:
        for sub_result in result:
            language, ratio = sub_result
            if language not in per_language_ratios:
                per_language_ratios[language] = [ratio]
                continue
            per_language_ratios[language].append(
                ratio
            )

    for language in per_language_ratios:
        merge.append(
            (
                language,
                round(
                    sum(
                        per_language_ratios[language]
                    ) / len(per_language_ratios[language]),
                    4
                )
            )
        )

    return sorted(merge, key=lambda x: x[1], reverse=True)


@lru_cache(maxsize=2048)
def coherence_ratio(decoded_sequence: str, threshold: float = 0.1, lg_inclusion: Optional[str] = None) -> CoherenceMatches:

    results: List[Tuple[str, float]] = []

    sufficient_match_count: int = 0

    if lg_inclusion is not None:
        lg_inclusion = lg_inclusion.split(",")

    if lg_inclusion is not None and "Latin Based" in lg_inclusion:
        lg_inclusion.remove("Latin Based")

    for layer in alpha_unicode_split(decoded_sequence):
        sequence_frequencies: Counter = Counter(layer)
        most_common = sequence_frequencies.most_common()

        character_count: int = sum([o for c, o in most_common])

        if character_count <= 32:
            continue

        popular_character_ordered: List[str] = [c for c, o in most_common]

        for language in lg_inclusion or alphabet_languages(popular_character_ordered):
            ratio: float = characters_popularity_compare(language, popular_character_ordered)

            if ratio < threshold:
                continue
            elif ratio >= 0.8:
                sufficient_match_count += 1

            results.append(
                (language, round(ratio, 4))
            )

            if sufficient_match_count >= 3:
                break

    return sorted(results, key=lambda x: x[1], reverse=True)
