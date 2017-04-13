from RestrictedPython._compat import IS_PY3
from tests import c_exec

import pytest


# Modified Example from http://stackabuse.com/python-async-await-tutorial/
YIELD_FORM_EXAMPLE = """
import asyncio

@asyncio.coroutine
def get_json(client, url):
    file_content = yield from load_file('data.ini')
"""


@pytest.mark.skipif(
    not IS_PY3,
    reason="yield from statement was first introduced in Python 3.3")
@pytest.mark.parametrize(*c_exec)
def test_yield_from(c_exec):
    result = c_exec(YIELD_FORM_EXAMPLE)
    assert result.code is None
    assert result.errors == (
        'Line 6: YieldFrom statements are not allowed.',
    )
    assert result.warnings == []
    assert result.used_names == {
        'asyncio': True,
    }
