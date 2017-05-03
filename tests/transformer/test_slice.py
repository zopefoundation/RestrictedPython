from tests import e_eval

import pytest


@pytest.mark.parametrize(*e_eval)
def test_slice(e_eval):
    low = 1
    high = 4
    stride = 3

    from operator import getitem
    rgbl = dict(_getitem_=getitem)  # restricted globals

    assert e_eval('[1, 2, 3, 4, 5]', rgbl) == [1, 2, 3, 4, 5]
    assert e_eval('[1, 2, 3, 4, 5][:]', rgbl) == [1, 2, 3, 4, 5]
    assert e_eval('[1, 2, 3, 4, 5][%d:]' % low, rgbl) == [2, 3, 4, 5]
    assert e_eval('[1, 2, 3, 4, 5][:%d]' % high, rgbl) == [1, 2, 3, 4]
    assert e_eval('[1, 2, 3, 4, 5][%d:%d]' % (low, high), rgbl) == [2, 3, 4]
    assert e_eval('[1, 2, 3, 4, 5][::%d]' % stride, rgbl) == [1, 4]
    assert e_eval('[1, 2, 3, 4, 5][%d::%d]' % (low, stride), rgbl) == [2, 5]
    assert e_eval('[1, 2, 3, 4, 5][:%d:%d]' % (high, stride), rgbl) == [1, 4]
    assert e_eval('[1, 2, 3, 4, 5][%d:%d:%d]' % (low, high, stride), rgbl) == [2]  # NOQA: E501
