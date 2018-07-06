from __future__ import print_function

from fields import BinaryProperty, LogicalProperty, Nameable

from utils import as_xxd


def gap_size(property, next):
    if property is None or next is None:
        return 0
    return next.offset - (property.offset + property.size)


try:
    from colorama import Fore
    AVAILABLE_COLORS = [
        Fore.BLUE,
        Fore.CYAN,
        Fore.GREEN,
        Fore.MAGENTA,
        Fore.RED,
        Fore.YELLOW,
    ]
except ImportError:
    AVAILABLE_COLORS = []


class SimpleStruct(object):
    __names_propagated = False

    @classmethod
    def binary_properties(cls):
        return sorted([
            (p, getattr(cls, p))
            for p in dir(cls)
            if isinstance(getattr(cls, p), BinaryProperty)
        ], key=lambda x: x[1].sort_order)

    @classmethod
    def logical_properties(cls):
        return sorted([
            (p, getattr(cls, p))
            for p in dir(cls)
            if isinstance(getattr(cls, p), LogicalProperty)
        ], key=lambda x: x[1].sort_order)

    @classmethod
    def propagate_names(cls):
        if cls.__names_propagated:
            return

        for p in dir(cls):
            if isinstance(getattr(cls, p), Nameable):
                getattr(cls, p).set_field_name(p)

        cls.__names_propagated = True

    @classmethod
    def parse_from(
        cls,
        input_bytes,
        allow_invalid=False,
        raise_exception=True
    ):
        cls.propagate_names()

        kwargs = {}
        for property_name, property in cls.binary_properties():
            kwargs[property_name] = property.parse_from(
                input_bytes[property.offset:property.offset + property.size]
            )
        instance = cls(**kwargs)
        if not allow_invalid:
            if not instance.validate(raise_exception):
                return None
        return instance

    @classmethod
    def size(cls):
        return sum([x.size for _, x in cls.binary_properties()])

    def __init__(self, **kwargs):
        self.__class__.propagate_names()
        self.struct_values = {}

        # Make sure we initialize proxies last
        binary_properties = self.binary_properties()
        binary_properties_dict = dict(binary_properties)
        for (k, v) in kwargs.iteritems():
            if k in binary_properties_dict:
                setattr(self, k, v)
        for property_name, property in binary_properties:
            if property_name not in kwargs:
                property.initialize_with_default(self)
        for (k, v) in kwargs.iteritems():
            # Proxies are not in the binary_properties dict
            if k not in binary_properties_dict:
                setattr(self, k, v)

    def serialize(self):
        parts = []
        previous = None
        for (property_name, property) in self.binary_properties():
            gap = gap_size(previous, property)
            if gap > 0:
                parts.append("\x00" * gap)
            parts.append(property.serialize(self))
            previous = property
        return "".join(parts)

    @property
    def is_valid(self):
        return self.validate(False)

    def validate(self, raise_exception=True):
        for property_name, property in self.logical_properties():
            if not property.validate(self, raise_exception):
                return False
        return True

    def as_hex(self, colorize=False, show_legend=True):
        color_array = []
        header = ''

        if colorize and AVAILABLE_COLORS:
            color_index = 0
            legend = []

            used_positions_and_colors = {}
            for (property_name, property) in self.logical_properties():
                position = (property.offset, property.offset + property.size)

                existing_color = used_positions_and_colors.get(position)
                if existing_color:
                    chosen_color = existing_color
                else:
                    chosen_color = AVAILABLE_COLORS[
                        color_index % len(AVAILABLE_COLORS)
                    ]
                    color_index += 1
                    used_positions_and_colors[position] = chosen_color

                color_array.append((position, chosen_color))
                legend.append(((property_name, property), chosen_color))

            if show_legend:
                header += "%s\nLegend:\n\t" % (self)
                header += "\n\t".join([
                    "%s%s: %s%s" % (
                        color,
                        property_name,
                        property.fget(self),
                        Fore.RESET
                    )
                    for ((property_name, property), color) in legend
                ])
                header += "\n"
        data = as_xxd(self.serialize(), colors=color_array)
        return header + data
