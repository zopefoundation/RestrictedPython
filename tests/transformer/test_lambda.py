from RestrictedPython._compat import IS_PY2
from RestrictedPython._compat import IS_PY3
from RestrictedPython.Eval import default_guarded_getiter
from RestrictedPython.Guards import guarded_unpack_sequence
from tests import c_exec
from tests import e_exec

import pytest


lambda_err_msg = 'Line 1: "_bad" is an invalid variable ' \
                 'name because it starts with "_"'


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Lambda__1(c_exec):
    """It prevents arguments starting with `_`."""
    result = c_exec("lambda _bad: None")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert lambda_err_msg in result.errors


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Lambda__2(c_exec):
    """It prevents keyword arguments starting with `_`."""
    result = c_exec("lambda _bad=1: None")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert lambda_err_msg in result.errors


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Lambda__3(c_exec):
    """It prevents * arguments starting with `_`."""
    result = c_exec("lambda *_bad: None")
    assert result.errors == (lambda_err_msg,)


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Lambda__4(c_exec):
    """It prevents ** arguments starting with `_`."""
    result = c_exec("lambda **_bad: None")
    assert result.errors == (lambda_err_msg,)


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Lambda__5(c_exec):
    """It prevents arguments starting with `_` in tuple unpacking."""
    result = c_exec("lambda (a, _bad): None")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and
    # **_bad would be allowed.
    assert lambda_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Lambda__6(c_exec):
    """It prevents arguments starting with `_` in nested tuple unpacking."""
    result = c_exec("lambda (a, (c, (_bad, c))): None")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and
    # **_bad would be allowed.
    assert lambda_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY2,
    reason="There is no single `*` argument in Python 2")
@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Lambda__7(c_exec):
    """It prevents arguments starting with `_` together with a single `*`."""
    result = c_exec("lambda good, *, _bad: None")
    assert result.errors == (lambda_err_msg,)


BAD_ARG_IN_LAMBDA = """\
def check_getattr_in_lambda(arg=lambda _bad=(lambda ob, name: name): _bad2):
    42
"""


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Lambda__8(c_exec):
    """It prevents arguments starting with `_` in weird lambdas."""
    result = c_exec(BAD_ARG_IN_LAMBDA)
    # On Python 2 the first error message is contained twice:
    assert lambda_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in python 3")
@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Lambda__9(
        e_exec, mocker):
    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it
    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence,
        '_getattr_': lambda ob, val: getattr(ob, val)
    }

    src = "m = lambda (a, (b, c)), *ag, **kw: a+b+c+sum(ag)+sum(kw.values())"
    e_exec(src, glb)

    ret = glb['m']((1, (2, 3)), 4, 5, 6, g=7, e=8)
    assert ret == 36
    assert 2 == _getiter_.call_count
    _getiter_.assert_any_call((1, (2, 3)))
    _getiter_.assert_any_call((2, 3))


LAMBDA_FUNC_1 = """
g = lambda x: x ** 2
"""


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Lambda__10(e_exec):
    """Simple lambda functions are allowed."""
    restricted_globals = dict(
        g=None,
    )
    e_exec(LAMBDA_FUNC_1, restricted_globals)
    assert 4 == restricted_globals['g'](2)


LAMBDA_FUNC_2 = """
g = lambda (x, y) : (x ** 2, x + y)
"""


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in python 3")
@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Lambda__11(e_exec):
    """Lambda functions with tuple unpacking are allowed."""
    restricted_globals = dict(
        g=None,
        _unpack_sequence_=guarded_unpack_sequence,
        _getiter_=default_guarded_getiter,
    )
    e_exec(LAMBDA_FUNC_2, restricted_globals)
    assert (9, 5) == restricted_globals['g']((3, 2))


LAMBDA_FUNC_3 = """
g = lambda (x, y), z : (x ** y, x + z)
"""


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in python 3")
@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Lambda__12(e_exec):
    """Lambda functions with tuple unpacking and simple params are allowed."""
    restricted_globals = dict(
        g=None,
        _unpack_sequence_=guarded_unpack_sequence,
        _getiter_=default_guarded_getiter,
    )
    e_exec(LAMBDA_FUNC_3, restricted_globals)
    assert (64, 6) == restricted_globals['g']((4, 3), 2)
