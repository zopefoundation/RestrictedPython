from tests.helper import restricted_eval


def test_In():
    assert restricted_eval('1 in [1, 2, 3]') is True


def test_NotIn():
    assert restricted_eval('4 not in [1, 2, 3]') is True
