from RestrictedPython.compiler import compile_restricted
import pytest


YIELD = """\
def no_yield():
    yield 42
"""


def test_transformer__RestrictingNodeTransformer__generic_visit__1():
    """It raises a SyntaxError if the code contains a `yield`."""
    with pytest.raises(SyntaxError) as err:
        compile_restricted(YIELD, '<undefined>', 'exec')
    assert "Node 'Yield' not allowed." == str(err.value)


def test_transformer__RestrictingNodeTransformer__generic_visit__2():
    """It compiles a number successfully."""
    code = compile_restricted('42', '<undefined>', 'exec')
    assert 'code' == str(code.__class__.__name__)
