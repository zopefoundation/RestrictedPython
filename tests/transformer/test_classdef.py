from RestrictedPython import compile_restricted_exec
from RestrictedPython.Guards import safe_builtins
from tests.helper import restricted_exec


GOOD_CLASS = '''
class Good:
    pass
'''


def test_RestrictingNodeTransformer__visit_ClassDef__1():
    """It allows to define an class."""
    result = compile_restricted_exec(GOOD_CLASS)
    assert result.errors == ()
    assert result.code is not None


BAD_CLASS = '''\
class _bad:
    pass
'''


def test_RestrictingNodeTransformer__visit_ClassDef__2():
    """It does not allow class names which start with an underscore."""
    result = compile_restricted_exec(BAD_CLASS)
    assert result.errors == (
        'Line 1: "_bad" is an invalid variable name '
        'because it starts with "_"',)


IMPLICIT_METACLASS = '''
class Meta:
    pass

b = Meta().foo
'''


def test_RestrictingNodeTransformer__visit_ClassDef__3():
    """It applies the global __metaclass__ to all generated classes if present.
    """
    def _metaclass(name, bases, dict):
        ob = type(name, bases, dict)
        ob.foo = 2411
        return ob

    restricted_globals = dict(
        __metaclass__=_metaclass,
        __name__='implicit_metaclass',
        b=None,
        _getattr_=getattr)

    restricted_exec(IMPLICIT_METACLASS, restricted_globals)

    assert restricted_globals['b'] == 2411


EXPLICIT_METACLASS = '''
class WithMeta(metaclass=MyMetaClass):
    pass
'''


def test_RestrictingNodeTransformer__visit_ClassDef__4():
    """It does not allow to pass a metaclass to class definitions."""

    result = compile_restricted_exec(EXPLICIT_METACLASS)

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


def test_RestrictingNodeTransformer__visit_ClassDef__5():
    """It preserves base classes and decorators for classes."""

    restricted_globals = dict(
        comb=None, _getattr_=getattr, _write_=lambda x: x, __metaclass__=type,
        __name__='restricted_module', __builtins__=safe_builtins)

    restricted_exec(DECORATED_CLASS, restricted_globals)

    comb = restricted_globals['comb']
    assert comb.class_att == 2342
    assert comb.base_att == 42
    assert comb.wrap_att == 23


CONSTRUCTOR_TEST = """\
class Test:
    def __init__(self, input):
        self.input = input

t = Test(42)
"""


def test_RestrictingNodeTransformer__visit_ClassDef__6():
    """It allows to define an ``__init__`` method."""
    restricted_globals = dict(
        t=None,
        _write_=lambda x: x,
        __metaclass__=type,
        __name__='constructor_test',
    )

    restricted_exec(CONSTRUCTOR_TEST, restricted_globals)
    t = restricted_globals['t']
    assert t.input == 42


COMPARE_TEST = """\
class Test:

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

a = Test(42)
b = Test(42)
c = Test(43)

result1 = (a == b)
result2 = (b == c)
"""


def test_RestrictingNodeTransformer__visit_ClassDef__7():
    """It allows to define an ``__eq__`` method."""
    restricted_globals = dict(
        result1=None,
        result2=None,
        _getattr_=getattr,
        _write_=lambda x: x,
        __metaclass__=type,
        __name__='compare_test',
    )

    restricted_exec(COMPARE_TEST, restricted_globals)
    assert restricted_globals['result1'] is True
    assert restricted_globals['result2'] is False


CONTAINER_TEST = """\
class Test(object):

    def __init__(self, values):
        self.values = values

    def __contains__(self, value):
        return value in self.values

a = Test([1, 2, 3])

result1 = (1 in a)
result2 = (4 not in a)
"""


def test_RestrictingNodeTransformer__visit_ClassDef__8():
    """It allows to define a ``__contains__`` method."""
    restricted_globals = dict(
        result1=None,
        result2=None,
        _getattr_=getattr,
        _write_=lambda x: x,
        __metaclass__=type,
        __name__='container_test',
        object=object,
    )

    restricted_exec(CONTAINER_TEST, restricted_globals)
    assert restricted_globals['result1'] is True
    assert restricted_globals['result2'] is True
