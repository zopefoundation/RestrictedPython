from tests import e_exec

import pytest


@pytest.mark.parametrize(*e_exec)
def test_RestrictingNodeTransformer__visit_Assert__1(e_exec):
    """It allows assert statements."""
    e_exec('assert 1')
