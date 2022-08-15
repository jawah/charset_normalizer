Optional speedup extension
===========================

Why?
-------

charset-normalizer will always remain pure Python, meaning that a environment without any build-capabilities will
run this program without any additional requirements.

Nonetheless, starting from the version 3.0 we introduce and publish some platform specific wheels including a
pre-build extension.

Most of the time is spent in the module `md.py` so we decided to "compile it" using Mypyc.

(1) It does not require to have a separate code base
(2) Our project code base is rather simple and lightweight
(3) Mypyc is robust enough today
(4) Four times faster!

How?
-------

If your platform and/or architecture is not served by this swift optimization you may compile it easily yourself.
Following those instructions (provided you have the necessary toolchain installed):

  ::

    git clone https://github.com/Ousret/charset_normalizer.git
    cd charset_normalizer
    git checkout 3.0
    pip install -r dev-requirements.txt
    python setup.py --use-mypyc install


How not to?
-------

You may install charset-normalizer without any specific (pre-built wheel) by directly using the universal wheel
(most likely hosted on PyPi or any valid mirror you use)

  ::

    pip install https://........./charset_normalizer-3.0.0b2-py3-none-any.whl

Directly.
