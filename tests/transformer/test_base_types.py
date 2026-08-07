from tests.helper import restricted_eval


def test_Num():
    """It allows to use number literals."""
    assert restricted_eval('42') == 42


def test_Bytes():
    """It allows to use bytes literals."""
    assert restricted_eval('b"code"') == b"code"


def test_Set():
    """It allows to use set literals."""
    assert restricted_eval('{1, 2, 3}') == {1, 2, 3}


def test_Ellipsis():
    """It allows to use the `ellipsis` statement."""
    assert restricted_eval('...') == ...
    assert restricted_eval('Ellipsis') == ...
