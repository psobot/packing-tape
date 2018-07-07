import sys

from field_classes import ByteAlignedStructField, \
    StringField, \
    Empty, \
    Bitfield, \
    Bit, \
    EmbeddedField, \
    SwitchField, \
    ArrayField

from bases import SpaceOccupyingProperty

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
    index = infer_index_from_position()
    return Empty(index, size)


def bit():
    return Bit()


def bitfield(*members, **kwargs):
    index = infer_index_from_position()
    return Bitfield(index, *members)


def unsigned_char():
    index = infer_index_from_position(stack_depth=1)
    return ByteAlignedStructField(
        index=index,
        format_string=UNSIGNED_CHAR,
        size=1,
        signed=False)


def signed_char():
    index = infer_index_from_position(stack_depth=1)
    return ByteAlignedStructField(
        index=index,
        format_string=SIGNED_CHAR,
        size=1,
        signed=True)


def little_endian_unsigned_integer(default=0, validate=None):
    index = infer_index_from_position(stack_depth=1)
    return ByteAlignedStructField(
        index=index,
        format_string=LITTLE_ENDIAN_UNSIGNED_INT,
        size=4,
        signed=False,
        endianness=Little,
        default=default,
        validate=validate)


def little_endian_signed_integer(default=0, validate=None):
    index = infer_index_from_position(stack_depth=1)
    return ByteAlignedStructField(
        index=index,
        format_string=LITTLE_ENDIAN_SIGNED_INT,
        size=4,
        signed=True,
        endianness=Little,
        default=default,
        validate=validate)


def big_endian_unsigned_integer(default=0, validate=None):
    index = infer_index_from_position(stack_depth=1)
    return ByteAlignedStructField(
        index=index,
        format_string=BIG_ENDIAN_UNSIGNED_INT,
        size=4,
        signed=False,
        endianness=Big,
        default=default,
        validate=validate)


def big_endian_signed_integer(default=0, validate=None):
    index = infer_index_from_position(stack_depth=1)
    return ByteAlignedStructField(
        index=index,
        format_string=BIG_ENDIAN_SIGNED_INT,
        size=4,
        signed=True,
        endianness=Big,
        default=default,
        validate=validate)


def string(size, default='', validate=None):
    index = infer_index_from_position(stack_depth=1)
    return StringField(
        index=index,
        size=size,
        default=default,
        validate=validate)


def embed(struct_type, default=None, validate=None):
    index = infer_index_from_position()
    return EmbeddedField(
        struct_type,
        index=index,
        default=default,
        validate=validate)


def one_of(*types, **kwargs):
    return SwitchField(
        types,
        index=infer_index_from_position(stack_depth=1),
        default=kwargs.get("default"))


def array(subtype, **kwargs):
    return ArrayField(
        subtype,
        index=infer_index_from_position(stack_depth=1),
        default=kwargs.get("default"))


def infer_index_from_position(stack_depth=0):
    others = sys._getframe(stack_depth + 2).f_locals.values()
    return len([
        p for p in others
        if isinstance(p, SpaceOccupyingProperty)
    ])


def integer(signed=False, endianness=Little, default=0, validate=None):
    if signed:
        if endianness is Little:
            return little_endian_signed_integer(default, validate)
        elif endianness is Big:
            return big_endian_signed_integer(default, validate)
        else:
            raise ValueError("endianness must be Little or Big")
    else:
        if endianness is Little:
            return little_endian_unsigned_integer(default, validate)
        elif endianness is Big:
            return big_endian_unsigned_integer(default, validate)
        else:
            raise ValueError("endianness must be Little or Big")
