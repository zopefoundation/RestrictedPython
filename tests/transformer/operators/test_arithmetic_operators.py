from RestrictedPython import compile_restricted_eval
from tests.helper import restricted_eval


# Arithmetic Operators

def test_Add():
    assert restricted_eval('1 + 1') == 2


def test_Sub():
    assert restricted_eval('5 - 3') == 2


def test_Mult():
    assert restricted_eval('2 * 2') == 4


def test_Div():
    assert restricted_eval('10 / 2') == 5


def test_Mod():
    assert restricted_eval('10 % 3') == 1


def test_Pow():
    assert restricted_eval('2 ** 8') == 256


def test_FloorDiv():
    assert restricted_eval('7 // 2') == 3


def test_MatMult():
    result = compile_restricted_eval('(8, 3, 5) @ (2, 7, 1)')
    assert result.errors == (
        'Line None: MatMult statements are not allowed.',
    )
    assert result.code is None
