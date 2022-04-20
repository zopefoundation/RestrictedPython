from RestrictedPython import compile_restricted_exec
from tests.helper import restricted_exec


BAD_NAME_STARTING_WITH_UNDERSCORE = """\
def bad_name():
    __ = 12
"""


def test_RestrictingNodeTransformer__visit_Name__1():
    """It denies a variable name starting in `__`."""
    result = compile_restricted_exec(BAD_NAME_STARTING_WITH_UNDERSCORE)
    assert result.errors == (
        'Line 2: "__" is an invalid variable name because it starts with "_"',)


BAD_NAME_OVERRIDE_GUARD_WITH_NAME = """\
def overrideGuardWithName():
    _getattr = None
"""


def test_RestrictingNodeTransformer__visit_Name__2():
    """It denies a variable name starting in `_`."""
    result = compile_restricted_exec(BAD_NAME_OVERRIDE_GUARD_WITH_NAME)
    assert result.errors == (
        'Line 2: "_getattr" is an invalid variable name because '
        'it starts with "_"',)


def test_RestrictingNodeTransformer__visit_Name__2_5():
    """It allows `_` as variable name."""
    glb = restricted_exec('_ = 2411')
    assert glb['_'] == 2411


BAD_NAME_OVERRIDE_OVERRIDE_GUARD_WITH_FUNCTION = """\
def overrideGuardWithFunction():
    def _getattr(o):
        return o
"""


def test_RestrictingNodeTransformer__visit_Name__3():
    """It denies a function name starting in `_`."""
    result = compile_restricted_exec(
        BAD_NAME_OVERRIDE_OVERRIDE_GUARD_WITH_FUNCTION)
    assert result.errors == (
        'Line 2: "_getattr" is an invalid variable name because it '
        'starts with "_"',)


BAD_NAME_OVERRIDE_GUARD_WITH_CLASS = """\
def overrideGuardWithClass():
    class _getattr:
        pass
"""


def test_RestrictingNodeTransformer__visit_Name__4():
    """It denies a class name starting in `_`."""
    result = compile_restricted_exec(BAD_NAME_OVERRIDE_GUARD_WITH_CLASS)
    assert result.errors == (
        'Line 2: "_getattr" is an invalid variable name because it '
        'starts with "_"',)


BAD_NAME_IN_WITH = """\
def with_as_bad_name():
    with x as _leading_underscore:
        pass
"""


def test_RestrictingNodeTransformer__visit_Name__4_4():
    """It denies a variable name in with starting in `_`."""
    result = compile_restricted_exec(BAD_NAME_IN_WITH)
    assert result.errors == (
        'Line 2: "_leading_underscore" is an invalid variable name because '
        'it starts with "_"',)


BAD_NAME_IN_COMPOUND_WITH = """\
def compound_with_bad_name():
    with a as b, c as _restricted_name:
        pass
"""


def test_RestrictingNodeTransformer__visit_Name__4_5():
    """It denies a variable name in with starting in `_`."""
    result = compile_restricted_exec(BAD_NAME_IN_COMPOUND_WITH)
    assert result.errors == (
        'Line 2: "_restricted_name" is an invalid variable name because '
        'it starts with "_"',)


BAD_NAME_DICT_COMP = """\
def dict_comp_bad_name():
    {y: y for _restricted_name in x}
"""


def test_RestrictingNodeTransformer__visit_Name__4_6():
    """It denies a variable name starting in `_` in a dict comprehension."""
    result = compile_restricted_exec(BAD_NAME_DICT_COMP)
    assert result.errors == (
        'Line 2: "_restricted_name" is an invalid variable name because '
        'it starts with "_"',)


BAD_NAME_SET_COMP = """\
def set_comp_bad_name():
    {y for _restricted_name in x}
"""


def test_RestrictingNodeTransformer__visit_Name__4_7():
    """It denies a variable name starting in `_` in a dict comprehension."""
    result = compile_restricted_exec(BAD_NAME_SET_COMP)
    assert result.errors == (
        'Line 2: "_restricted_name" is an invalid variable name because '
        'it starts with "_"',)


BAD_NAME_ENDING_WITH___ROLES__ = """\
def bad_name():
    myvar__roles__ = 12
"""


def test_RestrictingNodeTransformer__visit_Name__5():
    """It denies a variable name ending in `__roles__`."""
    result = compile_restricted_exec(BAD_NAME_ENDING_WITH___ROLES__)
    assert result.errors == (
        'Line 2: "myvar__roles__" is an invalid variable name because it '
        'ends with "__roles__".',)


BAD_NAME_PRINTED = """\
def bad_name():
    printed = 12
"""


def test_RestrictingNodeTransformer__visit_Name__6():
    """It denies a variable named `printed`."""
    result = compile_restricted_exec(BAD_NAME_PRINTED)
    assert result.errors == ('Line 2: "printed" is a reserved name.',)


BAD_NAME_PRINT = """\
def bad_name():
    def print():
        pass
"""


def test_RestrictingNodeTransformer__visit_Name__7():
    """It denies a variable named `print`."""
    result = compile_restricted_exec(BAD_NAME_PRINT)
    assert result.errors == ('Line 2: "print" is a reserved name.',)
