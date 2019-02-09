from tests.helper import restricted_eval


def test_BitAnd():
    assert restricted_eval('5 & 3') == 1


def test_BitOr():
    assert restricted_eval('5 | 3') == 7


def test_BitXor():
    assert restricted_eval('5 ^ 3') == 6


def test_Invert():
    assert restricted_eval('~17') == -18


def test_LShift():
    assert restricted_eval('8 << 2') == 32


def test_RShift():
    assert restricted_eval('8 >> 1') == 4
