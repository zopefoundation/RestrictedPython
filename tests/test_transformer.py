from RestrictedPython import compile_restricted
import pytest
import sys


YIELD = """\
def no_yield():
    yield 42
"""


def test_transformer__RestrictingNodeTransformer__generic_visit__1():
    """It compiles a number successfully."""
    code = compile_restricted('42', '<undefined>', 'exec')
    assert 'code' == str(code.__class__.__name__)


def test_transformer__RestrictingNodeTransformer__generic_visit__2():
    """It compiles a function call successfully."""
    code = compile_restricted('max([1, 2, 3])', '<undefined>', 'exec')
    assert 'code' == str(code.__class__.__name__)


def test_transformer__RestrictingNodeTransformer__generic_visit__100():
    """It raises a SyntaxError if the code contains a `yield`."""
    with pytest.raises(SyntaxError) as err:
        compile_restricted(YIELD, '<undefined>', 'exec')
    assert "Line 2: Yield statements are not allowed." == str(err.value)


EXEC_FUNCTION = """\
def no_exec():
    exec('q = 1')
"""


def test_transformer__RestrictingNodeTransformer__generic_visit__101():
    """It raises a SyntaxError if the code contains an `exec` function."""
    with pytest.raises(SyntaxError) as err:
        compile_restricted(EXEC_FUNCTION, '<undefined>', 'exec')
    assert "Line 2: Exec statements are not allowed." == str(err.value)


EXEC_STATEMENT = """\
def no_exec():
    exec 'q = 1'
"""


@pytest.mark.skipif(sys.version_info > (3,),
                    reason="exec statement no longer exists in Python 3")
def test_transformer__RestrictingNodeTransformer__generic_visit__102():
    """It raises a SyntaxError if the code contains an `exec` statement."""
    with pytest.raises(SyntaxError) as err:
        compile_restricted(EXEC_STATEMENT, '<undefined>', 'exec')
    assert "Line 2: Exec statements are not allowed." == str(err.value)


@pytest.mark.skipif(sys.version_info < (3,),
                    reason="exec statement no longer exists in Python 3")
def test_transformer__RestrictingNodeTransformer__generic_visit__103():
    """It raises a SyntaxError if the code contains an `exec` statement."""
    with pytest.raises(SyntaxError) as err:
        compile_restricted(EXEC_STATEMENT, '<undefined>', 'exec')
    assert ("Missing parentheses in call to 'exec' (<undefined>, line 2)" ==
            str(err.value))


BAD_NAME = """\
def bad_name():
    __ = 12
"""


def test_transformer__RestrictingNodeTransformer__generic_visit__104():
    """It raises a SyntaxError if a bad name is used."""
    with pytest.raises(SyntaxError) as err:
        compile_restricted(BAD_NAME, '<undefined>', 'exec')
    assert ('Line 2: "__" is an invalid variable name because it starts with "_"' ==
            str(err.value))


BAD_ATTR = """\
def bad_attr():
    some_ob._some_attr = 15
"""


def test_transformer__RestrictingNodeTransformer__generic_visit__105():
    """It raises a SyntaxError if a bad attribute name is used."""
    with pytest.raises(SyntaxError) as err:
        compile_restricted(BAD_ATTR, '<undefined>', 'exec')
    assert ('Line 2: "_some_attr" is an invalid attribute name because it starts with "_".' ==
            str(err.value))
