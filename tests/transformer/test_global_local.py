from RestrictedPython._compat import IS_PY3
from tests import c_exec
from tests import e_exec

import pytest


GLOBAL_EXAMPLE = """
def x():
    global a
    a = 11
x()
"""


@pytest.mark.parametrize(*e_exec)
def test_Global(e_exec):
    glb = {'a': None}
    e_exec(GLOBAL_EXAMPLE, glb)
    assert glb['a'] == 11


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
    assert result.errors == ('Line 5: Nonlocal statements are not allowed.',)
    assert result.code is None
