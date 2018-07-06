from unittest import TestCase
from simplestruct import SimpleStruct
from simplestruct.constants import Big
from simplestruct.field_types import integer


class BasicSimpleStruct(SimpleStruct):
    int_a = integer(signed=False, endianness=Big)
    int_b = integer(signed=False, endianness=Big)


class TestBasicSimpleStruct(TestCase):
    def test_create_simple(self):
        instance = BasicSimpleStruct(int_a=0xFFFFFFFF, int_b=0x01020304)
        assert "\xFF\xFF\xFF\xFF\x01\x02\x03\x04" == instance.serialize()

    def test_parse_simple(self):
        instance = BasicSimpleStruct.parse_from(
            "\xFF\xFF\xFF\xFF\x01\x02\x03\x04")
        assert instance.int_a == 0xFFFFFFFF
        assert instance.int_b == 0x01020304
