from RestrictedPython import compile_restricted_exec
from tests.helper import restricted_exec


lambda_err_msg = 'Line 1: "_bad" is an invalid variable ' \
                 'name because it starts with "_"'


def test_RestrictingNodeTransformer__visit_Lambda__1():
    """It prevents arguments starting with `_`."""
    result = compile_restricted_exec("lambda _bad: None")
    assert result.errors == (lambda_err_msg,)


def test_RestrictingNodeTransformer__visit_Lambda__2():
    """It prevents keyword arguments starting with `_`."""
    result = compile_restricted_exec("lambda _bad=1: None")
    assert result.errors == (lambda_err_msg,)


def test_RestrictingNodeTransformer__visit_Lambda__3():
    """It prevents * arguments starting with `_`."""
    result = compile_restricted_exec("lambda *_bad: None")
    assert result.errors == (lambda_err_msg,)


def test_RestrictingNodeTransformer__visit_Lambda__4():
    """It prevents ** arguments starting with `_`."""
    result = compile_restricted_exec("lambda **_bad: None")
    assert result.errors == (lambda_err_msg,)


def test_RestrictingNodeTransformer__visit_Lambda__7():
    """It prevents arguments starting with `_` together with a single `*`."""
    result = compile_restricted_exec("lambda good, *, _bad: None")
    assert result.errors == (lambda_err_msg,)


BAD_ARG_IN_LAMBDA = """\
def check_getattr_in_lambda(arg=lambda _bad=(lambda ob, name: name): _bad2):
    42
"""


def test_RestrictingNodeTransformer__visit_Lambda__8():
    """It prevents arguments starting with `_` in weird lambdas."""
    result = compile_restricted_exec(BAD_ARG_IN_LAMBDA)
    assert lambda_err_msg in result.errors


LAMBDA_FUNC_1 = """
g = lambda x: x ** 2
"""


def test_RestrictingNodeTransformer__visit_Lambda__10():
    """Simple lambda functions are allowed."""
    restricted_globals = dict(
        g=None,
    )
    restricted_exec(LAMBDA_FUNC_1, restricted_globals)
    assert 4 == restricted_globals['g'](2)
