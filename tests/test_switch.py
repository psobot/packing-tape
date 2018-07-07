from unittest import TestCase
from packing_tape import Struct
from packing_tape.constants import Big, Little
from packing_tape.fields import integer, one_of, string, embed


class SwitchStruct(Struct):
    int_a = one_of(
        integer(signed=False, endianness=Big, validate=lambda x: x < 50),
        integer(signed=False, endianness=Little, validate=lambda x: x > 100))


class TestSwitchStruct(TestCase):
    def test_create_valid(self):
        assert SwitchStruct(int_a=40).is_valid
        assert SwitchStruct(int_a=40).int_a == 40
        assert SwitchStruct(int_a=110).is_valid
        assert SwitchStruct(int_a=110).int_a == 110

    def test_create_invalid(self):
        invalid = SwitchStruct(int_a=55)
        assert not invalid.is_valid
        assert invalid.int_a is None

    def test_parse_valid(self):
        valid = SwitchStruct.parse_from("\x00\x00\x00\x01")
        assert valid.is_valid
        assert valid.int_a == 1

    def test_parse_valid_big_endian(self):
        valid = SwitchStruct.parse_from("\x00\x00\x00\xFF")
        assert valid.is_valid
        assert valid.int_a == 0xFF << 24


class EmbeddedSwitchStruct1(Struct):
    string = string(size=7, validate=lambda x: x == "good")


class EmbeddedSwitchStruct2(Struct):
    int1 = integer(signed=False, endianness=Big, default=1)
    int2 = integer(signed=False, endianness=Big, default=2)


class ComplexSwitchStruct(Struct):
    value = one_of(
        embed(EmbeddedSwitchStruct1),
        embed(EmbeddedSwitchStruct2))


class TestComplexSwitchStruct(TestCase):
    def test_create_valid(self):
        result = ComplexSwitchStruct(
            value=EmbeddedSwitchStruct1(string='good'))
        assert result.is_valid
        assert result.value.string == 'good'
        assert isinstance(result.value, EmbeddedSwitchStruct1)

        result = ComplexSwitchStruct(value=EmbeddedSwitchStruct2())
        assert result.is_valid
        assert isinstance(result.value, EmbeddedSwitchStruct2)
        assert result.value.int1 == 1
        assert result.value.int2 == 2

    def test_parse_valid(self):
        valid = ComplexSwitchStruct.parse_from(
            "\x00\x00\x00\x01\x00\x00\x00\x02")
        assert valid.is_valid
        assert valid.value.int1 == 1
        assert valid.value.int2 == 2

        valid = ComplexSwitchStruct.parse_from("good\x00\x00\x00\x00")
        assert valid.is_valid
        assert valid.value.string == "good"
