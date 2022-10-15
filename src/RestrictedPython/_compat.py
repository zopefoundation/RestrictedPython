import platform
import sys


_version = sys.version_info
IS_PY37_OR_GREATER = _version.major == 3 and _version.minor >= 7
IS_PY38_OR_GREATER = _version.major == 3 and _version.minor >= 8
IS_PY310_OR_GREATER = _version.major == 3 and _version.minor >= 10
IS_PY311_OR_GREATER = _version.major == 3 and _version.minor >= 11

IS_CPYTHON = platform.python_implementation() == 'CPython'
