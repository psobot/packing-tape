from unittest import TestCase
from packing_tape import Struct
from packing_tape.constants import Big
from packing_tape.fields import integer


class BasicStruct(Struct):
    int_a = integer(signed=False, endianness=Big)
    int_b = integer(signed=False, endianness=Big)


class TestBasicStruct(TestCase):
    def test_create_simple(self):
        instance = BasicStruct(int_a=0xFFFFFFFF, int_b=0x01020304)
        assert "\xFF\xFF\xFF\xFF\x01\x02\x03\x04" == instance.serialize()

    def test_parse_simple(self):
        instance = BasicStruct.parse_from(
            "\xFF\xFF\xFF\xFF\x01\x02\x03\x04")
        assert instance.int_a == 0xFFFFFFFF
        assert instance.int_b == 0x01020304
