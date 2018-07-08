from validatable import Validatable


class Sizeable:
    def get_size(self, storage_target):
        """
        A convenience method to allow properties to specify a static
        or dynamic size as a regular property or as a function.
        """
        return self.size


class SpaceOccupyingProperty:
    """
    Any property that takes up one or more bytes, even if a DummyProperty.
    """


class BinaryProperty(SpaceOccupyingProperty, Sizeable):
    """
    A property that should be written out to the binary stream.
    Includes things like integers and bitfields, but not single bits.
    Contrast with logical properties.
    """

    @property
    def sort_order(self):
        return self.index


class LogicalProperty(Sizeable):
    """
    A property that has semantic or logical meaning in Python,
    but not at the bitstream level (i.e.: maybe a single bit).
    Contrast with binary properties.
    """
    pass


class Parseable:
    """
    A property that requires parsing from the bitstream.
    """
    def parse_and_get_size(self, stream):
        """
        Returns a tuple of (
            Python logical value,
            number of bytes consumed from the bitstream
        )
        """
        raise NotImplementedError("Must implement parse_and_get_size!")

    @property
    def min_size(self):
        raise NotImplementedError("Must implement min_size!")


class Serializable:
    """
    A property that can be written to the bitstream.
    """
    def serialize(self, instance):
        return self.serialize_value(self.get(instance))


class DummyProperty(BinaryProperty):
    """
    A filler property that has no meaning to the binary stream or
    in Python land.
    """
    pass


class Storable:
    """
    Given some `instance` object with a `__struct_values` parameter,
    this class implements methods for storing arbitrary key-value data
    on that object keyed by an object.

    The methods in this class get hit very often, so try to keep them
    as small and lightweight as possible, duplicating logic if need be.
    """

    def get(self, target):
        try:
            return target._struct_values.get(hash(self))
        except AttributeError:
            return None

    def set(self, target, val):
        key = hash(self)
        try:
            target._struct_values[key] = val
        except AttributeError:
            setattr(target, '_struct_values', {key: val})


class StorageTarget:
    """
    Allows arbitrary key value pairs to be stored.
    """
    pass


class Nameable:
    field_name = None

    def set_field_name(self, name):
        self.field_name = name
