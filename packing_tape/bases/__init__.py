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


class DummyProperty(BinaryProperty):
    """
    A filler property that has no meaning to the binary stream or
    in Python land.
    """
    pass


class Nameable:
    field_name = None

    def set_field_name(self, name):
        self.field_name = name
