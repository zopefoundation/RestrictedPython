from RestrictedPython import compile_restricted_exec
from RestrictedPython._compat import IS_PY3
from RestrictedPython.Guards import guarded_unpack_sequence
from tests.helper import restricted_exec

import pytest


TRY_EXCEPT = """
def try_except(m):
    try:
        m('try')
        raise IndentationError('f1')
    except IndentationError as error:
        m('except')
"""


def test_RestrictingNodeTransformer__visit_Try__1(
        mocker):
    """It allows try-except statements."""
    trace = mocker.stub()
    restricted_exec(TRY_EXCEPT)['try_except'](trace)

    trace.assert_has_calls([
        mocker.call('try'),
        mocker.call('except')
    ])


TRY_EXCEPT_ELSE = """
def try_except_else(m):
    try:
        m('try')
    except:
        m('except')
    else:
        m('else')
"""


def test_RestrictingNodeTransformer__visit_Try__2(
        mocker):
    """It allows try-except-else statements."""
    trace = mocker.stub()
    restricted_exec(TRY_EXCEPT_ELSE)['try_except_else'](trace)

    trace.assert_has_calls([
        mocker.call('try'),
        mocker.call('else')
    ])


TRY_FINALLY = """
def try_finally(m):
    try:
        m('try')
        1 / 0
    finally:
        m('finally')
        return
"""


def test_RestrictingNodeTransformer__visit_TryFinally__1(
        mocker):
    """It allows try-finally statements."""
    trace = mocker.stub()
    restricted_exec(TRY_FINALLY)['try_finally'](trace)

    trace.assert_has_calls([
        mocker.call('try'),
        mocker.call('finally')
    ])


TRY_EXCEPT_FINALLY = """
def try_except_finally(m):
    try:
        m('try')
        1 / 0
    except:
        m('except')
    finally:
        m('finally')
"""


def test_RestrictingNodeTransformer__visit_TryFinally__2(
        mocker):
    """It allows try-except-finally statements."""
    trace = mocker.stub()
    restricted_exec(TRY_EXCEPT_FINALLY)['try_except_finally'](trace)

    trace.assert_has_calls([
        mocker.call('try'),
        mocker.call('except'),
        mocker.call('finally')
    ])


TRY_EXCEPT_ELSE_FINALLY = """
def try_except_else_finally(m):
    try:
        m('try')
    except:
        m('except')
    else:
        m('else')
    finally:
        m('finally')
"""


def test_RestrictingNodeTransformer__visit_TryFinally__3(
        mocker):
    """It allows try-except-else-finally statements."""
    trace = mocker.stub()
    restricted_exec(TRY_EXCEPT_ELSE_FINALLY)['try_except_else_finally'](trace)

    trace.assert_has_calls([
        mocker.call('try'),
        mocker.call('else'),
        mocker.call('finally')
    ])


EXCEPT_WITH_TUPLE_UNPACK = """
def tuple_unpack(err):
    try:
        raise err
    except Exception as (a, (b, c)):
        return a + b + c
"""


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple unpacking on exceptions is gone in python3")
def test_RestrictingNodeTransformer__visit_ExceptHandler__1(
        mocker):  # pragma: PY2
    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    restricted_exec(EXCEPT_WITH_TUPLE_UNPACK, glb)
    err = Exception(1, (2, 3))
    ret = glb['tuple_unpack'](err)
    assert ret == 6

    _getiter_.assert_has_calls([
        mocker.call(err),
        mocker.call((2, 3))])


BAD_TRY_EXCEPT = """
def except_using_bad_name():
    try:
        foo
    except NameError as _leading_underscore:
        # The name of choice (say, _write) is now assigned to an exception
        # object.  Hard to exploit, but conceivable.
        pass
"""


def test_RestrictingNodeTransformer__visit_ExceptHandler__2():
    """It denies bad names in the except as statement."""
    result = compile_restricted_exec(BAD_TRY_EXCEPT)
    assert result.errors == (
        'Line 5: "_leading_underscore" is an invalid variable name because '
        'it starts with "_"',)
