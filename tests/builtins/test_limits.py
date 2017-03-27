from RestrictedPython.Limits import limited_list
from RestrictedPython.Limits import limited_range
from RestrictedPython.Limits import limited_tuple

import pytest


def test_limited_range_length_1():
    result = limited_range(1)
    assert result == range(0, 1)


def test_limited_range_length_10():
    result = limited_range(10)
    assert result == range(0, 10)


def test_limited_range_5_10():
    result = limited_range(5, 10)
    assert result == range(5, 10)


def test_limited_range_5_10_sm1():
    result = limited_range(5, 10, -1)
    assert result == range(5, 10, -1)


def test_limited_range_15_10_s2():
    result = limited_range(15, 10, 2)
    assert result == range(15, 10, 2)


def test_limited_range_no_input():
    with pytest.raises(TypeError):
        limited_range()


def test_limited_range_more_steps():
    with pytest.raises(AttributeError):
        limited_range(0, 0, 0, 0)


def test_limited_range_zero_step():
    with pytest.raises(ValueError):
        limited_range(0, 10, 0)


def test_limited_range_range_overflow():
    with pytest.raises(ValueError):
        limited_range(0, 5000, 1)


def test_limited_list_valid_list_input():
    input = [1, 2, 3]
    result = limited_list(input)
    assert result == input


def test_limited_list_invalid_string_input():
    with pytest.raises(TypeError):
        limited_list('input')


def test_limited_tuple_valid_list_input():
    input = [1, 2, 3]
    result = limited_tuple(input)
    assert result == tuple(input)


def test_limited_tuple_invalid_string_input():
    with pytest.raises(TypeError):
        limited_tuple('input')
