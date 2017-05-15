from tests import c_exec
from tests import e_exec

import pytest


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Call__1(c_exec):
    """It compiles a function call successfully and returns the used name."""
    result = c_exec('a = max([1, 2, 3])')
    assert result.errors == ()
    loc = {}
    exec(result.code, {}, loc)
    assert loc['a'] == 3
    assert result.used_names == {'max': True}


# def f(a, b, c): pass
# f(*two_element_sequence, **dict_with_key_c)
#
# makes the elements of two_element_sequence
# visible to f via its 'a' and 'b' arguments,
# and the dict_with_key_c['c'] value visible via its 'c' argument.
# It is a devious way to extract values without going through security checks.

FUNCTIONC_CALLS = """
star = (3, 4)
kwargs = {'x': 5, 'y': 6}

def positional_args():
    return foo(1, 2)

def star_args():
    return foo(*star)

def positional_and_star_args():
    return foo(1, 2, *star)

def kw_args():
    return foo(**kwargs)

def star_and_kw():
    return foo(*star, **kwargs)

def positional_and_star_and_kw_args():
    return foo(1, *star, **kwargs)

def positional_and_star_and_keyword_and_kw_args():
    return foo(1, 2, *star, r=9, **kwargs)
"""


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Call__2(e_exec, mocker):
    _apply_ = mocker.stub()
    _apply_.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)

    glb = {
        '_apply_': _apply_,
        'foo': lambda *args, **kwargs: (args, kwargs)
    }

    e_exec(FUNCTIONC_CALLS, glb)

    ret = glb['positional_args']()
    assert ((1, 2), {}) == ret
    assert _apply_.called is False
    _apply_.reset_mock()

    ret = glb['star_args']()
    ref = ((3, 4), {})
    assert ref == ret
    _apply_.assert_called_once_with(glb['foo'], *ref[0])
    _apply_.reset_mock()

    ret = glb['positional_and_star_args']()
    ref = ((1, 2, 3, 4), {})
    assert ref == ret
    _apply_.assert_called_once_with(glb['foo'], *ref[0])
    _apply_.reset_mock()

    ret = glb['kw_args']()
    ref = ((), {'x': 5, 'y': 6})
    assert ref == ret
    _apply_.assert_called_once_with(glb['foo'], **ref[1])
    _apply_.reset_mock()

    ret = glb['star_and_kw']()
    ref = ((3, 4), {'x': 5, 'y': 6})
    assert ref == ret
    _apply_.assert_called_once_with(glb['foo'], *ref[0], **ref[1])
    _apply_.reset_mock()

    ret = glb['positional_and_star_and_kw_args']()
    ref = ((1, 3, 4), {'x': 5, 'y': 6})
    assert ref == ret
    _apply_.assert_called_once_with(glb['foo'], *ref[0], **ref[1])
    _apply_.reset_mock()

    ret = glb['positional_and_star_and_keyword_and_kw_args']()
    ref = ((1, 2, 3, 4), {'x': 5, 'y': 6, 'r': 9})
    assert ref == ret
    _apply_.assert_called_once_with(glb['foo'], *ref[0], **ref[1])
    _apply_.reset_mock()
