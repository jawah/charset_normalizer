"""
This submodule purpose is to load attached JSON asset.
Will be loaded once per package import / python init.

The file 'frequencies.json' is mandatory for language/coherence detection. Not having it will weaker considerably
the core detection.
"""
from json import load
from typing import Dict, List
from os.path import dirname, realpath, exists
from warnings import warn
from collections import OrderedDict

FILE_PATH = dirname(realpath(__file__)) + '/frequencies.json'  # type: str

if not exists(FILE_PATH):
    warn("Charset-Normalizer require '{}' to be existent for language/coherence detection. Detection WILL be weaker.".format(FILE_PATH))
    FREQUENCIES = {}  # type: Dict[str, List[str]]
else:
    with open(FILE_PATH, 'r', encoding='utf_8') as fp:
        FREQUENCIES = load(fp, object_pairs_hook=OrderedDict)
