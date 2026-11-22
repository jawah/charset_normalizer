"""Merge the native-tested x86_64 and arm64 wheel for each Python/ABI tag."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from delocate.fuse import fuse_wheels


def slices(directory: Path, arch: str) -> dict[str, Path]:
    wheels: dict[str, Path] = {}
    for wheel in directory.glob("*.whl"):
        key, platform = wheel.stem.rsplit("-", 1)
        if (
            not platform.startswith("macosx_")
            or not platform.endswith("_" + arch)
            or key in wheels
        ):
            raise ValueError(f"Unexpected or duplicate {arch} wheel: {wheel.name}")
        wheels[key] = wheel
    return wheels


def main(intel: Path, arm: Path, output: Path) -> None:
    x86 = slices(intel, "x86_64")
    arm64 = slices(arm, "arm64")
    if not x86 or x86.keys() != arm64.keys():
        raise ValueError(f"Missing macOS wheel partner(s): {x86.keys() ^ arm64.keys()}")
    output.mkdir(parents=True, exist_ok=True)
    for key in sorted(x86):
        merged = fuse_wheels(x86[key], arm64[key], output)
        if merged.stem.rsplit("-", 1)[0] != key or not merged.name.endswith(
            "_universal2.whl"
        ):
            raise ValueError(f"Unexpected merged tag: {merged.name}")
        with ZipFile(merged) as archive, TemporaryDirectory() as temp:
            for module in ("md", "cd"):
                (binary,) = (
                    n
                    for n in archive.namelist()
                    if n.startswith(f"charset_normalizer/{module}.")
                    and n.endswith(".so")
                )
                subprocess.run(
                    [
                        "lipo",
                        archive.extract(binary, temp),
                        "-verify_arch",
                        "x86_64",
                        "arm64",
                    ],
                    check=True,
                )


if __name__ == "__main__":
    main(*map(Path, sys.argv[1:]))
