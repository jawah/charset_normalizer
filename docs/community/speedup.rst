Optional speedup extension
==========================

Why?
----

charset-normalizer will always retain a pure Python implementation, so environments
without native build capabilities can use it without additional requirements.

Platform-specific wheels include pre-built Cython extensions for the mess and
coherence detectors. The extensions preserve the public Python API while moving
their hot loops to C.

When no compatible native wheel is available, charset-normalizer automatically
falls back to the pure Python implementation.

How?
----

If your platform or architecture is not served by a native wheel, you can compile
the extensions locally with a C compiler and Python development headers:

  ::

    export CHARSET_NORMALIZER_USE_CYTHON=1
    pip install charset-normalizer --no-binary charset-normalizer

Native x86-64 and ARM64 extension builds on Linux, macOS and Windows use
profile-guided optimization (PGO) by default with GCC, Clang or MSVC. The build
trains the extensions in a separate Python process using the text samples
bundled in ``data/``. To compile in a single pass, set
``CHARSET_NORMALIZER_USE_PGO=0`` alongside
``CHARSET_NORMALIZER_USE_CYTHON=1``. Set the same opt-out under CPU emulation.
Maintainers can set the GitHub Actions repository variable
``CHARSET_NORMALIZER_USE_PGO`` to ``0`` for CI and release builds.

How not to?
-----------

You may install charset-normalizer without the extensions by building the source
distribution without setting ``CHARSET_NORMALIZER_USE_CYTHON``.

E.g. when installing ``requests`` and you don't want to use the ``charset-normalizer`` speedups, you can do:

  ::

    pip install requests --no-binary charset-normalizer


When installing `charset-normalizer` by itself, you can also pass ``:all:`` as the specifier to ``--no-binary``.

  ::

    pip install charset-normalizer --no-binary :all:
