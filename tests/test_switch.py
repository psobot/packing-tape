from unittest import TestCase
from packing_tape import Struct
from packing_tape.constants import Big
from packing_tape.field_types import integer


class ValidStruct(Struct):
    int_a = integer(signed=False, endianness=Big, validate=lambda x: x < 50)
    int_b = integer(signed=False, endianness=Big, validate=lambda x: x > 50)


class TestValidStruct(TestCase):
    def test_create_simple(self):
        instance = ValidStruct(int_a=60, int_b=40)
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
            "\xFF\xFF\xFF\xFF\x01\x02\x03\x04",
            raise_exception=False)
        assert instance is None

        try:
            instance = ValidStruct.parse_from(
                "\xFF\xFF\xFF\xFF\x01\x02\x03\x04")
        except ValueError:
            pass
        else:
            self.fail("Expected exception, got nothing.")

    def test_parse_simple_allow_invalid(self):
        instance = ValidStruct.parse_from(
            "\xFF\xFF\xFF\xFF\x01\x02\x03\x04",
            allow_invalid=True)
        assert instance.int_a == 0xFFFFFFFF
        assert instance.int_b == 0x01020304
