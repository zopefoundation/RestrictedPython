from RestrictedPython._compat import IS_PY2
from RestrictedPython.Guards import guarded_unpack_sequence
from tests import e_exec

import pytest


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Assign__1(e_exec, mocker):
    src = "orig = (a, (x, z)) = (c, d) = g"

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence,
        'g': (1, (2, 3)),
    }

    e_exec(src, glb)
    assert glb['a'] == 1
    assert glb['x'] == 2
    assert glb['z'] == 3
    assert glb['c'] == 1
    assert glb['d'] == (2, 3)
    assert glb['orig'] == (1, (2, 3))
    assert _getiter_.call_count == 3
    _getiter_.assert_any_call((1, (2, 3)))
    _getiter_.assert_any_call((2, 3))
    _getiter_.reset_mock()


@pytest.mark.skipif(
    IS_PY2,
    reason="starred assignments are python3 only")
@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Assign__2(
        e_exec, mocker):
    src = "a, *d, (c, *e), x  = (1, 2, 3, (4, 3, 4), 5)"

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    e_exec(src, glb)
    assert glb['a'] == 1
    assert glb['d'] == [2, 3]
    assert glb['c'] == 4
    assert glb['e'] == [3, 4]
    assert glb['x'] == 5

    _getiter_.assert_has_calls([
        mocker.call((1, 2, 3, (4, 3, 4), 5)),
        mocker.call((4, 3, 4))])
