from tests import c_exec

import pytest


import_errmsg = (
    'Line 1: "%s" is an invalid variable name because it starts with "_"')


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Import__1(c_exec):
    """It allows importing a module."""
    result = c_exec('import a')
    assert result.errors == ()
    assert result.code is not None


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Import__2(c_exec):
    """It denies importing a module starting with `_`."""
    result = c_exec('import _a')
    assert result.errors == (import_errmsg % '_a',)


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Import__3(c_exec):
    """It denies importing a module starting with `_` as something."""
    result = c_exec('import _a as m')
    assert result.errors == (import_errmsg % '_a',)


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Import__4(c_exec):
    """It denies importing a module as something starting with `_`."""
    result = c_exec('import a as _m')
    assert result.errors == (import_errmsg % '_m',)


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Import__5(c_exec):
    """It allows importing from a module."""
    result = c_exec('from a import m')
    assert result.errors == ()
    assert result.code is not None


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Import_6(c_exec):
    """It allows importing from a module starting with `_`."""
    result = c_exec('from _a import m')
    assert result.errors == ()
    assert result.code is not None


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Import__7(c_exec):
    """It denies importing from a module as something starting with `_`."""
    result = c_exec('from a import m as _n')
    assert result.errors == (import_errmsg % '_n',)


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Import__8(c_exec):
    """It denies as-importing something starting with `_` from a module."""
    result = c_exec('from a import _m as n')
    assert result.errors == (import_errmsg % '_m',)


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Import__9(c_exec):
    """It denies relative from importing as something starting with `_`."""
    result = c_exec('from .x import y as _leading_underscore')
    assert result.errors == (import_errmsg % '_leading_underscore',)
