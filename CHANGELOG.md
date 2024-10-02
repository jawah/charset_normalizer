# Changelog
All notable changes to charset-normalizer will be documented in this file. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [3.3.3](https://github.com/Ousret/charset_normalizer/compare/3.3.2...master) (2024-09-??)

### Added
- Argument `--no-preemptive` in the CLI to prevent the detector to search for hints.

### Fixed
- Relax the TypeError exception thrown when trying to compare a CharsetMatch with anything else than a CharsetMatch.
- Improved the general reliability of the detector based on user feedbacks. (#520) (#509) (#498) (#407) (#537)
- Declared charset in content (preemptive detection) not changed when converting to utf-8 bytes. (#381)

## [3.3.2](https://github.com/Ousret/charset_normalizer/compare/3.3.1...3.3.2) (2023-10-31)

### Fixed
- Unintentional memory usage regression when using large payload that match several encoding (#376)
- Regression on some detection case showcased in the documentation (#371)

### Added
- Noise (md) probe that identify malformed arabic representation due to the presence of letters in isolated form (credit to my wife)

## [3.3.1](https://github.com/Ousret/charset_normalizer/compare/3.3.0...3.3.1) (2023-10-22)

### Changed
- Optional mypyc compilation upgraded to version 1.6.1 for Python >= 3.8
- Improved the general detection reliability based on reports from the community

## [3.3.0](https://github.com/Ousret/charset_normalizer/compare/3.2.0...3.3.0) (2023-09-30)

### Added
- Allow to execute the CLI (e.g. normalizer) through `python -m charset_normalizer.cli` or `python -m charset_normalizer`
- Support for 9 forgotten encoding that are supported by Python but unlisted in `encoding.aliases` as they have no alias (#323)

### Removed
- (internal) Redundant utils.is_ascii function and unused function is_private_use_only
- (internal) charset_normalizer.assets is moved inside charset_normalizer.constant

### Changed
- (internal) Unicode code blocks in constants are updated using the latest v15.0.0 definition to improve detection
- Optional mypyc compilation upgraded to version 1.5.1 for Python >= 3.8

### Fixed
- Unable to properly sort CharsetMatch when both chaos/noise and coherence were close due to an unreachable condition in \_\_lt\_\_ (#350)

## [3.2.0](https://github.com/Ousret/charset_normalizer/compare/3.1.0...3.2.0) (2023-06-07)

### Changed
- Typehint for function `from_path` no longer enforce `PathLike` as its first argument
- Minor improvement over the global detection reliability

### Added
- Introduce function `is_binary` that relies on main capabilities, and optimized to detect binaries
- Propagate `enable_fallback` argument throughout `from_bytes`, `from_path`, and `from_fp` that allow a deeper control over the detection (default True)
- Explicit support for Python 3.12

### Fixed
- Edge case detection failure where a file would contain 'very-long' camel cased word (Issue #289)

## [3.1.0](https://github.com/Ousret/charset_normalizer/compare/3.0.1...3.1.0) (2023-03-06)

### Added
- Argument `should_rename_legacy` for legacy function `detect` and disregard any new arguments without errors (PR #262)

### Removed
- Support for Python 3.6 (PR #260)

### Changed
- Optional speedup provided by mypy/c 1.0.1

## [3.0.1](https://github.com/Ousret/charset_normalizer/compare/3.0.0...3.0.1) (2022-11-18)

### Fixed
- Multi-bytes cutter/chunk generator did not always cut correctly (PR #233)

### Changed
- Speedup provided by mypy/c 0.990 on Python >= 3.7

## [3.0.0](https://github.com/Ousret/charset_normalizer/compare/2.1.1...3.0.0) (2022-10-20)

### Added
- Extend the capability of explain=True when cp_isolation contains at most two entries (min one), will log in details of the Mess-detector results
- Support for alternative language frequency set in charset_normalizer.assets.FREQUENCIES
- Add parameter `language_threshold` in `from_bytes`, `from_path` and `from_fp` to adjust the minimum expected coherence ratio
- `normalizer --version` now specify if current version provide extra speedup (meaning mypyc compilation whl)

### Changed
- Build with static metadata using 'build' frontend
- Make the language detection stricter
- Optional: Module `md.py` can be compiled using Mypyc to provide an extra speedup up to 4x faster than v2.1

### Fixed
- CLI with opt --normalize fail when using full path for files
- TooManyAccentuatedPlugin induce false positive on the mess detection when too few alpha character have been fed to it
- Sphinx warnings when generating the documentation

### Removed
- Coherence detector no longer return 'Simple English' instead return 'English'
- Coherence detector no longer return 'Classical Chinese' instead return 'Chinese'
- Breaking: Method `first()` and `best()` from CharsetMatch
- UTF-7 will no longer appear as "detected" without a recognized SIG/mark (is unreliable/conflict with ASCII)
- Breaking: Class aliases CharsetDetector, CharsetDoctor, CharsetNormalizerMatch and CharsetNormalizerMatches
- Breaking: Top-level function `normalize`
- Breaking: Properties `chaos_secondary_pass`, `coherence_non_latin` and `w_counter` from CharsetMatch
- Support for the backport `unicodedata2`

## [3.0.0rc1](https://github.com/Ousret/charset_normalizer/compare/3.0.0b2...3.0.0rc1) (2022-10-18)

### Added
- Extend the capability of explain=True when cp_isolation contains at most two entries (min one), will log in details of the Mess-detector results
- Support for alternative language frequency set in charset_normalizer.assets.FREQUENCIES
- Add parameter `language_threshold` in `from_bytes`, `from_path` and `from_fp` to adjust the minimum expected coherence ratio

### Changed
- Build with static metadata using 'build' frontend
- Make the language detection stricter

### Fixed
- CLI with opt --normalize fail when using full path for files
- TooManyAccentuatedPlugin induce false positive on the mess detection when too few alpha character have been fed to it

### Removed
- Coherence detector no longer return 'Simple English' instead return 'English'
- Coherence detector no longer return 'Classical Chinese' instead return 'Chinese'

## [3.0.0b2](https://github.com/Ousret/charset_normalizer/compare/3.0.0b1...3.0.0b2) (2022-08-21)

### Added
- `normalizer --version` now specify if current version provide extra speedup (meaning mypyc compilation whl)

### Removed
- Breaking: Method `first()` and `best()` from CharsetMatch
- UTF-7 will no longer appear as "detected" without a recognized SIG/mark (is unreliable/conflict with ASCII)

### Fixed
- Sphinx warnings when generating the documentation

## [3.0.0b1](https://github.com/Ousret/charset_normalizer/compare/2.1.0...3.0.0b1) (2022-08-15)

### Changed
- Optional: Module `md.py` can be compiled using Mypyc to provide an extra speedup up to 4x faster than v2.1

### Removed
- Breaking: Class aliases CharsetDetector, CharsetDoctor, CharsetNormalizerMatch and CharsetNormalizerMatches
- Breaking: Top-level function `normalize`
- Breaking: Properties `chaos_secondary_pass`, `coherence_non_latin` and `w_counter` from CharsetMatch
- Support for the backport `unicodedata2`

## [2.1.1](https://github.com/Ousret/charset_normalizer/compare/2.1.0...2.1.1) (2022-08-19)

### Deprecated
- Function `normalize` scheduled for removal in 3.0

### Changed
- Removed useless call to decode in fn is_unprintable (#206)

### Fixed
- Third-party library (i18n xgettext) crashing not recognizing utf_8 (PEP 263) with underscore from [@aleksandernovikov](https://github.com/aleksandernovikov) (#204)

## [2.1.0](https://github.com/Ousret/charset_normalizer/compare/2.0.12...2.1.0) (2022-06-19)

### Added
- Output the Unicode table version when running the CLI with `--version` (PR #194)

### Changed
- Re-use decoded buffer for single byte character sets from [@nijel](https://github.com/nijel) (PR #175)
- Fixing some performance bottlenecks from [@deedy5](https://github.com/deedy5) (PR #183)

### Fixed
- Workaround potential bug in cpython with Zero Width No-Break Space located in Arabic Presentation Forms-B, Unicode 1.1 not acknowledged as space (PR #175)
- CLI default threshold aligned with the API threshold from [@oleksandr-kuzmenko](https://github.com/oleksandr-kuzmenko) (PR #181)

### Removed
- Support for Python 3.5 (PR #192)

### Deprecated
- Use of backport unicodedata from `unicodedata2` as Python is quickly catching up, scheduled for removal in 3.0 (PR #194)

## [2.0.12](https://github.com/Ousret/charset_normalizer/compare/2.0.11...2.0.12) (2022-02-12)

### Fixed
- ASCII miss-detection on rare cases (PR #170) 

## [2.0.11](https://github.com/Ousret/charset_normalizer/compare/2.0.10...2.0.11) (2022-01-30)

### Added
- Explicit support for Python 3.11 (PR #164)

### Changed
- The logging behavior have been completely reviewed, now using only TRACE and DEBUG levels (PR #163 #165)

## [2.0.10](https://github.com/Ousret/charset_normalizer/compare/2.0.9...2.0.10) (2022-01-04)

### Fixed
- Fallback match entries might lead to UnicodeDecodeError for large bytes sequence (PR #154)

### Changed
- Skipping the language-detection (CD) on ASCII (PR #155)

## [2.0.9](https://github.com/Ousret/charset_normalizer/compare/2.0.8...2.0.9) (2021-12-03)

### Changed
- Moderating the logging impact (since 2.0.8) for specific environments (PR #147)

### Fixed
- Wrong logging level applied when setting kwarg `explain` to True (PR #146)

## [2.0.8](https://github.com/Ousret/charset_normalizer/compare/2.0.7...2.0.8) (2021-11-24)
### Changed
- Improvement over Vietnamese detection (PR #126)
- MD improvement on trailing data and long foreign (non-pure latin) data (PR #124)
- Efficiency improvements in cd/alphabet_languages from [@adbar](https://github.com/adbar) (PR #122)
- call sum() without an intermediary list following PEP 289 recommendations from [@adbar](https://github.com/adbar) (PR #129)
- Code style as refactored by Sourcery-AI (PR #131) 
- Minor adjustment on the MD around european words (PR #133)
- Remove and replace SRTs from assets / tests (PR #139)
- Initialize the library logger with a `NullHandler` by default from [@nmaynes](https://github.com/nmaynes) (PR #135)
- Setting kwarg `explain` to True will add provisionally (bounded to function lifespan) a specific stream handler (PR #135)

### Fixed
- Fix large (misleading) sequence giving UnicodeDecodeError (PR #137)
- Avoid using too insignificant chunk (PR #137)

### Added
- Add and expose function `set_logging_handler` to configure a specific StreamHandler from [@nmaynes](https://github.com/nmaynes) (PR #135)
- Add `CHANGELOG.md` entries, format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) (PR #141)

## [2.0.7](https://github.com/Ousret/charset_normalizer/compare/2.0.6...2.0.7) (2021-10-11)
### Added
- Add support for Kazakh (Cyrillic) language detection (PR #109)

### Changed
- Further, improve inferring the language from a given single-byte code page (PR #112)
- Vainly trying to leverage PEP263 when PEP3120 is not supported (PR #116)
- Refactoring for potential performance improvements in loops from [@adbar](https://github.com/adbar) (PR #113)
- Various detection improvement (MD+CD) (PR #117)

### Removed
- Remove redundant logging entry about detected language(s) (PR #115)

### Fixed
- Fix a minor inconsistency between Python 3.5 and other versions regarding language detection (PR #117 #102)

## [2.0.6](https://github.com/Ousret/charset_normalizer/compare/2.0.5...2.0.6) (2021-09-18)
### Fixed
- Unforeseen regression with the loss of the backward-compatibility with some older minor of Python 3.5.x (PR #100)
- Fix CLI crash when using --minimal output in certain cases (PR #103)

### Changed
- Minor improvement to the detection efficiency (less than 1%) (PR #106 #101)

## [2.0.5](https://github.com/Ousret/charset_normalizer/compare/2.0.4...2.0.5) (2021-09-14)
### Changed
- The project now comply with: flake8, mypy, isort and black to ensure a better overall quality (PR #81)
- The BC-support with v1.x was improved, the old staticmethods are restored (PR #82)
- The Unicode detection is slightly improved (PR #93)
- Add syntax sugar \_\_bool\_\_ for results CharsetMatches list-container (PR #91)

### Removed
- The project no longer raise warning on tiny content given for detection, will be simply logged as warning instead (PR #92)

### Fixed
- In some rare case, the chunks extractor could cut in the middle of a multi-byte character and could mislead the mess detection (PR #95)
- Some rare 'space' characters could trip up the UnprintablePlugin/Mess detection (PR #96)
- The MANIFEST.in was not exhaustive (PR #78)

## [2.0.4](https://github.com/Ousret/charset_normalizer/compare/2.0.3...2.0.4) (2021-07-30)
### Fixed
- The CLI no longer raise an unexpected exception when no encoding has been found (PR #70)
- Fix accessing the 'alphabets' property when the payload contains surrogate characters (PR #68)
- The logger could mislead (explain=True) on detected languages and the impact of one MBCS match (PR #72)
- Submatch factoring could be wrong in rare edge cases (PR #72)
- Multiple files given to the CLI were ignored when publishing results to STDOUT. (After the first path) (PR #72)
- Fix line endings from CRLF to LF for certain project files (PR #67)

### Changed
- Adjust the MD to lower the sensitivity, thus improving the global detection reliability (PR #69 #76)
- Allow fallback on specified encoding if any (PR #71)

## [2.0.3](https://github.com/Ousret/charset_normalizer/compare/2.0.2...2.0.3) (2021-07-16)
### Changed
- Part of the detection mechanism has been improved to be less sensitive, resulting in more accurate detection results. Especially ASCII. (PR #63)
- According to the community wishes, the detection will fall back on ASCII or UTF-8 in a last-resort case. (PR #64)

## [2.0.2](https://github.com/Ousret/charset_normalizer/compare/2.0.1...2.0.2) (2021-07-15)
### Fixed
- Empty/Too small JSON payload miss-detection fixed. Report from [@tseaver](https://github.com/tseaver) (PR #59) 

### Changed
- Don't inject unicodedata2 into sys.modules from [@akx](https://github.com/akx) (PR #57)

## [2.0.1](https://github.com/Ousret/charset_normalizer/compare/2.0.0...2.0.1) (2021-07-13)
### Fixed
- Make it work where there isn't a filesystem available, dropping assets frequencies.json. Report from [@sethmlarson](https://github.com/sethmlarson). (PR #55)
- Using explain=False permanently disable the verbose output in the current runtime (PR #47)
- One log entry (language target preemptive) was not show in logs when using explain=True (PR #47)
- Fix undesired exception (ValueError) on getitem of instance CharsetMatches (PR #52)

### Changed
- Public function normalize default args values were not aligned with from_bytes (PR #53)

### Added
- You may now use charset aliases in cp_isolation and cp_exclusion arguments (PR #47)

## [2.0.0](https://github.com/Ousret/charset_normalizer/compare/1.4.1...2.0.0) (2021-07-02)
### Changed
- 4x to 5 times faster than the previous 1.4.0 release. At least 2x faster than Chardet.
- Accent has been made on UTF-8 detection, should perform rather instantaneous.
- The backward compatibility with Chardet has been greatly improved. The legacy detect function returns an identical charset name whenever possible.
- The detection mechanism has been slightly improved, now Turkish content is detected correctly (most of the time)
- The program has been rewritten to ease the readability and maintainability. (+Using static typing)+
- utf_7 detection has been reinstated.

### Removed
- This package no longer require anything when used with Python 3.5 (Dropped cached_property)
- Removed support for these languages: Catalan, Esperanto, Kazakh, Baque, Volapük, Azeri, Galician, Nynorsk, Macedonian, and Serbocroatian.
- The exception hook on UnicodeDecodeError has been removed.

### Deprecated
- Methods coherence_non_latin, w_counter, chaos_secondary_pass of the class CharsetMatch are now deprecated and scheduled for removal in v3.0

### Fixed
- The CLI output used the relative path of the file(s). Should be absolute.

## [1.4.1](https://github.com/Ousret/charset_normalizer/compare/1.4.0...1.4.1) (2021-05-28)
### Fixed
- Logger configuration/usage no longer conflict with others (PR #44)

## [1.4.0](https://github.com/Ousret/charset_normalizer/compare/1.3.9...1.4.0) (2021-05-21)
### Removed
- Using standard logging instead of using the package loguru.
- Dropping nose test framework in favor of the maintained pytest.
- Choose to not use dragonmapper package to help with gibberish Chinese/CJK text.
- Require cached_property only for Python 3.5 due to constraint. Dropping for every other interpreter version.
- Stop support for UTF-7 that does not contain a SIG.
- Dropping PrettyTable, replaced with pure JSON output in CLI.

### Fixed
- BOM marker in a CharsetNormalizerMatch instance could be False in rare cases even if obviously present. Due to the sub-match factoring process.
- Not searching properly for the BOM when trying utf32/16 parent codec.

### Changed
- Improving the package final size by compressing frequencies.json.
- Huge improvement over the larges payload.

### Added
- CLI now produces JSON consumable output.
- Return ASCII if given sequences fit. Given reasonable confidence.

## [1.3.9](https://github.com/Ousret/charset_normalizer/compare/1.3.8...1.3.9) (2021-05-13)

### Fixed
- In some very rare cases, you may end up getting encode/decode errors due to a bad bytes payload (PR #40)

## [1.3.8](https://github.com/Ousret/charset_normalizer/compare/1.3.7...1.3.8) (2021-05-12)

### Fixed
- Empty given payload for detection may cause an exception if trying to access the `alphabets` property. (PR #39)

## [1.3.7](https://github.com/Ousret/charset_normalizer/compare/1.3.6...1.3.7) (2021-05-12)

### Fixed
- The legacy detect function should return UTF-8-SIG if sig is present in the payload. (PR #38)

## [1.3.6](https://github.com/Ousret/charset_normalizer/compare/1.3.5...1.3.6) (2021-02-09)

### Changed
- Amend the previous release to allow prettytable 2.0 (PR #35)

## [1.3.5](https://github.com/Ousret/charset_normalizer/compare/1.3.4...1.3.5) (2021-02-08)

### Fixed
- Fix error while using the package with a python pre-release interpreter (PR #33)

### Changed
- Dependencies refactoring, constraints revised.

### Added
- Add python 3.9 and 3.10 to the supported interpreters
