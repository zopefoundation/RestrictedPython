import pytest

from RestrictedPython.Utilities import reorder
from RestrictedPython.Utilities import test
from RestrictedPython.Utilities import utility_builtins


def test_Utilities__test_1():
    """It returns the first arg after the first argument which is True"""
    assert test(True, 1, False, 2) == 1
    assert test(False, 1, True, 2) == 2
    assert test(False, 1, False, 2, True, 3) == 3


def test_Utilities__test_2():
    """If the above is not met, and there is an extra argument
    it returns it."""
    assert test(False, 1, False, 2, 3) == 3
    assert test(False, 1, 2) == 2
    assert test(1) == 1
    assert not test(False)


def test_Utilities__test_3():
    """It returns None if there are only False args followed by something."""
    assert test(False, 1) is None
    assert test(False, 1, False, 2) is None


def test_Utilities__reorder_1():
    """It also supports 2-tuples containing key, value."""
    s = [('k1', 'v1'), ('k2', 'v2'), ('k3', 'v3')]
    _with = [('k2', 'v2'), ('k3', 'v3')]
    without = [('k2', 'v2'), ('k4', 'v4')]
    assert reorder(s, _with, without) == [('k3', 'v3')]


def test_Utilities_string_Formatter():
    """Access to ``string.Formatter`` is denied."""
    string = utility_builtins["string"]
    # access successful in principle
    assert string.ascii_lowercase == 'abcdefghijklmnopqrstuvwxyz'
    with pytest.raises(NotImplementedError) as exc:
        string.Formatter
    assert 'string.Formatter is not safe' == str(exc.value)
