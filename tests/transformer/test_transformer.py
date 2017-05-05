from RestrictedPython import RestrictingNodeTransformer
from RestrictedPython._compat import IS_PY2
from RestrictedPython._compat import IS_PY3
from RestrictedPython.Guards import guarded_iter_unpack_sequence
from RestrictedPython.Guards import guarded_unpack_sequence
from RestrictedPython.Guards import safe_builtins
from tests import c_exec
from tests import e_eval
from tests import e_exec

import ast
import contextlib
import pytest
import RestrictedPython
import types


def test_transformer__RestrictingNodeTransformer__generic_visit__1():
    """It log an error if there is an unknown ast node visited."""
    class MyFancyNode(ast.AST):
        pass

    transformer = RestrictingNodeTransformer()
    transformer.visit(MyFancyNode())
    assert transformer.errors == [
        'Line None: MyFancyNode statements are not allowed.']
    assert transformer.warnings == [
        'Line None: MyFancyNode statement is not known to RestrictedPython']


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Call__1(c_exec):
    """It compiles a function call successfully and returns the used name."""
    result = c_exec('a = max([1, 2, 3])')
    assert result.errors == ()
    loc = {}
    exec(result.code, {}, loc)
    assert loc['a'] == 3
    assert result.used_names == {'max': True}


EXEC_STATEMENT = """\
def no_exec():
    exec 'q = 1'
"""


@pytest.mark.skipif(IS_PY3,
                    reason="exec statement no longer exists in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Exec__1(c_exec):
    """It prevents using the `exec` statement. (Python 2 only)"""
    result = c_exec(EXEC_STATEMENT)
    assert result.errors == ('Line 2: Exec statements are not allowed.',)


BAD_NAME_STARTING_WITH_UNDERSCORE = """\
def bad_name():
    __ = 12
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__1(c_exec):
    """It denies a variable name starting in `__`."""
    result = c_exec(BAD_NAME_STARTING_WITH_UNDERSCORE)
    assert result.errors == (
        'Line 2: "__" is an invalid variable name because it starts with "_"',)


BAD_NAME_OVERRIDE_GUARD_WITH_NAME = """\
def overrideGuardWithName():
    _getattr = None
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__2(c_exec):
    """It denies a variable name starting in `_`."""
    result = c_exec(BAD_NAME_OVERRIDE_GUARD_WITH_NAME)
    assert result.errors == (
        'Line 2: "_getattr" is an invalid variable name because '
        'it starts with "_"',)


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__2_5(e_exec):
    """It allows `_` as variable name."""
    glb = e_exec('_ = 2411')
    assert glb['_'] == 2411


BAD_NAME_OVERRIDE_OVERRIDE_GUARD_WITH_FUNCTION = """\
def overrideGuardWithFunction():
    def _getattr(o):
        return o
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__3(c_exec):
    """It denies a function name starting in `_`."""
    result = c_exec(BAD_NAME_OVERRIDE_OVERRIDE_GUARD_WITH_FUNCTION)
    assert result.errors == (
        'Line 2: "_getattr" is an invalid variable name because it '
        'starts with "_"',)


BAD_NAME_OVERRIDE_GUARD_WITH_CLASS = """\
def overrideGuardWithClass():
    class _getattr:
        pass
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__4(c_exec):
    """It denies a class name starting in `_`."""
    result = c_exec(BAD_NAME_OVERRIDE_GUARD_WITH_CLASS)
    assert result.errors == (
        'Line 2: "_getattr" is an invalid variable name because it '
        'starts with "_"',)


BAD_NAME_IN_WITH = """\
def with_as_bad_name():
    with x as _leading_underscore:
        pass
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__4_4(c_exec):
    """It denies a variable name in with starting in `_`."""
    result = c_exec(BAD_NAME_IN_WITH)
    assert result.errors == (
        'Line 2: "_leading_underscore" is an invalid variable name because '
        'it starts with "_"',)


BAD_NAME_IN_COMPOUND_WITH = """\
def compound_with_bad_name():
    with a as b, c as _restricted_name:
        pass
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__4_5(c_exec):
    """It denies a variable name in with starting in `_`."""
    result = c_exec(BAD_NAME_IN_COMPOUND_WITH)
    assert result.errors == (
        'Line 2: "_restricted_name" is an invalid variable name because '
        'it starts with "_"',)


BAD_NAME_DICT_COMP = """\
def dict_comp_bad_name():
    {y: y for _restricted_name in x}
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__4_6(c_exec):
    """It denies a variable name starting in `_` in a dict comprehension."""
    result = c_exec(BAD_NAME_DICT_COMP)
    assert result.errors == (
        'Line 2: "_restricted_name" is an invalid variable name because '
        'it starts with "_"',)


BAD_NAME_SET_COMP = """\
def set_comp_bad_name():
    {y for _restricted_name in x}
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__4_7(c_exec):
    """It denies a variable name starting in `_` in a dict comprehension."""
    result = c_exec(BAD_NAME_SET_COMP)
    assert result.errors == (
        'Line 2: "_restricted_name" is an invalid variable name because '
        'it starts with "_"',)


BAD_NAME_ENDING_WITH___ROLES__ = """\
def bad_name():
    myvar__roles__ = 12
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__5(c_exec):
    """It denies a variable name ending in `__roles__`."""
    result = c_exec(BAD_NAME_ENDING_WITH___ROLES__)
    assert result.errors == (
        'Line 2: "myvar__roles__" is an invalid variable name because it '
        'ends with "__roles__".',)


BAD_NAME_PRINTED = """\
def bad_name():
    printed = 12
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__6(c_exec):
    """It denies a variable named `printed`."""
    result = c_exec(BAD_NAME_PRINTED)
    assert result.errors == ('Line 2: "printed" is a reserved name.',)


BAD_NAME_PRINT = """\
def bad_name():
    def print():
        pass
"""


@pytest.mark.skipif(IS_PY2,
                    reason="print is a statement in Python 2")
@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Name__7(c_exec):
    """It denies a variable named `print`."""
    result = c_exec(BAD_NAME_PRINT)
    assert result.errors == ('Line 2: "print" is a reserved name.',)


BAD_ATTR_UNDERSCORE = """\
def bad_attr():
    some_ob = object()
    some_ob._some_attr = 15
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__1(c_exec):
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
def test_transformer__RestrictingNodeTransformer__visit_Attribute__2(c_exec):
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
def test_transformer__RestrictingNodeTransformer__visit_Attribute__3(
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
def test_transformer__RestrictingNodeTransformer__visit_Attribute__4(c_exec):
    """It allows `_` as attribute name."""
    result = c_exec(ALLOW_UNDERSCORE_ONLY)
    assert result.errors == ()


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__5(
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
def test_transformer__RestrictingNodeTransformer__visit_Attribute__5_5(
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
def test_transformer__RestrictingNodeTransformer__visit_Attribute__6(c_exec):
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
def test_transformer__RestrictingNodeTransformer__visit_Attribute__7(
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
def test_transformer__RestrictingNodeTransformer__visit_Attribute__8(
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


EXEC_FUNCTION = """\
def no_exec():
    exec('q = 1')
"""


@pytest.mark.skipif(IS_PY2,
                    reason="exec is a statement in Python 2")
@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Call__2(c_exec):
    """It is an error if the code call the `exec` function."""
    result = c_exec(EXEC_FUNCTION)
    assert result.errors == ("Line 2: Exec calls are not allowed.",)


EVAL_FUNCTION = """\
def no_eval():
    eval('q = 1')
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Call__3(c_exec):
    """It is an error if the code call the `eval` function."""
    result = c_exec(EVAL_FUNCTION)
    if c_exec is RestrictedPython.compile.compile_restricted_exec:
        assert result.errors == ("Line 2: Eval calls are not allowed.",)
    else:
        # `eval()` is allowed in the old implementation. :-(
        assert result.errors == ()


ITERATORS = """
def for_loop(it):
    c = 0
    for a in it:
        c = c + a
    return c


def nested_for_loop(it1, it2):
    c = 0
    for a in it1:
        for b in it2:
            c = c + a + b
    return c

def dict_comp(it):
    return {a: a + a for a in it}

def list_comp(it):
    return [a + a for a in it]

def nested_list_comp(it1, it2):
    return [a + b for a in it1 if a > 1 for b in it2]

def set_comp(it):
    return {a + a for a in it}

def generator(it):
    return (a + a for a in it)

def nested_generator(it1, it2):
    return (a+b for a in it1 if a > 0 for b in it2)
"""


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__guard_iter(e_exec, mocker):
    it = (1, 2, 3)
    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda x: x
    glb = {'_getiter_': _getiter_}
    e_exec(ITERATORS, glb)

    ret = glb['for_loop'](it)
    assert 6 == ret
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['nested_for_loop']((1, 2), (3, 4))
    assert 20 == ret
    _getiter_.assert_has_calls([
        mocker.call((1, 2)),
        mocker.call((3, 4))
    ])
    _getiter_.reset_mock()

    ret = glb['dict_comp'](it)
    assert {1: 2, 2: 4, 3: 6} == ret
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['list_comp'](it)
    assert [2, 4, 6] == ret
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['nested_list_comp']((1, 2), (3, 4))
    assert [5, 6] == ret
    _getiter_.assert_has_calls([
        mocker.call((1, 2)),
        mocker.call((3, 4))
    ])
    _getiter_.reset_mock()

    ret = glb['set_comp'](it)
    assert {2, 4, 6} == ret
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['generator'](it)
    assert isinstance(ret, types.GeneratorType)
    assert list(ret) == [2, 4, 6]
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['nested_generator']((0, 1, 2), (1, 2))
    assert isinstance(ret, types.GeneratorType)
    assert list(ret) == [2, 3, 3, 4]
    _getiter_.assert_has_calls([
        mocker.call((0, 1, 2)),
        mocker.call((1, 2)),
        mocker.call((1, 2))])
    _getiter_.reset_mock()


ITERATORS_WITH_UNPACK_SEQUENCE = """
def for_loop(it):
    c = 0
    for (a, b) in it:
        c = c + a + b
    return c

def dict_comp(it):
    return {a: a + b for (a, b) in it}

def list_comp(it):
    return [a + b for (a, b) in it]

def set_comp(it):
    return {a + b for (a, b) in it}

def generator(it):
    return (a + b for (a, b) in it)
"""


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__guard_iter2(e_exec, mocker):
    it = ((1, 2), (3, 4), (5, 6))

    call_ref = [
        mocker.call(it),
        mocker.call(it[0]),
        mocker.call(it[1]),
        mocker.call(it[2])
    ]

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda x: x

    glb = {
        '_getiter_': _getiter_,
        '_iter_unpack_sequence_': guarded_iter_unpack_sequence
    }

    e_exec(ITERATORS_WITH_UNPACK_SEQUENCE, glb)

    ret = glb['for_loop'](it)
    assert ret == 21
    _getiter_.assert_has_calls(call_ref)
    _getiter_.reset_mock()

    ret = glb['dict_comp'](it)
    assert ret == {1: 3, 3: 7, 5: 11}
    _getiter_.assert_has_calls(call_ref)
    _getiter_.reset_mock()

    ret = glb['list_comp'](it)
    assert ret == [3, 7, 11]
    _getiter_.assert_has_calls(call_ref)
    _getiter_.reset_mock()

    ret = glb['set_comp'](it)
    assert ret == {3, 7, 11}
    _getiter_.assert_has_calls(call_ref)
    _getiter_.reset_mock()

    # The old code did not run with unpack sequence inside generators
    if compile == RestrictedPython.compile.compile_restricted_exec:
        ret = list(glb['generator'](it))
        assert ret == [3, 7, 11]
        _getiter_.assert_has_calls(call_ref)
        _getiter_.reset_mock()


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_AugAssign__1(
        e_exec, mocker):
    """It allows augmented assign for variables."""
    _inplacevar_ = mocker.stub()
    _inplacevar_.side_effect = lambda op, val, expr: val + expr

    glb = {
        '_inplacevar_': _inplacevar_,
        'a': 1,
        'x': 1,
        'z': 0
    }

    e_exec("a += x + z", glb)
    assert glb['a'] == 2
    _inplacevar_.assert_called_once_with('+=', 1, 1)
    _inplacevar_.reset_mock()


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_AugAssign__2(c_exec):
    """It forbids augmented assign of attributes."""
    result = c_exec("a.a += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of attributes is not allowed.',)


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_AugAssign__3(c_exec):
    """It forbids augmented assign of subscripts."""
    result = c_exec("a[a] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_AugAssign__4(c_exec):
    """It forbids augmented assign of slices."""
    result = c_exec("a[x:y] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_AugAssign__5(c_exec):
    """It forbids augmented assign of slices with steps."""
    result = c_exec("a[x:y:z] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_Assert__1(e_exec):
    """It allows assert statements."""
    e_exec('assert 1')


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
def test_transformer__RestrictingNodeTransformer__visit_Call(e_exec, mocker):
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


functiondef_err_msg = 'Line 1: "_bad" is an invalid variable ' \
                      'name because it starts with "_"'


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__1(
        c_exec):
    """It prevents function arguments starting with `_`."""
    result = c_exec("def foo(_bad): pass")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert functiondef_err_msg in result.errors


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__2(
        c_exec):
    """It prevents function keyword arguments starting with `_`."""
    result = c_exec("def foo(_bad=1): pass")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert functiondef_err_msg in result.errors


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__3(
        c_exec):
    """It prevents function * arguments starting with `_`."""
    result = c_exec("def foo(*_bad): pass")
    assert result.errors == (functiondef_err_msg,)


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__4(
        c_exec):
    """It prevents function ** arguments starting with `_`."""
    result = c_exec("def foo(**_bad): pass")
    assert result.errors == (functiondef_err_msg,)


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__5(
        c_exec):
    """It prevents function arguments starting with `_` in tuples."""
    result = c_exec("def foo((a, _bad)): pass")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert functiondef_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__6(
        c_exec):
    """It prevents function arguments starting with `_` in tuples."""
    # The old `compile` breaks with tuples in function arguments:
    if c_exec is RestrictedPython.compile.compile_restricted_exec:
        result = c_exec("def foo(a, (c, (_bad, c))): pass")
        # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
        # the error message twice. This is necessary as otherwise *_bad and
        # **_bad would be allowed.
        assert functiondef_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY2,
    reason="There is no single `*` argument in Python 2")
@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__7(
        c_exec):
    """It prevents `_` function arguments together with a single `*`."""
    result = c_exec("def foo(good, *, _bad): pass")
    assert result.errors == (functiondef_err_msg,)


NESTED_SEQ_UNPACK = """
def nested((a, b, (c, (d, e)))):
    return a, b, c, d, e

def nested_with_order((a, b), (c, d)):
    return a, b, c, d
"""


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in python 3")
@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef_2(
        e_exec, mocker):
    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    e_exec('def simple((a, b)): return a, b', glb)

    val = (1, 2)
    ret = glb['simple'](val)
    assert ret == val
    _getiter_.assert_called_once_with(val)
    _getiter_.reset_mock()

    try:
        e_exec(NESTED_SEQ_UNPACK, glb)
    except AttributeError:
        # The old RCompile did not support nested.
        return

    val = (1, 2, (3, (4, 5)))
    ret = glb['nested'](val)
    assert ret == (1, 2, 3, 4, 5)
    assert 3 == _getiter_.call_count
    _getiter_.assert_any_call(val)
    _getiter_.assert_any_call(val[2])
    _getiter_.assert_any_call(val[2][1])
    _getiter_.reset_mock()

    ret = glb['nested_with_order']((1, 2), (3, 4))
    assert ret == (1, 2, 3, 4)
    _getiter_.assert_has_calls([
        mocker.call((1, 2)),
        mocker.call((3, 4))])
    _getiter_.reset_mock()


lambda_err_msg = 'Line 1: "_bad" is an invalid variable ' \
                 'name because it starts with "_"'


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__1(c_exec):
    """It prevents arguments starting with `_`."""
    result = c_exec("lambda _bad: None")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert lambda_err_msg in result.errors


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__2(c_exec):
    """It prevents keyword arguments starting with `_`."""
    result = c_exec("lambda _bad=1: None")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert lambda_err_msg in result.errors


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__3(c_exec):
    """It prevents * arguments starting with `_`."""
    result = c_exec("lambda *_bad: None")
    assert result.errors == (lambda_err_msg,)


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__4(c_exec):
    """It prevents ** arguments starting with `_`."""
    result = c_exec("lambda **_bad: None")
    assert result.errors == (lambda_err_msg,)


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__5(c_exec):
    """It prevents arguments starting with `_` in tuple unpacking."""
    # The old `compile` breaks with tuples in arguments:
    if c_exec is RestrictedPython.compile.compile_restricted_exec:
        result = c_exec("lambda (a, _bad): None")
        # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
        # the error message twice. This is necessary as otherwise *_bad and
        # **_bad would be allowed.
        assert lambda_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__6(c_exec):
    """It prevents arguments starting with `_` in nested tuple unpacking."""
    # The old `compile` breaks with tuples in arguments:
    if c_exec is RestrictedPython.compile.compile_restricted_exec:
        result = c_exec("lambda (a, (c, (_bad, c))): None")
        # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
        # the error message twice. This is necessary as otherwise *_bad and
        # **_bad would be allowed.
        assert lambda_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY2,
    reason="There is no single `*` argument in Python 2")
@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__7(c_exec):
    """It prevents arguments starting with `_` together with a single `*`."""
    result = c_exec("lambda good, *, _bad: None")
    assert result.errors == (lambda_err_msg,)


BAD_ARG_IN_LAMBDA = """\
def check_getattr_in_lambda(arg=lambda _bad=(lambda ob, name: name): _bad2):
    42
"""


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__8(c_exec):
    """It prevents arguments starting with `_` in weird lambdas."""
    result = c_exec(BAD_ARG_IN_LAMBDA)
    # RestrictedPython.compile.compile_restricted_exec finds both invalid
    # names, while the old implementation seems to abort after the first.
    assert lambda_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in python 3")
@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_Lambda_2(
        e_exec, mocker):
    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it
    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence,
        '_getattr_': lambda ob, val: getattr(ob, val)
    }

    src = "m = lambda (a, (b, c)), *ag, **kw: a+b+c+sum(ag)+sum(kw.values())"
    try:
        e_exec(src, glb)
    except AttributeError:
        # Old implementation does not support tuple unpacking
        return

    ret = glb['m']((1, (2, 3)), 4, 5, 6, g=7, e=8)
    assert ret == 36
    assert 2 == _getiter_.call_count
    _getiter_.assert_any_call((1, (2, 3)))
    _getiter_.assert_any_call((2, 3))


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_Assign(e_exec, mocker):
    src = "orig = (a, (x, z)) = (c, d) = g"

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence,
        'g': (1, (2, 3)),
    }

    e_exec(src, glb)
    assert glb['a'] == 1
    assert glb['x'] == 2
    assert glb['z'] == 3
    assert glb['c'] == 1
    assert glb['d'] == (2, 3)
    assert glb['orig'] == (1, (2, 3))
    assert _getiter_.call_count == 3
    _getiter_.assert_any_call((1, (2, 3)))
    _getiter_.assert_any_call((2, 3))
    _getiter_.reset_mock()


@pytest.mark.skipif(
    IS_PY2,
    reason="starred assignments are python3 only")
@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_Assign2(
        e_exec, mocker):
    src = "a, *d, (c, *e), x  = (1, 2, 3, (4, 3, 4), 5)"

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    e_exec(src, glb)
    assert glb['a'] == 1
    assert glb['d'] == [2, 3]
    assert glb['c'] == 4
    assert glb['e'] == [3, 4]
    assert glb['x'] == 5

    _getiter_.assert_has_calls([
        mocker.call((1, 2, 3, (4, 3, 4), 5)),
        mocker.call((4, 3, 4))])


TRY_EXCEPT = """
def try_except(m):
    try:
        m('try')
        raise IndentationError('f1')
    except IndentationError as error:
        m('except')
"""


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_Try__1(
        e_exec, mocker):
    """It allows try-except statements."""
    trace = mocker.stub()
    e_exec(TRY_EXCEPT)['try_except'](trace)

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


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_Try__2(
        e_exec, mocker):
    """It allows try-except-else statements."""
    trace = mocker.stub()
    e_exec(TRY_EXCEPT_ELSE)['try_except_else'](trace)

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


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_TryFinally__1(
        e_exec, mocker):
    """It allows try-finally statements."""
    trace = mocker.stub()
    e_exec(TRY_FINALLY)['try_finally'](trace)

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


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_TryFinally__2(
        e_exec, mocker):
    """It allows try-except-finally statements."""
    trace = mocker.stub()
    e_exec(TRY_EXCEPT_FINALLY)['try_except_finally'](trace)

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


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_TryFinally__3(
        e_exec, mocker):
    """It allows try-except-else-finally statements."""
    trace = mocker.stub()
    e_exec(TRY_EXCEPT_ELSE_FINALLY)['try_except_else_finally'](trace)

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
@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_ExceptHandler(
        e_exec, mocker):
    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    e_exec(EXCEPT_WITH_TUPLE_UNPACK, glb)
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


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_ExceptHandler__2(
        c_exec):
    """It denies bad names in the except as statement."""
    result = c_exec(BAD_TRY_EXCEPT)
    assert result.errors == (
        'Line 5: "_leading_underscore" is an invalid variable name because '
        'it starts with "_"',)


import_errmsg = (
    'Line 1: "%s" is an invalid variable name because it starts with "_"')


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Import__1(c_exec):
    """It allows importing a module."""
    result = c_exec('import a')
    assert result.errors == ()
    assert result.code is not None


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Import__2(c_exec):
    """It denies importing a module starting with `_`."""
    result = c_exec('import _a')
    assert result.errors == (import_errmsg % '_a',)


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Import__3(c_exec):
    """It denies importing a module starting with `_` as something."""
    result = c_exec('import _a as m')
    assert result.errors == (import_errmsg % '_a',)


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Import__4(c_exec):
    """It denies importing a module as something starting with `_`."""
    result = c_exec('import a as _m')
    assert result.errors == (import_errmsg % '_m',)


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Import__5(c_exec):
    """It allows importing from a module."""
    result = c_exec('from a import m')
    assert result.errors == ()
    assert result.code is not None


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Import_6(c_exec):
    """It allows importing from a module starting with `_`."""
    result = c_exec('from _a import m')
    assert result.errors == ()
    assert result.code is not None


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Import__7(c_exec):
    """It denies importing from a module as something starting with `_`."""
    result = c_exec('from a import m as _n')
    assert result.errors == (import_errmsg % '_n',)


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Import__8(c_exec):
    """It denies as-importing something starting with `_` from a module."""
    result = c_exec('from a import _m as n')
    assert result.errors == (import_errmsg % '_m',)


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_Import__9(c_exec):
    """It denies relative from importing as something starting with `_`."""
    result = c_exec('from .x import y as _leading_underscore')
    assert result.errors == (import_errmsg % '_leading_underscore',)


GOOD_CLASS = '''
class Good:
    pass
'''


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_ClassDef__1(c_exec):
    """It allows to define an class."""
    result = c_exec(GOOD_CLASS)
    assert result.errors == ()
    assert result.code is not None


BAD_CLASS = '''\
class _bad:
    pass
'''


@pytest.mark.parametrize(*c_exec)
def test_transformer__RestrictingNodeTransformer__visit_ClassDef__2(c_exec):
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
def test_transformer__RestrictingNodeTransformer__visit_ClassDef__3(e_exec):
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
def test_transformer__RestrictingNodeTransformer__visit_ClassDef__4(c_exec):
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
def test_transformer__RestrictingNodeTransformer__visit_ClassDef__5(e_exec):
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


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__test_ternary_if(
        e_exec, mocker):
    src = 'x.y = y.a if y.z else y.b'
    _getattr_ = mocker.stub()
    _getattr_.side_effect = lambda ob, key: ob[key]
    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob

    glb = {
        '_getattr_': _getattr_,
        '_write_': _write_,
        'x': mocker.stub(),
        'y': {'a': 'a', 'b': 'b'},
    }

    glb['y']['z'] = True
    e_exec(src, glb)

    assert glb['x'].y == 'a'
    _write_.assert_called_once_with(glb['x'])
    _getattr_.assert_has_calls([
        mocker.call(glb['y'], 'z'),
        mocker.call(glb['y'], 'a')])

    _write_.reset_mock()
    _getattr_.reset_mock()

    glb['y']['z'] = False
    e_exec(src, glb)

    assert glb['x'].y == 'b'
    _write_.assert_called_once_with(glb['x'])
    _getattr_.assert_has_calls([
        mocker.call(glb['y'], 'z'),
        mocker.call(glb['y'], 'b')])


WHILE = """\
a = 5
while a < 7:
    a = a + 3
"""


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_While__1(e_exec):
    """It allows `while` statements."""
    glb = e_exec(WHILE)
    assert glb['a'] == 8


BREAK = """\
a = 5
while True:
    a = a + 3
    if a >= 7:
        break
"""


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_Break__1(e_exec):
    """It allows `break` statements."""
    glb = e_exec(BREAK)
    assert glb['a'] == 8


CONTINUE = """\
a = 3
while a < 10:
    if a < 5:
        a = a + 1
        continue
    a = a + 10
"""


@pytest.mark.parametrize(*e_exec)
def test_transformer__RestrictingNodeTransformer__visit_Continue__1(e_exec):
    """It allows `continue` statements."""
    glb = e_exec(CONTINUE)
    assert glb['a'] == 15


WITH_STMT_WITH_UNPACK_SEQUENCE = """
def call(ctx):
    with ctx() as (a, (c, b)):
        return a, c, b
"""


@pytest.mark.parametrize(*e_exec)
def test_transformer__with_stmt_unpack_sequence(e_exec, mocker):
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
def test_transformer__with_stmt_multi_ctx_unpack_sequence(c_exec, mocker):
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
def test_transformer_with_stmt_attribute_access(e_exec, mocker):
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
def test_transformer_with_stmt_subscript(e_exec, mocker):
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


DICT_COMPREHENSION_WITH_ATTRS = """
def call(seq):
    return {y.k: y.v for y in seq.z if y.k}
"""


@pytest.mark.parametrize(*e_exec)
def test_transformer_dict_comprehension_with_attrs(e_exec, mocker):
    _getattr_ = mocker.Mock()
    _getattr_.side_effect = getattr

    _getiter_ = mocker.Mock()
    _getiter_.side_effect = lambda ob: ob

    glb = {'_getattr_': _getattr_, '_getiter_': _getiter_}
    e_exec(DICT_COMPREHENSION_WITH_ATTRS, glb)

    z = [mocker.Mock(k=0, v='a'), mocker.Mock(k=1, v='b')]
    seq = mocker.Mock(z=z)

    ret = glb['call'](seq)
    assert ret == {1: 'b'}

    _getiter_.assert_called_once_with(z)
    _getattr_.assert_has_calls([
        mocker.call(seq, 'z'),
        mocker.call(z[0], 'k'),
        mocker.call(z[1], 'k'),
        mocker.call(z[1], 'v'),
        mocker.call(z[1], 'k')
    ])


@pytest.mark.parametrize(*e_eval)
def test_transformer__RestrictingNodeTransformer__visit_Eq__1(e_eval):
    """It allows == expressions."""
    assert e_eval('1 == int("1")') is True


@pytest.mark.parametrize(*e_eval)
def test_transformer__RestrictingNodeTransformer__visit_NotEq__1(e_eval):
    """It allows != expressions."""
    assert e_eval('1 != int("1")') is False


@pytest.mark.parametrize(*e_eval)
def test_transformer__RestrictingNodeTransformer__visit_Lt__1(e_eval):
    """It allows < expressions."""
    assert e_eval('1 < 3') is True


@pytest.mark.parametrize(*e_eval)
def test_transformer__RestrictingNodeTransformer__visit_LtE__1(e_eval):
    """It allows < expressions."""
    assert e_eval('1 <= 3') is True


@pytest.mark.parametrize(*e_eval)
def test_transformer__RestrictingNodeTransformer__visit_Gt__1(e_eval):
    """It allows > expressions."""
    assert e_eval('1 > 3') is False


@pytest.mark.parametrize(*e_eval)
def test_transformer__RestrictingNodeTransformer__visit_GtE__1(e_eval):
    """It allows >= expressions."""
    assert e_eval('1 >= 3') is False


@pytest.mark.parametrize(*e_eval)
def test_transformer__RestrictingNodeTransformer__visit_Is__1(e_eval):
    """It allows `is` expressions."""
    assert e_eval('None is None') is True


@pytest.mark.parametrize(*e_eval)
def test_transformer__RestrictingNodeTransformer__visit_IsNot__1(e_eval):
    """It allows `is not` expressions."""
    assert e_eval('2 is not None') is True


@pytest.mark.parametrize(*e_eval)
def test_transformer__RestrictingNodeTransformer__visit_In__1(e_eval):
    """It allows `in` expressions."""
    assert e_eval('2 in [1, 2, 3]') is True


@pytest.mark.parametrize(*e_eval)
def test_transformer__RestrictingNodeTransformer__visit_NotIn__1(e_eval):
    """It allows `in` expressions."""
    assert e_eval('2 not in [1, 2, 3]') is False
