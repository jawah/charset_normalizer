Advanced Search
===============

Charset Normalizer method ``from_bytes``, ``from_fp`` and ``from_path`` provide some
optional parameters that can be tweaked.

As follow ::

    from charset_normalizer import CharsetNormalizerMatches as CnM

    my_byte_str = '我没有埋怨，磋砣的只是一些时间。'.encode('gb18030')

    results = CnM.from_bytes(
        my_byte_str,
        steps=10,  # Number of steps/block to extract from my_byte_str
        chunk_size=512,  # Set block size of each extraction
        threshold=0.2,  # Maximum amount of chaos allowed on first pass
        cp_isolation=None,  # Finite list of encoding to use when searching for a match
        cp_exclusion=None,  # Finite list of encoding to avoid when searching for a match
        preemptive_behaviour=True,  # Determine if we should look into my_byte_str (ASCII-Mode) for pre-defined encoding
        explain=False  # Print on screen what is happening when searching for a match
    )


Using CharsetNormalizerMatches
------------------------------

Here, ``results`` is a ``CharsetNormalizerMatches`` object. It behave like a list.
Initially it is not sorted. Be cautious when extracting ``first()`` result without calling method ``best()``.

.. autoclass:: charset_normalizer.CharsetNormalizerMatches
    :members:

List behaviour
--------------

Like said earlier, ``CharsetNormalizerMatches`` object behave like a list.

  ::

    # Call len on results also work
    if len(results) == 0:
        print('No match for your sequence')

    # Iterate over results like a list
    for match in results:
        print(match.encoding, 'can decode properly your sequence using', match.alphabets, 'and language', match.language)

    # Using index to access results
    if len(results) > 0:
        print(str(results[0]))

Using best()
------------

Like said above, ``CharsetNormalizerMatches`` object behave like a list and it is not sorted after calling
``from_bytes``, ``from_fp`` or ``from_path``.

Using ``best()`` keep only the lowest chaotic results and in it the best coherent result if necessary.
It produce also a ``CharsetNormalizerMatches`` object as return value.

 ::

    results = results.best()

Calling first()
---------------

This method is callable from a ``CharsetNormalizerMatches`` object. It extract the first match in list.
This method return a ``CharsetNormalizerMatch`` object. See Handling result section.

Class aliases
-------------

``CharsetNormalizerMatches`` is also known as ``CharsetDetector``, ``CharsetDoctor`` and ``EncodingDetector``.
It is useful if you prefer short class name.

Verbose output
--------------

You may want to understand why a specific encoding was not picked by charset_normalizer. All you have to do is passing
``explain`` to True when using methods ``from_bytes``, ``from_fp`` or ``from_path``.
