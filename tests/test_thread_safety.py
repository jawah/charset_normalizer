from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from os import pardir, path

from charset_normalizer.api import from_path

DIR_PATH = path.join(path.dirname(path.realpath(__file__)), pardir)


# Each tuple: (file, expected_encoding, expected_language)
_THREAD_CASES = [
    ("sample-arabic-1.txt", "cp1256", "Arabic"),
    ("sample-french-1.txt", "cp1252", "French"),
    ("sample-chinese.txt", "big5", "Chinese"),
]


def _detect(case: tuple[str, str, str]) -> tuple[str, str, str, str | None, str | None]:
    file_name, expected_enc, expected_lang = case
    result = from_path(path.join(DIR_PATH, "data", file_name))
    best = result.best() if result else None
    return (
        file_name,
        expected_enc,
        expected_lang,
        best.encoding if best else None,
        best.language if best else None,
    )


class TestThreadSafety:
    def test_concurrent_detection(self) -> None:
        """Three files detected concurrently must each return the correct
        encoding and language, proving no shared mutable state corruption."""
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {pool.submit(_detect, case): case for case in _THREAD_CASES}

            for future in as_completed(futures):
                file_name, expected_enc, expected_lang, got_enc, got_lang = (
                    future.result()
                )
                assert got_enc == expected_enc, (
                    f"{file_name}: expected encoding {expected_enc}, got {got_enc}"
                )
                assert got_lang == expected_lang, (
                    f"{file_name}: expected language {expected_lang}, got {got_lang}"
                )

    def test_concurrent_detection_repeated(self) -> None:
        """Run the same three-file detection five times to surface any
        intermittent race conditions."""
        for _ in range(5):
            self.test_concurrent_detection()
