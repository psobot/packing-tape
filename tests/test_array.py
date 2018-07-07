from unittest import TestCase
from packing_tape import Struct
from packing_tape.constants import Big
from packing_tape.fields import integer, array


# class ArrayStruct(Struct):
#     array1 = array(
#         integer(signed=False, endianness=Big, validate=lambda x: x < 50))


# class TestArrayStruct(TestCase):
#     def test_create_valid(self):
#         assert ArrayStruct(array1=[40, 40, 40]).is_valid
#         assert ArrayStruct(array1=[40, 40, 40]).array1 == [40, 40, 40]

#     def test_parse_valid(self):
#         valid = ArrayStruct.parse_from(
#             "\x00\x00\x00\x28\x00\x00\x00\x28\x00\x00\x00\x28")
#         assert valid.is_valid
#         assert valid.array1 == [40, 40, 40]
