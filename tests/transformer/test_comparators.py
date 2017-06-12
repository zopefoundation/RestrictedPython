from tests import e_eval

import pytest


@pytest.mark.parametrize(*e_eval)
def test_RestrictingNodeTransformer__visit_Eq__1(e_eval):
    """It allows == expressions."""
    assert e_eval('1 == int("1")') is True


@pytest.mark.parametrize(*e_eval)
def test_RestrictingNodeTransformer__visit_NotEq__1(e_eval):
    """It allows != expressions."""
    assert e_eval('1 != int("1")') is False


@pytest.mark.parametrize(*e_eval)
def test_RestrictingNodeTransformer__visit_Lt__1(e_eval):
    """It allows < expressions."""
    assert e_eval('1 < 3') is True


@pytest.mark.parametrize(*e_eval)
def test_RestrictingNodeTransformer__visit_LtE__1(e_eval):
    """It allows < expressions."""
    assert e_eval('1 <= 3') is True


@pytest.mark.parametrize(*e_eval)
def test_RestrictingNodeTransformer__visit_Gt__1(e_eval):
    """It allows > expressions."""
    assert e_eval('1 > 3') is False


@pytest.mark.parametrize(*e_eval)
def test_RestrictingNodeTransformer__visit_GtE__1(e_eval):
    """It allows >= expressions."""
    assert e_eval('1 >= 3') is False


@pytest.mark.parametrize(*e_eval)
def test_RestrictingNodeTransformer__visit_Is__1(e_eval):
    """It allows `is` expressions."""
    assert e_eval('None is None') is True


@pytest.mark.parametrize(*e_eval)
def test_RestrictingNodeTransformer__visit_IsNot__1(e_eval):
    """It allows `is not` expressions."""
    assert e_eval('2 is not None') is True


@pytest.mark.parametrize(*e_eval)
def test_RestrictingNodeTransformer__visit_In__1(e_eval):
    """It allows `in` expressions."""
    assert e_eval('2 in [1, 2, 3]') is True


@pytest.mark.parametrize(*e_eval)
def test_RestrictingNodeTransformer__visit_NotIn__1(e_eval):
    """It allows `in` expressions."""
    assert e_eval('2 not in [1, 2, 3]') is False
