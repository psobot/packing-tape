from struct import unpack_from, pack, calcsize
from bases import BinaryProperty, \
    LogicalProperty, \
    DummyProperty, \
    Nameable, \
    Validatable, \
    Parseable, \
    Serializable, \
    Storable, \
    StorageTarget


class ByteAlignedStructField(
    property,
    BinaryProperty,
    LogicalProperty,
    Validatable,
    Nameable,
    Parseable,
    Serializable,
    Storable
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
            fget=self.get, fset=self.set)

        self.format_string = format_string
        self.size = size
        self.signed = signed
        self.endianness = endianness
        self.index = index
        self.default = default
        self.validator = validate

    def initialize_with_default(self, instance):
        self.set(instance, self.default)

    def parse_and_get_size(self, stream):
        return (
            unpack_from(self.format_string, stream, 0)[0],
            calcsize(self.format_string)
        )

    @property
    def min_size(self):
        return calcsize(self.format_string)

    def serialize(self, instance):
        return pack(self.format_string, self.get(instance))

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
    Parseable,
    Serializable,
    Storable
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
            fget=self.get, fset=self.set)

        self.size = size
        self.index = index
        self.null_terminated = null_terminated
        self.default = default
        self.validator = validate

    @property
    def sort_order(self):
        return self.index

    def initialize_with_default(self, instance):
        self.set(instance, self.default)

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
            return pack(self.format_string, self.get(instance))[:-1] + "\x00"
        else:
            return pack(self.format_string, self.get(instance))

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
    Parseable,
    Serializable,
    Storable
):
    def __init__(
        self,
        struct_type,
        index,
        default=None,
        validate=None
    ):
        super(EmbeddedField, self).__init__(
            fget=self.get, fset=self.set)
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
        self.set(instance, self.default)

    def parse_and_get_size(self, stream):
        instance = self.struct_type.parse_from(stream, allow_invalid=True)
        return instance, instance.size

    @property
    def min_size(self):
        return self.struct_type.min_size()

    def serialize(self, instance):
        return self.get(instance).serialize()

    def validate(self, instance, raise_exception=True):
        value = self.get(instance)
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
    Parseable,
    Serializable,
    Storable
):
    def __init__(
        self,
        subfields,
        index,
        default=None
    ):
        super(SwitchField, self).__init__(
            fget=self.get, fset=self.set)
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
        self.set(instance, self.default)

    def get_real_type(self, instance):
        return super(SwitchField, self).get(instance)

    def set_real_type(self, instance, type):
        super(SwitchField, self).set(instance, type)

    def get(self, instance):
        real_type = self.get_real_type(instance)
        if real_type:
            return real_type.get(instance)
        else:
            return None

    def set(self, instance, val):
        for subfield in self.subfields:
            if subfield.validate_value(val, raise_exception=False):
                subfield.set(instance, val)
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
        val = self.get(instance)
        return real_type.validate_value(
            val,
            raise_exception=raise_exception,
            instance=instance)

    def validate_value(self, val, raise_exception=True, instance='unknown'):
        for subfield in self.subfields:
            if subfield.validate_value(val, raise_exception=False):
                real_type = subfield
                break
        else:
            if raise_exception:
                raise ValueError(
                    "No valid subfields would accept value %s for %s" % (
                        val, self))
            else:
                return False

        return real_type.validate_value(
            val,
            raise_exception=raise_exception,
            instance=instance)

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
    Parseable,
    Serializable,
    Storable
):
    def __init__(
        self,
        subfield,
        index,
        default=None  # TODO: add minimum and maximum number of elements?
    ):
        super(ArrayField, self).__init__(
            fget=self.get, fset=self.set)
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
        self.set(instance, self.default)

    def get_storage_targets(self, instance):
        return super(ArrayField, self).get(instance)

    def set_storage_targets(self, instance, targets):
        return super(ArrayField, self).set(instance, targets)

    def get(self, instance):
        targets = super(ArrayField, self).get(instance)
        return [self.subfield.get(target) for target in targets]

    def set(self, instance, vals):
        if not isinstance(vals, list) and not isinstance(vals, tuple):
            raise ValueError(
                "This property (%s) requires an array or tuple value." % (
                    instance))
        # Create a new StorageTarget for each of the sub-values present.
        self.set_storage_targets(instance, [StorageTarget() for _ in vals])

        # Call the subfield's setter but passing each of these targets
        # instead of the original instance.
        for target, val in zip(self.get_storage_targets(instance), vals):
            self.subfield.set(target, val)

    def parse_and_get_size(self, stream):
        results = []
        total_size = 0
        while (total_size + self.subfield.min_size) <= len(stream):
            result, size = self.subfield.parse_and_get_size(
                stream[total_size:])

            if not self.subfield.validate_value(result, raise_exception=False):
                print "Subfield could not validate: %s" % result
                break

            results.append(result)
            total_size += size
        return results, total_size

    @property
    def min_size(self):
        return 0

    def serialize_value(self, values):
        return "".join([
            self.subfield.serialize_value(val)
            for val in values
        ])

    def validate(self, instance, raise_exception=True):
        values = self.get(instance)
        storage_targets = self.get_storage_targets(instance)
        if values:
            return all([
                self.subfield.validate_value(
                    value,
                    raise_exception=raise_exception,
                    instance=target)
                for (target, value) in zip(storage_targets, values)
            ])
        else:
            return True

    def __repr__(self):
        attrs = (
            "field_name",
            "subfield",
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
            fget=self.get,
            fset=self.set)
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

    def get(self, instance):
        value = self.parent.get(instance)
        if isinstance(value, str):
            asint = ord(value)
        else:
            asint = value
        return bool(asint & self.bitmask)

    def set(self, instance, value):
        existing_field_value = self.parent.get(instance)
        existing_field_value &= ~self.bitmask
        if value:
            existing_field_value |= self.bitmask
        return self.parent.set(instance, existing_field_value)


class Bitfield(property, ProxyTarget, BinaryProperty, Parseable,
               Serializable,
               Storable, Nameable):
    size = 1
    field_count = 8

    def __init__(self, index, *members):
        super(Bitfield, self).__init__(
            fget=self.get,
            fset=self.set)
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

    def parse_and_get_size(self, stream):
        return (unpack_from('B', stream, 0)[0], self.size)

    @property
    def min_size(self):
        return self.size

    def serialize(self, instance):
        return pack('B', self.get(instance))

    def initialize_with_default(self, instance):
        default = 0
        defaults = [member.default for member in self.members]
        for i, bit_default in enumerate(defaults):
            default <<= 1
            default |= 1 if bit_default else 0
        self.set(instance, default)

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
