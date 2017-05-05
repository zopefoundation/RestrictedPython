from RestrictedPython._compat import IS_PY35_OR_GREATER
from tests import c_eval
from tests import e_eval

import pytest


# Arithmetic Operators


@pytest.mark.parametrize(*e_eval)
def test_Add(e_eval):
    assert e_eval('1 + 1') == 2


@pytest.mark.parametrize(*e_eval)
def test_Sub(e_eval):
    assert e_eval('5 - 3') == 2


@pytest.mark.parametrize(*e_eval)
def test_Mult(e_eval):
    assert e_eval('2 * 2') == 4


@pytest.mark.parametrize(*e_eval)
def test_Div(e_eval):
    assert e_eval('10 / 2') == 5


@pytest.mark.parametrize(*e_eval)
def test_Mod(e_eval):
    assert e_eval('10 % 3') == 1


@pytest.mark.parametrize(*e_eval)
def test_Pow(e_eval):
    assert e_eval('2 ** 8') == 256


@pytest.mark.parametrize(*e_eval)
def test_FloorDiv(e_eval):
    assert e_eval('7 // 2') == 3


@pytest.mark.skipif(
    not IS_PY35_OR_GREATER,
    reason="MatMult was introducted on Python 3.5")
@pytest.mark.parametrize(*c_eval)
def test_MatMult(c_eval):
    result = c_eval('(8, 3, 5) @ (2, 7, 1)')
    assert result.errors == (
        'Line None: MatMult statements are not allowed.',
    )
    assert result.code is None
