from unittest import TestCase
from simplestruct import SimpleStruct
from simplestruct.constants import Big
from simplestruct.field_types import integer


class GapSimpleStruct(SimpleStruct):
    int_a = integer(signed=False, endianness=Big)
    int_b = integer(signed=False, endianness=Big, offset=8)


class TestGapSimpleStruct(TestCase):

    def test_create_simple(self):
        instance = GapSimpleStruct(int_a=0xFFFFFFFF, int_b=0x01020304)
        assert "\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x01\x02\x03\x04" == \
            instance.serialize()

    def test_parse_simple(self):
        instance = GapSimpleStruct.parse_from(
            "\xFF\xFF\xFF\xFF\xab\xab\xab\xab\x01\x02\x03\x04")
        assert instance.int_a == 0xFFFFFFFF
        assert instance.int_b == 0x01020304

    def test_mutate(self):
        instance = GapSimpleStruct.parse_from(
            "\xFF\xFF\xFF\xFF\xab\xab\xab\xab\x01\x02\x03\x04")
        instance.int_b = 0xFFFFFFFF
        assert instance.int_b == 0xFFFFFFFF
        assert "\xFF\xFF\xFF\xFF\x00\x00\x00\x00\xFF\xFF\xFF\xFF" == \
            instance.serialize()
