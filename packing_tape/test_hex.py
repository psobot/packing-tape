from packing_tape import Struct
from packing_tape.constants import Big
from packing_tape.fields import integer, bitfield, bit, empty


class BitStruct(Struct):
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


instance = BitStruct(
    int_a=0xFFFFFFFF,
    bit_a=True,
    bit_b=False,
    int_b=0x01020304)

print instance.as_hex(True)
