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


from field_classes import EmbeddedField, ArrayField, FieldProxy, ProxyTarget
from bases import DummyProperty


def generate_colors_and_header(obj, colorize=False, show_legend=False):
    legend_generator = LegendGenerator(obj, colorize, show_legend)
    return legend_generator.colors, legend_generator.header


class LegendGenerator(object):
    def __init__(self, obj, colorize=False, show_legend=False):
        self.obj = obj
        self.colorize = colorize
        self.show_legend = show_legend

        self.offset = 0
        self.color_index = 0

        self._header = []
        self.colors = []
        self.used_positions_and_colors = {}

        if self.show_legend:
            self._header.append(str(obj))

        if self.colorize and AVAILABLE_COLORS:
            self.generate(self.obj)

    @property
    def header(self):
        return "\n".join(self._header + [''])

    def generate(self, obj, tab_depth=1):
        tabs = "\t" * tab_depth

        for (property_name, property) in obj.all_properties():
            property_value = property.fget(obj)

            # TODO: OH GOD WHY, WE HAVE POLYMORPHIC OBJECTS,
            # WHY AM I CHECKING isisnstance EVERYWHERE
            if isinstance(property, EmbeddedField):
                if self.show_legend:
                    self._header.append(tabs + str(property_value))
                self.generate(property_value, tab_depth + 1)
                continue

            if isinstance(property, ArrayField):
                if self.show_legend:
                    self._header.append("%s%d objects:" % (
                        tabs,
                        len(property_value)))
                for sub_object in property_value:
                    self._header.append("%s%s" % (
                        "\t" * (tab_depth + 1),
                        sub_object))
                    self.generate(sub_object, tab_depth + 2)
                continue

            if not isinstance(property, FieldProxy):
                end = self.offset + property.get_size(obj)

            position = (self.offset, end)
            self.offset = end

            if isinstance(property, ProxyTarget) \
                    or isinstance(property, DummyProperty):
                continue

            existing_color = self.used_positions_and_colors.get(position)
            if existing_color:
                chosen_color = existing_color
            else:
                chosen_color = AVAILABLE_COLORS[
                    self.color_index % len(AVAILABLE_COLORS)
                ]
                self.color_index += 1
                self.used_positions_and_colors[position] = chosen_color

            self.colors.append((position, chosen_color))

            self._header.append(
                "%s%s%s: %s%s" % (
                    tabs,
                    chosen_color,
                    property_name,
                    property_value,
                    Fore.RESET
                ))
