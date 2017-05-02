from RestrictedPython._compat import IS_PY3
from tests import c_exec

import pytest


GLOBAL_EXAMPLE = """
global a
a = 1
"""


@pytest.mark.parametrize(*c_exec)
def test_Global(c_exec):
    result = c_exec(GLOBAL_EXAMPLE)
    assert result.errors == ()
    assert result.code is not None


# Example from:
# https://www.smallsurething.com/a-quick-guide-to-nonlocal-in-python-3/
NONLOCAL_EXAMPLE = """
def outside():
    msg = "Outside!"
    def inside():
        nonlocal msg
        msg = "Inside!"
        print(msg)
    inside()
    print(msg)
outside()
"""


@pytest.mark.skipif(
    not IS_PY3,
    reason="The `nonlocal` statement was introduced in Python 3.0.")
@pytest.mark.parametrize(*c_exec)
def test_Nonlocal(c_exec):
    result = c_exec(NONLOCAL_EXAMPLE)
    assert result.errors == (
        'Line 5: Nonlocal statements are not allowed.',
    )
    assert result.code is None
