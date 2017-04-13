from tests import c_eval
from tests import e_eval

import pytest


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Or(c_eval, e_eval):
    result = c_eval('False or True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('False or True') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_And(c_eval, e_eval):
    result = c_eval('True and True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('True and True') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Not(c_eval, e_eval):
    result = c_eval('not False')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('not False') is True
