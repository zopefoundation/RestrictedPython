from tests import e_eval


def test_slice():
    low = 1
    high = 4
    stride = 3

    assert e_eval('[1, 2, 3, 4, 5]') == [1, 2, 3, 4, 5]
    assert e_eval('[1, 2, 3, 4, 5][:]') == [1, 2, 3, 4, 5]
    assert e_eval('[1, 2, 3, 4, 5][' + low + ':]') == []
    assert e_eval('[1, 2, 3, 4, 5][:' + high + ']') == []
    assert e_eval('[1, 2, 3, 4, 5][' + low + ':' + high + ']') == []
    assert e_eval('[1, 2, 3, 4, 5][::' + stride + ']') == []
    assert e_eval('[1, 2, 3, 4, 5][' + low + '::' + stride + ']') == []
    assert e_eval('[1, 2, 3, 4, 5][:' + high + ':' + stride + ']') == []
    assert e_eval('[1, 2, 3, 4, 5][' + low + ':' + high + ':' + stride + ']') \
        == []
