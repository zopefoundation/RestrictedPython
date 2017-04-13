from RestrictedPython._compat import IS_PY35_OR_GREATER
from tests import c_eval
from tests import e_eval

import pytest


# Arithmetic Operators


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Add(c_eval, e_eval):
    result = c_eval('1 + 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 2
    assert e_eval('1 + 1') == 2


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Sub(c_eval, e_eval):
    result = c_eval('2 - 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 1
    assert e_eval('2 - 1') == 1


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Mult(c_eval, e_eval):
    result = c_eval('2 * 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 4
    assert e_eval('2 * 2') == 4


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Div(c_eval, e_eval):
    result = c_eval('10 / 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 5
    assert e_eval('10 / 2') == 5


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Mod(c_eval, e_eval):
    result = c_eval('10 % 3')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 1
    assert e_eval('10 % 3') == 1


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Pow(c_eval, e_eval):
    result = c_eval('2 ** 8')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 256
    assert e_eval('2 ** 8') == 256


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_FloorDiv(c_eval, e_eval):
    result = c_eval('7 // 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 3
    assert e_eval('7 // 2') == 3


@pytest.mark.skipif(
    not IS_PY35_OR_GREATER,
    reason="MatMult was introducted on Python 3.5")
@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_MatMult(c_eval, e_eval):
    result = c_eval('(8, 3, 5) @ (2, 7, 1)')
    assert result.code is None
    assert result.errors == (
        'Line None: MatMult statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}

    # TODO: Review
    # with pytest.raises(SyntaxError):
    #    e_eval('(8, 3, 5) @ (2, 7, 1)')

# Comparison Operators


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Eq(c_eval, e_eval):
    result = c_eval('1 == 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('1 == 1') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_NotEq(c_eval, e_eval):
    result = c_eval('1 != 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('1 != 2') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Gt(c_eval, e_eval):
    result = c_eval('2 > 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('2 > 1') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Lt(c_eval, e_eval):
    result = c_eval('1 < 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('1 < 2')


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_GtE(c_eval, e_eval):
    result = c_eval('2 >= 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('2 >= 2') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_LtE(c_eval, e_eval):
    result = c_eval('1 <= 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('1 <= 2') is True


# Bool Operators


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Or(c_eval, e_eval):
    result = c_eval('False or True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('False or True') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_And(c_eval, e_eval):
    result = c_eval('True and True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('True and True') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Not(c_eval, e_eval):
    result = c_eval('not False')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('not False') is True


# Bit wise Operators


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_BitAnd(c_eval, e_eval):
    result = c_eval('5 & 3')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 1
    assert e_eval('5 & 3') == 1


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_BitOr(c_eval, e_eval):
    result = c_eval('5 | 3')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 7
    assert e_eval('5 | 3') == 7


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_BitXor(c_eval, e_eval):
    result = c_eval('5 ^ 3')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 6
    assert e_eval('5 ^ 3') == 6


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Invert(c_eval, e_eval):
    result = c_eval('~17')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == -18
    assert e_eval('~17') == -18


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_LShift(c_eval, e_eval):
    result = c_eval('8 << 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 32
    assert e_eval('8 << 2') == 32


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_RShift(c_eval, e_eval):
    result = c_eval('8 >> 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 4
    assert e_eval('8 >> 1') == 4


# Logical Operators


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_In(c_eval, e_eval):
    result = c_eval('1 in [1, 2, 3]')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('1 in [1, 2, 3]') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_NotIn(c_eval, e_eval):
    result = c_eval('4 not in [1, 2, 3]')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('4 not in [1, 2, 3]') is True


# Identity Operator


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_Is(c_eval, e_eval):
    result = c_eval('True is True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('True is True') is True


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_NotIs(c_eval, e_eval):
    result = c_eval('1 is not True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True
    assert e_eval('1 is not True') is True


# Unary Operators


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_UAdd(c_eval, e_eval):
    result = c_eval('+1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 1
    assert e_eval('+1') == 1


@pytest.mark.parametrize(*c_eval)
@pytest.mark.parametrize(*e_eval)
def test_USub(c_eval, e_eval):
    result = c_eval('-1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == -1
    assert e_eval('-1') == -1
