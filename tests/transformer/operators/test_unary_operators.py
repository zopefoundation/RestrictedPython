from tests import e_eval

import pytest

# TODO: Review as in Python 2.7 -1 and +1 ar Num and not UAdd or USub Elems.


@pytest.mark.parametrize(*e_eval)
def test_UAdd(e_eval):
    assert e_eval('+1') == 1


@pytest.mark.parametrize(*e_eval)
def test_USub(e_eval):
    assert e_eval('-1') == -1
