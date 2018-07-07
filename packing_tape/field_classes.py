from struct import unpack_from, pack, calcsize
from bases import BinaryProperty, \
    LogicalProperty, \
    DummyProperty, \
    Nameable, \
    Validatable, \
    Parseable


class ByteAlignedStructField(
    property,
    BinaryProperty,
    LogicalProperty,
    Validatable,
    Nameable,
    Parseable
):
    def __init__(
        self,
        format_string,
        size,
        signed,
        endianness,
        index,
        default=0,
        validate=None
    ):
        super(ByteAlignedStructField, self).__init__(
            fget=self.fget, fset=self.fset)

        self.format_string = format_string
        self.size = size
        self.signed = signed
        self.endianness = endianness
        self.index = index
        self.default = default
        self.validator = validate

    def initialize_with_default(self, instance):
        self.fset(instance, self.default)

    def fget(self, instance):
        return instance.struct_values[hash(self)]

    def fset(self, instance, val):
        instance.struct_values[hash(self)] = val

    def parse_and_get_size(self, stream):
        return (
            unpack_from(self.format_string, stream, 0)[0],
            calcsize(self.format_string)
        )

    @property
    def min_size(self):
        return calcsize(self.format_string)

    def serialize(self, instance):
        return pack(self.format_string, self.fget(instance))

    def __repr__(self):
        attrs = (
            "field_name",
            "format_string",
            "size",
            "signed",
            "endianness",
            "index",
        )

        return "<%s %s>" % (
            self.__class__.__name__,
            " ".join([
                "%s=%s" % (attr, getattr(self, attr))
                for attr in attrs
            ])
        )


class StringField(
    property,
    BinaryProperty,
    LogicalProperty,
    Validatable,
    Nameable,
    Parseable
):
    def __init__(
        self,
        size,
        index,
        null_terminated=True,
        default='',
        validate=None
    ):
        super(StringField, self).__init__(
            fget=self.fget, fset=self.fset)

        self.size = size
        self.index = index
        self.null_terminated = null_terminated
        self.default = default
        self.validator = validate

    @property
    def sort_order(self):
        return self.index

    def initialize_with_default(self, instance):
        self.fset(instance, self.default)

    def fget(self, instance):
        return instance.struct_values[hash(self)]

    def fset(self, instance, val):
        instance.struct_values[hash(self)] = val

    @property
    def format_string(self):
        return str(self.size) + 's'

    def parse_and_get_size(self, stream):
        return (
            unpack_from(self.format_string, stream, 0)[0].rstrip("\x00"),
            calcsize(self.format_string)
        )

    @property
    def min_size(self):
        return calcsize(self.format_string)

    def serialize(self, instance):
        if self.null_terminated:
            return pack(self.format_string, self.fget(instance))[:-1] + "\x00"
        else:
            return pack(self.format_string, self.fget(instance))

    def __repr__(self):
        attrs = (
            "field_name",
            "size",
            "index",
        )

        return "<%s %s>" % (
            self.__class__.__name__,
            " ".join([
                "%s=%s" % (attr, getattr(self, attr))
                for attr in attrs
            ])
        )


class EmbeddedField(
    property,
    BinaryProperty,
    LogicalProperty,
    Validatable,
    Nameable,
    Parseable
):
    def __init__(
        self,
        struct_type,
        index,
        default=None,
        validate=None
    ):
        super(EmbeddedField, self).__init__(
            fget=self.fget, fset=self.fset)
        self.struct_type = struct_type
        self.index = index
        self.default = default
        self.validator = validate

    @property
    def size(self):
        return self.struct_type.size()

    @property
    def sort_order(self):
        return self.index

    def initialize_with_default(self, instance):
        self.fset(instance, self.default)

    def fget(self, instance):
        return instance.struct_values[hash(self)]

    def fset(self, instance, val):
        instance.struct_values[hash(self)] = val

    def parse_and_get_size(self, stream):
        instance = self.struct_type.parse_from(stream, allow_invalid=True)
        return instance, instance.size

    @property
    def min_size(self):
        return self.struct_type.min_size()

    def serialize(self, instance):
        return self.fget(instance).serialize()

    def validate(self, instance, raise_exception=True):
        value = self.fget(instance)
        if value is None:
            return False
        return self.validate_value(value, raise_exception, instance)

    def validate_value(self, value, raise_exception=False, instance='unknown'):
        if self.validator is not None:
            if self.validator(value):
                pass
            elif not raise_exception:
                return False
            else:
                if hasattr(self, 'field_name'):
                    field_name = self.field_name
                else:
                    field_name = self
                raise ValueError(
                    'Field "%s" is invalid (value "%s", instance %s)' % (
                        field_name, value, instance))
        return value.validate(raise_exception=raise_exception)

    def __repr__(self):
        attrs = (
            "field_name",
            "struct_type",
            "index",
            "default",
        )

        return "<%s %s>" % (
            self.__class__.__name__,
            " ".join([
                "%s=%s" % (attr, getattr(self, attr))
                for attr in attrs
            ])
        )


class SwitchField(
    property,
    BinaryProperty,
    LogicalProperty,
    Validatable,
    Nameable,
    Parseable
):
    def __init__(
        self,
        subfields,
        index,
        default=None
    ):
        super(SwitchField, self).__init__(
            fget=self.fget, fset=self.fset)
        self.subfields = subfields
        self.index = index
        self.default = default

    @property
    def size(self):
        # TODO: Allow for variable sizing based on instance data.
        return sum([s.size for s in self.subfields])

    @property
    def sort_order(self):
        return self.index

    def initialize_with_default(self, instance):
        self.fset(instance, self.default)

    def get_real_type(self, instance):
        return instance.struct_values.get(hash(self))

    def set_real_type(self, instance, type):
        instance.struct_values[hash(self)] = type

    def fget(self, instance):
        real_type = self.get_real_type(instance)
        if real_type:
            return real_type.fget(instance)
        else:
            return None

    def fset(self, instance, val):
        for subfield in self.subfields:
            subfield.fset(instance, val)
            if subfield.validate(instance, raise_exception=False):
                self.set_real_type(instance, subfield)
                return

    def parse_and_get_size(self, stream):
        for subfield in self.subfields:
            if len(stream) < subfield.min_size:
                continue
            result, size = subfield.parse_and_get_size(stream)

            # TODO: Expose a better API from subfields so that we don't
            # have to do this hackety hack:
            if hasattr(subfield, 'validate_value'):
                if subfield.validate_value(result, raise_exception=False):
                    return result, size
            else:
                raise ValueError("Subfield has no validator!")
        if all(len(stream) < subfield.min_size for subfield in self.subfields):
            raise ValueError(
                "All subfields had minimum sizes greater than the available "
                "data - no subfields parsed! (stream = %s)" % repr(stream))
        else:
            raise ValueError("No subfields parsed! (stream = %s)" % repr(
                stream))

    @property
    def min_size(self):
        return min([s.min_size for s in self.subfields])

    def serialize(self, instance):
        return self.get_real_type(instance).serialize(instance)

    def validate(self, instance, raise_exception=True):
        real_type = self.get_real_type(instance)
        if not real_type:
            if raise_exception:
                raise ValueError("No valid subfields found for %s" % self)
            else:
                return False
        return real_type.validate(
            instance,
            raise_exception=raise_exception)

    def __repr__(self):
        attrs = (
            "field_name",
            "subfields",
            "index",
            "default",
        )

        return "<%s %s>" % (
            self.__class__.__name__,
            " ".join([
                "%s=%s" % (attr, getattr(self, attr))
                for attr in attrs
            ])
        )


class ArrayField(
    property,
    BinaryProperty,
    LogicalProperty,
    Validatable,
    Nameable,
    Parseable
):
    def __init__(
        self,
        subfield,
        index,
        default=None  # TODO: add minimum and maximum number of elements?
    ):
        super(ArrayField, self).__init__(
            fget=self.fget, fset=self.fset)
        self.subfield = subfield
        self.index = index
        self.default = default

    @property
    def size(self):
        # TODO: Allow for variable sizing based on instance data.
        return self.subfield

    @property
    def sort_order(self):
        return self.index

    def initialize_with_default(self, instance):
        self.fset(instance, self.default)

    def get_real_type(self, instance):
        return instance.struct_values.get(hash(self))

    def set_real_type(self, instance, type):
        instance.struct_values[hash(self)] = type

    def fget(self, instance):
        real_type = self.get_real_type(instance)
        if real_type:
            return real_type.fget(instance)
        else:
            return None

    def fset(self, instance, val):
        for subfield in self.subfields:
            subfield.fset(instance, val)
            if subfield.validate(instance, raise_exception=False):
                self.set_real_type(instance, subfield)
                return

    def parse_and_get_size(self, stream):
        for subfield in self.subfields:
            result = subfield.parse_from(stream)

            # TODO: Expose a better API from subfields so that we don't
            # have to do this hackety hack:
            if hasattr(subfield, 'validate_value'):
                if subfield.validate_value(result, raise_exception=False):
                    return result
            else:
                raise ValueError("Subfield has no validator!")
        raise ValueError("No subfields parsed! (stream = %s)" % repr(stream))

    @property
    def min_size(self):
        return 0

    def serialize(self, instance):
        return self.get_real_type(instance).serialize(instance)

    def validate(self, instance, raise_exception=True):
        real_type = self.get_real_type(instance)
        if not real_type:
            if raise_exception:
                raise ValueError("No valid subfields found for %s" % self)
            else:
                return False
        return real_type.validate(
            instance,
            raise_exception=raise_exception)

    def __repr__(self):
        attrs = (
            "field_name",
            "subfields",
            "index",
            "default",
        )

        return "<%s %s>" % (
            self.__class__.__name__,
            " ".join([
                "%s=%s" % (attr, getattr(self, attr))
                for attr in attrs
            ])
        )


class Empty(DummyProperty):
    def __init__(self, index, size):
        self.index = index
        self.size = size

    default = 0

    def initialize_with_default(self, instance):
        pass

    def serialize(self, instance):
        return "\x00" * self.size

    def parse_and_get_size(self, instance):
        return None, self.size

    @property
    def min_size(self):
        return self.size


class Bit(object):
    size = 1

    def __init__(self, default=False, validate=None):
        self.default = default
        self.validator = validate


class FieldProxy(property, LogicalProperty, Nameable):
    parent = None

    @property
    def sort_order(self):
        return self.parent.sort_order + (self.index / self.parent.field_count)


class ProxyTarget:
    pass


class BitProxy(FieldProxy, Validatable):
    def __init__(self, parent, bit_index, default=False, validate=None):
        super(BitProxy, self).__init__(
            fget=self.fget,
            fset=self.fset)
        self.parent = parent
        self.bit_index = bit_index
        self.bitmask = 1 << (7 - self.bit_index)
        self.default = default
        self.validator = validate

    @property
    def index(self):
        return self.parent.index

    @property
    def size(self):
        return 1

    def fget(self, instance):
        value = self.parent.fget(instance)
        if isinstance(value, str):
            asint = ord(value)
        else:
            asint = value
        return bool(asint & self.bitmask)

    def fset(self, instance, value):
        existing_field_value = self.parent.fget(instance)
        existing_field_value &= ~self.bitmask
        if value:
            existing_field_value |= self.bitmask
        return self.parent.fset(instance, existing_field_value)


class Bitfield(property, ProxyTarget, BinaryProperty, Parseable, Nameable):
    size = 1
    field_count = 8

    def __init__(self, index, *members):
        super(Bitfield, self).__init__(
            fget=self.fget,
            fset=self.fset)
        if sum([m.size for m in members]) != self.field_count:
            raise ValueError(
                "Members passed to Bitfield must sum to %d "
                "bits (got: %s)." % (
                    self.field_count,
                    [m.size for m in members]))
        self.members = members
        self.index = index

    @property
    def sort_order(self):
        return self.index

    def fget(self, instance):
        return instance.struct_values[hash(self)]

    def fset(self, instance, val):
        instance.struct_values[hash(self)] = val

    def parse_and_get_size(self, stream):
        return (unpack_from('B', stream, 0)[0], self.size)

    @property
    def min_size(self):
        return self.size

    def serialize(self, instance):
        return pack('B', self.fget(instance))

    def initialize_with_default(self, instance):
        default = 0
        defaults = [member.default for member in self.members]
        for i, bit_default in enumerate(defaults):
            default <<= 1
            default |= 1 if bit_default else 0
        self.fset(instance, default)

    def __repr__(self):
        return "<%s index=%d members=%s>" % (
            self.__class__.__name__,
            self.index,
            " ".join([str(member) for member in self.members])
        )

    def expand(self):
        results = []
        index = 0
        for m in self.members:
            if isinstance(m, Bit):
                results.append(BitProxy(self, index, m.default, m.validator))
                index += 1
            elif isinstance(m, Empty):
                index += m.size
        return results
