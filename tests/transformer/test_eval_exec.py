from RestrictedPython._compat import IS_PY2
from RestrictedPython._compat import IS_PY3
from tests import c_exec

import pytest
import RestrictedPython


EXEC_STATEMENT = """\
def no_exec():
    exec 'q = 1'
"""


@pytest.mark.skipif(IS_PY3,
                    reason="exec statement no longer exists in Python 3")
@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Exec__1(c_exec):
    """It prevents using the `exec` statement. (Python 2 only)"""
    result = c_exec(EXEC_STATEMENT)
    assert result.errors == ('Line 2: Exec statements are not allowed.',)


EXEC_FUNCTION = """\
def no_exec():
    exec('q = 1')
"""


@pytest.mark.skipif(IS_PY2,
                    reason="exec is a statement in Python 2")
@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Exec__2(c_exec):
    """It is an error if the code call the `exec` function."""
    result = c_exec(EXEC_FUNCTION)
    assert result.errors == ("Line 2: Exec calls are not allowed.",)


EVAL_FUNCTION = """\
def no_eval():
    eval('q = 1')
"""


@pytest.mark.parametrize(*c_exec)
def test_RestrictingNodeTransformer__visit_Eval__1(c_exec):
    """It is an error if the code call the `eval` function."""
    result = c_exec(EVAL_FUNCTION)
    if c_exec is RestrictedPython.compile.compile_restricted_exec:
        assert result.errors == ("Line 2: Eval calls are not allowed.",)
    else:
        # `eval()` is allowed in the old implementation. :-(
        assert result.errors == ()
