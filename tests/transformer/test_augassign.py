from RestrictedPython import compile_restricted_exec
from tests.helper import restricted_exec


def test_RestrictingNodeTransformer__visit_AugAssign__1(
        mocker):
    """It allows augmented assign for variables."""
    _inplacevar_ = mocker.stub()
    _inplacevar_.side_effect = lambda op, val, expr: val + expr

    glb = {
        '_inplacevar_': _inplacevar_,
        'a': 1,
        'x': 1,
        'z': 0
    }

    restricted_exec("a += x + z", glb)
    assert glb['a'] == 2
    _inplacevar_.assert_called_once_with('+=', 1, 1)
    _inplacevar_.reset_mock()


def test_RestrictingNodeTransformer__visit_AugAssign__2():
    """It forbids augmented assign of attributes."""
    result = compile_restricted_exec("a.a += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of attributes is not allowed.',)


def test_RestrictingNodeTransformer__visit_AugAssign__3():
    """It forbids augmented assign of subscripts."""
    result = compile_restricted_exec("a[a] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)


def test_RestrictingNodeTransformer__visit_AugAssign__4():
    """It forbids augmented assign of slices."""
    result = compile_restricted_exec("a[x:y] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)


def test_RestrictingNodeTransformer__visit_AugAssign__5():
    """It forbids augmented assign of slices with steps."""
    result = compile_restricted_exec("a[x:y:z] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)
