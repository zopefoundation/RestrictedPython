from RestrictedPython.Guards import guarded_iter_unpack_sequence
from tests import e_exec

import pytest
import RestrictedPython
import types


ITERATORS = """
def for_loop(it):
    c = 0
    for a in it:
        c = c + a
    return c


def nested_for_loop(it1, it2):
    c = 0
    for a in it1:
        for b in it2:
            c = c + a + b
    return c

def dict_comp(it):
    return {a: a + a for a in it}

def list_comp(it):
    return [a + a for a in it]

def nested_list_comp(it1, it2):
    return [a + b for a in it1 if a > 1 for b in it2]

def set_comp(it):
    return {a + a for a in it}

def generator(it):
    return (a + a for a in it)

def nested_generator(it1, it2):
    return (a+b for a in it1 if a > 0 for b in it2)
"""


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__guard_iter__1(e_exec, mocker):
    it = (1, 2, 3)
    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda x: x
    glb = {'_getiter_': _getiter_}
    e_exec(ITERATORS, glb)

    ret = glb['for_loop'](it)
    assert 6 == ret
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['nested_for_loop']((1, 2), (3, 4))
    assert 20 == ret
    _getiter_.assert_has_calls([
        mocker.call((1, 2)),
        mocker.call((3, 4))
    ])
    _getiter_.reset_mock()

    ret = glb['dict_comp'](it)
    assert {1: 2, 2: 4, 3: 6} == ret
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['list_comp'](it)
    assert [2, 4, 6] == ret
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['nested_list_comp']((1, 2), (3, 4))
    assert [5, 6] == ret
    _getiter_.assert_has_calls([
        mocker.call((1, 2)),
        mocker.call((3, 4))
    ])
    _getiter_.reset_mock()

    ret = glb['set_comp'](it)
    assert {2, 4, 6} == ret
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['generator'](it)
    assert isinstance(ret, types.GeneratorType)
    assert list(ret) == [2, 4, 6]
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['nested_generator']((0, 1, 2), (1, 2))
    assert isinstance(ret, types.GeneratorType)
    assert list(ret) == [2, 3, 3, 4]
    _getiter_.assert_has_calls([
        mocker.call((0, 1, 2)),
        mocker.call((1, 2)),
        mocker.call((1, 2))])
    _getiter_.reset_mock()


ITERATORS_WITH_UNPACK_SEQUENCE = """
def for_loop(it):
    c = 0
    for (a, b) in it:
        c = c + a + b
    return c

def dict_comp(it):
    return {a: a + b for (a, b) in it}

def list_comp(it):
    return [a + b for (a, b) in it]

def set_comp(it):
    return {a + b for (a, b) in it}

def generator(it):
    return (a + b for (a, b) in it)
"""


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__guard_iter__2(e_exec, mocker):
    it = ((1, 2), (3, 4), (5, 6))

    call_ref = [
        mocker.call(it),
        mocker.call(it[0]),
        mocker.call(it[1]),
        mocker.call(it[2])
    ]

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda x: x

    glb = {
        '_getiter_': _getiter_,
        '_iter_unpack_sequence_': guarded_iter_unpack_sequence
    }

    e_exec(ITERATORS_WITH_UNPACK_SEQUENCE, glb)

    ret = glb['for_loop'](it)
    assert ret == 21
    _getiter_.assert_has_calls(call_ref)
    _getiter_.reset_mock()

    ret = glb['dict_comp'](it)
    assert ret == {1: 3, 3: 7, 5: 11}
    _getiter_.assert_has_calls(call_ref)
    _getiter_.reset_mock()

    ret = glb['list_comp'](it)
    assert ret == [3, 7, 11]
    _getiter_.assert_has_calls(call_ref)
    _getiter_.reset_mock()

    ret = glb['set_comp'](it)
    assert ret == {3, 7, 11}
    _getiter_.assert_has_calls(call_ref)
    _getiter_.reset_mock()

    # The old code did not run with unpack sequence inside generators
    if compile == RestrictedPython.compile.compile_restricted_exec:
        ret = list(glb['generator'](it))
        assert ret == [3, 7, 11]
        _getiter_.assert_has_calls(call_ref)
        _getiter_.reset_mock()
