from unittest import TestCase
from packing_tape import Struct
from packing_tape.constants import Big
from packing_tape.field_types import integer, embed


class IntStruct(Struct):
    int_a = integer(signed=False, endianness=Big)


class EmbedStruct(Struct):
    struct_a = embed(IntStruct)
    int_b = integer(signed=False, endianness=Big)


class TestEmbedStruct(TestCase):
    def test_create(self):
        instance = EmbedStruct(
            struct_a=IntStruct(int_a=0x12345678),
            int_b=0x01020304)
        assert "\x12\x34\x56\x78\x01\x02\x03\x04" == instance.serialize()

    def test_parse(self):
        instance = EmbedStruct.parse_from(
            "\x12\x34\x56\x78\x01\x02\x03\x04")
        assert instance.struct_a.int_a == 0x12345678
        assert instance.int_b == 0x01020304

    def test_mutate(self):
        instance = EmbedStruct.parse_from(
            "\x12\x34\x56\x78\x01\x02\x03\x04")
        assert instance.struct_a.int_a == 0x12345678
        assert instance.int_b == 0x01020304
        instance.struct_a.int_a = 0x45678912
        assert instance.struct_a.int_a == 0x45678912
        assert "\x45\x67\x89\x12\x01\x02\x03\x04" == instance.serialize()
