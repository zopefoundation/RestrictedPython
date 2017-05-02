from RestrictedPython._compat import IS_PY2
from tests import c_exec
from tests import e_eval

import pytest


@pytest.mark.parametrize(*e_eval)
def test_Num(e_eval):
    """It allows to use number literals."""
    assert e_eval('42') == 42


@pytest.mark.parametrize(*e_eval)
def test_Bytes(e_eval):
    """It allows to use bytes literals."""
    assert e_eval('b"code"') == b"code"


@pytest.mark.parametrize(*e_eval)
def test_Set(e_eval):
    """It allows to use set literals."""
    assert e_eval('{1, 2, 3}') == set([1, 2, 3])


@pytest.mark.skipif(IS_PY2,
                    reason="... is new in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_Ellipsis(c_exec):
    """It prevents using the `ellipsis` statement."""
    result = c_exec('...')
    assert result.errors == ('Line 1: Ellipsis statements are not allowed.',)
