import os
from unittest import TestCase
from packing_tape import Struct
from packing_tape.fields import integer, string, embed, array_of, one_of, empty

"""
This test attempts to parse an Apple Logic EXS24 sampler instrument,
which is a proprietary binary format with its roots in the 90s.
"""


class EXSObjectHeader(Struct):
    type_signature = integer()
    size = integer()
    object_id = integer()
    unknown = integer()
    atom = string(
        size=4,
        null_terminated=False,
        validate=lambda v: v in ('TBOS', 'JBOS'))
    name = string(size=64)


class EXSHeader(Struct):
    object_header = embed(
        EXSObjectHeader,
        validate=lambda header: header.type_signature in (0x00000101,))
    unknown = empty(164 - EXSObjectHeader.min_size())


class EXSZone(Struct):
    object_header = embed(
        EXSObjectHeader,
        validate=lambda header: header.type_signature in (0x01000101,))
    unknown = empty(220 - EXSObjectHeader.min_size())


class EXSGroup(Struct):
    object_header = embed(
        EXSObjectHeader,
        validate=lambda header: header.type_signature in (0x02000101,))
    unknown = empty(216 - EXSObjectHeader.min_size())


class EXSSample(Struct):
    object_header = embed(
        EXSObjectHeader,
        validate=lambda header: header.type_signature in (0x03000101,))
    unknown = empty(676 - EXSObjectHeader.min_size())


class EXSParam(Struct):
    object_header = embed(
        EXSObjectHeader,
        validate=lambda header: header.type_signature in (0x04000101,))
    unknown = empty(472 - EXSObjectHeader.min_size())


class EXSFile(Struct):
    objects = array_of(one_of(
        EXSHeader, EXSZone, EXSGroup, EXSSample, EXSParam))


class TestEXSHeaderParsing(TestCase):
    def test_parse_valid(self):
        filedir = os.path.realpath(os.path.dirname(__file__))
        test_file_path = os.path.join(filedir, '68 Bell Player.exs')
        indata = open(test_file_path).read()

        header = EXSFile.parse_from(indata)
        assert len(header.objects) == 618
        assert isinstance(header.objects[0], EXSHeader)

        assert len(header.serialize()) == len(indata)
