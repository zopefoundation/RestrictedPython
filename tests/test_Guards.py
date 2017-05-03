from RestrictedPython.Guards import safe_builtins
from tests import e_eval

import pytest


@pytest.mark.parametrize(*e_eval)
def test_Guards__safe_builtins__1(e_eval):
    """It contains `slice()`."""
    restricted_globals = dict(__builtins__=safe_builtins)
    assert e_eval('slice(1)', restricted_globals) == slice(1)
