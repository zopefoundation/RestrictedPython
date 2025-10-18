from string.templatelib import Template

import pytest

from RestrictedPython import compile_restricted_exec
from RestrictedPython._compat import IS_PY314_OR_GREATER
from RestrictedPython.Eval import default_guarded_getattr
from RestrictedPython.Eval import default_guarded_getiter
from RestrictedPython.PrintCollector import PrintCollector


@pytest.mark.skipif(
    not IS_PY314_OR_GREATER,
    reason="t-strings were added in Python 3.14.",
)
def test_transform():
    """It compiles a function call successfully and returns the used name."""

    result = compile_restricted_exec('a = t"{max([1, 2, 3])}"')
    assert result.errors == ()
    assert result.warnings == [
        'Line 1: TemplateStr statements are not yet allowed, please use f-strings or a real template engine instead.']  # NOQA: E501
    assert result.code is not None
    loc = {}
    exec(result.code, {}, loc)
    template = loc['a']
    assert isinstance(template, Template)
    assert template.values == (3, )
    assert result.used_names == {'max': True}


@pytest.mark.skipif(
    not IS_PY314_OR_GREATER,
    reason="t-strings were added in Python 3.14.",
)
def test_visit_invalid_variable_name():
    """Accessing private attributes is forbidden.

    This is just a smoke test to validate that restricted exec is used
    in the run-time evaluation of t-strings.
    """
    result = compile_restricted_exec('t"{__init__}"')
    assert result.errors == (
        'Line 1: "__init__" is an invalid variable name because it starts with "_"',  # NOQA: E501
    )


t_string_self_documenting_expressions_example = """
from datetime import date
from string.templatelib import Template, Interpolation

user = 'eric_idle'
member_since = date(1975, 7, 31)

def render_template(template: Template) -> str:
    result = ''
    for part in template:
        if isinstance(part, Interpolation):
            if isinstance(part.value, str):
                result += part.value.upper()
            else:
                result += str(part.value)
        else:
            result += part.lower()
    return result

print(render_template(t'The User {user} is a member since {member_since}'))
"""


@pytest.mark.skipif(
    not IS_PY314_OR_GREATER,
    reason="t-strings were added in Python 3.14.",
)
def test_t_string_self_documenting_expressions():
    """Checks if t-string self-documenting expressions is checked."""
    result = compile_restricted_exec(
        t_string_self_documenting_expressions_example,
    )
    # assert result.errors == (
    #   'Line 13: TemplateStr statements are not allowed.',
    # )
    # assert result.warnings == [
    #     'Line 13: TemplateStr statements are not yet allowed, please use '
    #     'f-strings or a real template engine instead.',
    #     "Line None: Prints, but never reads 'printed' variable."
    # ]
    # assert result.code is None
    assert result.errors == ()
    assert result.warnings == [
        'Line 20: TemplateStr statements are not yet allowed, '
        'please use f-strings or a real template engine instead.',
        "Line None: Prints, but never reads 'printed' variable."]
    assert result.code is not None

    glb = {
        '_print_': PrintCollector,
        '_getattr_': default_guarded_getattr,
        '_getiter_': default_guarded_getiter,
        '_inplacevar_': lambda x, y, z: y + z,
    }
    exec(result.code, glb)
    assert glb['_print']() == "the user ERIC_IDLE is a member since 1975-07-31\n"  # NOQA: E501
