from tests import e_eval

import pytest


@pytest.mark.parametrize(*e_eval)
def test_UAdd(e_eval):
    assert e_eval('+a', {'a': 42}) == 42


@pytest.mark.parametrize(*e_eval)
def test_USub(e_eval):
    assert e_eval('-a', {'a': 2411}) == -2411
