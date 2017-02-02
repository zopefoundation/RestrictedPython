from . import compile
from RestrictedPython import CompileResult
from RestrictedPython._compat import IS_PY2

import pytest


@pytest.mark.parametrize(*compile)
def test_compile__compile_restricted_exec__1(compile):
    """It returns a CompileResult on success."""
    result = compile('a = 42')
    assert result.__class__ == CompileResult
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}
    glob = {}
    exec(result.code, glob)
    assert glob['a'] == 42


EXEC_STATEMENT = """\
def no_exec():
    exec 'q = 1'
"""


@pytest.mark.skipif(
    IS_PY2,
    reason="exec statement in Python 2 is handled by RestrictedPython ")
@pytest.mark.parametrize(*compile)
def test_compile__compile_restricted_exec__10(compile):
    """It is a SyntaxError to use the `exec` statement. (Python 3 only)"""
    code, errors, warnings, used_names = compile(EXEC_STATEMENT)
    assert (
        "Line 2: SyntaxError: Missing parentheses in call to 'exec' in on "
        "statement: exec 'q = 1'",) == errors
