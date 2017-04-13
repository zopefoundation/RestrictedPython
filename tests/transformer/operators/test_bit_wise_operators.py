from tests import c_eval
from tests import e_eval

import pytest


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_BitAnd(c_eval, e_eval):
    result = c_eval('5 & 3')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 1
    assert e_eval('5 & 3') == 1


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_BitOr(c_eval, e_eval):
    result = c_eval('5 | 3')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 7
    assert e_eval('5 | 3') == 7


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_BitXor(c_eval, e_eval):
    result = c_eval('5 ^ 3')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 6
    assert e_eval('5 ^ 3') == 6


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Invert(c_eval, e_eval):
    result = c_eval('~17')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == -18
    assert e_eval('~17') == -18


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_LShift(c_eval, e_eval):
    result = c_eval('8 << 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 32
    assert e_eval('8 << 2') == 32


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_RShift(c_eval, e_eval):
    result = c_eval('8 >> 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 4
    assert e_eval('8 >> 1') == 4
