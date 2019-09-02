from RestrictedPython import compile_restricted_exec
from RestrictedPython._compat import IS_PY36_OR_GREATER

import pytest


@pytest.mark.skipif(
    not IS_PY36_OR_GREATER,
    reason="F-strings added in Python 3.6.",
)
def test_transform():
    """It compiles a function call successfully and returns the used name."""

    result = compile_restricted_exec('a = f"{max([1, 2, 3])}"')
    assert result.errors == ()
    loc = {}
    exec(result.code, {}, loc)
    assert loc['a'] == '3'
    assert result.used_names == {'max': True}


@pytest.mark.skipif(
    not IS_PY36_OR_GREATER,
    reason="F-strings added in Python 3.6.",
)
def test_visit_invalid_variable_name():
    """Accessing private attributes is forbidden.

    This is just a smoke test to validate that restricted exec is used
    in the run-time evaluation of f-strings.
    """
    result = compile_restricted_exec('f"{__init__}"')
    assert result.errors == (
        'Line 1: "__init__" is an invalid variable name because it starts with "_"',  # NOQA: E501
    )
