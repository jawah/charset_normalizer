# coding: utf-8
from charset_normalizer.normalizer import CharsetNormalizerMatches, CharsetNormalizerMatch, \
    CharsetDetector, CharsetDoctor, EncodingDetector  # Aliases
import charset_normalizer.unicode as unicode_utils
from charset_normalizer.probe_chaos import ProbeChaos
from charset_normalizer.probe_coherence import ProbeCoherence
from charset_normalizer.probe_words import ProbeWords
from charset_normalizer.legacy import detect
from charset_normalizer.hook import charset_normalizer_hook
from charset_normalizer.version import __version__, VERSION
