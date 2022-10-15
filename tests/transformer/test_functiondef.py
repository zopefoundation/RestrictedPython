from RestrictedPython import compile_restricted_exec


functiondef_err_msg = 'Line 1: "_bad" is an invalid variable ' \
                      'name because it starts with "_"'


def test_RestrictingNodeTransformer__visit_FunctionDef__1():
    """It prevents function arguments starting with `_`."""
    result = compile_restricted_exec("def foo(_bad): pass")
    assert result.errors == (functiondef_err_msg,)


def test_RestrictingNodeTransformer__visit_FunctionDef__2():
    """It prevents function keyword arguments starting with `_`."""
    result = compile_restricted_exec("def foo(_bad=1): pass")
    assert result.errors == (functiondef_err_msg,)


def test_RestrictingNodeTransformer__visit_FunctionDef__3():
    """It prevents function * arguments starting with `_`."""
    result = compile_restricted_exec("def foo(*_bad): pass")
    assert result.errors == (functiondef_err_msg,)


def test_RestrictingNodeTransformer__visit_FunctionDef__4():
    """It prevents function ** arguments starting with `_`."""
    result = compile_restricted_exec("def foo(**_bad): pass")
    assert result.errors == (functiondef_err_msg,)


def test_RestrictingNodeTransformer__visit_FunctionDef__7():
    """It prevents `_` function arguments together with a single `*`."""
    result = compile_restricted_exec("def foo(good, *, _bad): pass")
    assert result.errors == (functiondef_err_msg,)


BLACKLISTED_FUNC_NAMES_CALL_TEST = """
def __init__(test):
    test

__init__(1)
"""


def test_RestrictingNodeTransformer__module_func_def_name_call():
    """It forbids definition and usage of magic methods as functions ...

    ... at module level.
    """
    result = compile_restricted_exec(BLACKLISTED_FUNC_NAMES_CALL_TEST)
    # assert result.errors == ('Line 1: ')
    assert result.errors == (
        'Line 2: "__init__" is an invalid variable name because it starts with "_"',  # NOQA: E501
        'Line 5: "__init__" is an invalid variable name because it starts with "_"',  # NOQA: E501
    )
