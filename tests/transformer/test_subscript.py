from tests import e_exec

import pytest


GET_SUBSCRIPTS = """
def simple_subscript(a):
    return a['b']

def tuple_subscript(a):
    return a[1, 2]

def slice_subscript_no_upper_bound(a):
    return a[1:]

def slice_subscript_no_lower_bound(a):
    return a[:1]

def slice_subscript_no_step(a):
    return a[1:2]

def slice_subscript_with_step(a):
    return a[1:2:3]

def extended_slice_subscript(a):
    return a[0, :1, 1:, 1:2, 1:2:3]
"""


@pytest.mark.parametrize(*e_exec)
def test_read_subscripts(
        e_exec, mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    e_exec(GET_SUBSCRIPTS, glb)

    ret = glb['simple_subscript'](value)
    ref = (value, 'b')
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

    ret = glb['tuple_subscript'](value)
    ref = (value, (1, 2))
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

    ret = glb['slice_subscript_no_upper_bound'](value)
    ref = (value, slice(1, None, None))
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

    ret = glb['slice_subscript_no_lower_bound'](value)
    ref = (value, slice(None, 1, None))
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

    ret = glb['slice_subscript_no_step'](value)
    ref = (value, slice(1, 2, None))
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

    ret = glb['slice_subscript_with_step'](value)
    ref = (value, slice(1, 2, 3))
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

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
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()


WRITE_SUBSCRIPTS = """
def assign_subscript(a):
    a['b'] = 1

def del_subscript(a):
    del a['b']
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
    _write_.assert_called_once_with(value)
    _write_.reset_mock()

    glb['del_subscript'](value)
    assert value == {}
    _write_.assert_called_once_with(value)
    _write_.reset_mock()
