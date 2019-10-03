================
 Handling Result
================

When initiating search upon a buffer, bytes or file you can assign the return value and fully exploit it.

 ::

    my_byte_str = '我没有埋怨，磋砣的只是一些时间。'.encode('gb18030')

    # Assign return value so we can fully exploit result
    result = CnM.from_bytes(
        my_byte_str
    ).best().first()


Exploit result
---------------

Here, ``result`` is a ``CharsetNormalizerMatch`` object or ``None``.

.. class:: CharsetNormalizerMatch

    .. attribute:: submatch
        :getter: Return a list of submatch that produce the EXACT same output as this one. This return a list of CharsetNormalizerMatch and NOT a CharsetNormalizerMatches.
        :type: list[CharsetNormalizerMatch]

    .. attribute:: has_submatch
        :getter: Determine if current match has any other match linked to it.
        :type: bool

    .. attribute:: alphabets
        :getter: Discover list of alphabet in decoded content
        :type: list[str]

    .. attribute:: could_be_from_charset
        :getter: Return list of possible originating charset that is giving the exact same output
        :type: list[str]

    .. attribute:: coherence
        :getter: Return a value between 0. and 1. Closest to 0. means that the initial string is considered coherent, Closest to 1. means that the initial string SEEMS NOT coherent.
        :type: float

    .. attribute:: languages
        :getter: Return a list of probable language in text. Maximum three.
        :type: list[str]

    .. attribute:: language
        :getter: Return the most probable language found in text. May return 'Unknown' if unavailable.
        :type: str

    .. attribute:: chaos
        :getter: Return a value between 0. and 1. Closest to 1. means that the initial string is considered as chaotic, Closest to 0. means that the initial string SEEMS NOT chaotic.
        :type: float

    .. attribute:: percent_chaos
        :getter: Convert chaos ratio to readable percentage with ndigits=3 from 0.000 % to 100.000 %
        :type: float

    .. attribute:: percent_coherence
        :getter: Convert coherence ratio to readable percentage with ndigits=3 from 0.000 % to 100.000 %
        :type: float

    .. attribute:: chaos_secondary_pass
        :getter: Check once again chaos in decoded text, except this time, with full content. Return ratio between 0. and 1.
        :type: float

    .. attribute:: encoding
        :getter: Guessed possible/probable originating charset. IANA Encoding Name ONLY.
        :type: str

    .. attribute:: encoding_aliases
        :getter: Encoding name are known by many name, using this could help when searching for IBM855 when it's listed as CP855.
        :type: list[str]

    .. attribute:: bom
        :getter: Precise if file has a valid bom or sig associated with discovered encoding.
        :type: bool

    .. attribute:: raw
        :getter: Get untouched bytes content
        :type: bytes

    .. attribute:: fingerprint
        :getter: Generate sha256 checksum of encoded unicode self
        :type: str

    .. method:: output()

        :param str encoding: Target encoding
        :return: Newly encoded content
        :rtype: bytes

        Encode raw content to a new encoding, default to utf_8

Miscellaneous
--------------

Any ``CharsetNormalizerMatch`` object can be transformed to exploitable ``str`` variable.

 ::

    # This should print '我没有埋怨，磋砣的只是一些时间。'
    print(str(result))
