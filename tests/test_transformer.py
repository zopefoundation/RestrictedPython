import sys

import pytest

import RestrictedPython

# Define the arguments for @pytest.mark.parametrize to be able to test both the
# old and the new implementation to be equal:
compile = ('compile', [RestrictedPython.compile])
if sys.version_info < (3,):
    from RestrictedPython import RCompile
    compile[1].append(RCompile)


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__1(compile):
    """It compiles a number successfully."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        '42', '<undefined>')
    assert 'code' == str(code.__class__.__name__)
    assert errors == ()
    assert warnings == []
    assert used_names == {}


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__2(compile):
    """It compiles a function call successfully and returns the used name."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        'max([1, 2, 3])', '<undefined>')
    assert errors == ()
    assert warnings == []
    assert 'code' == str(code.__class__.__name__)
    if compile is RestrictedPython.compile:
        # The new version not yet supports `used_names`:
        assert used_names == {}
    else:
        assert used_names == {'max': True}


YIELD = """\
def no_yield():
    yield 42
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__100(compile):
    """It is an error if the code contains a `yield` statement."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        YIELD, '<undefined>')
    assert ("Line 2: Yield statements are not allowed.",) == errors
    assert warnings == []
    assert used_names == {}


EXEC_STATEMENT = """\
def no_exec():
    exec 'q = 1'
"""


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="exec statement no longer exists in Python 3")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__102(compile):
    """It raises a SyntaxError if the code contains an `exec` statement."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        EXEC_STATEMENT, '<undefined>')
    assert ('Line 2: Exec statements are not allowed.',) == errors


@pytest.mark.skipif(
    sys.version_info < (3, 0),
    reason="exec statement in Python 3 raises SyntaxError itself")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__generic_visit__103(compile):
    """It is an error if the code contains an `exec` statement."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        EXEC_STATEMENT, '<undefined>')
    assert (
        "Line 2: SyntaxError: Missing parentheses in call to 'exec' in on "
        "statement: exec 'q = 1'",) == errors


BAD_NAME = """\
def bad_name():
    __ = 12
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Name__1(compile):
    """It is an error if a bad variable name is used."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        BAD_NAME, '<undefined>')
    assert ('Line 2: "__" is an invalid variable name because it starts with '
            '"_"',) == errors


BAD_ATTR = """\
def bad_attr():
    some_ob = object()
    some_ob._some_attr = 15
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Attribute__1(compile):
    """It is an error if a bad attribute name is used."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        BAD_ATTR, '<undefined>')
    assert ('Line 3: "_some_attr" is an invalid attribute name because it '
            'starts with "_".',) == errors


EXEC_FUNCTION = """\
def no_exec():
    exec('q = 1')
"""


@pytest.mark.skipif(sys.version_info < (3, 0),
                    reason="exec is a statement in Python 2")
@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Call__1(compile):
    """It is an error if the code call the `exec` function."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        EXEC_FUNCTION, '<undefined>')
    assert ("Line 2: Exec calls are not allowed.",) == errors


EVAL_FUNCTION = """\
def no_eval():
    eval('q = 1')
"""


@pytest.mark.parametrize(*compile)
def test_transformer__RestrictingNodeTransformer__visit_Call__2(compile):
    """It is an error if the code call the `eval` function."""
    code, errors, warnings, used_names = compile.compile_restricted_exec(
        EVAL_FUNCTION, '<undefined>')
    if compile is RestrictedPython.compile:
        assert ("Line 2: Eval calls are not allowed.",) == errors
    else:
        # `eval()` is allowed in the old implementation.
        assert () == errors
