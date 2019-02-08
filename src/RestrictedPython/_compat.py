import platform
import sys


_version = sys.version_info
IS_PY2 = _version.major == 2
IS_PY3 = _version.major == 3
IS_PY34_OR_GREATER = _version.major == 3 and _version.minor >= 4
IS_PY35_OR_GREATER = _version.major == 3 and _version.minor >= 5
IS_PY36_OR_GREATER = _version.major == 3 and _version.minor >= 6
IS_PY37_OR_GREATER = _version.major == 3 and _version.minor >= 7
IS_PY38_OR_GREATER = _version.major == 3 and _version.minor >= 8

if IS_PY2:
    basestring = basestring  # NOQA: F821  # Python 2 only built-in function
else:
    basestring = str

IS_CPYTHON = platform.python_implementation() == 'CPython'
