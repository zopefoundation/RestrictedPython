import pytest

from RestrictedPython import compile_restricted_exec
from RestrictedPython._compat import IS_PY311_OR_GREATER
from tests.helper import restricted_exec


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


TRY_EXCEPT_STAR = """
def try_except_star(m):
    try:
        m('try')
        raise ExceptionGroup("group", [IndentationError('f1'), ValueError(65)])
    except* IndentationError:
        m('IndentationError')
    except* ValueError:
        m('ValueError')
    except* RuntimeError:
        m('RuntimeError')
"""


@pytest.mark.skipif(
    not IS_PY311_OR_GREATER,
    reason="ExceptionGroup class was added in Python 3.11.",
)
def test_RestrictingNodeTransformer__visit_TryStar__1(mocker):
    """It allows try-except* PEP 654 statements."""
    trace = mocker.stub()
    restricted_exec(TRY_EXCEPT_STAR)['try_except_star'](trace)

    trace.assert_has_calls([
        mocker.call('try'),
        mocker.call('IndentationError'),
        mocker.call('ValueError')
    ])

    with pytest.raises(AssertionError):
        trace.assert_has_calls([mocker.call('RuntimeError')])


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
