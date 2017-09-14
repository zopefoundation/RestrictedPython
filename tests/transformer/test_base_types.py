from RestrictedPython import safe_builtins
from RestrictedPython._compat import IS_PY2
from RestrictedPython._compat import IS_PY3
from tests import c_exec
from tests import e_eval
from tests import e_exec

import pytest


@pytest.mark.parametrize(*e_eval)
def test_Num(e_eval):
    """It allows to use number literals."""
    assert e_eval('42') == 42


@pytest.mark.parametrize(*e_eval)
def test_Bytes(e_eval):
    """It allows to use bytes literals."""
    glb = {'_str_': str}
    assert e_eval('b"code"', glb) == b"code"


@pytest.mark.parametrize(*e_eval)
def test_Set(e_eval):
    """It allows to use set literals."""
    assert e_eval('{1, 2, 3}') == set([1, 2, 3])


@pytest.mark.skipif(IS_PY2,
                    reason="... is new in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_Ellipsis(c_exec):
    """It prevents using the `ellipsis` statement."""
    result = c_exec('...')
    assert result.errors == ('Line 1: Ellipsis statements are not allowed.',)


@pytest.mark.parametrize(*e_exec)
def test_Str__1(e_exec):
    """It returns a str subclass for strings."""
    glb = {
        '_getattr_': getattr,
        '__builtins__': safe_builtins,
    }
    e_exec('a = "Hello world!"', glb)
    assert isinstance(glb['a'], str)


@pytest.mark.skipif(IS_PY3, reason="In Python 3 there is no unicode.")
@pytest.mark.parametrize(*e_exec)
def test_Str__2(e_exec):
    """It returns a unicode subclass for unicodes."""
    glb = {
        '_getattr_': getattr,
        '__builtins__': safe_builtins,
    }
    e_exec('a = u"Hello world!"', glb)
    assert isinstance(glb['a'], unicode)


STRING_DOT_FORMAT_DENIED = """\
'Hello {}'.format('world')
"""


@pytest.mark.parametrize(*e_eval)
def test_Str__3(e_eval):
    """It prevents using the format method of a string.

    format() is considered harmful:
    http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
    """
    if IS_PY2:
        from RestrictedPython import RCompile
        if e_eval.compile_func is RCompile.compile_restricted_eval:
            pytest.skip('RCompile does not support secure strings.')
    glb = {
        '_getattr_': getattr,
        '__builtins__': safe_builtins,
    }
    with pytest.raises(NotImplementedError) as err:
        e_eval(STRING_DOT_FORMAT_DENIED, glb)
    assert 'Using format() is not safe.' == str(err.value)


UNICODE_DOT_FORMAT_DENIED = """\
u'Hello {}'.format('world')
"""


@pytest.mark.parametrize(*e_eval)
def test_Str__4(e_eval):
    """It prevents using the format method of a unicode.

    format() is considered harmful:
    http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
    """
    if IS_PY2:
        from RestrictedPython import RCompile
        if e_eval.compile_func is RCompile.compile_restricted_eval:
            pytest.skip('RCompile does not support secure unicode.')
    glb = {
        '_getattr_': getattr,
        '__builtins__': safe_builtins,
    }
    with pytest.raises(NotImplementedError) as err:
        e_eval(UNICODE_DOT_FORMAT_DENIED, glb)
    assert 'Using format() is not safe.' == str(err.value)
