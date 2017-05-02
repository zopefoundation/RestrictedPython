from tests import e_eval

import pytest


@pytest.mark.parametrize(*e_eval)
def test_Or(e_eval):
    assert e_eval('False or True') is True


@pytest.mark.parametrize(*e_eval)
def test_And(e_eval):
    assert e_eval('True and True') is True


@pytest.mark.parametrize(*e_eval)
def test_Not(e_eval):
    assert e_eval('not False') is True
