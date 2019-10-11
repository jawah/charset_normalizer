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

    print(result.encoding)  # gb18030

Using CharsetNormalizerMatch
----------------------------

Here, ``result`` is a ``CharsetNormalizerMatch`` object or ``None``.

.. autoclass:: charset_normalizer.CharsetNormalizerMatch
    :members:

