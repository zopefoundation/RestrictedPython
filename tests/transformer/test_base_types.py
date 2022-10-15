from RestrictedPython import compile_restricted_exec
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
    """It prevents using the `ellipsis` statement."""
    result = compile_restricted_exec('...')
    assert result.errors == ('Line 1: Ellipsis statements are not allowed.',)
