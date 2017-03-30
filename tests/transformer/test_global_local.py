from tests import c_exec

import pytest


GLOBAL_EXAMPLE = """
a = 1
global a
"""


@pytest.mark.parametrize(*c_exec)
def test_Global(c_exec):
    result = c_exec(GLOBAL_EXAMPLE)
    assert result.code is None
    assert result.errors == (
        'Line 3: Global statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}


NONLOCAL_EXAMPLE = """
a = 1
nonlocal a
"""


@pytest.mark.parametrize(*c_exec)
def test_Nonlocal(c_exec):
    result = c_exec(NONLOCAL_EXAMPLE)
    assert result.code is None
    assert result.errors == (
        'Line 3: Nonlocal statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}
