=====================
 Register new Charset
=====================

Add a new encoding to the detector
----------------------------------

Charset-Normalizer don't have to know about your encoding to be able to detect it.
This library is rather agnostic of encodings and tries its best to be generic.

If Python knows about your encoding, we will be able to attempt detecting it.

How it works
~~~~~~~~~~~~

Charset-Normalizer iterates through every encoding registered in Python's ``encodings.aliases`` registry.
If your custom encoding is registered there, it will be tried automatically alongside the built-in ones.

Python provides a codec registration mechanism via ``codecs.register()`` that lets you plug in any
encoding table. Once registered, both Python's ``str.encode()``/``bytes.decode()`` **and** Charset-Normalizer
will recognize it.

Registering a custom encoding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is a complete example that registers a fictitious single-byte encoding called ``x-my-encoding``.

**Step 1 -- Define the codec**

A codec needs at minimum an ``IncrementalDecoder``, an ``IncrementalEncoder``, and a ``codec_info`` search
function. For a simple byte-to-character mapping, you only need a decoding table (256 entries). ::

    import codecs

    # Decoding table: maps each byte (0x00-0xFF) to a Unicode character.
    # Start from latin-1 as a base and override specific positions.
    DECODING_TABLE = list(bytes(range(256)).decode("latin-1"))

    # Example: remap bytes 0x80-0x83 to specific characters
    DECODING_TABLE[0x80] = "\u0410"  # А (Cyrillic)
    DECODING_TABLE[0x81] = "\u0411"  # Б
    DECODING_TABLE[0x82] = "\u0412"  # В
    DECODING_TABLE[0x83] = "\u0413"  # Г

    DECODING_TABLE = "".join(DECODING_TABLE)

    # Build the encoding map (reverse lookup: character -> byte)
    ENCODING_MAP = codecs.charmap_build(DECODING_TABLE)

**Step 2 -- Create the codec classes** ::

    class MyCodec(codecs.Codec):
        def encode(self, input, errors="strict"):
            return codecs.charmap_encode(input, errors, ENCODING_MAP)

        def decode(self, input, errors="strict"):
            return codecs.charmap_decode(input, errors, DECODING_TABLE)


    class MyIncrementalEncoder(codecs.IncrementalEncoder):
        def encode(self, input, final=False):
            return codecs.charmap_encode(input, self.errors, ENCODING_MAP)[0]


    class MyIncrementalDecoder(codecs.IncrementalDecoder):
        def decode(self, input, final=False):
            return codecs.charmap_decode(input, self.errors, DECODING_TABLE)[0]


    class MyStreamReader(MyCodec, codecs.StreamReader):
        pass


    class MyStreamWriter(MyCodec, codecs.StreamWriter):
        pass

**Step 3 -- Create a helper that returns the CodecInfo** ::

    def _get_codec_info():
        return codecs.CodecInfo(
            name="x_my_encoding",
            encode=MyCodec().encode,
            decode=MyCodec().decode,
            incrementalencoder=MyIncrementalEncoder,
            incrementaldecoder=MyIncrementalDecoder,
            streamreader=MyStreamReader,
            streamwriter=MyStreamWriter,
        )

**Step 4 -- Register the codec with Python** ::

    codecs.register(
        lambda name: _get_codec_info()
        if name in ("x-my-encoding", "x_my_encoding")
        else None
    )

**Step 5 -- Make it discoverable by Charset-Normalizer**

Charset-Normalizer uses ``importlib.import_module("encodings.<name>")`` internally to
inspect the ``IncrementalDecoder`` of each encoding. A codec registered only via
``codecs.register()`` won't have a corresponding module. You need to create one::

    import sys
    import types
    from encodings.aliases import aliases

    # Expose the codec as a module so the import-based lookup works.
    mod = types.ModuleType("encodings.x_my_encoding")
    mod.IncrementalDecoder = MyIncrementalDecoder
    mod.IncrementalEncoder = MyIncrementalEncoder
    mod.getregentry = _get_codec_info
    sys.modules["encodings.x_my_encoding"] = mod

    # Register the alias so it appears in the candidate list.
    aliases["x_my_encoding"] = "x_my_encoding"

.. warning::

   Both the module registration and the alias **must happen before** importing
   ``charset_normalizer``. The candidate list is built once at import time from
   ``encodings.aliases``.

**Step 6 -- Verify** ::

    from charset_normalizer import from_bytes

    sample = (
        b"Hello world, this is a test of custom encoding "
        b"with mapped bytes: \x80\x81\x82\x83 mixed in here."
    )

    results = from_bytes(sample, cp_isolation=["x_my_encoding"])
    best = results.best()
    print(best.encoding)   # x_my_encoding
    print(str(best))        # Hello world, ... АБВГ mixed in here.

Important notes
~~~~~~~~~~~~~~~

- The codec **must** provide an ``IncrementalDecoder``. Charset-Normalizer uses incremental
  decoding internally and will skip encodings that don't provide one.
- For single-byte encodings, ``codecs.charmap_decode`` / ``codecs.charmap_encode`` handle everything.
  For multi-byte encodings, you will need a more involved decoder implementation.
- You do **not** need to modify any Charset-Normalizer source code. The library dynamically
  discovers encodings from the ``encodings.aliases`` registry at runtime.

Using ``cp_isolation`` to target your encoding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you only want to test your custom encoding (useful during development), use the
``cp_isolation`` parameter::

    results = from_bytes(sample, cp_isolation=["x_my_encoding"])

This restricts detection to only the specified encoding(s), making the output deterministic
and the execution faster.
