from RestrictedPython import compile_restricted_exec
from RestrictedPython.PrintCollector import PrintCollector


def test_transform():
    """It compiles a function call successfully and returns the used name."""

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
    result = compile_restricted_exec('f"{__init__}"')
    assert result.errors == (
        'Line 1: "__init__" is an invalid variable name because it starts with "_"',  # NOQA: E501
    )


f_string_self_documenting_expressions_example = """
from datetime import date

user = 'eric_idle'
member_since = date(1975, 7, 31)
print(f'{user=} {member_since=}')
"""


def test_f_string_self_documenting_expressions():
    """Checks if f-string self-documenting expressions is checked."""
    result = compile_restricted_exec(
        f_string_self_documenting_expressions_example,
    )
    assert result.errors == ()

    glb = {'_print_': PrintCollector, '_getattr_': None}
    exec(result.code, glb)
    assert glb['_print']() == "user='eric_idle' member_since=datetime.date(1975, 7, 31)\n"  # NOQA: E501
