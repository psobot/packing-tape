from __future__ import print_function

from field_classes import \
    BinaryProperty, LogicalProperty, Nameable, ProxyTarget

from bases import StorageTarget

from utils import as_xxd


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


class Struct(object, StorageTarget):
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
    def min_size(cls):
        return sum([p.min_size for _, p in cls.binary_properties()])

    @classmethod
    def parse_from(
        cls,
        input_bytes,
        allow_invalid=False,
        raise_exception=True
    ):
        cls.propagate_names()

        kwargs = {}
        offset = 0
        for property_name, property in cls.binary_properties():
            data = input_bytes[offset:]
            min_size = property.min_size
            if len(data) < min_size:
                if allow_invalid:
                    # TODO: Should we store the fact that
                    # the buffer was too small?
                    break
                else:
                    if raise_exception:
                        raise ValueError(
                            (
                                "Not enough buffer left to decode %s "
                                "(needed at least %d bytes, had %d)"
                            ) % (
                                cls.__name__,
                                offset + min_size,
                                offset + len(data)
                            )
                        )
                    return None
            val, size = property.parse_and_get_size(data)
            offset += size
            if isinstance(property, LogicalProperty) \
                    or isinstance(property, ProxyTarget):
                kwargs[property_name] = val

        kwargs['allow_invalid'] = allow_invalid
        kwargs['raise_exception'] = raise_exception
        instance = cls(**kwargs)
        if not allow_invalid:
            if not instance.validate(raise_exception):
                return None

        return instance

    @property
    def size(self):
        return len(self.serialize())

    RESERVED_KWARGS = ('allow_invalid', 'raise_exception')

    def __init__(self, **kwargs):
        self.__class__.propagate_names()

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
            if k not in binary_properties_dict \
                    and k not in self.RESERVED_KWARGS:
                setattr(self, k, v)

        # As Python constructors can never return None,
        # we should only call validate if we're allowed to raise an exception.
        if not kwargs.get('allow_invalid', False) \
                and kwargs.get('raise_exception', True):
            self.validate(raise_exception=True)

    def serialize(self):
        return "".join([
            property.serialize(self)
            for (_, property) in self.binary_properties()
        ])

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
