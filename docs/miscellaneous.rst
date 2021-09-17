==============
 Miscellaneous
==============

Convert to str
--------------

Any ``CharsetMatch`` object can be transformed to exploitable ``str`` variable.

 ::

    my_byte_str = '我没有埋怨，磋砣的只是一些时间。'.encode('gb18030')

    # Assign return value so we can fully exploit result
    result = from_bytes(
        my_byte_str
    ).best()

    # This should print '我没有埋怨，磋砣的只是一些时间。'
    print(str(result))
