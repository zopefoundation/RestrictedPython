from RestrictedPython.Eval import RestrictionCapableEval

import pytest


exp = """
    {'a':[m.pop()]}['a'] \
        + [m[0]]
"""


def test_init():
    ob = RestrictionCapableEval(exp)

    assert ob.expr == "{'a':[m.pop()]}['a']         + [m[0]]"
    assert ob.used == ('m', )
    assert ob.ucode is not None
    assert ob.rcode is None


def test_init_with_syntax_error():
    with pytest.raises(SyntaxError):
        RestrictionCapableEval("if:")


def test_prepRestrictedCode():
    ob = RestrictionCapableEval(exp)
    ob.prepRestrictedCode()
    assert ob.used == ('m', )
    assert ob.rcode is not None


def test_call():
    ob = RestrictionCapableEval(exp)
    ret = ob(m=[1, 2])
    assert ret == [2, 1]


def test_eval():
    ob = RestrictionCapableEval(exp)
    ret = ob.eval({'m': [1, 2]})
    assert ret == [2, 1]
