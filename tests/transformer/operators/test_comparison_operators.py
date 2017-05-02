from tests import e_eval

import pytest


@pytest.mark.parametrize(*e_eval)
def test_Eq(e_eval):
    assert e_eval('1 == 1') is True


@pytest.mark.parametrize(*e_eval)
def test_NotEq(e_eval):
    assert e_eval('1 != 2') is True


@pytest.mark.parametrize(*e_eval)
def test_Gt(e_eval):
    assert e_eval('2 > 1') is True


@pytest.mark.parametrize(*e_eval)
def test_Lt(e_eval):
    assert e_eval('1 < 2')


@pytest.mark.parametrize(*e_eval)
def test_GtE(e_eval):
    assert e_eval('2 >= 2') is True


@pytest.mark.parametrize(*e_eval)
def test_LtE(e_eval):
    assert e_eval('1 <= 2') is True
