from tests.helper import restricted_exec


WHILE = """\
a = 5
while a < 7:
    a = a + 3
"""


def test_RestrictingNodeTransformer__visit_While__1():
    """It allows `while` statements."""
    glb = restricted_exec(WHILE)
    assert glb['a'] == 8


BREAK = """\
a = 5
while True:
    a = a + 3
    if a >= 7:
        break
"""


def test_RestrictingNodeTransformer__visit_Break__1():
    """It allows `break` statements."""
    glb = restricted_exec(BREAK)
    assert glb['a'] == 8


CONTINUE = """\
a = 3
while a < 10:
    if a < 5:
        a = a + 1
        continue
    a = a + 10
"""


def test_RestrictingNodeTransformer__visit_Continue__1():
    """It allows `continue` statements."""
    glb = restricted_exec(CONTINUE)
    assert glb['a'] == 15
