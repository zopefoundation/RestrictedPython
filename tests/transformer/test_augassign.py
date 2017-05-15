from tests import c_exec
from tests import e_exec

import pytest


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_AugAssign__1(
        e_exec, mocker):
    """It allows augmented assign for variables."""
    _inplacevar_ = mocker.stub()
    _inplacevar_.side_effect = lambda op, val, expr: val + expr

    glb = {
        '_inplacevar_': _inplacevar_,
        'a': 1,
        'x': 1,
        'z': 0
    }

    e_exec("a += x + z", glb)
    assert glb['a'] == 2
    _inplacevar_.assert_called_once_with('+=', 1, 1)
    _inplacevar_.reset_mock()


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_AugAssign__2(c_exec):
    """It forbids augmented assign of attributes."""
    result = c_exec("a.a += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of attributes is not allowed.',)


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_AugAssign__3(c_exec):
    """It forbids augmented assign of subscripts."""
    result = c_exec("a[a] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_AugAssign__4(c_exec):
    """It forbids augmented assign of slices."""
    result = c_exec("a[x:y] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_AugAssign__5(c_exec):
    """It forbids augmented assign of slices with steps."""
    result = c_exec("a[x:y:z] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)
