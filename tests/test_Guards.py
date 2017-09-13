from RestrictedPython.Guards import guarded_unpack_sequence
from RestrictedPython.Guards import safe_builtins
from tests import e_eval
from tests import e_exec

import pytest


@pytest.mark.parametrize(*e_eval)
def test_Guards__safe_builtins__1(e_eval):
    """It contains `slice()`."""
    restricted_globals = dict(__builtins__=safe_builtins)
    assert e_eval('slice(1)', restricted_globals) == slice(1)


CLASS_SOURCE = '''
class C:
    value = None
    def display(self):
        return str(self.value)

c1 = C()
c1.value = 2411
b = c1.display()
'''


@pytest.mark.parametrize(*e_exec)
def test_Guards__safe_builtins__2(e_exec):
    """It allows to define new classes by allowing `__build_class__`.

    `__build_class__` is only needed in Python 3.
    """
    restricted_globals = dict(
        __builtins__=safe_builtins, b=None,
        __name__='restricted_module',
        __metaclass__=type,
        _write_=lambda x: x,
        _getattr_=getattr,)

    e_exec(CLASS_SOURCE, restricted_globals)
    assert restricted_globals['b'] == '2411'


class D:
    value = None
    _guarded_writes = 1


SET_ATTRIBUTE = '''
d1 = D()
setattr(d1, 'value', 9999)
'''


DEL_ATTRIBUTE = '''
delattr(d1, 'value')
'''


@pytest.mark.parametrize(*e_exec)
def test_Guards__safe_builtins__3(e_exec):
    """It allows use setattr and delattr when _guarded_writes is True.

    `__build_class__` is only needed in Python 3.
    """
    restricted_globals = dict(
        __builtins__=safe_builtins, D=D, d1=None,
        __name__='restricted_module',
        __metaclass__=type,
        _write_=lambda x: x,
        _getattr_=getattr,)

    e_exec(SET_ATTRIBUTE, restricted_globals)
    assert 9999 == restricted_globals['d1'].value

    e_exec(DEL_ATTRIBUTE, restricted_globals)
    assert None is restricted_globals['d1'].value


class E:
    foo = None


SET_ATTRIBUTE_WITHOUT_GUARDED_WRITES = '''
e1 = E()
setattr(e1, 'foo', 'bar')
'''


@pytest.mark.parametrize(*e_exec)
def test_Guards__write_wrapper__1(e_exec):
    """It wraps it when it is not marked with _guarded_writes."""
    restricted_globals = dict(
        __builtins__=safe_builtins, E=E, e1=None,
        __name__='restricted_module',
        __metaclass__=type,
        _write_=lambda x: x,
        _getattr_=getattr,)

    with pytest.raises(TypeError) as excinfo:
        e_exec(SET_ATTRIBUTE_WITHOUT_GUARDED_WRITES, restricted_globals)
    assert 'attribute-less object (assign or del)' in str(excinfo.value)


class F:
    foo = None

    def __guarded_setattr__(self, key, value):
        setattr(self, key, value)


SET_ATTRIBUTE_USING_GUARDED_SETATTR = '''
f1 = F()
setattr(f1, 'foo', 'bar')
'''


@pytest.mark.parametrize(*e_exec)
def test_Guards__write_wrapper__2(e_exec):
    """It wraps it and it works when guarded_setattr is implemented."""
    restricted_globals = dict(
        __builtins__=safe_builtins, F=F, f1=None,
        __name__='restricted_module',
        __metaclass__=type,
        _write_=lambda x: x,
        _getattr_=getattr,)

    e_exec(SET_ATTRIBUTE_USING_GUARDED_SETATTR, restricted_globals)
    assert restricted_globals['f1'].foo == 'bar'


@pytest.mark.parametrize(*e_exec)
def test_Guards__guarded_unpack_sequence__1(e_exec, mocker):
    """It does not protect unpacking when the sequence is shorter
    than expected."""
    src = "one, two, three = (1, 2)"

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it
    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence,
    }

    with pytest.raises(ValueError) as excinfo:
        e_exec(src, glb)
    assert 'values to unpack' in str(excinfo.value)
    assert _getiter_.call_count == 1
