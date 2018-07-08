from unittest import TestCase
from packing_tape import Struct
from packing_tape.constants import Big
from packing_tape.fields import integer, embed


class IntStruct(Struct):
    signature = integer(
        signed=False,
        endianness=Big,
        validate=lambda x: x == 1234)


class ValidStruct(Struct):
    int_a = integer(signed=False, endianness=Big, validate=lambda x: x < 50)
    int_b = integer(signed=False, endianness=Big, validate=lambda x: x > 50)
    embedded = embed(IntStruct, default=IntStruct(signature=1234))


class TestValidStruct(TestCase):
    def test_create_simple(self):
        instance = ValidStruct(int_a=60, int_b=40, allow_invalid=True)
        assert not instance.validate(False)
        assert not instance.is_valid

        try:
            instance.validate()
        except ValueError:
            pass
        else:
            self.fail("Expected exception, got nothing.")

    def test_parse_simple(self):
        instance = ValidStruct.parse_from(
            "\xFF\xFF\xFF\xFF\x01\x02\x03\x04\x00\x00\x04\xd2",
            raise_exception=False)
        assert instance is None

        try:
            instance = ValidStruct.parse_from(
                "\xFF\xFF\xFF\xFF\x01\x02\x03\x04\x00\x00\x04\xd2")
        except ValueError:
            pass
        else:
            self.fail("Expected exception, got nothing.")

    def test_parse_simple_allow_invalid(self):
        instance = ValidStruct.parse_from(
            "\xFF\xFF\xFF\xFF\x01\x02\x03\x04\x00\x00\x04\xd2",
            allow_invalid=True)
        assert instance.int_a == 0xFFFFFFFF
        assert instance.int_b == 0x01020304

    def test_parse_invalid_embedded(self):
        assert ValidStruct.parse_from(
            "\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00\xd2",
            raise_exception=False) is None

        try:
            ValidStruct.parse_from(
                "\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00\xd2")
        except ValueError:
            pass
        else:
            self.fail("Expected exception, got nothing.")
