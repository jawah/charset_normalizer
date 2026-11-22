"""Two-pass build for native CPython extensions on supported desktop targets."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import sysconfig
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterator

from setuptools.command.build_ext import build_ext  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]


def _compiler_macros(command: list[str]) -> set[bytes]:
    # CC and its flags may override the target that setuptools reports.
    probe = subprocess.run(
        [*command, "-dM", "-E", "-x", "c", "-"], input=b"", capture_output=True
    )
    if probe.returncode:
        return set()
    return {
        line.split()[1]
        for line in probe.stdout.splitlines()
        if line.startswith(b"#define ")
    }


def _toolchain(compiler: Any, plat_name: str) -> str | None:
    """Select a profiler only if this interpreter can train the compiled target."""
    machine = platform.machine().lower()
    arch = {"amd64": "x86_64", "arm64": "aarch64"}.get(machine, machine)
    if sys.implementation.name != "cpython" or arch not in {"x86_64", "aarch64"}:
        return None
    if sys.platform == "win32":
        target = "win-amd64" if arch == "x86_64" else "win-arm64"
        if (
            compiler.compiler_type == "msvc"
            and plat_name == sysconfig.get_platform() == target
        ):
            return "msvc"
        return None
    if compiler.compiler_type != "unix":
        return None
    command = compiler.compiler_so
    if sys.platform == "darwin":
        target = "arm64" if arch == "aarch64" else arch
        archflags = os.environ.get("ARCHFLAGS", "").split()
        if not plat_name.startswith("macosx-") or not plat_name.endswith("-" + target):
            return None
        if archflags and archflags != ["-arch", target]:
            return None
        from _osx_support import compiler_fixup  # type: ignore[import-not-found]

        command = compiler_fixup(command, [])
        os_macro = b"__ENVIRONMENT_MAC_OS_X_VERSION_MIN_REQUIRED__"
    elif sys.platform == "linux" and plat_name == "linux-" + arch:
        os_macro = b"__linux__"
    else:
        return None
    macros = _compiler_macros(command)
    target_macro = b"__aarch64__" if arch == "aarch64" else b"__x86_64__"
    if not {os_macro, b"__GNUC__", target_macro}.issubset(macros):
        return None
    if b"__ILP32__" in macros or b"__ANDROID__" in macros:
        return None
    return "clang" if b"__clang__" in macros else "gcc"


def _pgo_flags(
    toolchain: str, profiles: Path, binary: Path, *, instrument: bool
) -> tuple[list[str], list[str]]:
    if toolchain == "msvc":
        option = "/GENPROFILE" if instrument else "/USEPROFILE"
        return ["/GL"], ["/LTCG", f"{option}:PGD={binary.with_suffix('.pgd')}"]
    if toolchain == "clang":
        if instrument:
            return ["-fprofile-instr-generate"], ["-fprofile-instr-generate"]
        return [
            f"-fprofile-instr-use={profiles / 'training.profdata'}",
            "-Werror=profile-instr-unprofiled",
            "-Werror=profile-instr-out-of-date",
        ], []
    if instrument:
        flag = f"-fprofile-generate={profiles}"
        return [flag], [flag]
    flag = f"-fprofile-use={profiles}"
    return [flag, "-Werror=missing-profile", "-Werror=coverage-mismatch"], [flag]


def _msvc_pgo_runtime(compiler: Path, target: str) -> Path:
    # setuptools can use Hostx86/x64/cl.exe for an x64 build. MSVC also
    # ships the target's profiling runtime under bin/Hostx64/x64.
    compiler_dir = compiler.resolve().parent
    arch = {"win-amd64": "x64", "win-arm64": "arm64"}[target]
    native_dir = compiler_dir.parent.parent / ("Host" + arch) / arch
    paths = [directory / "pgort140.dll" for directory in (native_dir, compiler_dir)]
    for path in paths:
        if path.is_file():
            return path
    raise RuntimeError(
        f"Missing {arch} MSVC profiling runtime. Checked: {', '.join(map(str, paths))}"
    )


class PGOBuildExt(build_ext):  # type: ignore[misc]
    build_lib: str
    build_temp: str
    force: bool

    def build_extensions(self) -> None:
        toolchain = _toolchain(self.compiler, self.plat_name)
        if toolchain is None:
            super().build_extensions()
            return

        with TemporaryDirectory(prefix="charset-pgo-") as temp:
            scratch = Path(temp)
            stage = scratch / "lib"
            profiles = scratch / "profiles"
            profiles.mkdir()
            with self._staged_build(stage, scratch / "objects"):
                binaries = [
                    Path(self.get_ext_fullpath(ext.name)) for ext in self.extensions
                ]
                self._build_pass(toolchain, profiles, instrument=True)
                self._train(toolchain, stage, profiles, binaries)
                self._build_pass(toolchain, profiles, instrument=False)

            # Publish only the optimized binaries into the wheel's build tree.
            for ext, binary in zip(self.extensions, binaries):
                output = Path(self.get_ext_fullpath(ext.name))
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(binary, output)

    @contextmanager
    def _staged_build(self, stage: Path, objects: Path) -> Iterator[None]:
        """Use the same paths for both forced builds so profile data matches."""
        source_root = ROOT / "src"
        for source in (source_root / "charset_normalizer").rglob("*.py"):
            target = stage / source.relative_to(source_root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

        build_lib, build_temp = self.build_lib, self.build_temp
        force, compiler_force = self.force, self.compiler.force
        try:
            self.build_lib, self.build_temp = str(stage), str(objects)
            self.force = self.compiler.force = True
            yield
        finally:
            self.build_lib, self.build_temp = build_lib, build_temp
            self.force, self.compiler.force = force, compiler_force

    def _build_pass(self, toolchain: str, profiles: Path, *, instrument: bool) -> None:
        original_flags = [
            (ext, ext.extra_compile_args, ext.extra_link_args)
            for ext in self.extensions
        ]
        try:
            for ext, compile_args, link_args in original_flags:
                binary = Path(self.get_ext_fullpath(ext.name))
                compile_flags, link_flags = _pgo_flags(
                    toolchain, profiles, binary, instrument=instrument
                )
                ext.extra_compile_args = [*compile_args, *compile_flags]
                ext.extra_link_args = [*link_args, *link_flags]
            super().build_extensions()
        finally:
            for ext, compile_args, link_args in original_flags:
                ext.extra_compile_args = compile_args
                ext.extra_link_args = link_args

    def _train(
        self, toolchain: str, stage: Path, profiles: Path, binaries: list[Path]
    ) -> None:
        package_dir = binaries[0].parent
        env = os.environ.copy()
        if toolchain == "clang":
            env["LLVM_PROFILE_FILE"] = str(profiles / "%m.profraw")
        elif toolchain == "msvc":
            runtime = _msvc_pgo_runtime(Path(self.compiler.cc), self.plat_name)
            shutil.copy2(runtime, package_dir)

        trainer = ROOT / "bin" / "train_pgo.py"
        subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(trainer), str(stage)],
            cwd=package_dir,
            env=env,
            check=True,
        )

        if toolchain == "clang":
            raw = sorted(profiles.glob("*.profraw"))
            if len(raw) < len(binaries):
                raise RuntimeError("Missing Clang profiles after PGO training")
            profdata = ["llvm-profdata"]
            if sys.platform == "darwin":
                profdata = ["xcrun", "llvm-profdata"]
            merged = profiles / "training.profdata"
            subprocess.run(
                [*profdata, "merge", "-o", str(merged), *map(str, raw)], check=True
            )
        elif toolchain == "msvc":
            for binary in binaries:
                if not any(package_dir.glob(binary.stem + "!*.pgc")):
                    raise RuntimeError(
                        f"Missing MSVC training counts for {binary.name}"
                    )
        # GCC diagnoses missing or incompatible profiles in the second pass.
