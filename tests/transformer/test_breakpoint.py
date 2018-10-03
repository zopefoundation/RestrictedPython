from tests import c_exec

import pytest


@pytest.mark.parametrize(*c_exec)
def test_call_breakpoint(c_exec):
    """The Python3.7+ builtin function breakpoint should not
    be used and is forbidden in RestrictedPython.
    """
    result = c_exec('breakpoint()')
    assert result.errors == ('Line 1: "breakpoint" is a reserved name.',)
    assert result.code is None
