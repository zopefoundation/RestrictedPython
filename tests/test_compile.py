from RestrictedPython import compile_restricted
from RestrictedPython import CompileResult
from RestrictedPython._compat import IS_PY2
from RestrictedPython._compat import IS_PY3
from tests import c_eval
from tests import c_exec
from tests import c_single
from tests import e_eval

import platform
import pytest
import types


def test_compile__compile_restricted_invalid_code_input():
    with pytest.raises(TypeError):
        compile_restricted(object(), '<string>', 'exec')
    with pytest.raises(TypeError):
        compile_restricted(object(), '<string>', 'eval')
    with pytest.raises(TypeError):
        compile_restricted(object(), '<string>', 'single')


def test_compile__compile_restricted_invalid_policy_input():
    with pytest.raises(TypeError):
        compile_restricted("pass", '<string>', 'exec', policy=object)


def test_compile__compile_restricted_invalid_mode_input():
    with pytest.raises(TypeError):
        compile_restricted("pass", '<string>', 'invalid')


@pytest.mark.parametrize(*c_exec)
def test_compile__compile_restricted_exec__1(c_exec):
    """It returns a CompileResult on success."""
    result = c_exec('a = 42')
    assert result.__class__ == CompileResult
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}
    glob = {}
    exec(result.code, glob)
    assert glob['a'] == 42


@pytest.mark.parametrize(*c_exec)
def test_compile__compile_restricted_exec__2(c_exec):
    """It compiles without restrictions if there is no policy."""
    result = c_exec('_a = 42', policy=None)
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}
    glob = {}
    exec(result.code, glob)
    assert glob['_a'] == 42


@pytest.mark.parametrize(*c_exec)
def test_compile__compile_restricted_exec__3(c_exec):
    """It returns a tuple of errors if the code is not allowed.

    There is no code in this case.
    """
    result = c_exec('_a = 42\n_b = 43')
    errors = (
        'Line 1: "_a" is an invalid variable name because it starts with "_"',
        'Line 2: "_b" is an invalid variable name because it starts with "_"')
    assert result.errors == errors
    assert result.warnings == []
    assert result.used_names == {}
    assert result.code is None


@pytest.mark.parametrize(*c_exec)
def test_compile__compile_restricted_exec__4(c_exec):
    """It does not return code on a SyntaxError."""
    result = c_exec('asdf|')
    assert result.code is None
    assert result.warnings == []
    assert result.used_names == {}
    assert result.errors == (
        'Line 1: SyntaxError: invalid syntax in on statement: asdf|',)


@pytest.mark.parametrize(*c_exec)
def test_compile__compile_restricted_exec__5(c_exec):
    """It does not return code if the code contains a NULL byte."""
    result = c_exec('a = 5\x00')
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
@pytest.mark.parametrize(*c_exec)
def test_compile__compile_restricted_exec__10(c_exec):
    """It is a SyntaxError to use the `exec` statement. (Python 3 only)"""
    result = c_exec(EXEC_STATEMENT)
    assert (
        "Line 2: SyntaxError: Missing parentheses in call to 'exec' in on "
        "statement: exec 'q = 1'",) == result.errors


FUNCTION_DEF = """\
def a():
    pass
"""


@pytest.mark.parametrize(*c_eval)
def test_compile__compile_restricted_eval__1(c_eval):
    """It compiles code as an Expression.

    Function definitions are not allowed in Expressions.
    """
    result = c_eval(FUNCTION_DEF)
    assert result.errors == (
        'Line 1: SyntaxError: invalid syntax in on statement: def a():',)


@pytest.mark.parametrize(*e_eval)
def test_compile__compile_restricted_eval__2(e_eval):
    """It compiles code as an Expression."""
    assert e_eval('4 * 6') == 24


@pytest.mark.parametrize(*c_eval)
def test_compile__compile_restricted_eval__used_names(c_eval):
    result = c_eval("a + b + func(x)")
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {'a': True, 'b': True, 'x': True, 'func': True}


@pytest.mark.parametrize(*c_single)
def test_compile__compile_restricted_csingle(c_single):
    """It compiles code as an Interactive."""
    result = c_single('4 * 6')
    assert result.code is None
    assert result.errors == (
        'Line None: Interactive statements are not allowed.',
    )


PRINT_EXAMPLE = """
def a():
    print 'Hello World!'
"""


@pytest.mark.skipif(
    IS_PY3,
    reason="Print statement is gone in Python 3."
           "Test Deprecation Warming in Python 2")
def test_compile_restricted():
    """This test checks compile_restricted itself if that emit Python warnings.
    For actual tests for print statement see: test_print_stmt.py
    """
    with pytest.warns(SyntaxWarning) as record:
        result = compile_restricted(PRINT_EXAMPLE, '<string>', 'exec')
        assert isinstance(result, types.CodeType)
        # Non-CPython versions have a RuntimeWarning, too.
        if len(record) > 2:  # pragma: no cover
            record.pop()
        assert len(record) == 2
        assert record[0].message.args[0] == \
            'Line 3: Print statement is deprecated ' \
            'and not avaliable anymore in Python 3.'
        assert record[1].message.args[0] == \
            "Line 2: Prints, but never reads 'printed' variable."


EVAL_EXAMPLE = """
def a():
    eval('2 + 2')
"""


def test_compile_restricted_eval():
    """This test checks compile_restricted itself if that raise Python errors.
    """
    with pytest.raises(SyntaxError,
                       message="Line 3: Eval calls are not allowed."):
        compile_restricted(EVAL_EXAMPLE, '<string>', 'exec')


def test_compile___compile_restricted_mode__1(recwarn, mocker):
    """It warns when using another Python implementation than CPython."""
    if platform.python_implementation() == 'CPython':
        # Using CPython we have to fake the check:
        mocker.patch('RestrictedPython.compile.IS_CPYTHON', new=False)
    compile_restricted('42')
    assert len(recwarn) == 1
    w = recwarn.pop()
    assert w.category == RuntimeWarning
    assert str(w.message) == str(
        'RestrictedPython is only supported on CPython: use on other Python '
        'implementations may create security issues.'
    )


@pytest.mark.skipif(
    platform.python_implementation() == 'CPython',
    reason='Warning only present if not CPython.')
def test_compile_CPython_warning(recwarn, mocker):
    """It warns when using another Python implementation than CPython."""
    assert platform.python_implementation() != 'CPython'
    with pytest.warns(RuntimeWarning) as record:
        compile_restricted('42')
    assert len(record) == 1
    assert str(record[0].message) == str(
        'RestrictedPython is only supported on CPython: use on other Python '
        'implementations may create security issues.'
    )
