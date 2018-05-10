# Stubs for galaxy.util.object_wrapper (Python 3.4)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any, Optional
from six.moves import copyreg as copy_reg
from galaxy.util import sanitize_lists_to_string as _sanitize_lists_to_string

NoneType = ...  # type: Any
NotImplementedType = ...  # type: Any
EllipsisType = ...  # type: Any
XRangeType = ...  # type: Any
SliceType = ...  # type: Any
BufferType = ...  # type: Any
DictProxyType = ...  # type: Any
log = ...  # type: Any
__CALLABLE_TYPES__ = ...  # type: Any
__WRAP_NO_SUBCLASS__ = ...  # type: Any
__DONT_SANITIZE_TYPES__ = ...  # type: Any
__DONT_WRAP_TYPES__ = ...  # type: Any
__WRAP_SEQUENCES__ = ...  # type: Any
__WRAP_SETS__ = ...  # type: Any
__WRAP_MAPPINGS__ = ...  # type: Any
VALID_CHARACTERS = ...  # type: Any
CHARACTER_MAP = ...  # type: Any
INVALID_CHARACTER = ...  # type: str

def coerce(x, y): ...
def cmp(x, y): ...
def sanitize_lists_to_string(values, valid_characters: Any = ..., character_map: Any = ..., invalid_character: Any = ...): ...
def wrap_with_safe_string(value, no_wrap_classes: Optional[Any] = ...): ...

class SafeStringWrapper:
    __UNSANITIZED_ATTRIBUTE_NAME__ = ...  # type: str
    __NO_WRAP_NAMES__ = ...  # type: Any
    def __new__(cls, *arg, **kwd): ...
    unsanitized = ...  # type: Any
    __safe_string_wrapper_function__ = ...  # type: Any
    def __init__(self, value, safe_string_wrapper_function: Any = ...) -> None: ...
    def __lt__(self, other): ...
    def __le__(self, other): ...
    def __eq__(self, other): ...
    def __ne__(self, other): ...
    def __gt__(self, other): ...
    def __ge__(self, other): ...
    def __cmp__(self, other): ...
    def __hash__(self): ...
    def __bool__(self): ...
    __nonzero__ = ...  # type: Any
    def __getattr__(self, name): ...
    def __setattr__(self, name, value): ...
    def __delattr__(self, name): ...
    def __getattribute__(self, name): ...
    def __len__(self): ...
    def __getitem__(self, key): ...
    def __setitem__(self, key, value): ...
    def __delitem__(self, key): ...
    def __iter__(self): ...
    def __contains__(self, item): ...
    def __getslice__(self, i, j): ...
    def __setslice__(self, i, j, value): ...
    def __delslice__(self, i, j): ...
    def __add__(self, other): ...
    def __sub__(self, other): ...
    def __mul__(self, other): ...
    def __floordiv__(self, other): ...
    def __mod__(self, other): ...
    def __divmod__(self, other): ...
    def __pow__(self, *other): ...
    def __lshift__(self, other): ...
    def __rshift__(self, other): ...
    def __and__(self, other): ...
    def __xor__(self, other): ...
    def __or__(self, other): ...
    def __div__(self, other): ...
    def __truediv__(self, other): ...
    def __rpow__(self, other): ...
    def __neg__(self): ...
    def __pos__(self): ...
    def __abs__(self): ...
    def __invert__(self): ...
    def __complex__(self): ...
    def __int__(self): ...
    def __float__(self): ...
    def __oct__(self): ...
    def __hex__(self): ...
    def __index__(self): ...
    def __coerce__(self, other): ...
    def __enter__(self): ...
    def __exit__(self, *args): ...

class CallableSafeStringWrapper(SafeStringWrapper):
    def __call__(self, *args, **kwds): ...

def pickle_SafeStringWrapper(safe_object): ...
