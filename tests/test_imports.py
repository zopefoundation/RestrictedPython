"""
Tests about imports
"""

from RestrictedPython import safe_builtins
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
