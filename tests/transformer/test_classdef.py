from RestrictedPython._compat import IS_PY2
from RestrictedPython.Guards import safe_builtins
from tests import c_exec
from tests import e_exec

import pytest
import RestrictedPython


GOOD_CLASS = '''
class Good:
    pass
'''


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_ClassDef__1(c_exec):
    """It allows to define an class."""
    result = c_exec(GOOD_CLASS)
    assert result.errors == ()
    assert result.code is not None


BAD_CLASS = '''\
class _bad:
    pass
'''


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_ClassDef__2(c_exec):
    """It does not allow class names which start with an underscore."""
    result = c_exec(BAD_CLASS)
    assert result.errors == (
        'Line 1: "_bad" is an invalid variable name '
        'because it starts with "_"',)


IMPLICIT_METACLASS = '''
class Meta:
    pass

b = Meta().foo
'''


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_ClassDef__3(e_exec):
    """It applies the global __metaclass__ to all generated classes if present.
    """
    def _metaclass(name, bases, dict):
        ob = type(name, bases, dict)
        ob.foo = 2411
        return ob

    restricted_globals = dict(
        __metaclass__=_metaclass, b=None, _getattr_=getattr)

    e_exec(IMPLICIT_METACLASS, restricted_globals)

    assert restricted_globals['b'] == 2411


EXPLICIT_METACLASS = '''
class WithMeta(metaclass=MyMetaClass):
    pass
'''


@pytest.mark.skipif(IS_PY2, reason="No valid syntax in Python 2.")
@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_ClassDef__4(c_exec):
    """It does not allow to pass a metaclass to class definitions."""

    result = c_exec(EXPLICIT_METACLASS)

    assert result.errors == (
        'Line 2: The keyword argument "metaclass" is not allowed.',)
    assert result.code is None


DECORATED_CLASS = '''\
def wrap(cls):
    cls.wrap_att = 23
    return cls

class Base:
    base_att = 42

@wrap
class Combined(Base):
    class_att = 2342

comb = Combined()
'''


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_ClassDef__5(e_exec):
    """It preserves base classes and decorators for classes."""

    restricted_globals = dict(
        comb=None, _getattr_=getattr, _write_=lambda x: x, __metaclass__=type,
        __name__='restricted_module', __builtins__=safe_builtins)

    e_exec(DECORATED_CLASS, restricted_globals)

    comb = restricted_globals['comb']
    assert comb.class_att == 2342
    assert comb.base_att == 42
    if e_exec.compile_func is RestrictedPython.compile.compile_restricted_exec:
        # Class decorators are only supported by the new implementation.
        assert comb.wrap_att == 23
