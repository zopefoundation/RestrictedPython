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
    assert e_eval('[1, 2, 3, 4, 5][%d:]' % low, rglb) == [2, 3, 4, 5]
    assert e_eval('[1, 2, 3, 4, 5][:%d]' % high, rglb) == [1, 2, 3, 4]
    assert e_eval('[1, 2, 3, 4, 5][%d:%d]' % (low, high), rglb) == [2, 3, 4]
    assert e_eval('[1, 2, 3, 4, 5][::%d]' % stride, rglb) == [1, 4]
    assert e_eval('[1, 2, 3, 4, 5][%d::%d]' % (low, stride), rglb) == [2, 5]
    assert e_eval('[1, 2, 3, 4, 5][:%d:%d]' % (high, stride), rglb) == [1, 4]
    assert e_eval('[1, 2, 3, 4, 5][%d:%d:%d]' % (low, high, stride), rglb) == [2]  # NOQA: E501
