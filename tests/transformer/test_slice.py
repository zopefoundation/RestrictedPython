# -*- coding: utf-8 -*-

from operator import getitem
from tests import e_eval

import pytest


@pytest.mark.parametrize(*e_eval)
def test_slice(e_eval):
    low = 1
    high = 4
    stride = 3

    rglb = {'_getitem_': getitem}  # restricted globals

    assert e_eval('[1, 2, 3, 4, 5]', rglb) == [1, 2, 3, 4, 5]
    assert e_eval('[1, 2, 3, 4, 5][:]', rglb) == [1, 2, 3, 4, 5]
    assert e_eval('[1, 2, 3, 4, 5][{low:d}:]'.format(low=low), rglb) == [2, 3, 4, 5]  # NOQA: E501
    assert e_eval('[1, 2, 3, 4, 5][:{high:d}]'.format(high=high), rglb) == [1, 2, 3, 4]  # NOQA: E501
    assert e_eval('[1, 2, 3, 4, 5][{low:d}:{high:d}]'.format(low=low, high=high), rglb) == [2, 3, 4]  # NOQA: E501
    assert e_eval('[1, 2, 3, 4, 5][::{stride:d}]'.format(stride=stride), rglb) == [1, 4]  # NOQA: E501
    assert e_eval('[1, 2, 3, 4, 5][{low:d}::{stride:d}]'.format(low=low, stride=stride), rglb) == [2, 5]  # NOQA: E501
    assert e_eval('[1, 2, 3, 4, 5][:{high:d}:{stride:d}]'.format(high=high, stride=stride), rglb) == [1, 4]  # NOQA: E501
    assert e_eval('[1, 2, 3, 4, 5][{low:d}:{high:d}:{stride:d}]'.format(low=low, high=high, stride=stride), rglb) == [2]  # NOQA: E501
