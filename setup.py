#!/usr/bin/env python
from __future__ import annotations

import os
from pathlib import Path
from runpy import run_path

from setuptools import Extension, setup

USE_CYTHON = os.getenv("CHARSET_NORMALIZER_USE_CYTHON") == "1"
LIMITED_API = os.getenv("CHARSET_NORMALIZER_CYTHON_ABI3") == "1"

CYTHON_MODULES = None

if USE_CYTHON:
    try:
        from Cython.Build import cythonize
    except ImportError:
        cythonize = None

    if cythonize is not None:
        extension_kwargs = {}
        if LIMITED_API:
            extension_kwargs.update(
                define_macros=[
                    ("Py_LIMITED_API", "0x03070000"),
                    ("CYTHON_PEP489_MULTI_PHASE_INIT", "0"),
                ],
                py_limited_api=True,
            )
        if os.name != "nt":
            extension_kwargs["extra_compile_args"] = ["-g0"]

        CYTHON_MODULES = cythonize(
            [
                Extension(
                    "charset_normalizer.md",
                    ["src/charset_normalizer/md.pyx"],
                    **extension_kwargs,
                ),
                Extension(
                    "charset_normalizer.cd",
                    ["src/charset_normalizer/cd.pyx"],
                    **extension_kwargs,
                ),
            ],
            annotate=False,
            force=True,
            compiler_directives={
                "boundscheck": False,
                "cdivision": True,
                "initializedcheck": False,
                "language_level": 3,
                "nonecheck": False,
                "wraparound": False,
            },
        )

cmdclass = {}
if CYTHON_MODULES and os.getenv("CHARSET_NORMALIZER_USE_PGO", "1") == "1":
    pgo_hook = Path(__file__).resolve().parent / "_build_hook" / "pgo.py"
    cmdclass["build_ext"] = run_path(str(pgo_hook))["PGOBuildExt"]

setup(
    name="charset-normalizer",
    cmdclass=cmdclass,
    ext_modules=CYTHON_MODULES,
    options={"bdist_wheel": {"py_limited_api": "cp37"}} if LIMITED_API else {},
)
