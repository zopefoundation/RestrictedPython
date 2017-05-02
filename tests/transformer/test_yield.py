from RestrictedPython._compat import IS_PY3
from tests import c_exec

import pytest


YIELD_EXAMPLE = """\
def no_yield():
    yield 42
"""


@pytest.mark.parametrize(*c_exec)
def test_yield(c_exec):
    """It prevents using the `yield` statement."""
    result = c_exec(YIELD_EXAMPLE)
    assert result.errors == ("Line 2: Yield statements are not allowed.",)
    assert result.code is None


# Modified Example from http://stackabuse.com/python-async-await-tutorial/
YIELD_FORM_EXAMPLE = """
import asyncio

@asyncio.coroutine
def get_json(client, url):
    file_content = yield from load_file('data.ini')
"""


@pytest.mark.skipif(
    not IS_PY3,
    reason="`yield from` statement was first introduced in Python 3.3")
@pytest.mark.parametrize(*c_exec)
def test_yield_from(c_exec):
    result = c_exec(YIELD_FORM_EXAMPLE)
    assert result.errors == ('Line 6: YieldFrom statements are not allowed.',)
    assert result.code is None
