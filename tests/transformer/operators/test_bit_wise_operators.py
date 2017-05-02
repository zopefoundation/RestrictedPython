from tests import e_eval

import pytest


@pytest.mark.parametrize(*e_eval)
def test_BitAnd(e_eval):
    assert e_eval('5 & 3') == 1


@pytest.mark.parametrize(*e_eval)
def test_BitOr(e_eval):
    assert e_eval('5 | 3') == 7


@pytest.mark.parametrize(*e_eval)
def test_BitXor(e_eval):
    assert e_eval('5 ^ 3') == 6


@pytest.mark.parametrize(*e_eval)
def test_Invert(e_eval):
    assert e_eval('~17') == -18


@pytest.mark.parametrize(*e_eval)
def test_LShift(e_eval):
    assert e_eval('8 << 2') == 32


@pytest.mark.parametrize(*e_eval)
def test_RShift(e_eval):
    assert e_eval('8 >> 1') == 4
