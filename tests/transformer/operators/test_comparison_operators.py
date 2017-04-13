from tests import c_eval
from tests import e_eval

import pytest


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Eq(c_eval, e_eval):
    result = c_eval('1 == 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('1 == 1') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_NotEq(c_eval, e_eval):
    result = c_eval('1 != 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('1 != 2') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Gt(c_eval, e_eval):
    result = c_eval('2 > 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('2 > 1') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Lt(c_eval, e_eval):
    result = c_eval('1 < 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('1 < 2')


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_GtE(c_eval, e_eval):
    result = c_eval('2 >= 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('2 >= 2') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_LtE(c_eval, e_eval):
    result = c_eval('1 <= 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('1 <= 2') is True
