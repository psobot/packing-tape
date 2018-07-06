import string


try:
    # Try to use colorama, but which might not be installed.
    from colorama import Style
    RESET_ALL = Style.RESET_ALL
except ImportError:
    RESET_ALL = ''


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def colorize(i, char, colors):
    """
    Apply the colors from the colors array onto the given
    character given the index i.
    """
    for (start, end), color in colors:
        if start <= i and end > i:
            return color + char + RESET_ALL
        if start > i:
            break
    return char


def yield_xxd_bufs(buf, start, line_length, colors):
    for chunk in chunks(buf, line_length):
        hexdata = [('%02x' % ord(i)) for i in chunk]
        header = ('%07x' % (start))
        datastring = ' '.join([
            ''.join([
                colorize(start + i + j, char, colors)
                for j, char in enumerate(hexdata[i:i + 2])

            ]) if i < len(hexdata) else '    '
            for i in range(0, line_length, 2)
        ])
        as_text = ''.join([
            colorize(
                start + i,
                c if c in string.printable[:-5] else '.',
                colors)
            for i, c in enumerate(chunk)
        ])
        yield '{0}: {1:<39}  {2}'.format(header, datastring, as_text)
        start += line_length


def pre_process_color_array(colors):
    """
    Ensure colors are in ascending order and that no colors
    have overlapping regions.
    """
    previous_end = None
    for (start, end), color in sorted(colors, key=lambda t: t[0][0]):
        if end < start:
            raise ValueError(
                "(start, end) pair in color array is out of order! (%s)",
                (start, end))
        if previous_end is not None and previous_end > start:
            raise ValueError("Overlapping color regions detected!")
        yield ((start, end), color)


def as_xxd(buf, start=0, line_length=16, colors=[]):
    """
    Convert a string into an xxd-formatted hex dump.
    "colors" should be a of non-overlapping tuples where
    the first element of the tuple is a [start, end) pair and the second
    element is a Colorama (i.e.: ANSI) color code.
    """
    colors = list(pre_process_color_array(colors))
    return '\n'.join(yield_xxd_bufs(buf, start, line_length, colors))
