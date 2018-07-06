from unittest import TestCase
from packing_tape import Struct
from packing_tape.constants import Big
from packing_tape.field_types import integer, empty


class EmptyStruct(Struct):
    int_a = integer(signed=False, endianness=Big)
    empty_space = empty(size=3)
    int_b = integer(signed=False, endianness=Big)


class TestEmptyStruct(TestCase):
    def test_create(self):
        instance = EmptyStruct(int_a=0xFFFFFFFF, int_b=0x01020304)
        assert "\xFF\xFF\xFF\xFF\x00\x00\x00\x01\x02\x03\x04" == \
            instance.serialize()

    def test_parse(self):
        instance = EmptyStruct.parse_from(
            "\xFF\xFF\xFF\xFF\xab\xab\xab\x01\x02\x03\x04")
        assert instance.int_a == 0xFFFFFFFF
        assert instance.int_b == 0x01020304

    def test_mutate(self):
        instance = EmptyStruct.parse_from(
            "\xFF\xFF\xFF\xFF\xab\xab\xab\x01\x02\x03\x04")
        instance.int_b = 0xFFFFFFFF
        assert instance.int_b == 0xFFFFFFFF
        assert "\xFF\xFF\xFF\xFF\x00\x00\x00\xFF\xFF\xFF\xFF" == \
            instance.serialize()
