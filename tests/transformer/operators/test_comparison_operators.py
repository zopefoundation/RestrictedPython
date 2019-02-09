from tests.helper import restricted_eval


def test_Eq():
    assert restricted_eval('1 == 1') is True


def test_NotEq():
    assert restricted_eval('1 != 2') is True


def test_Gt():
    assert restricted_eval('2 > 1') is True


def test_Lt():
    assert restricted_eval('1 < 2')


def test_GtE():
    assert restricted_eval('2 >= 2') is True


def test_LtE():
    assert restricted_eval('1 <= 2') is True
