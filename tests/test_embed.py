from unittest import TestCase
from simplestruct import SimpleStruct
from simplestruct.constants import Big
from simplestruct.field_types import integer, embed


class IntSimpleStruct(SimpleStruct):
    int_a = integer(signed=False, endianness=Big)


class EmbedSimpleStruct(SimpleStruct):
    struct_a = embed(IntSimpleStruct)
    int_b = integer(signed=False, endianness=Big)


class TestEmbedSimpleStruct(TestCase):
    def test_create(self):
        instance = EmbedSimpleStruct(
            struct_a=IntSimpleStruct(int_a=0x12345678),
            int_b=0x01020304)
        assert "\x12\x34\x56\x78\x01\x02\x03\x04" == instance.serialize()

    def test_parse(self):
        instance = EmbedSimpleStruct.parse_from(
            "\x12\x34\x56\x78\x01\x02\x03\x04")
        assert instance.struct_a.int_a == 0x12345678
        assert instance.int_b == 0x01020304

    def test_mutate(self):
        instance = EmbedSimpleStruct.parse_from(
            "\x12\x34\x56\x78\x01\x02\x03\x04")
        assert instance.struct_a.int_a == 0x12345678
        assert instance.int_b == 0x01020304
        instance.struct_a.int_a = 0x45678912
        assert instance.struct_a.int_a == 0x45678912
        assert "\x45\x67\x89\x12\x01\x02\x03\x04" == instance.serialize()
