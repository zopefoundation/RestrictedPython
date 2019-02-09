from RestrictedPython import compile_restricted_exec


import_errmsg = (
    'Line 1: "%s" is an invalid variable name because it starts with "_"')


def test_RestrictingNodeTransformer__visit_Import__1():
    """It allows importing a module."""
    result = compile_restricted_exec('import a')
    assert result.errors == ()
    assert result.code is not None


def test_RestrictingNodeTransformer__visit_Import__2():
    """It denies importing a module starting with `_`."""
    result = compile_restricted_exec('import _a')
    assert result.errors == (import_errmsg % '_a',)


def test_RestrictingNodeTransformer__visit_Import__3():
    """It denies importing a module starting with `_` as something."""
    result = compile_restricted_exec('import _a as m')
    assert result.errors == (import_errmsg % '_a',)


def test_RestrictingNodeTransformer__visit_Import__4():
    """It denies importing a module as something starting with `_`."""
    result = compile_restricted_exec('import a as _m')
    assert result.errors == (import_errmsg % '_m',)


def test_RestrictingNodeTransformer__visit_Import__5():
    """It allows importing from a module."""
    result = compile_restricted_exec('from a import m')
    assert result.errors == ()
    assert result.code is not None


def test_RestrictingNodeTransformer__visit_Import_6():
    """It allows importing from a module starting with `_`."""
    result = compile_restricted_exec('from _a import m')
    assert result.errors == ()
    assert result.code is not None


def test_RestrictingNodeTransformer__visit_Import__7():
    """It denies importing from a module as something starting with `_`."""
    result = compile_restricted_exec('from a import m as _n')
    assert result.errors == (import_errmsg % '_n',)


def test_RestrictingNodeTransformer__visit_Import__8():
    """It denies as-importing something starting with `_` from a module."""
    result = compile_restricted_exec('from a import _m as n')
    assert result.errors == (import_errmsg % '_m',)


def test_RestrictingNodeTransformer__visit_Import__9():
    """It denies relative from importing as something starting with `_`."""
    result = compile_restricted_exec('from .x import y as _leading_underscore')
    assert result.errors == (import_errmsg % '_leading_underscore',)


def test_RestrictingNodeTransformer__visit_Import_star__1():
    """Importing `*` is a SyntaxError in Python itself."""
    result = compile_restricted_exec('import *')
    assert result.errors == (
        "Line 1: SyntaxError: invalid syntax at statement: 'import *'",)
    assert result.code is None


def test_RestrictingNodeTransformer__visit_Import_star__2():
    """It denies importing `*` from a module."""
    result = compile_restricted_exec('from a import *')
    assert result.errors == ('Line 1: "*" imports are not allowed.',)
    assert result.code is None
