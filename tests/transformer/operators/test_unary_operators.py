from tests import c_eval
from tests import e_eval

import pytest

# TODO: Review as in Python 2.7 -1 and +1 ar Num and not UAdd or USub Elems.


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_UAdd(c_eval, e_eval):
    result = c_eval('+1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 1
    assert e_eval('+1') == 1


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_USub(c_eval, e_eval):
    result = c_eval('-1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == -1
    assert e_eval('-1') == -1
