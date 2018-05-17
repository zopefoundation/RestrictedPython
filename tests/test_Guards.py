from RestrictedPython._compat import IS_PY2
from RestrictedPython.Guards import guarded_unpack_sequence
from RestrictedPython.Guards import safe_builtins
from RestrictedPython.Guards import safer_getattr
from tests import e_eval
from tests import e_exec

import pytest


@pytest.mark.parametrize(*e_eval)
def test_Guards__safe_builtins__1(e_eval):
    """It contains `slice()`."""
    restricted_globals = dict(__builtins__=safe_builtins)
    assert e_eval('slice(1)', restricted_globals) == slice(1)


@pytest.mark.parametrize(*e_exec)
def test_Guards__safe_builtins__2(e_exec):
    """It allows to define new classes by allowing `__build_class__`.
    """

    class_can_be_defined_code = '''
class MyClass:
    value = None
    def display(self):
        return str(self.value)

ob1 = MyClass()
ob1.value = 2411
result = ob1.display()'''

    restricted_globals = dict(
        __builtins__=safe_builtins,
        result=None,
        __name__='restricted_module',
        __metaclass__=type,
        _write_=lambda x: x,
        _getattr_=getattr)

    e_exec(class_can_be_defined_code, restricted_globals)
    assert restricted_globals['result'] == '2411'


@pytest.mark.parametrize(*e_exec)
def test_Guards__guarded_setattr__1(e_exec):
    """It allows use setattr and delattr when _guarded_writes is True.
    """
    class MyObjectD:
        value = None
        _guarded_writes = 1

    setattr_code = '''
my_object_d = MyObjectD()
setattr(my_object_d, 'value', 9999)'''

    delattr_code = "delattr(my_object_d, 'value')"

    restricted_globals = dict(
        __builtins__=safe_builtins,
        MyObjectD=MyObjectD,
        my_object_d=None,
        __name__='restricted_module',
        __metaclass__=type,
        _write_=lambda x: x,
        _getattr_=getattr,)

    e_exec(setattr_code, restricted_globals)
    assert 9999 == restricted_globals['my_object_d'].value

    e_exec(delattr_code, restricted_globals)
    assert None is restricted_globals['my_object_d'].value


@pytest.mark.parametrize(*e_exec)
def test_Guards__write_wrapper__1(e_exec):
    """It wraps the value attribute when it is not
    marked with _guarded_writes."""
    class ObjWithoutGuardedWrites:
        my_attr = None

    setattr_without_guarded_writes_code = '''
my_ob = ObjWithoutGuardedWrites()
setattr(my_ob, 'my_attr', 'bar')'''

    restricted_globals = dict(
        __builtins__=safe_builtins,
        ObjWithoutGuardedWrites=ObjWithoutGuardedWrites,
        my_attr=None,
        __name__='restricted_module',
        __metaclass__=type,
        _write_=lambda x: x,
        _getattr_=getattr,)

    with pytest.raises(TypeError) as excinfo:
        e_exec(setattr_without_guarded_writes_code, restricted_globals)
    assert 'attribute-less object (assign or del)' in str(excinfo.value)


@pytest.mark.parametrize(*e_exec)
def test_Guards__write_wrapper__2(e_exec):
    """It wraps setattr and it works when guarded_setattr is implemented."""

    class ObjWithGuardedSetattr:
        my_attr = None

        def __guarded_setattr__(self, key, value):
            setattr(self, key, value)

    set_attribute_using_guarded_setattr_code = '''
myobj_with_guarded_setattr = ObjWithGuardedSetattr()
setattr(myobj_with_guarded_setattr, 'my_attr', 'bar')
    '''

    restricted_globals = dict(
        __builtins__=safe_builtins,
        ObjWithGuardedSetattr=ObjWithGuardedSetattr,
        myobj_with_guarded_setattr=None,
        __name__='restricted_module',
        __metaclass__=type,
        _write_=lambda x: x,
        _getattr_=getattr,)

    e_exec(set_attribute_using_guarded_setattr_code, restricted_globals)
    assert restricted_globals['myobj_with_guarded_setattr'].my_attr == 'bar'


@pytest.mark.parametrize(*e_exec)
def test_Guards__guarded_unpack_sequence__1(e_exec, mocker):
    """If the sequence is shorter then expected the interpreter will raise
    'ValueError: need more than X value to unpack' anyway
    => No childs are unpacked => nothing to protect."""
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


STRING_DOT_FORMAT_DENIED = """\
a = 'Hello {}'
b = a.format('world')
"""


@pytest.mark.parametrize(*e_exec)
def test_Guards__safer_getattr__1(e_exec):
    """It prevents using the format method of a string.

    format() is considered harmful:
    http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
    """
    glb = {
        '__builtins__': safe_builtins,
    }
    with pytest.raises(NotImplementedError) as err:
        e_exec(STRING_DOT_FORMAT_DENIED, glb)
    assert 'Using format() on a str is not safe.' == str(err.value)


UNICODE_DOT_FORMAT_DENIED = """\
a = u'Hello {}'
b = a.format(u'world')
"""


@pytest.mark.parametrize(*e_exec)
def test_Guards__safer_getattr__2(e_exec):
    """It prevents using the format method of a unicode.

    format() is considered harmful:
    http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
    """
    glb = {
        '__builtins__': safe_builtins,
    }
    with pytest.raises(NotImplementedError) as err:
        e_exec(UNICODE_DOT_FORMAT_DENIED, glb)
    if IS_PY2:
        assert 'Using format() on a unicode is not safe.' == str(err.value)
    else:
        assert 'Using format() on a str is not safe.' == str(err.value)


SAFER_GETATTR_ALLOWED = """\
class A:

    def __init__(self, value):
        self.value = value

a = A(2)
result = getattr(a, 'value')
"""


@pytest.mark.parametrize(*e_exec)
def test_Guards__safer_getattr__3(e_exec):
    """It allows to use `safer_getattr`."""
    restricted_globals = dict(
        __builtins__=safe_builtins,
        __name__=None,
        __metaclass__=type,
        _write_=lambda x: x,
        getattr=safer_getattr,
        result=None,
    )
    e_exec(SAFER_GETATTR_ALLOWED, restricted_globals)
    assert restricted_globals['result'] == 2
