from operator import getitem
from RestrictedPython import compile_restricted_eval
from RestrictedPython import compile_restricted_exec
from RestrictedPython._compat import IS_PY2
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


@pytest.mark.xfail
@pytest.mark.skipif(
    IS_PY2,
    reason="Ellipsis is Python 3 only."
)
def test_ellipsis_slice_01():
    rglb = {'_getitem_': getitem}  # restricted globals

    assert eval(
        compile_restricted_eval(
            '[1, 2, 3, 4, 5, 6, 7] == [1, 2, 3, ... , 7]'
        ).code,
        rglb
    ) is True


ELLIPSIS_EXAMPLE = """
from array import Array

data_array = Array('l', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

data[1, ..., 1]
"""


@pytest.mark.skipif(
    IS_PY2,
    reason="Ellipsis is Python 3 only."
)
def test_ellipsis_slice_02():
    result = compile_restricted_exec(ELLIPSIS_EXAMPLE)
    assert result.errors == ()
    assert result.warnings == []
    assert result.code is not None
