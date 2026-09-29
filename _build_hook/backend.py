from __future__ import annotations

import os
from typing import Any

from setuptools import build_meta as _orig  # type: ignore[import-untyped]

USE_CYTHON = os.getenv("CHARSET_NORMALIZER_USE_CYTHON", "0") == "1"
# Cython 3.3 requires a Python 3.9+ Limited API; our abi3 wheels target 3.7.
CYTHON_SPEC = (
    "Cython>=3.2,<3.3"
    if os.getenv("CHARSET_NORMALIZER_CYTHON_ABI3") == "1"
    else "Cython>=3.2,<3.4"
)

# Expose all the PEP 517 hooks from setuptools
get_requires_for_build_sdist = _orig.get_requires_for_build_sdist
prepare_metadata_for_build_wheel = _orig.prepare_metadata_for_build_wheel
build_sdist = _orig.build_sdist

if hasattr(_orig, "prepare_metadata_for_build_editable"):
    prepare_metadata_for_build_editable = _orig.prepare_metadata_for_build_editable
if hasattr(_orig, "build_editable"):
    build_editable = _orig.build_editable


def _with_cython(requires: list[str]) -> list[str]:
    if USE_CYTHON and CYTHON_SPEC not in requires:
        requires = list(requires) if requires else []
        requires.append(CYTHON_SPEC)
    return requires


def get_requires_for_build_wheel(
    config_settings: dict[str, Any] | None = None,
) -> list[str]:
    """Get wheel build requirements, conditionally adding Cython."""
    return _with_cython(_orig.get_requires_for_build_wheel(config_settings))


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, Any] | None = None,
    metadata_directory: str | None = None,
) -> str:
    """Build a wheel, requiring Cython when native extensions are requested."""
    if USE_CYTHON:
        try:
            import Cython  # type: ignore[import-not-found]  # noqa: F401
        except ImportError as exception:
            raise RuntimeError(
                "Cython is required for the optimized build"
            ) from exception
    return _orig.build_wheel(wheel_directory, config_settings, metadata_directory)  # type: ignore[no-any-return]


if hasattr(_orig, "get_requires_for_build_editable"):

    def get_requires_for_build_editable(
        config_settings: dict[str, Any] | None = None,
    ) -> list[str]:
        """Get editable build requirements, conditionally adding Cython."""
        return _with_cython(_orig.get_requires_for_build_editable(config_settings))
