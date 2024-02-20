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
    class Vector:
        def __init__(self, values):
            self.values = values

        def __matmul__(self, other):
            return sum(x * y for x, y in zip(self.values, other.values))

    assert restricted_eval(
        'Vector((8, 3, 5)) @ Vector((2, 7, 1))', {'Vector': Vector}) == 42
