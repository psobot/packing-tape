from unittest import TestCase
from packing_tape import Struct
from packing_tape.constants import Big
from packing_tape.field_types import integer, string


class StringStruct(Struct):
    int_a = integer(signed=False, endianness=Big)
    str_a = string(size=4)
    int_b = integer(signed=False, endianness=Big)


class TestStringStruct(TestCase):
    def test_create_simple(self):
        instance = StringStruct(
            int_a=0xFFFFFFFF,
            str_a='flop',
            int_b=0x01020304)
        assert "\xFF\xFF\xFF\xFFflop\x01\x02\x03\x04" == instance.serialize()

    def test_parse_simple(self):
        instance = StringStruct.parse_from(
            "\xFF\xFF\xFF\xFFflop\x01\x02\x03\x04")
        assert instance.int_a == 0xFFFFFFFF
        assert instance.int_b == 0x01020304
        assert instance.str_a == 'flop'
