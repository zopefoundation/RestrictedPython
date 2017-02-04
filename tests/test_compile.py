from . import compile
from . import compile_eval
from RestrictedPython import compile_restricted
from RestrictedPython import CompileResult
from RestrictedPython._compat import IS_PY2

import pytest
import RestrictedPython.compile


def test_compile__compile_restricted_invalid_code_input():
    with pytest.raises(TypeError):
        compile_restricted(object(), '<string>', 'exec')
    with pytest.raises(TypeError):
        compile_restricted(object(), '<string>', 'eval')
    with pytest.raises(TypeError):
        compile_restricted(object(), '<string>', 'single')


def test_compile__compile_restricted_invalid_policy_input():
    with pytest.raises(TypeError):
        compile_restricted("pass", '<string>', 'exec', policy=object())


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


@pytest.mark.parametrize(*compile)
def test_compile__compile_restricted_exec__2(compile):
    """It compiles without restrictions if there is no policy."""
    if compile is RestrictedPython.compile.compile_restricted_exec:
        # The old version does not support a custom policy
        result = compile('_a = 42', policy=None)
        assert result.errors == ()
        assert result.warnings == []
        assert result.used_names == {}
        glob = {}
        exec(result.code, glob)
        assert glob['_a'] == 42


@pytest.mark.parametrize(*compile)
def test_compile__compile_restricted_exec__3(compile):
    """It returns a tuple of errors if the code is not allowed.

    There is no code in this case.
    """
    result = compile('_a = 42\n_b = 43')
    errors = (
        'Line 1: "_a" is an invalid variable name because it starts with "_"',
        'Line 2: "_b" is an invalid variable name because it starts with "_"')
    if compile is RestrictedPython.compile.compile_restricted_exec:
        assert result.errors == errors
    else:
        # The old version did only return the first error message.
        assert result.errors == (errors[0],)
    assert result.warnings == []
    assert result.used_names == {}
    assert result.code is None


@pytest.mark.parametrize(*compile)
def test_compile__compile_restricted_exec__4(compile):
    """It does not return code on a SyntaxError."""
    result = compile('asdf|')
    assert result.code is None
    assert result.warnings == []
    assert result.used_names == {}
    if compile is RestrictedPython.compile.compile_restricted_exec:
        assert result.errors == (
            'Line 1: SyntaxError: invalid syntax in on statement: asdf|',)
    else:
        # The old version had a less nice error message:
        assert result.errors == ('invalid syntax (<string>, line 1)',)


@pytest.mark.parametrize(*compile)
def test_compile__compile_restricted_exec__5(compile):
    """It does not return code if the code contains a NULL byte."""
    result = compile('a = 5\x00')
    assert result.code is None
    assert result.warnings == []
    assert result.used_names == {}
    if IS_PY2:
        assert result.errors == (
            'compile() expected string without null bytes',)
    else:
        assert result.errors == (
            'source code string cannot contain null bytes',)


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
    result = compile(EXEC_STATEMENT)
    assert (
        "Line 2: SyntaxError: Missing parentheses in call to 'exec' in on "
        "statement: exec 'q = 1'",) == result.errors


FUNCTION_DEF = """\
def a():
    pass
"""


@pytest.mark.parametrize(*compile_eval)
def test_compile__compile_restricted_eval__1(compile_eval):
    """It compiles code as an Expression.

    Function definitions are not allowed in Expressions.
    """
    result = compile_eval(FUNCTION_DEF)
    if compile_eval is RestrictedPython.compile.compile_restricted_eval:
        assert result.errors == (
            'Line 1: SyntaxError: invalid syntax in on statement: def a():',)
    else:
        assert result.errors == ('invalid syntax (<string>, line 1)',)
