from tests import c_eval
from tests import e_eval

import pytest


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Is(c_eval, e_eval):
    result = c_eval('True is True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('True is True') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_NotIs(c_eval, e_eval):
    result = c_eval('1 is not True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('1 is not True') is True
