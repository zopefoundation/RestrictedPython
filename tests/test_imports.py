"""
Tests about imports
"""

import pytest

from RestrictedPython import compile_restricted_exec
from RestrictedPython import safe_builtins
from tests.helper import restricted_exec


OS_IMPORT_EXAMPLE = """
import os

os.listdir('/')
"""


def test_os_import():
    """It does not allow to import anything by default.

    The `__import__` function is not provided as it is not safe.
    """
    # Caution: This test is broken on PyPy until the following issue is fixed:
    # https://bitbucket.org/pypy/pypy/issues/2653
    # PyPy currently ignores the restriction of the `__builtins__`.
    glb = {'__builtins__': safe_builtins}

    with pytest.raises(ImportError) as err:
        restricted_exec(OS_IMPORT_EXAMPLE, glb)
    assert '__import__ not found' == str(err.value)


BUILTINS_EXAMPLE = """
import builtins

mygetattr = builtins['getattr']
"""


def test_import_py3_builtins():
    """It should not be allowed to access global builtins in Python3."""
    result = compile_restricted_exec(BUILTINS_EXAMPLE)
    assert result.code is None
    assert result.errors == (
        'Line 2: "builtins" is a reserved name.',
        'Line 4: "builtins" is a reserved name.'
    )


BUILTINS_AS_EXAMPLE = """
import builtins as glb

mygetattr = glb['getattr']
"""


def test_import_py3_as_builtins():
    """It should not be allowed to access global builtins in Python3."""
    result = compile_restricted_exec(BUILTINS_AS_EXAMPLE)
    assert result.code is None
    assert result.errors == ('Line 2: "builtins" is a reserved name.',)
