#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from re import search

from setuptools import setup


def get_version():
    with open('charset_normalizer/version.py') as version_file:
        return search(r"""__version__\s+=\s+(['"])(?P<version>.+?)\1""",
                      version_file.read()).group('version')


USE_MYPYC = False

if len(sys.argv) > 1 and sys.argv[1] == "--use-mypyc":
    sys.argv.pop(1)
    USE_MYPYC = True
if os.getenv("CHARSET_NORMALIZER_USE_MYPYC", None) == "1":
    USE_MYPYC = True

if USE_MYPYC:
    from mypyc.build import mypycify

    MYPYC_MODULES = mypycify([
        "charset_normalizer/md.py",
    ], debug_level="0")
else:
    MYPYC_MODULES = None

setup(
    name="charset-normalizer",
    version=get_version(),
    ext_modules=MYPYC_MODULES
)
