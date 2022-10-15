from operator import getitem

from tests.helper import restricted_eval


def test_slice():
    rglb = {'_getitem_': getitem}  # restricted globals

    assert restricted_eval('[1, 2, 3, 4, 5]', rglb) == [1, 2, 3, 4, 5]
    assert restricted_eval('[1, 2, 3, 4, 5][:]', rglb) == [1, 2, 3, 4, 5]
    assert restricted_eval('[1, 2, 3, 4, 5][1:]', rglb) == [2, 3, 4, 5]
    assert restricted_eval('[1, 2, 3, 4, 5][:4]', rglb) == [1, 2, 3, 4]
    assert restricted_eval('[1, 2, 3, 4, 5][1:4]', rglb) == [2, 3, 4]
    assert restricted_eval('[1, 2, 3, 4, 5][::3]', rglb) == [1, 4]
    assert restricted_eval('[1, 2, 3, 4, 5][1::3]', rglb) == [2, 5]
    assert restricted_eval('[1, 2, 3, 4, 5][:4:3]', rglb) == [1, 4]
    assert restricted_eval('[1, 2, 3, 4, 5][1:4:3]', rglb) == [2]
