from json import load
from typing import Dict, List
from os.path import dirname, realpath, exists
from warnings import warn

FILE_PATH: str = f'{dirname(realpath(__file__))}/frequencies.json'
FREQUENCIES: Dict[str, List[str]]

if not exists(FILE_PATH):
    warn(f"Charset-Normalizer require '{FILE_PATH}' to be existent for language/coherence detection")
    FREQUENCIES = {}
else:
    with open(FILE_PATH, 'r', encoding='utf_8') as fp:
        FREQUENCIES = load(fp)
