# -*- coding: utf_8 -*-
"""
Charset-Normalizer
~~~~~~~~~~~~~~
The Real First Universal Charset Detector.
A library that helps you read text from an unknown charset encoding.
Motivated by chardet, This package is trying to resolve the issue by taking a new approach.
All IANA character set names for which the Python core library provides codecs are supported.

Basic usage:
   >>> from charset_normalizer import from_bytes
   >>> results = from_bytes('Bсеки човек има право на образование. Oбразованието!'.encode('utf_8'))
   >>> best_guess = results.best()
   >>> str(best_guess)
   'Bсеки човек има право на образование. Oбразованието!'

Others methods and usages are available - see the full documentation
at <https://github.com/Ousret/charset_normalizer>.
:copyright: (c) 2021 by Ahmed TAHRI
:license: MIT, see LICENSE for more details.
"""
import logging

from .api import from_bytes, from_fp, from_path, normalize
from .legacy import (
    CharsetDetector,
    CharsetDoctor,
    CharsetNormalizerMatch,
    CharsetNormalizerMatches,
    detect,
)
from .models import CharsetMatch, CharsetMatches
from .version import VERSION, __version__

__all__ = (
    "from_fp",
    "from_path",
    "from_bytes",
    "normalize",
    "detect",
    "CharsetMatch",
    "CharsetMatches",
    "CharsetNormalizerMatch",
    "CharsetNormalizerMatches",
    "CharsetDetector",
    "CharsetDoctor",
    "__version__",
    "VERSION",
)


def set_logging_handler(
    name: str = "charset_normalizer",
    level: int = logging.INFO,
    format_string: str = None,
) -> None:

    if format_string is None:
        format_string = "%(asctime)s | %(levelname)s | %(message)s"
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(handler)


# Attach a NullHandler to the top level logger by default
# https://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library


logging.getLogger(__name__).addHandler(logging.NullHandler())
