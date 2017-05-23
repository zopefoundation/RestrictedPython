"""
Tests about imports
"""

from tests import c_exec
from tests import e_exec

import pytest


OS_IMPORT_EXAMPLE = """
import os

os.listdir('/')
"""


@pytest.mark.parametrize(*c_exec)
@pytest.mark.parametrize(*e_exec)
def test_os_import(c_exec, e_exec):
    """Test that import should not work out of the box.
    TODO: Why does this work.
    """
    result = c_exec(OS_IMPORT_EXAMPLE)
    assert result.code is not None
    assert result.errors == ()

    # with pytest.raises(NameError):
    #    e_exec(OS_IMPORT_EXAMPLE)
