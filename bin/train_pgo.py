"""Train the instrumented wheel extensions in a fresh build interpreter."""

from __future__ import annotations

import argparse
import sys
from importlib.machinery import EXTENSION_SUFFIXES
from pathlib import Path


def train(stage: Path) -> None:
    stage = stage.resolve()
    sys.path.insert(0, str(stage))
    from charset_normalizer import cd, detect, md  # type: ignore[import-not-found]

    for module in (cd, md):
        if module.__file__ is None:
            raise RuntimeError(f"PGO could not locate {module.__name__}")
        binary = Path(module.__file__).resolve()
        if binary.parent != stage / "charset_normalizer" or not str(binary).endswith(
            tuple(EXTENSION_SUFFIXES)
        ):
            raise RuntimeError(f"PGO imported an unexpected module: {binary}")

    corpus = Path(__file__).resolve().parents[1] / "data"
    samples = sorted(corpus.glob("*.txt"))
    if not samples:
        raise RuntimeError(f"No PGO training samples in {corpus}")
    print(
        f"Training charset-normalizer on {len(samples)} files from {corpus}", flush=True
    )
    for sample in samples:
        detect(sample.read_bytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage",
        type=Path,
        help="build directory containing the instrumented charset_normalizer package",
    )
    train(parser.parse_args().stage)
