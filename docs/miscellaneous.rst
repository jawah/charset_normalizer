==============
 Miscellaneous
==============

Convert to str
--------------

Any ``CharsetNormalizerMatch`` object can be transformed to exploitable ``str`` variable.

 ::

    my_byte_str = '我没有埋怨，磋砣的只是一些时间。'.encode('gb18030')

    # Assign return value so we can fully exploit result
    result = CnM.from_bytes(
        my_byte_str
    ).best().first()

    # This should print '我没有埋怨，磋砣的只是一些时间。'
    print(str(result))


Expect UnicodeDecodeError
-------------------------

This package also offer you the possibility to reconfigure the way ``UnicodeDecodeError`` is raised.
Charset Normalizer offer the possibility to extend the actual message inside it to provide a clue about what
encoding it should actually be.

 ::

    import charset_normalizer  # Nothing else is needed

    my_byte_str = '我没有埋怨，磋砣的只是一些时间。'.encode('gb18030')
    my_byte_str.decode('utf_8')  # raise UnicodeDecodeError

    # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xce in position 0: invalid continuation byte; you may want to consider gb18030 codec for this sequence.
    # instead of
    # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xce in position 0: invalid continuation byte

Here, the addition is "you may want to consider gb18030 codec for this sequence.".
Is does not work when using ``try`` .. ``except`` block.
