from RestrictedPython._compat import IS_PY35_OR_GREATER
from tests import c_eval
from tests import e_eval

import pytest


# Arithmetic Operators


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Add(c_eval, e_eval):
    result = c_eval('1 + 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 2
    assert e_eval('1 + 1') == 2


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Sub(c_eval, e_eval):
    result = c_eval('2 - 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 1
    assert e_eval('2 - 1') == 1


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Mult(c_eval, e_eval):
    result = c_eval('2 * 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 4
    assert e_eval('2 * 2') == 4


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Div(c_eval, e_eval):
    result = c_eval('10 / 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 5
    assert e_eval('10 / 2') == 5


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Mod(c_eval, e_eval):
    result = c_eval('10 % 3')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 1
    assert e_eval('10 % 3') == 1


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Pow(c_eval, e_eval):
    result = c_eval('2 ** 8')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 256
    assert e_eval('2 ** 8') == 256


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_FloorDiv(c_eval, e_eval):
    result = c_eval('7 // 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 3
    assert e_eval('7 // 2') == 3


@pytest.mark.skipif(
    not IS_PY35_OR_GREATER,
    reason="MatMult was introducted on Python 3.5")
@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_MatMult(c_eval, e_eval):
    result = c_eval('(8, 3, 5) @ (2, 7, 1)')
    assert result.code is None
    assert result.errors == (
        'Line None: MatMult statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}

    # TODO: Review
    # with pytest.raises(SyntaxError):
    #    e_eval('(8, 3, 5) @ (2, 7, 1)')
