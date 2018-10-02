"""
Tests about imports
"""

from RestrictedPython import safe_builtins
from RestrictedPython._compat import IS_PY2
from RestrictedPython._compat import IS_PY3
from tests import c_exec
from tests import e_exec

import pytest


OS_IMPORT_EXAMPLE = """
import os

os.listdir('/')
"""


@pytest.mark.parametrize(*e_exec)
def test_os_import(e_exec):
    """It does not allow to import anything by default.

    The `__import__` function is not provided as it is not safe.
    """
    # Caution: This test is broken on PyPy until the following issue is fixed:
    # https://bitbucket.org/pypy/pypy/issues/2653
    # PyPy currently ignores the restriction of the `__builtins__`.
    glb = {'__builtins__': safe_builtins}

    with pytest.raises(ImportError) as err:
        e_exec(OS_IMPORT_EXAMPLE, glb)
    assert '__import__ not found' == str(err.value)


__BUILTINS_EXAMPLE = """
import __builtins__

mygetattr = __builtins__['getattr']
"""


@pytest.mark.skipif(
    IS_PY3,
    reason="__builtins__ has been renamed in Python3 to builtins, "
    "so no __builtins__ in Python3."
)
@pytest.mark.parametrize(*c_exec)
def test_import_py2_builtins(c_exec):
    """It should not be allowed to access global __builtins__ in Python2."""
    result = c_exec(__BUILTINS_EXAMPLE)
    assert result.code is None
    assert result.errors == (
        'Line 2: "__builtins__" is an invalid variable name because it starts with "_"',  # NOQA: E501
        'Line 4: "__builtins__" is an invalid variable name because it starts with "_"'  # NOQA: E501
    )


__BUILTINS_AS_EXAMPLE = """
import __builtins__ as builtins

mygetattr = builtins['getattr']
"""


@pytest.mark.skipif(
    IS_PY3,
    reason="__builtins__ has been renamed in Python3 to builtins, "
    "so no __builtins__ in Python3."
)
@pytest.mark.parametrize(*c_exec)
def test_import_py2_as_builtins(c_exec):
    """It should not be allowed to access global __builtins__ in Python2."""
    result = c_exec(__BUILTINS_EXAMPLE)
    assert result.code is None
    assert result.errors == (
        'Line 2: "__builtins__" is an invalid variable name because it starts with "_"',  # NOQA: E501
        'Line 4: "__builtins__" is an invalid variable name because it starts with "_"'  # NOQA: E501
    )


BUILTINS_EXAMPLE = """
import builtins

mygetattr = builtins['getattr']
"""


@pytest.mark.skipif(
    IS_PY2,
    reason="__builtins__ has been renamed in Python3 to builtins, "
    "and need only to be tested there."
)
@pytest.mark.parametrize(*c_exec)
def test_import_py3_builtins(c_exec):
    """It should not be allowed to access global builtins in Python3."""
    result = c_exec(BUILTINS_EXAMPLE)
    assert result.code is None
    assert result.errors == (
        'Line 2: "builtins" is a reserved name.',
        'Line 4: "builtins" is a reserved name.'
    )


BUILTINS_AS_EXAMPLE = """
import builtins as glb

mygetattr = glb['getattr']
"""


@pytest.mark.skipif(
    IS_PY2,
    reason="__builtins__ has been renamed in Python3 to builtins, "
    "and need only to be tested there."
)
@pytest.mark.parametrize(*c_exec)
def test_import_py3_as_builtins(c_exec):
    """It should not be allowed to access global builtins in Python3."""
    result = c_exec(BUILTINS_AS_EXAMPLE)
    assert result.code is None
    assert result.errors == ('Line 2: "builtins" is a reserved name.',)
