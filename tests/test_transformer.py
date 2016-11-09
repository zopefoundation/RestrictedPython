from RestrictedPython.Guards import guarded_iter_unpack_sequence
from RestrictedPython.Guards import guarded_unpack_sequence

import pytest
import RestrictedPython
import six
import sys
import types


# Define the arguments for @pytest.mark.parametrize to be able to test both the
# old and the new implementation to be equal:
compile = ('compile', [RestrictedPython.compile.compile_restricted_exec])
if sys.version_info < (3,):
    from RestrictedPython import RCompile
    compile[1].append(RCompile.compile_restricted_exec)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__1(compile):
    """It compiles a number successfully."""
    code, errors, warnings, used_names = compile('42')
    assert 'code' == str(code.__class__.__name__)
    assert errors == ()
    assert warnings == []
    assert used_names == {}


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__2(compile):
    """It compiles a function call successfully and returns the used name."""
    code, errors, warnings, used_names = compile('max([1, 2, 3])')
    assert errors == ()
    assert warnings == []
    assert 'code' == str(code.__class__.__name__)
    if compile is RestrictedPython.compile.compile_restricted_exec:
        # The new version not yet supports `used_names`:
        assert used_names == {}
    else:
        assert used_names == {'max': True}


YIELD = """\
def no_yield():
    yield 42
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__100(compile):
    """It is an error if the code contains a `yield` statement."""
    code, errors, warnings, used_names = compile(YIELD)
    assert ("Line 2: Yield statements are not allowed.",) == errors
    assert warnings == []
    assert used_names == {}


EXEC_STATEMENT = """\
def no_exec():
    exec 'q = 1'
"""


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="exec statement no longer exists in Python 3")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__102(compile):
    """It raises a SyntaxError if the code contains an `exec` statement."""
    code, errors, warnings, used_names = compile(EXEC_STATEMENT)
    assert ('Line 2: Exec statements are not allowed.',) == errors


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="exec statement in Python 3 raises SyntaxError itself")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__103(compile):
    """It is an error if the code contains an `exec` statement."""
    code, errors, warnings, used_names = compile(EXEC_STATEMENT)
    assert (
        "Line 2: SyntaxError: Missing parentheses in call to 'exec' in on "
        "statement: exec 'q = 1'",) == errors


BAD_NAME = """\
def bad_name():
    __ = 12
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Name__1(compile):
    """It is an error if a bad variable name is used."""
    code, errors, warnings, used_names = compile(BAD_NAME)
    assert ('Line 2: "__" is an invalid variable name because it starts with '
            '"_"',) == errors


BAD_ATTR_UNDERSCORE = """\
def bad_attr():
    some_ob = object()
    some_ob._some_attr = 15
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__1(compile):
    """It is an error if a bad attribute name is used."""
    code, errors, warnings, used_names = compile(BAD_ATTR_UNDERSCORE)

    assert ('Line 3: "_some_attr" is an invalid attribute name because it '
            'starts with "_".',) == errors


BAD_ATTR_ROLES = """\
def bad_attr():
    some_ob = object()
    some_ob.abc__roles__
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__2(compile):
    """It is an error if a bad attribute name is used."""
    code, errors, warnings, used_names = compile(BAD_ATTR_ROLES)

    assert ('Line 3: "abc__roles__" is an invalid attribute name because it '
            'ends with "__roles__".',) == errors


TRANSFORM_ATTRIBUTE_ACCESS = """\
def func():
    return a.b
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__3(compile, mocker):
    code, errors, warnings, used_names = compile(TRANSFORM_ATTRIBUTE_ACCESS)

    glb = {
        '_getattr_': mocker.stub(),
        'a': [],
        'b': 'b'
    }

    six.exec_(code, glb)
    glb['func']()
    glb['_getattr_'].assert_called_once_with([], 'b')


ALLOW_UNDERSCORE_ONLY = """\
def func():
    some_ob = object()
    some_ob._
    _ = some_ob
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__4(compile, mocker):
    code, errors, warnings, used_names = compile(ALLOW_UNDERSCORE_ONLY)

    assert errors == ()
    assert warnings == []
    assert code is not None


TRANSFORM_ATTRIBUTE_WRITE = """\
def func():
    a.b = 'it works'
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__5(compile, mocker):
    code, errors, warnings, used_names = compile(TRANSFORM_ATTRIBUTE_WRITE)

    glb = {
        '_write_': mocker.stub(),
        'a': mocker.stub(),
    }
    glb['_write_'].return_value = glb['a']

    six.exec_(code, glb)
    glb['func']()

    glb['_write_'].assert_called_once_with(glb['a'])
    assert glb['a'].b == 'it works'


EXEC_FUNCTION = """\
def no_exec():
    exec('q = 1')
"""


@pytest.mark.skipif(sys.version_info < (3, 0),
                    reason="exec is a statement in Python 2")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Call__1(compile):
    """It is an error if the code call the `exec` function."""
    code, errors, warnings, used_names = compile(EXEC_FUNCTION)
    assert ("Line 2: Exec calls are not allowed.",) == errors


EVAL_FUNCTION = """\
def no_eval():
    eval('q = 1')
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Call__2(compile):
    """It is an error if the code call the `eval` function."""
    code, errors, warnings, used_names = compile(EVAL_FUNCTION)
    if compile is RestrictedPython.compile.compile_restricted_exec:
        assert ("Line 2: Eval calls are not allowed.",) == errors
    else:
        # `eval()` is allowed in the old implementation.
        assert () == errors


ITERATORS = """
def for_loop(it):
    c = 0
    for a in it:
        c = c + a
    return c

def dict_comp(it):
    return {a: a + a for a in it}

def list_comp(it):
    return [a + a for a in it]

def set_comp(it):
    return {a + a for a in it}

def generator(it):
    return (a + a for a in it)
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__guard_iter(compile, mocker):
    """It is an error if the code call the `eval` function."""
    code, errors, warnings, used_names = compile(ITERATORS)

    it = (1, 2, 3)
    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda x: x
    glb = {'_getiter_': _getiter_}
    six.exec_(code, glb)

    ret = glb['for_loop'](it)
    assert 6 == ret
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['dict_comp'](it)
    assert {1: 2, 2: 4, 3: 6} == ret
    _getiter_.assert_called_once_with(it)
    _getiter_.reset_mock()

    ret = glb['list_comp'](it)
    assert [2, 4, 6] == ret
    _getiter_.assert_called_once_with(it)
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
    """It is an error if the code call the `eval` function."""
    code, errors = compile(ITERATORS_WITH_UNPACK_SEQUENCE)[:2]

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

    six.exec_(code, glb)

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
def test_transformer__RestrictingNodeTransformer__visit_Subscript_1(compile, mocker):
    code, errors, warnings, used_names = compile(GET_SUBSCRIPTS)

    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    six.exec_(code, glb)

    ret = glb['simple_subscript'](value)
    ref = (value, 'b')
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
def test_transformer__RestrictingNodeTransformer__visit_Subscript_2(compile, mocker):
    code, errors, warnings, used_names = compile(WRITE_SUBSCRIPTS)

    value = {'b': None}
    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob
    glb = {'_write_': _write_}
    six.exec_(code, glb)

    glb['assign_subscript'](value)
    assert value['b'] == 1
    _write_.assert_called_once_with(value)
    _write_.reset_mock()

    glb['del_subscript'](value)
    assert value == {}
    _write_.assert_called_once_with(value)
    _write_.reset_mock()


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_AugAssign(compile, mocker):
    _inplacevar_ = mocker.stub()
    _inplacevar_.side_effect = lambda op, val, expr: val + expr

    glb = {'a': 1, '_inplacevar_': _inplacevar_}
    code, errors = compile("a += 1")[:2]
    six.exec_(code, glb)

    assert code is not None
    assert errors == ()
    assert glb['a'] == 2
    _inplacevar_.assert_called_once_with('+=', 1, 1)
    _inplacevar_.reset_mock()

    code, errors = compile("a.a += 1")[:2]
    assert code is None
    assert ('Line 1: Augmented assignment of attributes '
            'is not allowed.',) == errors

    code, errors = compile("a[a] += 1")[:2]
    assert code is None
    assert ('Line 1: Augmented assignment of object items and '
            'slices is not allowed.',) == errors


FUNCTIONC_CALLS = """
def no_star_args_no_kwargs():
    return foo(1, 2)

def star_args_no_kwargs():
    star = (10, 20, 30)
    return foo(1, 2, *star)

def star_args_kwargs():
    star = (10, 20, 30)
    kwargs = {'x': 100, 'z': 200}
    return foo(1, 2, *star, r=9, **kwargs)
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Call(compile, mocker):
    code, errors = compile(FUNCTIONC_CALLS)[:2]

    _apply_ = mocker.stub()
    _apply_.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)

    glb = {
        '_apply_': _apply_,
        'foo': lambda *args, **kwargs: (args, kwargs)
    }

    six.exec_(code, glb)

    ret = (glb['no_star_args_no_kwargs']())
    assert ((1, 2), {}) == ret
    assert _apply_.called is False
    _apply_.reset_mock()

    ret = (glb['star_args_no_kwargs']())
    ref = ((1, 2, 10, 20, 30), {})
    assert ref == ret
    _apply_.assert_called_once_with(glb['foo'], *ref[0])
    _apply_.reset_mock()

    ret = (glb['star_args_kwargs']())
    ref = ((1, 2, 10, 20, 30), {'r': 9, 'z': 200, 'x': 100})
    assert ref == ret
    _apply_.assert_called_once_with(glb['foo'], *ref[0], **ref[1])
    _apply_.reset_mock()


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef_1(compile):
    err_msg = 'Line 1: "_bad" is an invalid variable ' \
              'name because it starts with "_"'

    code, errors = compile("def foo(_bad): pass")[:2]
    assert code is None
    assert errors[0] == err_msg

    code, errors = compile("def foo(_bad=1): pass")[:2]
    assert code is None
    assert errors[0] == err_msg

    code, errors = compile("def foo(*_bad): pass")[:2]
    assert code is None
    assert errors[0] == err_msg

    code, errors = compile("def foo(**_bad): pass")[:2]
    assert code is None
    assert errors[0] == err_msg

    if sys.version_info.major == 2:
        code, errors = compile("def foo((a, _bad)): pass")[:2]
        assert code is None
        assert errors[0] == err_msg

        # The old one did not support nested checks.
        if compile is RestrictedPython.compile.compile_restricted_exec:
            code, errors = compile("def foo(a, (c, (_bad, c))): pass")[:2]
            assert code is None
            assert errors[0] == err_msg

    if sys.version_info.major == 3:
        code, errors = compile("def foo(good, *, _bad): pass")[:2]
        assert code is None
        assert errors[0] == err_msg


NESTED_SEQ_UNPACK = """
def nested((a, b, (c, (d, e)))):
    return a, b, c, d, e

def nested_with_order((a, b), (c, d)):
    return a, b, c, d
"""


@pytest.mark.skipif(
    sys.version_info.major == 3,
    reason="tuple parameter unpacking is gone in python 3")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_FunctionDef_2(compile, mocker):
    code, errors = compile('def simple((a, b)): return a, b')[:2]

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    six.exec_(code, glb)

    val = (1, 2)
    ret = glb['simple'](val)
    assert ret == val
    _getiter_.assert_called_once_with(val)
    _getiter_.reset_mock()

    # The old RCompile did not support nested.
    if compile is RestrictedPython.RCompile.compile_restricted_exec:
        return

    code, errors = compile(NESTED_SEQ_UNPACK)[:2]
    six.exec_(code, glb)

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


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Lambda_1(compile):
    err_msg = 'Line 1: "_bad" is an invalid variable ' \
              'name because it starts with "_"'

    code, errors = compile("lambda _bad: None")[:2]
    assert code is None
    assert errors[0] == err_msg

    code, errors = compile("lambda _bad=1: None")[:2]
    assert code is None
    assert errors[0] == err_msg

    code, errors = compile("lambda *_bad: None")[:2]
    assert code is None
    assert errors[0] == err_msg

    code, errors = compile("lambda **_bad: None")[:2]
    assert code is None
    assert errors[0] == err_msg

    if sys.version_info.major == 2:
        # The old one did not support tuples at all.
        if compile is RestrictedPython.compile.compile_restricted_exec:
            code, errors = compile("lambda (a, _bad): None")[:2]
            assert code is None
            assert errors[0] == err_msg

            code, errors = compile("lambda (a, (c, (_bad, c))): None")[:2]
            assert code is None
            assert errors[0] == err_msg

    if sys.version_info.major == 3:
        code, errors = compile("lambda good, *, _bad: None")[:2]
        assert code is None
        assert errors[0] == err_msg


@pytest.mark.skipif(
    sys.version_info.major == 3,
    reason="tuple parameter unpacking is gone in python 3")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Lambda_2(compile, mocker):
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
    code, errors = compile(src)[:2]
    six.exec_(code, glb)

    ret = glb['m']((1, (2, 3)), 4, 5, 6, g=7, e=8)
    assert ret == 36
    assert 2 == _getiter_.call_count
    _getiter_.assert_any_call((1, (2, 3)))
    _getiter_.assert_any_call((2, 3))


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Assign(compile, mocker):
    src = "orig = (a, (x, z)) = (c, d) = g"
    code, errors = compile(src)[:2]

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence,
        'g': (1, (2, 3)),
    }

    six.exec_(code, glb)
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
    sys.version_info.major == 2,
    reason="starred assignments are python3 only")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Assign2(compile, mocker):
    src = "a, *d, (c, *e), x  = (1, 2, 3, (4, 3, 4), 5)"
    code, errors = compile(src)[:2]

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    six.exec_(code, glb)

    assert glb['a'] == 1
    assert glb['d'] == [2, 3]
    assert glb['c'] == 4
    assert glb['e'] == [3, 4]
    assert glb['x'] == 5

    _getiter_.assert_has_calls([
        mocker.call((1, 2, 3, (4, 3, 4), 5)),
        mocker.call((4, 3, 4))])


TRY_EXCEPT_FINALLY = """
def try_except(m):
    try:
        m('try')
        raise IndentationError('f1')
    except IndentationError as error:
        m('except')

def try_except_else(m):
    try:
        m('try')
    except:
        m('except')
    else:
        m('else')

def try_finally(m):
    try:
        m('try')
        1 / 0
    finally:
        m('finally')
        return

def try_except_finally(m):
    try:
        m('try')
        1 / 0
    except:
        m('except')
    finally:
        m('finally')

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


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__error_handling(compile, mocker):
    code, errors = compile(TRY_EXCEPT_FINALLY)[:2]
    assert code is not None

    glb = {}
    six.exec_(code, glb)

    trace = mocker.stub()

    glb['try_except'](trace)
    trace.assert_has_calls([
        mocker.call('try'),
        mocker.call('except')
    ])
    trace.reset_mock()

    glb['try_except_else'](trace)
    trace.assert_has_calls([
        mocker.call('try'),
        mocker.call('else')
    ])
    trace.reset_mock()

    glb['try_finally'](trace)
    trace.assert_has_calls([
        mocker.call('try'),
        mocker.call('finally')
    ])
    trace.reset_mock()

    glb['try_except_finally'](trace)
    trace.assert_has_calls([
        mocker.call('try'),
        mocker.call('except'),
        mocker.call('finally')
    ])
    trace.reset_mock()

    glb['try_except_else_finally'](trace)
    trace.assert_has_calls([
        mocker.call('try'),
        mocker.call('else'),
        mocker.call('finally')
    ])
    trace.reset_mock()


EXCEPT_WITH_TUPLE_UNPACK = """
def tuple_unpack(err):
    try:
        raise err
    except Exception as (a, (b, c)):
        return a + b + c
"""


@pytest.mark.skipif(
    sys.version_info.major == 3,
    reason="tuple unpacking on exceptions is gone in python3")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_ExceptHandler(compile, mocker):
    code, errors = compile(EXCEPT_WITH_TUPLE_UNPACK)[:2]
    assert code is not None

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it

    glb = {
        '_getiter_': _getiter_,
        '_unpack_sequence_': guarded_unpack_sequence
    }

    six.exec_(code, glb)

    err = Exception(1, (2, 3))
    ret = glb['tuple_unpack'](err)
    assert ret == 6

    _getiter_.assert_has_calls([
        mocker.call(err),
        mocker.call((2, 3))])


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Import(compile):
    errmsg = 'Line 1: "%s" is an invalid variable name ' \
             'because it starts with "_"'

    code, errors = compile('import a')[:2]
    assert code is not None
    assert errors == ()

    code, errors = compile('import _a')[:2]
    assert code is None
    assert errors[0] == (errmsg % '_a')

    code, errors = compile('import _a as m')[:2]
    assert code is None
    assert errors[0] == (errmsg % '_a')

    code, errors = compile('import a as _m')[:2]
    assert code is None
    assert errors[0] == (errmsg % '_m')

    code, errors = compile('from a import m')[:2]
    assert code is not None
    assert errors == ()

    code, errors = compile('from _a import m')[:2]
    assert code is not None
    assert errors == ()

    code, errors = compile('from a import m as _n')[:2]
    assert code is None
    assert errors[0] == (errmsg % '_n')

    code, errors = compile('from a import _m as n')[:2]
    assert code is None
    assert errors[0] == (errmsg % '_m')


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_ClassDef(compile):
    code, errors = compile('class Good: pass')[:2]
    assert code is not None
    assert errors == ()

    # Do not allow class names which start with an underscore.
    code, errors = compile('class _bad: pass')[:2]
    assert code is None
    assert errors[0] == 'Line 1: "_bad" is an invalid variable name ' \
                        'because it starts with "_"'
