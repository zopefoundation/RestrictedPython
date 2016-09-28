from RestrictedPython import compile_restricted
from RestrictedPython import compile_restricted_exec
from RestrictedPython import compile_restricted_eval
#from RestrictedPython import compile_restricted_single
from RestrictedPython import compile_restricted_function

import pytest
import sys


YIELD = """\
def no_yield():
    yield 42
"""


def test_transformer__RestrictingNodeTransformer__generic_visit__1():
    """It compiles a number successfully."""
    code, errors, warnings, used_names = compile_restricted_exec('42', '<undefined>')
    assert 'code' == str(code.__class__.__name__)


def test_transformer__RestrictingNodeTransformer__generic_visit__2():
    """It compiles a function call successfully."""
    code, errors, warnings, used_names = compile_restricted_exec('max([1, 2, 3])', '<undefined>')
    assert 'code' == str(code.__class__.__name__)


def test_transformer__RestrictingNodeTransformer__generic_visit__100():
    """It raises a SyntaxError if the code contains a `yield`."""
    code, errors, warnings, used_names = compile_restricted_exec(YIELD, '<undefined>')
    assert "Line 2: Yield statements are not allowed." in errors
    #with pytest.raises(SyntaxError) as err:
    #    code, errors, warnings, used_names = compile_restricted_exec(YIELD, '<undefined>')
    #assert "Line 2: Yield statements are not allowed." == str(err.value)


EXEC_FUNCTION = """\
def no_exec():
    exec('q = 1')
"""


def test_transformer__RestrictingNodeTransformer__generic_visit__101():
    """It raises a SyntaxError if the code contains an `exec` function."""
    code, errors, warnings, used_names = compile_restricted_exec(EXEC_FUNCTION, '<undefined>')
    assert "Line 2: Exec statements are not allowed." in errors


EXEC_STATEMENT = """\
def no_exec():
    exec 'q = 1'
"""


@pytest.mark.skipif(sys.version_info > (3,),
                    reason="exec statement no longer exists in Python 3")
def test_transformer__RestrictingNodeTransformer__generic_visit__102():
    """It raises a SyntaxError if the code contains an `exec` statement."""
    code, errors, warnings, used_names = compile_restricted_exec(EXEC_STATEMENT, '<undefined>')
    assert "Line 2: Exec statements are not allowed." in errors


@pytest.mark.skipif(sys.version_info < (3,),
                    reason="exec statement no longer exists in Python 3")
def test_transformer__RestrictingNodeTransformer__generic_visit__103():
    """It raises a SyntaxError if the code contains an `exec` statement."""
    code, errors, warnings, used_names = compile_restricted_exec(EXEC_STATEMENT, '<undefined>')
    assert "Missing parentheses in call to 'exec' (<undefined>, line 2)" in errors


BAD_NAME = """\
def bad_name():
    __ = 12
"""


def test_transformer__RestrictingNodeTransformer__generic_visit__104():
    """It raises a SyntaxError if a bad name is used."""
    code, errors, warnings, used_names = compile_restricted_exec(BAD_NAME, '<undefined>')
    assert 'Line 2: "__" is an invalid variable name because it starts with "_"' in errors


BAD_ATTR = """\
def bad_attr():
    some_ob._some_attr = 15
"""


def test_transformer__RestrictingNodeTransformer__generic_visit__105():
    """It raises a SyntaxError if a bad attribute name is used."""
    code, errors, warnings, used_names = compile_restricted_exec(BAD_ATTR, '<undefined>')
    assert 'Line 2: "_some_attr" is an invalid attribute name because it starts with "_".' in errors
