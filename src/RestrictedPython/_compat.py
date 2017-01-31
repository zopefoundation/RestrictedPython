import sys


_version = sys.version_info
IS_PY2 = _version.major == 2
IS_PY3 = _version.major == 3
IS_PY34_OR_GREATER = _version.major == 3 and _version.minor >= 4
IS_PY35_OR_GREATER = _version.major == 3 and _version.minor >= 5
