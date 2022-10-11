from tests.helper import restricted_eval


def test_RestrictingNodeTransformer__visit_Eq__1():
    """It allows == expressions."""
    assert restricted_eval('1 == int("1")') is True


def test_RestrictingNodeTransformer__visit_NotEq__1():
    """It allows != expressions."""
    assert restricted_eval('1 != int("1")') is False


def test_RestrictingNodeTransformer__visit_Lt__1():
    """It allows < expressions."""
    assert restricted_eval('1 < 3') is True


def test_RestrictingNodeTransformer__visit_LtE__1():
    """It allows < expressions."""
    assert restricted_eval('1 <= 3') is True


def test_RestrictingNodeTransformer__visit_Gt__1():
    """It allows > expressions."""
    assert restricted_eval('1 > 3') is False


def test_RestrictingNodeTransformer__visit_GtE__1():
    """It allows >= expressions."""
    assert restricted_eval('1 >= 3') is False


def test_RestrictingNodeTransformer__visit_Is__1():
    """It allows `is` expressions."""
    assert restricted_eval('None is None') is True


def test_RestrictingNodeTransformer__visit_IsNot__1():
    """It allows `is not` expressions."""
    assert restricted_eval('2 is not None') is True


def test_RestrictingNodeTransformer__visit_In_List():
    """It allows `in` expressions for lists."""
    assert restricted_eval('2 in [1, 2, 3]') is True


def test_RestrictingNodeTransformer__visit_NotIn_List():
    """It allows `not in` expressions for lists."""
    assert restricted_eval('2 not in [1, 2, 3]') is False


def test_RestrictingNodeTransformer__visit_In_Set():
    """It allows `in` expressions for sets."""
    assert restricted_eval('2 in {1, 1, 2, 3}') is True


def test_RestrictingNodeTransformer__visit_NotIn_Set():
    """It allows `not in` expressions for sets."""
    assert restricted_eval('2 not in {1, 2, 3}') is False


def test_RestrictingNodeTransformer__visit_In_Dict():
    """It allows `in` expressions for dicts."""
    assert restricted_eval('2 in {1: 1, 2: 2, 3: 3}') is True


def test_RestrictingNodeTransformer__visit_NotIn_Dict():
    """It allows `not in` expressions for dicts."""
    assert restricted_eval('2 not in {1: 1, 2: 2, 3: 3}') is False
