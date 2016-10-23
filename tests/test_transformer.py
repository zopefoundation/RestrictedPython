import pytest
import RestrictedPython
import six
import sys
import types


# Define the arguments for @pytest.mark.parametrize to be able to test both the
# old and the new implementation to be equal:
compile = ('compile', [RestrictedPython.compile])
if sys.version_info < (3,):
    from RestrictedPython import RCompile
    compile[1].append(RCompile)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__1(compile):
    """It compiles a number successfully."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        '42', '<undefined>')
    assert 'code' == str(code.__class__.__name__)
    assert errors == ()
    assert warnings == []
    assert used_names == {}


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__2(compile):
    """It compiles a function call successfully and returns the used name."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        'max([1, 2, 3])', '<undefined>')
    assert errors == ()
    assert warnings == []
    assert 'code' == str(code.__class__.__name__)
    if compile is RestrictedPython.compile:
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
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        YIELD, '<undefined>')
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
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        EXEC_STATEMENT, '<undefined>')
    assert ('Line 2: Exec statements are not allowed.',) == errors


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="exec statement in Python 3 raises SyntaxError itself")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__103(compile):
    """It is an error if the code contains an `exec` statement."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        EXEC_STATEMENT, '<undefined>')
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
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        BAD_NAME, '<undefined>')
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
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        BAD_ATTR_UNDERSCORE, '<undefined>')

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
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        BAD_ATTR_ROLES, '<undefined>')

    assert ('Line 3: "abc__roles__" is an invalid attribute name because it '
            'ends with "__roles__".',) == errors


TRANSFORM_ATTRIBUTE_ACCESS = """\
def func():
    return a.b
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__3(compile, mocker):
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        TRANSFORM_ATTRIBUTE_ACCESS)

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
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        ALLOW_UNDERSCORE_ONLY)

    assert errors == ()
    assert warnings == []
    assert code is not None


TRANSFORM_ATTRIBUTE_WRITE = """\
def func():
    a.b = 'it works'
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__5(compile, mocker):
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        TRANSFORM_ATTRIBUTE_WRITE)

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
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        EXEC_FUNCTION, '<undefined>')
    assert ("Line 2: Exec calls are not allowed.",) == errors


EVAL_FUNCTION = """\
def no_eval():
    eval('q = 1')
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Call__2(compile):
    """It is an error if the code call the `eval` function."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        EVAL_FUNCTION, '<undefined>')
    if compile is RestrictedPython.compile:
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
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        ITERATORS)

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
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        GET_SUBSCRIPTS)

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
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        WRITE_SUBSCRIPTS)

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
def test_transformer__RestrictingNodeTransformer__visit_AugAssing(compile, mocker):
    def do_compile(code):
        return compile.compile_restricted_exec(code)[:2]

    _inplacevar_ = mocker.stub()
    _inplacevar_.side_effect = lambda op, val, expr: val + expr

    glb = {'a': 1, '_inplacevar_': _inplacevar_}
    code, errors = do_compile("a += 1")
    six.exec_(code, glb)

    assert code is not None
    assert errors == ()
    assert glb['a'] == 2
    _inplacevar_.assert_called_once_with('+=', 1, 1)
    _inplacevar_.reset_mock()

    code, errors = do_compile("a.a += 1")
    assert code is None
    assert ('Line 1: Augmented assignment of attributes '
            'is not allowed.',) == errors

    code, errors = do_compile("a[a] += 1")
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
    code, errors = compile.compile_restricted_exec(FUNCTIONC_CALLS)[:2]

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
    def do_compile(src):
        return compile.compile_restricted_exec(src)[:2]

    err_msg = 'Line 1: "_bad" is an invalid variable ' \
              'name because it starts with "_"'

    code, errors = do_compile("def foo(_bad): pass")
    assert code is None
    assert errors[0] == err_msg

    code, errors = do_compile("def foo(_bad=1): pass")
    assert code is None
    assert errors[0] == err_msg

    code, errors = do_compile("def foo(*_bad): pass")
    assert code is None
    assert errors[0] == err_msg

    code, errors = do_compile("def foo(**_bad): pass")
    assert code is None
    assert errors[0] == err_msg

    if sys.version_info.major == 2:
        code, errors = do_compile("def foo((a, _bad)): pass")
        assert code is None
        assert errors[0] == err_msg

        # The old one did not support nested checks.
        if compile is RestrictedPython.compile:
            code, errors = do_compile("def foo(a, (c, (_bad, c))): pass")
            assert code is None
            assert errors[0] == err_msg

    if sys.version_info.major == 3:
        code, errors = do_compile("def foo(good, *, _bad): pass")
        assert code is None
        assert errors[0] == err_msg


NESTED_SEQ_UNPACK =  """
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
    def do_compile(code):
        return compile.compile_restricted_exec(code)[:2]

    code, errors = do_compile('def simple((a, b)): return a, b')

    _getiter_ = mocker.stub()
    _getiter_.side_effect = lambda it: it
    glb = {'_getiter_': _getiter_}
    six.exec_(code, glb)

    val = (1, 2)
    ret = glb['simple'](val)
    assert ret == val
    _getiter_.assert_called_once_with(val)
    _getiter_.reset_mock()

    # The old RCompile did not support nested.
    if compile is RestrictedPython.RCompile:
        return

    code, errors = do_compile(NESTED_SEQ_UNPACK)
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
    def do_compile(src):
        return compile.compile_restricted_exec(src)[:2]

    err_msg = 'Line 1: "_bad" is an invalid variable ' \
              'name because it starts with "_"'

    code, errors = do_compile("lambda _bad: None")
    assert code is None
    assert errors[0] == err_msg

    code, errors = do_compile("lambda _bad=1: None")
    assert code is None
    assert errors[0] == err_msg

    code, errors = do_compile("lambda *_bad: None")
    assert code is None
    assert errors[0] == err_msg

    code, errors = do_compile("lambda **_bad: None")
    assert code is None
    assert errors[0] == err_msg

    if sys.version_info.major == 2:
        # The old one did not support tuples at all.
        if compile is RestrictedPython.compile:
            code, errors = do_compile("lambda (a, _bad): None")
            assert code is None
            assert errors[0] == err_msg

            code, errors = do_compile("lambda (a, (c, (_bad, c))): None")
            assert code is None
            assert errors[0] == err_msg

    if sys.version_info.major == 3:
        code, errors = do_compile("lambda good, *, _bad: None")
        assert code is None
        assert errors[0] == err_msg
