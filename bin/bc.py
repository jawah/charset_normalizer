#!/bin/python
from __future__ import annotations

import argparse
from glob import glob
from os.path import isdir
from sys import argv

from chardet import detect as chardet_detect

from charset_normalizer import detect as tbt_detect
from charset_normalizer.utils import iana_name


def calc_equivalence(content: bytes, cp_a: str, cp_b: str):
    try:
        str_a = content.decode(cp_a)
        str_b = content.decode(cp_b)
    except UnicodeDecodeError:
        return 0.0

    character_count = len(str_a)
    diff_character_count = sum(chr_a != chr_b for chr_a, chr_b in zip(str_a, str_b))

    return 1.0 - (diff_character_count / character_count)


def cli_bc(arguments: list[str]):
    parser = argparse.ArgumentParser(
        description="BC script checker for Charset-Normalizer with Chardet"
    )

    parser.add_argument(
        "-c",
        "--coverage",
        action="store",
        default=85,
        type=int,
        dest="coverage",
        help="Define the minimum acceptable coverage to succeed",
    )

    args = parser.parse_args(arguments)

    if not isdir("./char-dataset"):
        print(
            "This script require https://github.com/Ousret/char-dataset to be cloned on package root directory"
        )
        exit(1)

    success_count = 0
    total_count = 0

    for tbt_path in sorted(glob("./char-dataset/**/*.*")):
        total_count += 1

        with open(tbt_path, "rb") as fp:
            content = fp.read()

        chardet_result = chardet_detect(content)
        chardet_encoding = chardet_result["encoding"]

        charset_normalizer_result = tbt_detect(content)
        charset_normalizer_encoding = charset_normalizer_result["encoding"]

        if [chardet_encoding, charset_normalizer_encoding].count(None) == 1:
            print(
                f"⚡⚡ '{tbt_path}' (BC-Break) New('{charset_normalizer_encoding}') vs Legacy('{chardet_encoding}')"
            )
            continue

        if charset_normalizer_encoding == chardet_encoding:
            success_count += 1
            print(f"✅✅ '{tbt_path}' (BC)")
            continue

        if (chardet_encoding is None and charset_normalizer_encoding is None) or (
            iana_name(chardet_encoding, False)
            == iana_name(charset_normalizer_encoding, False)
        ):
            success_count += 1
            print(f"✅✅ '{tbt_path}' (BC)")
            continue

        calc_eq = calc_equivalence(
            content, chardet_encoding, charset_normalizer_encoding
        )

        if calc_eq >= 0.98:
            success_count += 1
            print(
                f"️✅ ️'{tbt_path}' (got '{charset_normalizer_encoding}' but "
                f"eq {chardet_encoding} WITH {round(calc_eq * 100., 3)} %)"
            )
            continue

        print(
            f"⚡⚡ '{tbt_path}' (BC-Break) New('{charset_normalizer_encoding}') vs Legacy('{chardet_encoding}')"
        )

    success_ratio = round(success_count / total_count, 2) * 100.0

    print(f"Total EST BC = {success_ratio} % ({success_count} / {total_count} files)")

    return 0 if success_ratio >= args.coverage else 1


if __name__ == "__main__":
    exit(cli_bc(argv[1:]))
