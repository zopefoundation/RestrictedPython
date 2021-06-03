from RestrictedPython import compile_restricted_exec
from RestrictedPython._compat import IS_PY2
from RestrictedPython._compat import IS_PY3

import pytest


EXEC_STATEMENT = """\
def no_exec():
    exec 'q = 1'
"""


@pytest.mark.skipif(IS_PY3,
                    reason="exec statement no longer exists in Python 3")
def test_RestrictingNodeTransformer__visit_Exec__1():  # pragma: PY2
    """It prevents using the `exec` statement. (Python 2 only)"""
    result = compile_restricted_exec(EXEC_STATEMENT)
    assert result.errors == ('Line 2: Exec statements are not allowed.',)


EXEC_FUNCTION = """\
def no_exec():
    exec('q = 1')
"""


@pytest.mark.skipif(IS_PY2,
                    reason="exec is a statement in Python 2")
def test_RestrictingNodeTransformer__visit_Exec__2():  # pragma: PY3
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
