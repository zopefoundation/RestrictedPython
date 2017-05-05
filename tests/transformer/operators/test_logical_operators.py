# Test framework imports
import pytest

# Test internals (fixures and helpers)
from tests import e_eval


@pytest.mark.parametrize(*e_eval)
def test_In(e_eval):
    assert e_eval('1 in [1, 2, 3]') is True


@pytest.mark.parametrize(*e_eval)
def test_NotIn(e_eval):
    assert e_eval('4 not in [1, 2, 3]') is True
