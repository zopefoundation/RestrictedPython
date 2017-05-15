from RestrictedPython.Guards import guarded_unpack_sequence
from tests import c_exec
from tests import e_exec

import contextlib
import pytest


WITH_STMT_WITH_UNPACK_SEQUENCE = """
def call(ctx):
    with ctx() as (a, (c, b)):
        return a, c, b
"""


@pytest.mark.parametrize(*e_exec)
def test_with_stmt_unpack_sequence(e_exec, mocker):
    @contextlib.contextmanager
    def ctx():
        yield (1, (2, 3))

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda ob: ob

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    e_exec(WITH_STMT_WITH_UNPACK_SEQUENCE, glb)

    ret = glb['call'](ctx)

    assert ret == (1, 2, 3)
    _getiter_.assert_has_calls([
        mocker.call((1, (2, 3))),
        mocker.call((2, 3))])


WITH_STMT_MULTI_CTX_WITH_UNPACK_SEQUENCE = """
def call(ctx1, ctx2):
    with ctx1() as (a, (b, c)), ctx2() as ((x, z), (s, h)):
        return a, b, c, x, z, s, h
"""


@pytest.mark.parametrize(*c_exec)
def test_with_stmt_multi_ctx_unpack_sequence(c_exec, mocker):
    result = c_exec(WITH_STMT_MULTI_CTX_WITH_UNPACK_SEQUENCE)
    assert result.errors == ()

    @contextlib.contextmanager
    def ctx1():
        yield (1, (2, 3))

    @contextlib.contextmanager
    def ctx2():
        yield (4, 5), (6, 7)

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda ob: ob

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    exec(result.code, glb)

    ret = glb['call'](ctx1, ctx2)

    assert ret == (1, 2, 3, 4, 5, 6, 7)
    _getiter_.assert_has_calls([
        mocker.call((1, (2, 3))),
        mocker.call((2, 3)),
        mocker.call(((4, 5), (6, 7))),
        mocker.call((4, 5)),
        mocker.call((6, 7))
    ])


WITH_STMT_ATTRIBUTE_ACCESS = """
def simple(ctx):
    with ctx as x:
        x.z = x.y + 1

def assign_attr(ctx, x):
    with ctx as x.y:
        x.z = 1

def load_attr(w):
    with w.ctx as x:
        x.z = 1

"""


@pytest.mark.parametrize(*e_exec)
def test_with_stmt_attribute_access(e_exec, mocker):
    _getattr_ = mocker.stub()
    _getattr_.side_effect = getattr

    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob

    glb = {'_getattr_': _getattr_, '_write_': _write_}
    e_exec(WITH_STMT_ATTRIBUTE_ACCESS, glb)

    # Test simple
    ctx = mocker.MagicMock(y=1)
    ctx.__enter__.return_value = ctx

    glb['simple'](ctx)

    assert ctx.z == 2
    _write_.assert_called_once_with(ctx)
    _getattr_.assert_called_once_with(ctx, 'y')

    _write_.reset_mock()
    _getattr_.reset_mock()

    # Test assign_attr
    x = mocker.Mock()
    glb['assign_attr'](ctx, x)

    assert x.z == 1
    assert x.y == ctx
    _write_.assert_has_calls([
        mocker.call(x),
        mocker.call(x)
    ])

    _write_.reset_mock()

    # Test load_attr
    ctx = mocker.MagicMock()
    ctx.__enter__.return_value = ctx

    w = mocker.Mock(ctx=ctx)

    glb['load_attr'](w)

    assert w.ctx.z == 1
    _getattr_.assert_called_once_with(w, 'ctx')
    _write_.assert_called_once_with(w.ctx)


WITH_STMT_SUBSCRIPT = """
def single_key(ctx, x):
    with ctx as x['key']:
        pass


def slice_key(ctx, x):
    with ctx as x[2:3]:
        pass
"""


@pytest.mark.parametrize(*e_exec)
def test_with_stmt_subscript(e_exec, mocker):
    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob

    glb = {'_write_': _write_}
    e_exec(WITH_STMT_SUBSCRIPT, glb)

    # Test single_key
    ctx = mocker.MagicMock()
    ctx.__enter__.return_value = ctx
    x = {}

    glb['single_key'](ctx, x)

    assert x['key'] == ctx
    _write_.assert_called_once_with(x)
    _write_.reset_mock()

    # Test slice_key
    ctx = mocker.MagicMock()
    ctx.__enter__.return_value = (1, 2)

    x = [0, 0, 0, 0, 0, 0]
    glb['slice_key'](ctx, x)

    assert x == [0, 0, 1, 2, 0, 0, 0]
    _write_.assert_called_once_with(x)
