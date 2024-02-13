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
    source_code = """
class Vector:
    def __init__(self, values):
        self.values = values

    def __matmul__(self, other):
        return sum(x * y for x, y in zip(self.values, other.values))

result = Vector((8, 3, 5)) @ Vector((2, 7, 1))
"""
    # Assuming restricted_eval can execute the source_code and return the value of 'result'
    assert restricted_eval(source_code) == 42
    
