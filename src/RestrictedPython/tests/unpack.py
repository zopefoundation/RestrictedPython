# A series of short tests for unpacking sequences.


def u1(L):
    x, y = L
    assert x == 1
    assert y == 2

u1([1, 2])
u1((1, 2))


def u1a(L):
    x, y = L
    assert x == '1'
    assert y == '2'

u1a("12")

try:
    u1([1])
except ValueError:
    pass
else:
    raise AssertionError("expected 'unpack list of wrong size'")


def u2(L):
    x, (a, b), y = L
    assert x == 1
    assert a == 2
    assert b == 3
    assert y == 4

u2([1, [2, 3], 4])
u2((1, (2, 3), 4))

try:
    u2([1, 2, 3])
except TypeError:
    pass
else:
    raise AssertionError("expected 'iteration over non-sequence'")


def u3((x, y)):
    assert x == 'a'
    assert y == 'b'
    return x, y

u3(('a', 'b'))


def u4(x):
    (a, b), c = d, (e, f) = x
    assert a == 1 and b == 2 and c == (3, 4)
    assert d == (1, 2) and e == 3 and f == 4


u4(((1, 2), (3, 4)))


def u5(x):
    try:
        raise TypeError(x)
    # This one is tricky to test, because the first level of unpacking
    # has a TypeError instance.  That's a headache for the test driver.
    except TypeError, [(a, b)]:
        assert a == 42
        assert b == 666

u5([42, 666])


def u6(x):
    expected = 0
    for i, j in x:
        assert i == expected
        expected += 1
        assert j == expected
        expected += 1

u6([[0, 1], [2, 3], [4, 5]])


def u7(x):
    stuff = [i + j for toplevel, in x for i, j in toplevel]
    assert stuff == [3, 7]


u7(([[[1, 2]]], [[[3, 4]]]))
