from tests import e_eval

import pytest


@pytest.mark.parametrize(*e_eval)
def test_Is(e_eval):
    assert e_eval('True is True') is True


@pytest.mark.parametrize(*e_eval)
def test_NotIs(e_eval):
    assert e_eval('1 is not True') is True
