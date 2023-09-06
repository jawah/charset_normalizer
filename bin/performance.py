#!/bin/python
from glob import glob
from time import time_ns
import argparse
from sys import argv
from os.path import isdir

from charset_normalizer import detect
from chardet import detect as chardet_detect

from statistics import mean
from math import ceil


def calc_percentile(data, percentile):
    n = len(data)
    p = n * percentile / 100
    sorted_data = sorted(data)

    return sorted_data[int(p)] if p.is_integer() else sorted_data[int(ceil(p)) - 1]


def performance_compare(arguments):
    parser = argparse.ArgumentParser(
        description="Performance CI/CD check for Charset-Normalizer"
    )

    parser.add_argument(
        "-s",
        "--size-increase",
        action="store",
        default=1,
        type=int,
        dest="size_coeff",
        help="Apply artificial size increase to challenge the detection mechanism further",
    )

    args = parser.parse_args(arguments)

    if not isdir("./char-dataset"):
        print(
            "This script require https://github.com/Ousret/char-dataset to be cloned on package root directory"
        )
        exit(1)

    chardet_results = []
    charset_normalizer_results = []

    file_list = sorted(glob("./char-dataset/**/*.*"))
    total_files = len(file_list)

    for idx, tbt_path in enumerate(file_list):
        with open(tbt_path, "rb") as fp:
            content = fp.read() * args.size_coeff

        before = time_ns()
        chardet_detect(content)
        chardet_time = round((time_ns() - before) / 1000000000, 5)
        chardet_results.append(chardet_time)

        before = time_ns()
        detect(content)
        charset_normalizer_time = round((time_ns() - before) / 1000000000, 5)
        charset_normalizer_results.append(charset_normalizer_time)

        cn_faster = (chardet_time / charset_normalizer_time) * 100 - 100
        print(
            f"{idx+1:>3}/{total_files} {tbt_path:<82} C:{chardet_time:<10} CN:{charset_normalizer_time:<10} {cn_faster:.1f} %"
        )

    chardet_avg_delay = round(mean(chardet_results) * 1000)
    chardet_99p = round(calc_percentile(chardet_results, 99) * 1000)
    chardet_95p = round(calc_percentile(chardet_results, 95) * 1000)
    chardet_50p = round(calc_percentile(chardet_results, 50) * 1000)

    charset_normalizer_avg_delay = round(mean(charset_normalizer_results) * 1000)
    charset_normalizer_99p = round(
        calc_percentile(charset_normalizer_results, 99) * 1000
    )
    charset_normalizer_95p = round(
        calc_percentile(charset_normalizer_results, 95) * 1000
    )
    charset_normalizer_50p = round(
        calc_percentile(charset_normalizer_results, 50) * 1000
    )

    # mypyc can offer performance ~1ms in the 50p. When eq to 0 assume 1 due to imprecise nature of this test.
    if charset_normalizer_50p == 0:
        charset_normalizer_50p = 1

    print("")

    print("------------------------------")
    print("--> Chardet Conclusions")
    print("   --> Avg: " + str(chardet_avg_delay) + "ms")
    print("   --> 99th: " + str(chardet_99p) + "ms")
    print("   --> 95th: " + str(chardet_95p) + "ms")
    print("   --> 50th: " + str(chardet_50p) + "ms")

    print("------------------------------")
    print("--> Charset-Normalizer Conclusions")
    print("   --> Avg: " + str(charset_normalizer_avg_delay) + "ms")
    print("   --> 99th: " + str(charset_normalizer_99p) + "ms")
    print("   --> 95th: " + str(charset_normalizer_95p) + "ms")
    print("   --> 50th: " + str(charset_normalizer_50p) + "ms")

    print("------------------------------")
    print("--> Charset-Normalizer / Chardet: Performance Сomparison")
    print(
        "   --> Avg: x"
        + str(round(chardet_avg_delay / charset_normalizer_avg_delay, 2))
    )
    print("   --> 99th: x" + str(round(chardet_99p / charset_normalizer_99p, 2)))
    print("   --> 95th: x" + str(round(chardet_95p / charset_normalizer_95p, 2)))
    print("   --> 50th: x" + str(round(chardet_50p / charset_normalizer_50p, 2)))

    return (
        0
        if chardet_avg_delay > charset_normalizer_avg_delay
        and chardet_99p > charset_normalizer_99p
        else 1
    )


if __name__ == "__main__":
    exit(performance_compare(argv[1:]))
