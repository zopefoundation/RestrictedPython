from RestrictedPython._compat import IS_PY3
from RestrictedPython.PrintCollector import PrintCollector
from tests import c_exec

import pytest
import RestrictedPython


pytestmark = pytest.mark.skipif(
    IS_PY3,
    reason="print statement no longer exists in Python 3")


ALLOWED_PRINT_STATEMENT = """
print 'Hello World!'
"""

ALLOWED_PRINT_STATEMENT_WITH_NO_NL = """
print 'Hello World!',
"""

ALLOWED_MULTI_PRINT_STATEMENT = """
print 'Hello World!', 'Hello Earth!'
"""

# It looks like a function, but is still a statement in python2.X
ALLOWED_PRINT_TUPLE = """
print('Hello World!')
"""


ALLOWED_PRINT_MULTI_TUPLE = """
print('Hello World!', 'Hello Earth!')
"""


@pytest.mark.parametrize(*c_exec)
def test_print_stmt__simple_prints(c_exec):
    glb = {'_print_': PrintCollector, '_getattr_': None}

    code, errors = c_exec(ALLOWED_PRINT_STATEMENT)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == 'Hello World!\n'

    code, errors = c_exec(ALLOWED_PRINT_STATEMENT_WITH_NO_NL)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == 'Hello World!'

    code, errors = c_exec(ALLOWED_MULTI_PRINT_STATEMENT)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == 'Hello World! Hello Earth!\n'

    code, errors = c_exec(ALLOWED_PRINT_TUPLE)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == "Hello World!\n"

    code, errors = c_exec(ALLOWED_PRINT_MULTI_TUPLE)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == "('Hello World!', 'Hello Earth!')\n"


@pytest.mark.parametrize(*c_exec)
def test_print_stmt__fail_with_none_target(c_exec, mocker):
    code, errors = c_exec('print >> None, "test"')[:2]

    assert code is not None
    assert errors == ()

    glb = {'_getattr_': getattr, '_print_': PrintCollector}

    with pytest.raises(AttributeError) as excinfo:
        exec(code, glb)

    assert "'NoneType' object has no attribute 'write'" in str(excinfo.value)


PROTECT_PRINT_STATEMENT_WITH_CHEVRON = """
def print_into_stream(stream):
    print >> stream, 'Hello World!'
"""


@pytest.mark.parametrize(*c_exec)
def test_print_stmt__protect_chevron_print(c_exec, mocker):
    code, errors = c_exec(PROTECT_PRINT_STATEMENT_WITH_CHEVRON)[:2]

    _getattr_ = mocker.stub()
    _getattr_.side_effect = getattr
    glb = {'_getattr_': _getattr_, '_print_': PrintCollector}

    exec(code, glb)

    stream = mocker.stub()
    stream.write = mocker.stub()
    glb['print_into_stream'](stream)

    stream.write.assert_has_calls([
        mocker.call('Hello World!'),
        mocker.call('\n')
    ])

    _getattr_.assert_called_once_with(stream, 'write')


# 'printed' is scope aware.
# => on a new function scope a new printed is generated.
INJECT_PRINT_COLLECTOR_NESTED = """
def f2():
    return 'f2'

def f1():
    print 'f1'

    def inner():
        print 'inner'
        return printed

    return inner() + printed + f2()

def main():
    print 'main'
    return f1() + printed
"""


@pytest.mark.parametrize(*c_exec)
def test_print_stmt__nested_print_collector(c_exec, mocker):
    code, errors = c_exec(INJECT_PRINT_COLLECTOR_NESTED)[:2]

    glb = {"_print_": PrintCollector, '_getattr_': None}
    exec(code, glb)

    ret = glb['main']()
    assert ret == 'inner\nf1\nf2main\n'


WARN_PRINTED_NO_PRINT = """
def foo():
    return printed
"""


@pytest.mark.parametrize(*c_exec)
def test_print_stmt__with_printed_no_print(c_exec):
    code, errors, warnings = c_exec(WARN_PRINTED_NO_PRINT)[:3]

    assert code is not None
    assert errors == ()

    if c_exec is RestrictedPython.compile.compile_restricted_exec:
        assert warnings == [
            "Line 2: Doesn't print, but reads 'printed' variable."]

    if c_exec is RestrictedPython.RCompile.compile_restricted_exec:
        assert warnings == ["Doesn't print, but reads 'printed' variable."]


WARN_PRINTED_NO_PRINT_NESTED = """
print 'a'
def foo():
    return printed
printed
"""


@pytest.mark.parametrize(*c_exec)
def test_print_stmt__with_printed_no_print_nested(c_exec):
    code, errors, warnings = c_exec(WARN_PRINTED_NO_PRINT_NESTED)[:3]

    assert code is not None
    assert errors == ()

    if c_exec is RestrictedPython.compile.compile_restricted_exec:
        assert warnings == [
            "Line 2: Print statement is deprecated and not avaliable anymore in Python 3.",  # NOQA: E501
            "Line 3: Doesn't print, but reads 'printed' variable."
        ]

    if c_exec is RestrictedPython.RCompile.compile_restricted_exec:
        assert warnings == ["Doesn't print, but reads 'printed' variable."]


WARN_PRINT_NO_PRINTED = """
def foo():
    print 1
"""


@pytest.mark.parametrize(*c_exec)
def test_print_stmt__with_print_no_printed(c_exec):
    code, errors, warnings = c_exec(WARN_PRINT_NO_PRINTED)[:3]

    assert code is not None
    assert errors == ()

    if c_exec is RestrictedPython.compile.compile_restricted_exec:
        assert warnings == [
            "Line 3: Print statement is deprecated and not avaliable anymore in Python 3.",  # NOQA: E501
            "Line 2: Prints, but never reads 'printed' variable."
        ]

    if c_exec is RestrictedPython.RCompile.compile_restricted_exec:
        assert warnings == ["Prints, but never reads 'printed' variable."]


WARN_PRINT_NO_PRINTED_NESTED = """
print 'a'
def foo():
    print 'x'
printed
"""


@pytest.mark.parametrize(*c_exec)
def test_print_stmt__with_print_no_printed_nested(c_exec):
    code, errors, warnings = c_exec(WARN_PRINT_NO_PRINTED_NESTED)[:3]

    assert code is not None
    assert errors == ()

    if c_exec is RestrictedPython.compile.compile_restricted_exec:
        assert warnings == [
            "Line 2: Print statement is deprecated and not avaliable anymore in Python 3.",  # NOQA: E501
            "Line 4: Print statement is deprecated and not avaliable anymore in Python 3.",  # NOQA: E501
            "Line 3: Prints, but never reads 'printed' variable.",
        ]

    if c_exec is RestrictedPython.RCompile.compile_restricted_exec:
        assert warnings == ["Prints, but never reads 'printed' variable."]


# python2 generates a new frame/scope for:
# modules, functions, class, lambda
# Since print statement cannot be used in lambda only ensure that no new scope
# for classes is generated.

NO_PRINT_SCOPES = """
def class_scope():
    class A:
        print 'a'
    return printed
"""


@pytest.mark.parametrize(*c_exec)
def test_print_stmt_no_new_scope(c_exec):
    code, errors = c_exec(NO_PRINT_SCOPES)[:2]
    glb = {'_print_': PrintCollector, '_getattr_': None}
    exec(code, glb)

    ret = glb['class_scope']()
    assert ret == 'a\n'


CONDITIONAL_PRINT = """
def func(cond):
    if cond:
        print 1
    return printed
"""


@pytest.mark.parametrize(*c_exec)
def test_print_stmt_conditional_print(c_exec):
    code, errors = c_exec(CONDITIONAL_PRINT)[:2]
    glb = {'_print_': PrintCollector, '_getattr_': None}
    exec(code, glb)

    assert glb['func'](True) == '1\n'
    assert glb['func'](False) == ''
