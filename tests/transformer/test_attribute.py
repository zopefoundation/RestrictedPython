from tests import c_exec
from tests import e_exec

import pytest


BAD_ATTR_UNDERSCORE = """\
def bad_attr():
    some_ob = object()
    some_ob._some_attr = 15
"""


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Attribute__1(c_exec):
    """It is an error if a bad attribute name is used."""
    result = c_exec(BAD_ATTR_UNDERSCORE)
    assert result.errors == (
        'Line 3: "_some_attr" is an invalid attribute name because it '
        'starts with "_".',)


BAD_ATTR_ROLES = """\
def bad_attr():
    some_ob = object()
    some_ob.abc__roles__
"""


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Attribute__2(c_exec):
    """It is an error if a bad attribute name is used."""
    result = c_exec(BAD_ATTR_ROLES)
    assert result.errors == (
        'Line 3: "abc__roles__" is an invalid attribute name because it '
        'ends with "__roles__".',)


TRANSFORM_ATTRIBUTE_ACCESS = """\
def func():
    return a.b
"""


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Attribute__3(
        e_exec, mocker):
    """It transforms the attribute access to `_getattr_`."""
    glb = {
        '_getattr_': mocker.stub(),
        'a': [],
        'b': 'b'
    }
    e_exec(TRANSFORM_ATTRIBUTE_ACCESS, glb)
    glb['func']()
    glb['_getattr_'].assert_called_once_with([], 'b')


ALLOW_UNDERSCORE_ONLY = """\
def func():
    some_ob = object()
    some_ob._
"""


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Attribute__4(c_exec):
    """It allows `_` as attribute name."""
    result = c_exec(ALLOW_UNDERSCORE_ONLY)
    assert result.errors == ()


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Attribute__5(
        e_exec, mocker):
    """It transforms writing to an attribute to `_write_`."""
    glb = {
        '_write_': mocker.stub(),
        'a': mocker.stub(),
    }
    glb['_write_'].return_value = glb['a']

    e_exec("a.b = 'it works'", glb)

    glb['_write_'].assert_called_once_with(glb['a'])
    assert glb['a'].b == 'it works'


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Attribute__5_5(
        e_exec, mocker):
    """It transforms deleting of an attribute to `_write_`."""
    glb = {
        '_write_': mocker.stub(),
        'a': mocker.stub(),
    }
    glb['a'].b = 'it exists'
    glb['_write_'].return_value = glb['a']

    e_exec("del a.b", glb)

    glb['_write_'].assert_called_once_with(glb['a'])
    assert not hasattr(glb['a'], 'b')


DISALLOW_TRACEBACK_ACCESS = """
try:
    raise Exception()
except Exception as e:
    tb = e.__traceback__
"""


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Attribute__6(c_exec):
    """It denies access to the __traceback__ attribute."""
    result = c_exec(DISALLOW_TRACEBACK_ACCESS)
    assert result.errors == (
        'Line 5: "__traceback__" is an invalid attribute name because '
        'it starts with "_".',)


TRANSFORM_ATTRIBUTE_ACCESS_FUNCTION_DEFAULT = """
def func_default(x=a.a):
    return x
"""


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Attribute__7(
        e_exec, mocker):
    """It transforms attribute access in function default kw to `_write_`."""
    _getattr_ = mocker.Mock()
    _getattr_.side_effect = getattr

    glb = {
        '_getattr_': _getattr_,
        'a': mocker.Mock(a=1),
    }

    e_exec(TRANSFORM_ATTRIBUTE_ACCESS_FUNCTION_DEFAULT, glb)

    _getattr_.assert_has_calls([mocker.call(glb['a'], 'a')])
    assert glb['func_default']() == 1


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Attribute__8(
        e_exec, mocker):
    """It transforms attribute access in lamda default kw to `_write_`."""
    _getattr_ = mocker.Mock()
    _getattr_.side_effect = getattr

    glb = {
        '_getattr_': _getattr_,
        'b': mocker.Mock(b=2)
    }

    e_exec('lambda_default = lambda x=b.b: x', glb)

    _getattr_.assert_has_calls([mocker.call(glb['b'], 'b')])
    assert glb['lambda_default']() == 2
