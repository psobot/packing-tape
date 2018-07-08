from packing_tape import Struct
from packing_tape.constants import Big
from packing_tape.fields import integer, bitfield, bit, empty, string, embed


class EmbeddedStruct(Struct):
    int_b = integer(signed=False, endianness=Big)
    int_c = integer(signed=False, endianness=Big)
    int_d = integer(signed=False, endianness=Big)
    int_e = integer(signed=False, endianness=Big)


class MyStruct(Struct):
    int_a = integer(signed=False, endianness=Big)

    empty_space = empty(size=3)

    bits = bitfield(
        empty(),
        bit(),
        empty(size=5),
        bit(),
    )

    bit_a, bit_b = bits.expand()

    embedded = embed(EmbeddedStruct, default=EmbeddedStruct(2, 3, 4, 5))


instance = MyStruct(
    int_a=0xFFFFFFFF,
    bit_a=True,
    bit_b=False,
    int_b=0x01020304,
    str_a="foo")

print instance.as_hex(True)
