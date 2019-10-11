Installation
============

This installs a package that can be used from Python (``import charset_normalizer``).

To install for all users on the system, administrator rights (root) may be required.

Using PIP
---------
Charset Normalizer can be installed from pip::

    pip install charset-normalizer

You may enable extra feature unicode data v12 backport as follow::

    pip install charset-normalizer[UnicodeDataBackport]

From git via master
-----------------------
You can install from dev-master branch using git::

    git clone https://github.com/Ousret/charset_normalizer.git
    cd charset_normalizer/
    python setup.py install

Basic Usage
===========

The new way
-----------

You may want to get right to it. ::

    from charset_normalizer import CharsetNormalizerMatches as CnM

    # This is going to print out your sequence once properly decoded
    print(
        CnM.from_bytes(
            my_byte_str
        ).best().first()
    )

    # You could also want the same from a file
    print(
        CnM.from_path(
            './data/sample.1.ar.srt'
        ).best().first()
    )


Backward compatibility
----------------------

If you were used to python chardet, we are providing the very same ``detect()`` method as chardet.

 ::

    from charset_normalizer import detect

    # This will behave exactly the same as python chardet
    result = detect(my_byte_str)

    if result['encoding'] is not None:
        print('got', result['encoding'], 'as detected encoding')


You may upgrade your code with ease.
CTRL + R ``from chardet import detect`` to ``from charset_normalizer import detect``.
