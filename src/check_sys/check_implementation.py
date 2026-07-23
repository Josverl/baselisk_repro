# sys.implementation is a namedtuple, not a tuple
# https://github.com/Josverl/micropython-stubs/issues/708

# https://docs.micropython.org/en/latest/library/sys.html#sys.implementation
# name - string "micropython"
# version - tuple (major, minor, micro, releaselevel), e.g. (1, 22, 0, ‘’)
# _machine - string describing the underlying machine
# _mpy - supported mpy file-format version (optional attribute)
# _build - string that can help identify the configuration that MicroPython was built with

import sys
from typing import Dict, NamedTuple, Tuple

from typing_extensions import assert_type, get_type_hints
