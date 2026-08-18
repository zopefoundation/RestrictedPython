import pytest

from RestrictedPython import compile_restricted_exec
from RestrictedPython._compat import IS_PY315_OR_GREATER
from RestrictedPython.Eval import default_guarded_getiter
from tests.helper import restricted_eval


unpacking_errmsg = 'Line 1: Unpacking in comprehensions is not allowed.'


@pytest.mark.skipif(
    not IS_PY315_OR_GREATER,
    reason="unpacking in comprehensions was added in Python 3.15.",
)
def test_RestrictingNodeTransformer__visit_ListComp__unpacking():
    """It denies `*` unpacking in a list comprehension."""
    result = compile_restricted_exec('[*x for x in seq]')
    assert result.errors == (unpacking_errmsg,)


@pytest.mark.skipif(
    not IS_PY315_OR_GREATER,
    reason="unpacking in comprehensions was added in Python 3.15.",
)
def test_RestrictingNodeTransformer__visit_SetComp__unpacking():
    """It denies `*` unpacking in a set comprehension."""
    result = compile_restricted_exec('{*x for x in seq}')
    assert result.errors == (unpacking_errmsg,)


@pytest.mark.skipif(
    not IS_PY315_OR_GREATER,
    reason="unpacking in comprehensions was added in Python 3.15.",
)
def test_RestrictingNodeTransformer__visit_GeneratorExp__unpacking():
    """It denies `*` unpacking in a generator expression."""
    result = compile_restricted_exec('(*x for x in seq)')
    assert result.errors == (unpacking_errmsg,)


@pytest.mark.skipif(
    not IS_PY315_OR_GREATER,
    reason="unpacking in comprehensions was added in Python 3.15.",
)
def test_RestrictingNodeTransformer__visit_DictComp__unpacking():
    """It denies `**` unpacking in a dict comprehension."""
    result = compile_restricted_exec('{**x for x in seq}')
    assert result.errors == (unpacking_errmsg,)


def test_RestrictingNodeTransformer__visit_ListComp__no_unpacking():
    """It still allows list comprehensions without unpacking."""
    glb = {'_getiter_': default_guarded_getiter}
    assert restricted_eval('[x for x in (1, 2)]', glb) == [1, 2]


def test_RestrictingNodeTransformer__visit_DictComp__no_unpacking():
    """It still allows dict comprehensions without unpacking."""
    glb = {'_getiter_': default_guarded_getiter}
    assert restricted_eval('{x: x for x in (1, 2)}', glb) == {1: 1, 2: 2}


def test_RestrictingNodeTransformer__visit_List__unpacking():
    """It still allows `*` unpacking in a list display."""
    assert restricted_eval('[*(1, 2), 3]') == [1, 2, 3]
