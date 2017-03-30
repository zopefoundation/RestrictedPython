from RestrictedPython._compat import IS_PY35_OR_GREATER
from tests import c_eval

import pytest


# Arithmetic Operators


@pytest.mark.parametrize(*c_eval)
def test_Add(c_eval):
    result = c_eval('1 + 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 2


@pytest.mark.parametrize(*c_eval)
def test_Sub(c_eval):
    result = c_eval('2 - 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 1


@pytest.mark.parametrize(*c_eval)
def test_Mult(c_eval):
    result = c_eval('2 * 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 4


@pytest.mark.parametrize(*c_eval)
def test_Div(c_eval):
    result = c_eval('10 / 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 5


@pytest.mark.parametrize(*c_eval)
def test_Mod(c_eval):
    result = c_eval('10 % 2')
    assert result.code is None
    assert result.errors == (
        'Line None: Mod statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}


@pytest.mark.parametrize(*c_eval)
def test_Pow(c_eval):
    result = c_eval('2 ** 8')
    assert result.code is None
    assert result.errors == (
        'Line None: Pow statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}


@pytest.mark.parametrize(*c_eval)
def test_FloorDiv(c_eval):
    result = c_eval('8 // 2')
    assert result.code is None
    assert result.errors == (
        'Line None: FloorDiv statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}


@pytest.mark.skipif(
    not IS_PY35_OR_GREATER,
    reason="MatMult was introducted on Python 3.5")
@pytest.mark.parametrize(*c_eval)
def test_MatMult(c_eval):
    result = c_eval('(8, 3, 5) @ (2, 7, 1)')
    assert result.code is None
    assert result.errors == (
        'Line None: MatMult statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}

# Comparison Operators


@pytest.mark.parametrize(*c_eval)
def test_Eq(c_eval):
    result = c_eval('1 == 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


@pytest.mark.parametrize(*c_eval)
def test_NotEq(c_eval):
    result = c_eval('1 != 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


@pytest.mark.parametrize(*c_eval)
def test_Gt(c_eval):
    result = c_eval('2 > 1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


@pytest.mark.parametrize(*c_eval)
def test_Lt(c_eval):
    result = c_eval('1 < 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


@pytest.mark.parametrize(*c_eval)
def test_GtE(c_eval):
    result = c_eval('2 >= 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


@pytest.mark.parametrize(*c_eval)
def test_LtE(c_eval):
    result = c_eval('1 <= 2')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


# Bool Operators


@pytest.mark.parametrize(*c_eval)
def test_Or(c_eval):
    result = c_eval('False or True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


@pytest.mark.parametrize(*c_eval)
def test_And(c_eval):
    result = c_eval('True and True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


@pytest.mark.parametrize(*c_eval)
def test_Not(c_eval):
    result = c_eval('not False')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


# Bit wise Operators


@pytest.mark.parametrize(*c_eval)
def test_BitAnd(c_eval):
    result = c_eval('60 & 13')
    assert result.code is None
    assert result.errors == (
        'Line None: BitAnd statements are not allowed.',)
    assert result.warnings == []
    assert result.used_names == {}


@pytest.mark.parametrize(*c_eval)
def test_BitOr(c_eval):
    result = c_eval('60 | 13')
    assert result.code is None
    assert result.errors == (
        'Line None: BitOr statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}


@pytest.mark.parametrize(*c_eval)
def test_BitXor(c_eval):
    result = c_eval('60 ^ 13')
    assert result.code is None
    assert result.errors == (
        'Line None: BitXor statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}


@pytest.mark.parametrize(*c_eval)
def test_Invert(c_eval):
    result = c_eval('~60')
    assert result.code is None
    assert result.errors == (
        'Line None: Invert statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}


@pytest.mark.parametrize(*c_eval)
def test_LShift(c_eval):
    result = c_eval('60 << 2')
    assert result.code is None
    assert result.errors == (
        'Line None: LShift statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}


@pytest.mark.parametrize(*c_eval)
def test_RShift(c_eval):
    result = c_eval('60 >> 2')
    assert result.code is None
    assert result.errors == (
        'Line None: RShift statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {}


# Logical Operators


@pytest.mark.parametrize(*c_eval)
def test_In(c_eval):
    result = c_eval('1 in [1, 2, 3]')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


@pytest.mark.parametrize(*c_eval)
def test_NotIn(c_eval):
    result = c_eval('4 not in [1, 2, 3]')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


# Identity Operator


@pytest.mark.parametrize(*c_eval)
def test_Is(c_eval):
    result = c_eval('True is True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


@pytest.mark.parametrize(*c_eval)
def test_NotIs(c_eval):
    result = c_eval('1 is not True')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result is True


# Unary Operators


@pytest.mark.parametrize(*c_eval)
def test_UAdd(c_eval):
    result = c_eval('+1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == 1


@pytest.mark.parametrize(*c_eval)
def test_USub(c_eval):
    result = c_eval('-1')
    assert result.code is not None
    assert result.errors == ()
    assert result.warnings == []
    # assert result.used_names == {}

    eval_result = eval(result.code)
    assert eval_result == -1
