import sys

from fields import ByteAlignedStructField, \
    StringField, \
    Empty, \
    Bitfield, \
    Bit, \
    EmbeddedField, \
    SwitchField
from fields import SpaceOccupyingProperty

from constants import (
    Big,
    Little,
    SIGNED_CHAR,
    UNSIGNED_CHAR,
    LITTLE_ENDIAN_UNSIGNED_INT,
    LITTLE_ENDIAN_SIGNED_INT,
    BIG_ENDIAN_UNSIGNED_INT,
    BIG_ENDIAN_SIGNED_INT,
)


def empty(size=1):
    return Empty(size)


def bit():
    return Bit()


def bitfield(*members, **kwargs):
    offset = kwargs.get('offset')
    offset = infer_offset_from_position_or(offset)
    return Bitfield(offset, *members)


def unsigned_char(offset):
    return ByteAlignedStructField(
        offset=offset,
        format_string=UNSIGNED_CHAR,
        size=1,
        signed=False)


def signed_char(offset):
    return ByteAlignedStructField(
        offset=offset,
        format_string=SIGNED_CHAR,
        size=1,
        signed=True)


def little_endian_unsigned_integer(offset, default=0, validate=None):
    return ByteAlignedStructField(
        offset=offset,
        format_string=LITTLE_ENDIAN_UNSIGNED_INT,
        size=4,
        signed=False,
        endianness=Little,
        default=default,
        validate=validate)


def little_endian_signed_integer(offset, default=0, validate=None):
    return ByteAlignedStructField(
        offset=offset,
        format_string=LITTLE_ENDIAN_SIGNED_INT,
        size=4,
        signed=True,
        endianness=Little,
        default=default,
        validate=validate)


def big_endian_unsigned_integer(offset, default=0, validate=None):
    return ByteAlignedStructField(
        offset=offset,
        format_string=BIG_ENDIAN_UNSIGNED_INT,
        size=4,
        signed=False,
        endianness=Big,
        default=default,
        validate=validate)


def big_endian_signed_integer(offset, default=0, validate=None):
    return ByteAlignedStructField(
        offset=offset,
        format_string=BIG_ENDIAN_SIGNED_INT,
        size=4,
        signed=True,
        endianness=Big,
        default=default,
        validate=validate)


def string(size, offset=None, default='', validate=None):
    offset = infer_offset_from_position_or(offset)
    return StringField(
        offset=offset,
        size=size,
        default=default,
        validate=validate)


def embed(struct_type, offset=None, default=None, validate=None):
    offset = infer_offset_from_position_or(offset)
    return EmbeddedField(
        struct_type,
        offset=offset,
        default=default,
        validate=validate)


def one_of(*types, **kwargs):
    offset, default = kwargs.get("offset"), kwargs.get("default")
    offset = infer_offset_from_position_or(offset)
    return SwitchField(types, offset=offset, default=default)


def infer_offset_from_position_or(offset):
    if offset is None:
        others = sys._getframe(2).f_locals.values()
        existing_properties = [
            p for p in others
            if isinstance(p, SpaceOccupyingProperty)
        ]
        offset = sum([prop.size for prop in existing_properties])
    return offset


def integer(
    signed=False,
    endianness=Little,
    offset=None,
    default=0,
    validate=None
):
    offset = infer_offset_from_position_or(offset)

    if signed:
        if endianness is Little:
            return little_endian_signed_integer(offset, default, validate)
        elif endianness is Big:
            return big_endian_signed_integer(offset, default, validate)
        else:
            raise ValueError("endianness must be Little or Big")
    else:
        if endianness is Little:
            return little_endian_unsigned_integer(offset, default, validate)
        elif endianness is Big:
            return big_endian_unsigned_integer(offset, default, validate)
        else:
            raise ValueError("endianness must be Little or Big")
