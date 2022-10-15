from RestrictedPython import compile_restricted_exec


YIELD_EXAMPLE = """\
def test_generator():
    yield 42
"""


def test_yield():
    """`yield` statement should be allowed."""
    result = compile_restricted_exec(YIELD_EXAMPLE)
    assert result.errors == ()
    assert result.code is not None
    local = {}
    exec(result.code, {}, local)
    test_generator = local['test_generator']
    exec_result = list(test_generator())
    assert exec_result == [42]


YIELD_FORM_EXAMPLE = """
def reader_wapper(input):
    yield from input
"""


def test_yield_from():
    """`yield from` statement should be allowed."""
    result = compile_restricted_exec(YIELD_FORM_EXAMPLE)
    assert result.errors == ()
    assert result.code is not None

    def my_external_generator():
        my_list = [1, 2, 3, 4, 5]
        yield from my_list

    local = {}
    exec(result.code, {}, local)
    reader_wapper = local['reader_wapper']
    exec_result = list(reader_wapper(my_external_generator()))
    assert exec_result == [1, 2, 3, 4, 5]


# Modified Example from http://stackabuse.com/python-async-await-tutorial/
ASYNCIO_YIELD_FORM_EXAMPLE = """
import asyncio

@asyncio.coroutine
def get_json(client, url):
    file_content = yield from load_file('data.ini')
"""


def test_asyncio_yield_from():
    """`yield from` statement should be allowed."""
    result = compile_restricted_exec(ASYNCIO_YIELD_FORM_EXAMPLE)
    assert result.errors == ()
    assert result.code is not None


ASYNC_YIELD_FORM_EXAMPLE = """
import asyncio

async def get_json(client, url):
    file_content = yield from load_file('data.ini')
"""


def test_async_yield_from():
    """`yield from` statement should be allowed."""
    result = compile_restricted_exec(ASYNC_YIELD_FORM_EXAMPLE)
    assert result.errors == (
        'Line 4: AsyncFunctionDef statements are not allowed.',
    )
    assert result.code is None
