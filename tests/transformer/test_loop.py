from tests import e_exec

import pytest


WHILE = """\
a = 5
while a < 7:
    a = a + 3
"""


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_While__1(e_exec):
    """It allows `while` statements."""
    glb = e_exec(WHILE)
    assert glb['a'] == 8


BREAK = """\
a = 5
while True:
    a = a + 3
    if a >= 7:
        break
"""


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Break__1(e_exec):
    """It allows `break` statements."""
    glb = e_exec(BREAK)
    assert glb['a'] == 8


CONTINUE = """\
a = 3
while a < 10:
    if a < 5:
        a = a + 1
        continue
    a = a + 10
"""


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Continue__1(e_exec):
    """It allows `continue` statements."""
    glb = e_exec(CONTINUE)
    assert glb['a'] == 15
