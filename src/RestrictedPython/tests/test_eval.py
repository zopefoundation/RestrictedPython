import pytest

from RestrictedPython.Eval import RestrictionCapableEval


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


def test_Eval__RestrictionCapableEval_1():
    """It raises SyntaxError when there are errors
    (by using forbidden stuff) in the code."""
    ob = RestrictionCapableEval("_a")
    with pytest.raises(SyntaxError):
        ob.prepRestrictedCode()


def test_Eval__RestrictionCapableEval__2():
    """It stores used names."""
    ob = RestrictionCapableEval("[x for x in (1, 2, 3)]")
    assert ob.used == ('x',)


def test_Eval__RestictionCapableEval__prepUnrestrictedCode_1():
    """It does nothing when unrestricted code is already set by init."""
    ob = RestrictionCapableEval("a")
    assert ob.used == ('a',)
    ob.expr = "b"
    ob.prepUnrestrictedCode()
    assert ob.used == ('a',)


def test_Eval__RestictionCapableEval__prepUnrestrictedCode_2():
    """It does not re-set 'used' if it is already set by an earlier call."""
    ob = RestrictionCapableEval("a")
    assert ob.used == ('a',)
    ob.used = ('b',)
    # This is needed to force re-compilation
    ob.ucode = None
    ob.prepUnrestrictedCode()
    # If it was called again, used would be ('a',) again.
    assert ob.used == ('b',)


def test_Eval__RestictionCapableEval__prepRestrictedCode_1():
    """It does nothing when restricted code is already set by
    prepRestrictedCode."""
    ob = RestrictionCapableEval("a")
    ob.prepRestrictedCode()
    assert ob.used == ('a',)
    ob.expr = "b"
    ob.prepRestrictedCode()
    assert ob.used == ('a',)


def test_Eval__RestictionCapableEval__eval_1():
    """It does not add names from the mapping to the
    global scope which are already there."""
    ob = RestrictionCapableEval("a + b + c")
    ob.globals['c'] = 8
    result = ob.eval(dict(a=1, b=2, c=4))
    assert result == 11


def test_Eval__RestictionCapableEval__eval__2():
    """It allows to use list comprehensions."""
    ob = RestrictionCapableEval("[item for item in (1, 2)]")
    result = ob.eval({})
    assert result == [1, 2]
