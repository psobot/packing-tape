from validatable import Validatable


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

    @property
    def sort_order(self):
        return self.index


class LogicalProperty:
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

    def serialize_value(self, value):
        raise NotImplementedError("Must implement serialize_value!")


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
    """

    @property
    def storage_key(self):
        return hash(self)

    def get(self, target):
        return self.get_key(target, self.storage_key)

    def set(self, target, val):
        self.set_key(target, self.storage_key, val)

    def get_key(self, target, key):
        return target._get_struct_value(key)

    def set_key(self, target, key, val):
        target._set_struct_value(key, val)


class StorageTarget:
    """
    Allows arbitrary key value pairs to be stored.
    """

    def _get_struct_value(self, key):
        if not hasattr(self, '_struct_values'):
            return None
        return self._struct_values.get(key)

    def _set_struct_value(self, key, val):
        if not hasattr(self, '_struct_values'):
            setattr(self, '_struct_values', {})
        self._struct_values[key] = val


class Nameable:
    field_name = None

    def set_field_name(self, name):
        self.field_name = name
