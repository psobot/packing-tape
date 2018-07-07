from unittest import TestCase
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


class TestBitStruct(TestCase):
    def test_create(self):
        instance = BitStruct(
            int_a=0xFFFFFFFF,
            bit_a=True,
            bit_b=False,
            int_b=0x01020304)
        assert "\xFF\xFF\xFF\xFF\x00\x00\x00@\x01\x02\x03\x04" == \
            instance.serialize()

    def test_parse(self):
        instance = BitStruct.parse_from(
            "\xFF\xFF\xFF\xFF\xab\xab\xab\x42\x01\x02\x03\x04")
        assert instance.int_a == 0xFFFFFFFF
        assert instance.int_b == 0x01020304
        assert instance.bits == 0x42
        assert instance.bit_a is True
        assert instance.bit_b is False

    def test_mutate(self):
        instance = BitStruct.parse_from(
            "\xFF\xFF\xFF\xFF\xab\xab\xab\x42\x01\x02\x03\x04")
        instance.bit_a = False
        assert instance.bit_a is False
        assert "\xFF\xFF\xFF\xFF\x00\x00\x00\x02\x01\x02\x03\x04" == \
            instance.serialize()
