from RestrictedPython import compile_restricted_exec
from tests.helper import restricted_exec

from sys import version_info


def test_transform():
    """It compiles a function call successfully and returns the used name."""

    # F-strings were introduced in Python 3.6.
    if version_info.major >= 3 and version_info.minor >= 6:
        result = compile_restricted_exec('a = f"{max([1, 2, 3])}"')
        assert result.errors == ()
        loc = {}
        exec(result.code, {}, loc)
        assert loc['a'] == '3'
        assert result.used_names == {'max': True}


def test_visit_invalid_variable_name():
    """Accessing private attributes is forbidden.

    This is just a smoke test to validate that restricted exec is used
    in the run-time evaluation of f-strings.
    """
    # F-strings were introduced in Python 3.6.
    if version_info.major >= 3 and version_info.minor >= 6:
        result = compile_restricted_exec('f"{__init__}"')
        assert result.errors == (
            'Line 1: "__init__" is an invalid variable name because it starts with "_"',  # NOQA: E501
        )
