from struct import unpack_from, pack


class SpaceOccupyingProperty:
    """
    Any property that takes up one or more bytes, even if a DummyProperty.
    """


class BinaryProperty(SpaceOccupyingProperty):
    """
    A property that should be written out to the binary stream.
    Includes things like integers and bitfields, but not single bits.
    Contrast with logical properties.
    """
    pass


class LogicalProperty:
    """
    A property that has semantic or logical meaning in Python,
    but not at the bitstream level (i.e.: maybe a single bit).
    Contrast with binary properties.
    """
    pass


class DummyProperty(SpaceOccupyingProperty):
    """
    A filler property that has no meaning to the binary stream or
    in Python land.
    """
    pass


class Validatable:
    def validate(self, instance, raise_exception=True):
        return self.validate_value(
            self.fget(instance),
            raise_exception,
            instance)

    def preprocess_value_for_validator(self, value):
        return value

    def validate_value(self, value, raise_exception=False, instance='unknown'):
        """
        Given a value (not an instance), run the appropriate validators on it.
        """
        if self.validator is None:
            return True
        if not self.validator(self.preprocess_value_for_validator(value)):
            message = \
                'Field "%s" failed validation (value "%s", instance %s)' % (
                    self.field_name if hasattr(self, 'field_name') else self,
                    value,
                    instance)
            if not raise_exception:
                return False
            raise ValueError(message)
        return True


class Nameable:
    field_name = None

    def set_field_name(self, name):
        self.field_name = name


class ByteAlignedStructField(
    property,
    BinaryProperty,
    LogicalProperty,
    Validatable,
    Nameable
):
    def __init__(
        self,
        format_string,
        size,
        signed,
        endianness,
        offset,
        default=0,
        validate=None
    ):
        super(ByteAlignedStructField, self).__init__(
            fget=self.fget, fset=self.fset)

        self.format_string = format_string
        self.size = size
        self.signed = signed
        self.endianness = endianness
        self.offset = offset
        self.default = default
        self.validator = validate

    @property
    def sort_order(self):
        return self.offset

    def initialize_with_default(self, instance):
        self.fset(instance, self.default)

    def fget(self, instance):
        return instance.struct_values[hash(self)]

    def fset(self, instance, val):
        instance.struct_values[hash(self)] = val

    def parse_from(self, stream):
        return unpack_from(self.format_string, stream, 0)[0]

    def serialize(self, instance):
        return pack(self.format_string, self.fget(instance))

    def __repr__(self):
        attrs = (
            "field_name",
            "format_string",
            "size",
            "signed",
            "endianness",
            "offset",
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
    Nameable
):
    def __init__(
        self,
        size,
        offset,
        default='',
        validate=None
    ):
        super(StringField, self).__init__(
            fget=self.fget, fset=self.fset)

        self.size = size
        self.offset = offset
        self.default = default
        self.validator = validate

    @property
    def sort_order(self):
        return self.offset

    def initialize_with_default(self, instance):
        self.fset(instance, self.default)

    def fget(self, instance):
        return instance.struct_values[hash(self)]

    def fset(self, instance, val):
        instance.struct_values[hash(self)] = val

    def parse_from(self, stream):
        return unpack_from(str(self.size) + 's', stream, 0)[0].rstrip("\x00")

    def serialize(self, instance):
        return pack(str(self.size) + 's', self.fget(instance))

    def __repr__(self):
        attrs = (
            "field_name",
            "size",
            "offset",
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
    Nameable
):
    def __init__(
        self,
        struct_type,
        offset,
        default=None,
        validate=None
    ):
        super(EmbeddedField, self).__init__(
            fget=self.fget, fset=self.fset)
        self.struct_type = struct_type
        self.offset = offset
        self.default = default
        self.validator = validate

    @property
    def size(self):
        return self.struct_type.size()

    @property
    def sort_order(self):
        return self.offset

    def initialize_with_default(self, instance):
        self.fset(instance, self.default)

    def fget(self, instance):
        return instance.struct_values[hash(self)]

    def fset(self, instance, val):
        instance.struct_values[hash(self)] = val

    def parse_from(self, stream):
        return self.struct_type.parse_from(stream, allow_invalid=True)

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
            "offset",
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
    Nameable
):
    def __init__(
        self,
        subfields,
        offset,
        default=None
    ):
        super(SwitchField, self).__init__(
            fget=self.fget, fset=self.fset)
        self.subfields = subfields
        self.offset = offset
        self.default = default

    @property
    def size(self):
        # TODO: Allow for variable sizing based on instance data.
        return sum([s.size for s in self.subfields])

    @property
    def sort_order(self):
        return self.offset

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

    def parse_from(self, stream):
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
            "offset",
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
    def __init__(self, size):
        self.size = size

    default = 0


class Bit(object):
    size = 1

    def __init__(self, default=False, validate=None):
        self.default = default
        self.validator = validate


class FieldProxy(property, LogicalProperty, Nameable):
    parent = None

    @property
    def sort_order(self):
        return self.parent.sort_order + (self.offset * 0.001)


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
    def offset(self):
        return self.parent.offset

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


class Bitfield(property, ProxyTarget, BinaryProperty, Nameable):
    # TODO: Should inherit from ByteAlignedStructField
    size = 1

    def __init__(self, offset, *members):
        super(Bitfield, self).__init__(
            fget=self.fget,
            fset=self.fset)
        if sum([m.size for m in members]) != 8:
            raise ValueError(
                "Members passed to Bitfield must sum to 8 "
                "bits (got: %s)." % [m.size for m in members])
        self.members = members
        self.offset = offset

    @property
    def sort_order(self):
        return self.offset

    def fget(self, instance):
        return instance.struct_values[hash(self)]

    def fset(self, instance, val):
        instance.struct_values[hash(self)] = val

    def parse_from(self, stream):
        return unpack_from('B', stream, 0)[0]

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
        return "<%s members=%s>" % (
            self.__class__.__name__,
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
