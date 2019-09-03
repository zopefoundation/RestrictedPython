from RestrictedPython import compile_restricted_exec
from RestrictedPython._compat import IS_PY38_OR_GREATER
from RestrictedPython.PrintCollector import PrintCollector

import pytest


AssignmentExpressionExample = """
a = range(15)
if (n := len(a)) > 10:
    print(f"List is too long ({n} elements, expected <= 10)")
"""


@pytest.mark.skipif(
    not IS_PY38_OR_GREATER,
    reason="AssignmentExpression (Walrus-Operator) added in Python 3.6.",
)
def test_RestrictingNodeTransformer__visit_AssignmentExpression__1():
    """Checks if the Walrus-Operator is checked."""
    result = compile_restricted_exec(AssignmentExpressionExample)
    assert result.errors == ()

    glb = {'_print_': PrintCollector, '_getattr_': None}
    exec(result.code, glb)
    assert glb['_print']() == "List is too long (15 elements, expected <= 10)\n"  # NOQA: E501
