from tests import e_eval


def test_slice():
    low = 1
    high = 4
    stride = 3
    
    from operator import getitem
    restricted_globals = dict(_getitem_=getitem)
    restricted_eval = lambda code: e_eval[1][1](code, restricted_globals)

    assert restricted_eval('[1, 2, 3, 4, 5]') == [1, 2, 3, 4, 5]
    assert restricted_eval('[1, 2, 3, 4, 5][:]') == [1, 2, 3, 4, 5]
    assert restricted_eval('[1, 2, 3, 4, 5][%d:]' % low) == [2, 3, 4, 5]
    assert restricted_eval('[1, 2, 3, 4, 5][:%d]' % high) == [1, 2, 3, 4]
    assert restricted_eval('[1, 2, 3, 4, 5][%d:%d]' % (low, high)) == [2, 3, 4]
    assert restricted_eval('[1, 2, 3, 4, 5][::%d]' % stride) == [1, 4]
    assert restricted_eval('[1, 2, 3, 4, 5][%d::%d]' % (low, stride)) == [2, 5]
    assert restricted_eval('[1, 2, 3, 4, 5][:%d:%d]' % (high, stride)) == [1, 4]
    assert restricted_eval('[1, 2, 3, 4, 5][%d:%d:%d]' % (low, high, stride)) == [2]
