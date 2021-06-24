from json import load
from typing import Dict, List
from os.path import dirname, realpath, exists
from warnings import warn

FILE_PATH: str = f'{dirname(realpath(__file__))}/frequencies.json'
FREQUENCIES: Dict[str, List[str]]

if not exists(FILE_PATH):
    warn("Charset-Normalizer require '{}' to be existent for language/coherence detection".format(FILE_PATH))
    FREQUENCIES = {}
else:
    with open(FILE_PATH, 'r', encoding='utf_8') as fp:
        FREQUENCIES = load(fp)
