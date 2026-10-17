from __future__ import annotations

import pytest

from charset_normalizer.md import _char_info, is_suspiciously_successive_range, mess_ratio


@pytest.mark.parametrize("codepoint", range(128))
def test_ascii_character_properties(codepoint):
    character = chr(codepoint)
    info = _char_info(character)

    assert info.alpha == character.isalpha()
    assert info.upper == character.isupper()
    assert info.lower == character.islower()
    assert info.space == character.isspace()
    assert info.digit == character.isdigit()
    assert info.printable == character.isprintable()


@pytest.mark.parametrize("separator", ["\x1c", "\x1d", "\x1e", "\x1f"])
def test_ascii_information_separators(separator):
    assert mess_ratio(separator.join(["name", "Alice", "Bob", "Carol"])) == 0.0


@pytest.mark.parametrize("character", ["\x00", "\x01", "\x1b", "\x7f"])
def test_ascii_unprintable_controls(character):
    assert mess_ratio(f"hello{character}world") >= 0.2


@pytest.mark.parametrize(
    "content, min_expected_ratio, max_expected_ratio",
    [
        (
            "典肇乎庚辰年十二月廿一，及己丑年二月十九，收各方語言二百五十，合逾七百萬目；二十大卷佔八成，單英文卷亦過二百萬。悉文乃天下有志共筆而成；有意助之，幾網路、隨纂作，大典茁焉。",
            0.0,
            0.0,
        ),
        ("العقلية , التنويم المغناطيسي و / أو الاقتراح", 0.0, 0.0),
        ("RadoZ تـــعــــديــل الـــتــــوقــيــــت مـــن قــبــل", 0.0, 0.0),
        ("Cehennemin Sava■þ²s²'da kim?", 0.1, 0.5),
        ("´Á¥½³ø§i --  ±i®Ìºû, ³¯·Ø©v", 0.5, 1.0),
        (
            "ïstanbul, T■rkiye'nin en kalabal»k, iktisadi ve k■lt■rel aÓ»dan en —nemli",
            0.1,
            0.5,
        ),
        (
            "<i>Parce que Óa, c'est la vÕritable histoire de la rencontre avec votre Tante Robin.</i>",
            0.01,
            0.5,
        ),
        (
            """ØĢØŠØģØ§ØĶŲ ŲŲ ØĢŲ Ø§ŲŲØ§Øģ ŲŲŲ ŲØ§ ØģŲŲŲØŠØģØ§ØĶŲŲŲØ ØŊØđŲØ§ ŲØģŲØđ ØđŲ (ŲØąŲØŊŲ) ŲØ§ŲØŪØ§ØŠŲ""",
            0.8,
            3.0,
        ),
        ("""ÇáÚŞáíÉ , ÇáÊäæíã ÇáãÛäÇØíÓí æ / Ãæ ÇáÇŞÊÑÇÍ""", 0.8, 2.5),
        (
            """hishamkoc@yahoo.com ุชุฑุฌูููุฉ ููุดูููุงู ุงููููููููุงูRadoZ ุชูููุนููููุฏูููู ุงููููุชูููููููููููููุช ููููู ูููุจููู""",
            0.5,
            2.0,
        ),
    ],
)
def test_mess_detection(content, min_expected_ratio, max_expected_ratio):
    calculated_mess_ratio = mess_ratio(content, maximum_threshold=1.0)

    assert (
        min_expected_ratio <= calculated_mess_ratio <= max_expected_ratio
    ), "The mess detection ratio calculated for given content is not well adjusted!"


@pytest.mark.parametrize(
    "content",
    [
        "plain\x1bANSI escape",
        "niezale¿n¹",
        "niezaleæn¹",
        "ﾅﾓﾉﾔ瘕齴黵",
    ],
)
def test_decisive_mess_patterns(content):
    assert mess_ratio(content, maximum_threshold=1.0) >= 1.0


@pytest.mark.parametrize(
    "content", ["¿Dónde?", "encyclopædia", "R²", "日本語ﾅﾓﾉﾔ"]
)
def test_legitimate_nearby_patterns(content):
    assert mess_ratio(content, maximum_threshold=1.0) == 0.0


@pytest.mark.parametrize(
    "character, property_name",
    [
        ("ア", "is_katakana"),
        ("ﾅ", "is_halfwidth_katakana"),
        ("æ", "is_ligature"),
        ("²", "is_superscript"),
        ("¿", "is_sentence_open_punctuation"),
    ],
)
def test_semantic_character_information(character, property_name):
    assert getattr(_char_info(character), property_name) is True


@pytest.mark.parametrize(
    "range_a, range_b",
    [
        ("CJK Unified Ideographs", "Bopomofo"),
        ("CJK Unified Ideographs", "Kanbun"),
        ("Basic Latin", "IPA Extensions"),
        ("IPA Extensions", "Phonetic Extensions"),
        ("Basic Latin", "Spacing Modifier Letters"),
        ("Alphabetic Presentation Forms", "Hebrew"),
        ("Halfwidth and Fullwidth Forms", "Hangul Syllables"),
        ("Basic Latin", "Hiragana"),
        ("Basic Latin", "Kana Extended-A"),
    ],
)
def test_compatible_successive_ranges(range_a, range_b):
    assert is_suspiciously_successive_range(range_a, range_b) is False
    assert is_suspiciously_successive_range(range_b, range_a) is False


@pytest.mark.parametrize(
    "transparent_range",
    [
        "Combining Diacritical Marks",
        "Variation Selectors",
        "Emoticons",
        "Miscellaneous Symbols and Pictographs",
    ],
)
def test_transparent_successive_ranges(transparent_range):
    assert is_suspiciously_successive_range("Cyrillic", transparent_range) is False
    assert is_suspiciously_successive_range(transparent_range, "Cyrillic") is False
