Advanced Search
===============

Charset Normalizer method ``from_bytes``, ``from_fp`` and ``from_path`` provide some
optional parameters that can be tweaked.

As follow ::

    CharsetDetector.from_bytes(
        my_byte_str,
        steps=10,  # Number of steps/block to extract from my_byte_str
        chunk_size=512,  # Set block size of each extraction
        threshold=0.2,  # Maximum amount of chaos allowed on first pass
        cp_isolation=None,  # Finite list of encoding to use when searching for a match
        cp_exclusion=None,  # Finite list of encoding to avoid when searching for a match
        preemptive_behaviour=True,  # Determine if we should look into my_byte_str (ASCII-Mode) for pre-defined encoding
        explain=False  # Print on screen what is happening when searching for a match
    )

!! Warning !! Work in Progress Documentation !!
