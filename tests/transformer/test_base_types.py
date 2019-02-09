from RestrictedPython._compat import IS_PY2
from tests.helper import restricted_eval

import pytest


def test_Num():
    """It allows to use number literals."""
    assert restricted_eval('42') == 42


def test_Bytes():
    """It allows to use bytes literals."""
    assert restricted_eval('b"code"') == b"code"


def test_Set():
    """It allows to use set literals."""
    assert restricted_eval('{1, 2, 3}') == set([1, 2, 3])


@pytest.mark.skipif(IS_PY2,
                    reason="... is new in Python 3")
def test_Ellipsis():
    """It allows using the `...` statement."""
    assert restricted_eval('...') == Ellipsis
