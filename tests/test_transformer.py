from . import compile
from . import execute
from RestrictedPython._compat import IS_PY2
from RestrictedPython._compat import IS_PY3
from RestrictedPython.Guards import guarded_iter_unpack_sequence
from RestrictedPython.Guards import guarded_unpack_sequence

import contextlib
import pytest
import RestrictedPython
import types


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Num__1(compile):
    """It compiles a number successfully."""
    result = compile('42')
    assert result.errors == ()
    assert str(result.code.__class__.__name__) == 'code'


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Call__1(compile):
    """It compiles a function call successfully and returns the used name."""
    result = compile('a = max([1, 2, 3])')
    assert result.errors == ()
    loc = {}
    exec(result.code, {}, loc)
    assert loc['a'] == 3
    if compile is RestrictedPython.compile.compile_restricted_exec:
        # The new version not yet supports `used_names`:
        assert result.used_names == {}
    else:
        assert result.used_names == {'max': True}


YIELD = """\
def no_yield():
    yield 42
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Yield__1(compile):
    """It prevents using the `yield` statement."""
    result = compile(YIELD)
    assert result.errors == ("Line 2: Yield statements are not allowed.",)


EXEC_STATEMENT = """\
def no_exec():
    exec 'q = 1'
"""


@pytest.mark.skipif(IS_PY3,
                    reason="exec statement no longer exists in Python 3")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Exec__1(compile):
    """It prevents using the `exec` statement. (Python 2 only)"""
    result = compile(EXEC_STATEMENT)
    assert result.errors == ('Line 2: Exec statements are not allowed.',)


BAD_NAME_STARTING_WITH_UNDERSCORE = """\
def bad_name():
    __ = 12
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Name__1(compile):
    """It is an error if a variable name starts with `__`."""
    result = compile(BAD_NAME_STARTING_WITH_UNDERSCORE)
    assert result.errors == (
        'Line 2: "__" is an invalid variable name because it starts with "_"',)


BAD_NAME_OVERRIDE_GUARD_WITH_NAME = """\
def overrideGuardWithName():
    _getattr = None
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Name__2(compile):
    """It is an error if a variable name starts with `_`."""
    result = compile(BAD_NAME_OVERRIDE_GUARD_WITH_NAME)
    assert result.errors == (
        'Line 2: "_getattr" is an invalid variable name because '
        'it starts with "_"',)


BAD_NAME_OVERRIDE_OVERRIDE_GUARD_WITH_FUNCTION = """\
def overrideGuardWithFunction():
    def _getattr(o):
        return o
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Name__3(compile):
    """It is an error if a function name starts with `_`."""
    result = compile(BAD_NAME_OVERRIDE_OVERRIDE_GUARD_WITH_FUNCTION)
    assert result.errors == (
        'Line 2: "_getattr" is an invalid variable name because it '
        'starts with "_"',)


BAD_NAME_OVERRIDE_GUARD_WITH_CLASS = """\
def overrideGuardWithClass():
    class _getattr:
        pass
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Name__4(compile):
    """It is an error if a class name starts with `_`."""
    result = compile(BAD_NAME_OVERRIDE_GUARD_WITH_CLASS)
    assert result.errors == (
        'Line 2: "_getattr" is an invalid variable name because it '
        'starts with "_"',)


BAD_NAME_IN_WITH = """\
def with_as_bad_name():
    with x as _leading_underscore:
        pass
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Name__4_5(compile):
    """It is an error if a variable in with starts with `_`."""
    result = compile(BAD_NAME_IN_WITH)
    assert result.errors == (
        'Line 2: "_leading_underscore" is an invalid variable name because '
        'it starts with "_"',)


BAD_NAME_ENDING_WITH___ROLES__ = """\
def bad_name():
    myvar__roles__ = 12
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Name__5(compile):
    """It is an error if a variable name ends with `__roles__`."""
    result = compile(BAD_NAME_ENDING_WITH___ROLES__)
    assert result.errors == (
        'Line 2: "myvar__roles__" is an invalid variable name because it '
        'ends with "__roles__".',)


BAD_NAME_PRINTED = """\
def bad_name():
    printed = 12
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Name__6(compile):
    """It is an error if a variable is named `printed`."""
    result = compile(BAD_NAME_PRINTED)
    assert result.errors == ('Line 2: "printed" is a reserved name.',)


BAD_NAME_PRINT = """\
def bad_name():
    def print():
        pass
"""


@pytest.mark.skipif(IS_PY2,
                    reason="print is a statement in Python 2")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Name__7(compile):
    """It is an error if a variable is named `printed`."""
    result = compile(BAD_NAME_PRINT)
    assert result.errors == ('Line 2: "print" is a reserved name.',)


BAD_ATTR_UNDERSCORE = """\
def bad_attr():
    some_ob = object()
    some_ob._some_attr = 15
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__1(compile):
    """It is an error if a bad attribute name is used."""
    result = compile(BAD_ATTR_UNDERSCORE)
    assert result.errors == (
        'Line 3: "_some_attr" is an invalid attribute name because it '
        'starts with "_".',)


BAD_ATTR_ROLES = """\
def bad_attr():
    some_ob = object()
    some_ob.abc__roles__
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__2(compile):
    """It is an error if a bad attribute name is used."""
    result = compile(BAD_ATTR_ROLES)
    assert result.errors == (
        'Line 3: "abc__roles__" is an invalid attribute name because it '
        'ends with "__roles__".',)


TRANSFORM_ATTRIBUTE_ACCESS = """\
def func():
    return a.b
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__3(
        compile, mocker):
    result = compile(TRANSFORM_ATTRIBUTE_ACCESS)
    assert result.errors == ()

    glb = {
        '_getattr_': mocker.stub(),
        'a': [],
        'b': 'b'
    }

    exec(result.code, glb)
    glb['func']()
    glb['_getattr_'].assert_called_once_with([], 'b')


ALLOW_UNDERSCORE_ONLY = """\
def func():
    some_ob = object()
    some_ob._
    _ = some_ob
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__4(
        compile, mocker):
    result = compile(ALLOW_UNDERSCORE_ONLY)
    assert result.errors == ()


TRANSFORM_ATTRIBUTE_WRITE = """\
def func():
    a.b = 'it works'
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__5(
        compile, mocker):
    result = compile(TRANSFORM_ATTRIBUTE_WRITE)
    assert result.errors == ()

    glb = {
        '_write_': mocker.stub(),
        'a': mocker.stub(),
    }
    glb['_write_'].return_value = glb['a']

    exec(result.code, glb)
    glb['func']()

    glb['_write_'].assert_called_once_with(glb['a'])
    assert glb['a'].b == 'it works'


EXEC_FUNCTION = """\
def no_exec():
    exec('q = 1')
"""


DISALLOW_TRACEBACK_ACCESS = """
try:
    raise Exception()
except Exception as e:
    tb = e.__traceback__
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__6(compile):
    result = compile(DISALLOW_TRACEBACK_ACCESS)
    assert result.errors == (
        'Line 5: "__traceback__" is an invalid attribute name because '
        'it starts with "_".',)


TRANSFORM_ATTRIBUTE_ACCESS_FUNCTION_DEFAULT = """
def func_default(x=a.a):
    return x

lambda_default = lambda x=b.b: x
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__7(
        compile, mocker):
    result = compile(TRANSFORM_ATTRIBUTE_ACCESS_FUNCTION_DEFAULT)
    assert result.errors == ()

    _getattr_ = mocker.Mock()
    _getattr_.side_effect = getattr

    glb = {
        '_getattr_': _getattr_,
        'a': mocker.Mock(a=1),
        'b': mocker.Mock(b=2)
    }

    exec(result.code, glb)

    _getattr_.assert_has_calls([
        mocker.call(glb['a'], 'a'),
        mocker.call(glb['b'], 'b')
    ])

    ret = glb['func_default']()
    assert ret == 1

    ret = glb['lambda_default']()
    assert ret == 2


@pytest.mark.skipif(IS_PY2,
                    reason="exec is a statement in Python 2")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Call__2(compile):
    """It is an error if the code call the `exec` function."""
    result = compile(EXEC_FUNCTION)
    assert result.errors == ("Line 2: Exec calls are not allowed.",)


EVAL_FUNCTION = """\
def no_eval():
    eval('q = 1')
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Call__3(compile):
    """It is an error if the code call the `eval` function."""
    result = compile(EVAL_FUNCTION)
    if compile is RestrictedPython.compile.compile_restricted_exec:
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


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__guard_iter(compile, mocker):
    result = compile(ITERATORS)
    assert result.errors == ()

    it = (1, 2, 3)
    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda x: x
    glb = {'_getiter_': _getiter_}
    exec(result.code, glb)

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


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__guard_iter2(compile, mocker):
    result = compile(ITERATORS_WITH_UNPACK_SEQUENCE)
    assert result.errors == ()

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

    exec(result.code, glb)

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


GET_SUBSCRIPTS = """
def simple_subscript(a):
    return a['b']

def tuple_subscript(a):
    return a[1, 2]

def slice_subscript_no_upper_bound(a):
    return a[1:]

def slice_subscript_no_lower_bound(a):
    return a[:1]

def slice_subscript_no_step(a):
    return a[1:2]

def slice_subscript_with_step(a):
    return a[1:2:3]

def extended_slice_subscript(a):
    return a[0, :1, 1:, 1:2, 1:2:3]
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Subscript_1(
        compile, mocker):
    result = compile(GET_SUBSCRIPTS)
    assert result.errors == ()

    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    exec(result.code, glb)

    ret = glb['simple_subscript'](value)
    ref = (value, 'b')
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

    ret = glb['tuple_subscript'](value)
    ref = (value, (1, 2))
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

    ret = glb['slice_subscript_no_upper_bound'](value)
    ref = (value, slice(1, None, None))
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

    ret = glb['slice_subscript_no_lower_bound'](value)
    ref = (value, slice(None, 1, None))
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

    ret = glb['slice_subscript_no_step'](value)
    ref = (value, slice(1, 2, None))
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

    ret = glb['slice_subscript_with_step'](value)
    ref = (value, slice(1, 2, 3))
    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()

    ret = glb['extended_slice_subscript'](value)
    ref = (
        value,
        (
            0,
            slice(None, 1, None),
            slice(1, None, None),
            slice(1, 2, None),
            slice(1, 2, 3)
        )
    )

    assert ref == ret
    _getitem_.assert_called_once_with(*ref)
    _getitem_.reset_mock()


WRITE_SUBSCRIPTS = """
def assign_subscript(a):
    a['b'] = 1

def del_subscript(a):
    del a['b']
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Subscript_2(
        compile, mocker):
    result = compile(WRITE_SUBSCRIPTS)
    assert result.errors == ()

    value = {'b': None}
    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob
    glb = {'_write_': _write_}
    exec(result.code, glb)

    glb['assign_subscript'](value)
    assert value['b'] == 1
    _write_.assert_called_once_with(value)
    _write_.reset_mock()

    glb['del_subscript'](value)
    assert value == {}
    _write_.assert_called_once_with(value)
    _write_.reset_mock()


@pytest.mark.parametrize(*execute)
def test_transformer__RestrictingNodeTransformer__visit_AugAssign__1(
        execute, mocker):
    """It allows augmented assign for variables."""
    _inplacevar_ = mocker.stub()
    _inplacevar_.side_effect = lambda op, val, expr: val + expr

    glb = {
        '_inplacevar_': _inplacevar_,
        'a': 1,
        'x': 1,
        'z': 0
    }

    execute("a += x + z", glb)
    assert glb['a'] == 2
    _inplacevar_.assert_called_once_with('+=', 1, 1)
    _inplacevar_.reset_mock()


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_AugAssign__2(compile):
    """It forbids augmented assign of attributes."""
    result = compile("a.a += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of attributes is not allowed.',)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_AugAssign__3(compile):
    """It forbids augmented assign of subscripts."""
    result = compile("a[a] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_AugAssign__4(compile):
    """It forbids augmented assign of slices."""
    result = compile("a[x:y] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_AugAssign__5(compile):
    """It forbids augmented assign of slices with steps."""
    result = compile("a[x:y:z] += 1")
    assert result.errors == (
        'Line 1: Augmented assignment of object items and slices is not '
        'allowed.',)


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


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Call(compile, mocker):
    result = compile(FUNCTIONC_CALLS)
    assert result.errors == ()

    _apply_ = mocker.stub()
    _apply_.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)

    glb = {
        '_apply_': _apply_,
        'foo': lambda *args, **kwargs: (args, kwargs)
    }

    exec(result.code, glb)

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


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__1(
        compile):
    """It prevents function arguments starting with `_`."""
    result = compile("def foo(_bad): pass")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert functiondef_err_msg in result.errors


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__2(
        compile):
    """It prevents function keyword arguments starting with `_`."""
    result = compile("def foo(_bad=1): pass")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert functiondef_err_msg in result.errors


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__3(
        compile):
    """It prevents function * arguments starting with `_`."""
    result = compile("def foo(*_bad): pass")
    assert result.errors == (functiondef_err_msg,)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__4(
        compile):
    """It prevents function ** arguments starting with `_`."""
    result = compile("def foo(**_bad): pass")
    assert result.errors == (functiondef_err_msg,)


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__5(
        compile):
    """It prevents function arguments starting with `_` in tuples."""
    result = compile("def foo((a, _bad)): pass")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert functiondef_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__6(
        compile):
    """It prevents function arguments starting with `_` in tuples."""
    # The old `compile` breaks with tuples in function arguments:
    if compile is RestrictedPython.compile.compile_restricted_exec:
        result = compile("def foo(a, (c, (_bad, c))): pass")
        # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
        # the error message twice. This is necessary as otherwise *_bad and
        # **_bad would be allowed.
        assert functiondef_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY2,
    reason="There is no single `*` argument in Python 2")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef__7(
        compile):
    """It prevents `_` function arguments together with a single `*`."""
    result = compile("def foo(good, *, _bad): pass")
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
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef_2(
        compile, mocker):
    result = compile('def simple((a, b)): return a, b')
    assert result.errors == ()

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    exec(result.code, glb)

    val = (1, 2)
    ret = glb['simple'](val)
    assert ret == val
    _getiter_.assert_called_once_with(val)
    _getiter_.reset_mock()

    # The old RCompile did not support nested.
    if compile is RestrictedPython.RCompile.compile_restricted_exec:
        return

    result = compile(NESTED_SEQ_UNPACK)
    assert result.errors == ()
    exec(result.code, glb)

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


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__1(compile):
    """It prevents arguments starting with `_`."""
    result = compile("lambda _bad: None")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert lambda_err_msg in result.errors


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__2(compile):
    """It prevents keyword arguments starting with `_`."""
    result = compile("lambda _bad=1: None")
    # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
    # the error message twice. This is necessary as otherwise *_bad and **_bad
    # would be allowed.
    assert lambda_err_msg in result.errors


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__3(compile):
    """It prevents * arguments starting with `_`."""
    result = compile("lambda *_bad: None")
    assert result.errors == (lambda_err_msg,)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__4(compile):
    """It prevents ** arguments starting with `_`."""
    result = compile("lambda **_bad: None")
    assert result.errors == (lambda_err_msg,)


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__5(compile):
    """It prevents arguments starting with `_` in tuple unpacking."""
    # The old `compile` breaks with tuples in arguments:
    if compile is RestrictedPython.compile.compile_restricted_exec:
        result = compile("lambda (a, _bad): None")
        # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
        # the error message twice. This is necessary as otherwise *_bad and
        # **_bad would be allowed.
        assert lambda_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in Python 3")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__6(compile):
    """It prevents arguments starting with `_` in nested tuple unpacking."""
    # The old `compile` breaks with tuples in arguments:
    if compile is RestrictedPython.compile.compile_restricted_exec:
        result = compile("lambda (a, (c, (_bad, c))): None")
        # RestrictedPython.compile.compile_restricted_exec on Python 2 renders
        # the error message twice. This is necessary as otherwise *_bad and
        # **_bad would be allowed.
        assert lambda_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY2,
    reason="There is no single `*` argument in Python 2")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__7(compile):
    """It prevents arguments starting with `_` together with a single `*`."""
    result = compile("lambda good, *, _bad: None")
    assert result.errors == (lambda_err_msg,)


BAD_ARG_IN_LAMBDA = """\
def check_getattr_in_lambda(arg=lambda _bad=(lambda ob, name: name): _bad2):
    42
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Lambda__8(compile):
    """It prevents arguments starting with `_` in weird lambdas."""
    result = compile(BAD_ARG_IN_LAMBDA)
    # RestrictedPython.compile.compile_restricted_exec finds both invalid
    # names, while the old implementation seems to abort after the first.
    assert lambda_err_msg in result.errors


@pytest.mark.skipif(
    IS_PY3,
    reason="tuple parameter unpacking is gone in python 3")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Lambda_2(
        compile, mocker):
    if compile is not RestrictedPython.compile.compile_restricted_exec:
        return

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it
    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence,
        '_getattr_': lambda ob, val: getattr(ob, val)
    }

    src = "m = lambda (a, (b, c)), *ag, **kw: a+b+c+sum(ag)+sum(kw.values())"
    result = compile(src)
    assert result.errors == ()
    exec(result.code, glb)

    ret = glb['m']((1, (2, 3)), 4, 5, 6, g=7, e=8)
    assert ret == 36
    assert 2 == _getiter_.call_count
    _getiter_.assert_any_call((1, (2, 3)))
    _getiter_.assert_any_call((2, 3))


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Assign(
        compile, mocker):
    src = "orig = (a, (x, z)) = (c, d) = g"
    result = compile(src)
    assert result.errors == ()

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence,
        'g': (1, (2, 3)),
    }

    exec(result.code, glb)
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
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Assign2(
        compile, mocker):
    src = "a, *d, (c, *e), x  = (1, 2, 3, (4, 3, 4), 5)"
    result = compile(src)
    assert result.errors == ()

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    exec(result.code, glb)

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


@pytest.mark.parametrize(*execute)
def test_transformer__RestrictingNodeTransformer__visit_Try__1(
        execute, mocker):
    """It allows try-except statements."""
    trace = mocker.stub()
    execute(TRY_EXCEPT)['try_except'](trace)

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


@pytest.mark.parametrize(*execute)
def test_transformer__RestrictingNodeTransformer__visit_Try__2(
        execute, mocker):
    """It allows try-except-else statements."""
    trace = mocker.stub()
    execute(TRY_EXCEPT_ELSE)['try_except_else'](trace)

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


@pytest.mark.parametrize(*execute)
def test_transformer__RestrictingNodeTransformer__visit_TryFinally__1(
        execute, mocker):
    """It allows try-finally statements."""
    trace = mocker.stub()
    execute(TRY_FINALLY)['try_finally'](trace)

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


@pytest.mark.parametrize(*execute)
def test_transformer__RestrictingNodeTransformer__visit_TryFinally__2(
        execute, mocker):
    """It allows try-except-finally statements."""
    trace = mocker.stub()
    execute(TRY_EXCEPT_FINALLY)['try_except_finally'](trace)

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


@pytest.mark.parametrize(*execute)
def test_transformer__RestrictingNodeTransformer__visit_TryFinally__3(
        execute, mocker):
    """It allows try-except-else-finally statements."""
    trace = mocker.stub()
    execute(TRY_EXCEPT_ELSE_FINALLY)['try_except_else_finally'](trace)

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
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_ExceptHandler(
        compile, mocker):
    result = compile(EXCEPT_WITH_TUPLE_UNPACK)
    assert result.errors == ()

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    exec(result.code, glb)

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


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_ExceptHandler__2(
        compile):
    """It denies bad names in the except as statement."""
    result = compile(BAD_TRY_EXCEPT)
    assert result.errors == (
        'Line 5: "_leading_underscore" is an invalid variable name because '
        'it starts with "_"',)


import_errmsg = (
    'Line 1: "%s" is an invalid variable name because it starts with "_"')


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Import__1(compile):
    """It allows importing a module."""
    result = compile('import a')
    assert result.errors == ()
    assert result.code is not None


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Import__2(compile):
    """It denies importing a module starting with `_`."""
    result = compile('import _a')
    assert result.errors == (import_errmsg % '_a',)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Import__3(compile):
    """It denies importing a module starting with `_` as something."""
    result = compile('import _a as m')
    assert result.errors == (import_errmsg % '_a',)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Import__4(compile):
    """It denies importing a module as something starting with `_`."""
    result = compile('import a as _m')
    assert result.errors == (import_errmsg % '_m',)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Import__5(compile):
    """It allows importing from a module."""
    result = compile('from a import m')
    assert result.errors == ()
    assert result.code is not None


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Import_6(compile):
    """It allows importing from a module starting with `_`."""
    result = compile('from _a import m')
    assert result.errors == ()
    assert result.code is not None


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Import__7(compile):
    """It denies importing from a module as something starting with `_`."""
    result = compile('from a import m as _n')
    assert result.errors == (import_errmsg % '_n',)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Import__8(compile):
    """It denies as-importing something starting with `_` from a module."""
    result = compile('from a import _m as n')
    assert result.errors == (import_errmsg % '_m',)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Import__9(compile):
    """It denies relative from importing as something starting with `_`."""
    result = compile('from .x import y as _leading_underscore')
    assert result.errors == (import_errmsg % '_leading_underscore',)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_ClassDef(compile):
    result = compile('class Good: pass')
    assert result.errors == ()
    assert result.code is not None

    # Do not allow class names which start with an underscore.
    result = compile('class _bad: pass')
    assert result.errors == (
        'Line 1: "_bad" is an invalid variable name '
        'because it starts with "_"',)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__test_ternary_if(
        compile, mocker):
    result = compile('x.y = y.a if y.z else y.b')
    assert result.errors == ()

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
    exec(result.code, glb)

    assert glb['x'].y == 'a'
    _write_.assert_called_once_with(glb['x'])
    _getattr_.assert_has_calls([
        mocker.call(glb['y'], 'z'),
        mocker.call(glb['y'], 'a')])

    _write_.reset_mock()
    _getattr_.reset_mock()

    glb['y']['z'] = False
    exec(result.code, glb)

    assert glb['x'].y == 'b'
    _write_.assert_called_once_with(glb['x'])
    _getattr_.assert_has_calls([
        mocker.call(glb['y'], 'z'),
        mocker.call(glb['y'], 'b')])


WITH_STMT_WITH_UNPACK_SEQUENCE = """
def call(ctx):
    with ctx() as (a, (c, b)):
        return a, c, b
"""


@pytest.mark.parametrize(*compile)
def test_transformer__with_stmt_unpack_sequence(compile, mocker):
    result = compile(WITH_STMT_WITH_UNPACK_SEQUENCE)
    assert result.errors == ()

    @contextlib.contextmanager
    def ctx():
        yield (1, (2, 3))

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda ob: ob

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    exec(result.code, glb)

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


@pytest.mark.parametrize(*compile)
def test_transformer__with_stmt_multi_ctx_unpack_sequence(compile, mocker):
    result = compile(WITH_STMT_MULTI_CTX_WITH_UNPACK_SEQUENCE)
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


@pytest.mark.parametrize(*compile)
def test_transformer_with_stmt_attribute_access(compile, mocker):
    result = compile(WITH_STMT_ATTRIBUTE_ACCESS)
    assert result.errors == ()

    _getattr_ = mocker.stub()
    _getattr_.side_effect = getattr

    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob

    glb = {'_getattr_': _getattr_, '_write_': _write_}
    exec(result.code, glb)

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


@pytest.mark.parametrize(*compile)
def test_transformer_with_stmt_subscript(compile, mocker):
    result = compile(WITH_STMT_SUBSCRIPT)
    assert result.errors == ()

    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob

    glb = {'_write_': _write_}
    exec(result.code, glb)

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


@pytest.mark.parametrize(*compile)
def test_transformer_dict_comprehension_with_attrs(compile, mocker):
    result = compile(DICT_COMPREHENSION_WITH_ATTRS)
    assert result.errors == ()

    _getattr_ = mocker.Mock()
    _getattr_.side_effect = getattr

    _getiter_ = mocker.Mock()
    _getiter_.side_effect = lambda ob: ob

    glb = {'_getattr_': _getattr_, '_getiter_': _getiter_}
    exec(result.code, glb)

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
