# packing-tape

A quick-and-dirty wrapper for Python's `struct` module that exposes a simple,
intuitive interface to read (unpack), write (pack), validate, and manipulate
binary data, usually written by other programs. Useful for reverse engineering.

```python
from packing_tape import Struct
from packing_tape.constants import Big
from packing_tape.fields import integer, string, empty

class SomeStructFromAFile(Struct):
    number_of_things = integer(signed=False, endianness=Big)
    name = string(size=64, validate=lambda x: 'bad word' not in x)
    not_sure_what_this_field_is_yet = empty(32)

struct = SomeStructFromAFile.parse_from(open('./some_file'))
print struct.number_of_things  # => 10
print struct.name  # => "This is a name!"

print struct.as_hex()
# 0000000: 0000 000a 5468 6973 2069 7320 6120 6e61  ....This is a na
# 0000010: 6d65 2100 0000 0000 0000 0000 0000 0000  me!.............
# 0000020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
# 0000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................
# 0000040: 0000 0000                                ..

struct.name = "Use this name instead."
print struct.as_hex()
# 0000000: 0000 000a 5573 6520 7468 6973 206e 616d  ....Use this nam
# 0000010: 6520 696e 7374 6561 642e 0000 0000 0000  e instead.......
# 0000020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
# 0000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................
# 0000040: 0000 0000                                ....
```

`packing_tape` is super alpha software and should not be used for anything
serious just yet, but it _is_ built on some pretty nice Python magic.


## Development

Run tests with `python -m pytest tests -s`.


# License

```
The MIT License

Copyright (c) 2018 Peter Sobot http://petersobot.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
