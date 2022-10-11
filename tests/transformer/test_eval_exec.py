from RestrictedPython import compile_restricted_exec


EXEC_FUNCTION = """\
def no_exec():
    exec('q = 1')
"""


def test_RestrictingNodeTransformer__visit_Exec__2():
    """It is an error if the code call the `exec` function."""
    result = compile_restricted_exec(EXEC_FUNCTION)
    assert result.errors == ("Line 2: Exec calls are not allowed.",)


EVAL_FUNCTION = """\
def no_eval():
    eval('q = 1')
"""


def test_RestrictingNodeTransformer__visit_Eval__1():
    """It is an error if the code call the `eval` function."""
    result = compile_restricted_exec(EVAL_FUNCTION)
    assert result.errors == ("Line 2: Eval calls are not allowed.",)
