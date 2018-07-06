from unittest import TestCase
from packing_tape import Struct
from packing_tape.constants import Big
from packing_tape.field_types import integer


class GapStruct(Struct):
    int_a = integer(signed=False, endianness=Big)
    int_b = integer(signed=False, endianness=Big, offset=8)


class TestGapStruct(TestCase):

    def test_create_simple(self):
        instance = GapStruct(int_a=0xFFFFFFFF, int_b=0x01020304)
        assert "\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x01\x02\x03\x04" == \
            instance.serialize()

    def test_parse_simple(self):
        instance = GapStruct.parse_from(
            "\xFF\xFF\xFF\xFF\xab\xab\xab\xab\x01\x02\x03\x04")
        assert instance.int_a == 0xFFFFFFFF
        assert instance.int_b == 0x01020304

    def test_mutate(self):
        instance = GapStruct.parse_from(
            "\xFF\xFF\xFF\xFF\xab\xab\xab\xab\x01\x02\x03\x04")
        instance.int_b = 0xFFFFFFFF
        assert instance.int_b == 0xFFFFFFFF
        assert "\xFF\xFF\xFF\xFF\x00\x00\x00\x00\xFF\xFF\xFF\xFF" == \
            instance.serialize()
