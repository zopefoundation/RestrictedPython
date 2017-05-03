from tests import e_exec

import pytest


SIMPLE_SUBSCRIPTS = """
def simple_subscript(a):
    return a['b']
"""


@pytest.mark.parametrize(*e_exec)
def test_read_simple_subscript(e_exec, mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    e_exec(SIMPLE_SUBSCRIPTS, glb)

    assert (value, 'b') == glb['simple_subscript'](value)


TUPLE_SUBSCRIPTS = """
def tuple_subscript(a):
    return a[1, 2]
"""


@pytest.mark.parametrize(*e_exec)
def test_tuple_subscript(e_exec, mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    e_exec(TUPLE_SUBSCRIPTS, glb)

    assert (value, (1, 2)) == glb['tuple_subscript'](value)


SLICE_SUBSCRIPT_NO_UPPER_BOUND = """
def slice_subscript_no_upper_bound(a):
    return a[1:]
"""


@pytest.mark.parametrize(*e_exec)
def test_read_slice_subscript_no_upper_bound(e_exec, mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    e_exec(SLICE_SUBSCRIPT_NO_UPPER_BOUND, glb)

    assert (value, slice(1, None, None)) == glb['slice_subscript_no_upper_bound'](value)  # NOQA: E501


SLICE_SUBSCRIPT_NO_LOWER_BOUND = """
def slice_subscript_no_lower_bound(a):
    return a[:1]
"""


@pytest.mark.parametrize(*e_exec)
def test_read_slice_subscript_no_lower_bound(e_exec, mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    e_exec(SLICE_SUBSCRIPT_NO_LOWER_BOUND, glb)

    assert (value, slice(None, 1, None)) == glb['slice_subscript_no_lower_bound'](value)  # NOQA: E501


SLICE_SUBSCRIPT_NO_STEP = """
def slice_subscript_no_step(a):
    return a[1:2]
"""


@pytest.mark.parametrize(*e_exec)
def test_read_slice_subscript_no_step(e_exec, mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    e_exec(SLICE_SUBSCRIPT_NO_STEP, glb)

    assert (value, slice(1, 2, None)) == glb['slice_subscript_no_step'](value)


SLICE_SUBSCRIPT_WITH_STEP = """
def slice_subscript_with_step(a):
    return a[1:2:3]
"""


@pytest.mark.parametrize(*e_exec)
def test_read_slice_subscript_with_step(e_exec, mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    e_exec(SLICE_SUBSCRIPT_WITH_STEP, glb)

    assert (value, slice(1, 2, 3)) == glb['slice_subscript_with_step'](value)


EXTENDED_SLICE_SUBSCRIPT = """

def extended_slice_subscript(a):
    return a[0, :1, 1:, 1:2, 1:2:3]
"""


@pytest.mark.parametrize(*e_exec)
def test_read_extended_slice_subscript(e_exec, mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    e_exec(EXTENDED_SLICE_SUBSCRIPT, glb)
    ret = glb['extended_slice_subscript'](value)
    ref = (
        value,
        (
            0,
            slice(None, 1, None),
            slice(1, None, None),
            slice(1, 2, None),
            slice(1, 2, 3)
        )
    )

    assert ref == ret


WRITE_SUBSCRIPTS = """
def assign_subscript(a):
    a['b'] = 1
"""


@pytest.mark.parametrize(*e_exec)
def test_write_subscripts(
        e_exec, mocker):
    value = {'b': None}
    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob
    glb = {'_write_': _write_}
    e_exec(WRITE_SUBSCRIPTS, glb)

    glb['assign_subscript'](value)
    assert value['b'] == 1


DEL_SUBSCRIPT = """
def del_subscript(a):
    del a['b']
"""


@pytest.mark.parametrize(*e_exec)
def test_del_subscripts(
        e_exec, mocker):
    value = {'b': None}
    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob
    glb = {'_write_': _write_}
    e_exec(DEL_SUBSCRIPT, glb)
    glb['del_subscript'](value)

    assert value == {}
