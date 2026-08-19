import pytest

from RestrictedPython import compile_restricted_exec
from RestrictedPython._compat import IS_PY315_OR_GREATER


lazy_import_errmsg = 'Line 1: Lazy import statements are not allowed.'


@pytest.mark.skipif(
    not IS_PY315_OR_GREATER,
    reason="lazy imports were added in Python 3.15.",
)
def test_RestrictingNodeTransformer__visit_Import__lazy():
    """It denies lazy importing a module."""
    result = compile_restricted_exec('lazy import a')
    assert result.errors == (lazy_import_errmsg,)


@pytest.mark.skipif(
    not IS_PY315_OR_GREATER,
    reason="lazy imports were added in Python 3.15.",
)
def test_RestrictingNodeTransformer__visit_ImportFrom__lazy():
    """It denies lazy importing from a module."""
    result = compile_restricted_exec('lazy from a import m')
    assert result.errors == (lazy_import_errmsg,)
