from simplestruct import SimpleStruct
from simplestruct.constants import Big
from simplestruct.field_types import integer, bitfield, bit, empty


class BitSimpleStruct(SimpleStruct):
    int_a = integer(signed=False, endianness=Big)

    empty_space = empty(size=3)

    bits = bitfield(
        empty(),
        bit(),
        empty(size=5),
        bit(),
    )

    bit_a, bit_b = bits.expand()

    int_b = integer(signed=False, endianness=Big)
    int_b = integer(signed=False, endianness=Big)
    int_b = integer(signed=False, endianness=Big)
    int_b = integer(signed=False, endianness=Big)
    int_b = integer(signed=False, endianness=Big)
    int_b = integer(signed=False, endianness=Big)
    int_b = integer(signed=False, endianness=Big)


instance = BitSimpleStruct(
    int_a=0xFFFFFFFF,
    bit_a=True,
    bit_b=False,
    int_b=0x01020304)

print instance.as_hex(True)
