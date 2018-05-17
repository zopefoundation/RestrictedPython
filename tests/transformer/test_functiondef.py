from RestrictedPython._compat import IS_PY2
from RestrictedPython._compat import IS_PY3
from RestrictedPython.Guards import guarded_unpack_sequence
from tests import c_exec
from tests import e_exec

import pytest


functiondef_err_msg = 'Line 1: "_bad" is an invalid variable ' \
                      'name because it starts with "_"'


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_FunctionDef__1(
        c_exec):
    """It prevents function arguments starting with `_`."""
    result = c_exec("def foo(_bad): pass")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert functiondef_err_msg in result.errors


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_FunctionDef__2(
        c_exec):
    """It prevents function keyword arguments starting with `_`."""
    result = c_exec("def foo(_bad=1): pass")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert functiondef_err_msg in result.errors


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_FunctionDef__3(
        c_exec):
    """It prevents function * arguments starting with `_`."""
    result = c_exec("def foo(*_bad): pass")
    assert result.errors == (functiondef_err_msg,)


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_FunctionDef__4(
        c_exec):
    """It prevents function ** arguments starting with `_`."""
    result = c_exec("def foo(**_bad): pass")
    assert result.errors == (functiondef_err_msg,)


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_FunctionDef__5(
        c_exec):
    """It prevents function arguments starting with `_` in tuples."""
    result = c_exec("def foo((a, _bad)): pass")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert functiondef_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_FunctionDef__6(
        c_exec):
    """It prevents function arguments starting with `_` in tuples."""
    result = c_exec("def foo(a, (c, (_bad, c))): pass")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and
    # **_bad would be allowed.
    assert functiondef_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY2,
    reason="There is no single `*` argument in Python 2")
@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_FunctionDef__7(
        c_exec):
    """It prevents `_` function arguments together with a single `*`."""
    result = c_exec("def foo(good, *, _bad): pass")
    assert result.errors == (functiondef_err_msg,)


NESTED_SEQ_UNPACK = """
def nested((a, b, (c, (d, e)))):
    return a, b, c, d, e

def nested_with_order((a, b), (c, d)):
    return a, b, c, d
"""


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in python 3")
@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_FunctionDef__8(
        e_exec, mocker):
    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    e_exec('def simple((a, b)): return a, b', glb)

    val = (1, 2)
    ret = glb['simple'](val)
    assert ret == val
    _getiter_.assert_called_once_with(val)
    _getiter_.reset_mock()

    e_exec(NESTED_SEQ_UNPACK, glb)

    val = (1, 2, (3, (4, 5)))
    ret = glb['nested'](val)
    assert ret == (1, 2, 3, 4, 5)
    assert 3 == _getiter_.call_count
    _getiter_.assert_any_call(val)
    _getiter_.assert_any_call(val[2])
    _getiter_.assert_any_call(val[2][1])
    _getiter_.reset_mock()

    ret = glb['nested_with_order']((1, 2), (3, 4))
    assert ret == (1, 2, 3, 4)
    _getiter_.assert_has_calls([
        mocker.call((1, 2)),
        mocker.call((3, 4))])
    _getiter_.reset_mock()


BLACKLISTED_FUNC_NAMES_CALL_TEST = """
def __init__(test):
    test

__init__(1)
"""


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__module_func_def_name_call(c_exec):
    """It forbids definition and usage of magic methods as functions ...

    ... at module level.
    """
    result = c_exec(BLACKLISTED_FUNC_NAMES_CALL_TEST)
    # assert result.errors == ('Line 1: ')
    assert result.errors == (
        'Line 2: "__init__" is an invalid variable name because it starts with "_"',  # NOQA: E501
        'Line 5: "__init__" is an invalid variable name because it starts with "_"',  # NOQA: E501
    )
