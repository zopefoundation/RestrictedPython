from RestrictedPython import compile_restricted_exec
from RestrictedPython.transformer import RestrictingNodeTransformer


# Example from https://docs.python.org/3/library/asyncio-task.html
ASYNC_DEF_EXMAPLE = """
import asyncio

async def hello_world():
    print()

loop = asyncio.get_event_loop()
# Blocking call which returns when the hello_world() coroutine is done
loop.run_until_complete(hello_world())
loop.close()
"""


def test_async_def():
    result = compile_restricted_exec(ASYNC_DEF_EXMAPLE)
    assert result.errors == (
        'Line 4: AsyncFunctionDef statements are not allowed.',
    )
    assert result.code is None


class RestrictingAsyncNodeTransformer(RestrictingNodeTransformer):
    """Transformer which allows `async def` for the tests."""

    def visit_AsyncFunctionDef(self, node):
        """Allow `async def`.

        This is needed to get the function body to be parsed thus allowing
        to catch `await`, `async for` and `async with`.
        """
        return self.node_contents_visit(node)


# Modified example from https://docs.python.org/3/library/asyncio-task.html
AWAIT_EXAMPLE = """
import asyncio
import datetime

async def display_date(loop):
    end_time = loop.time() + 5.0
    while True:
        print(datetime.datetime.now())
        if (loop.time() + 1.0) >= end_time:
            break
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
# Blocking call which returns when the display_date() coroutine is done
loop.run_until_complete(display_date(loop))
loop.close()
"""


def test_await():
    result = compile_restricted_exec(
        AWAIT_EXAMPLE,
        policy=RestrictingAsyncNodeTransformer)
    assert result.errors == ('Line 11: Await statements are not allowed.',)
    assert result.code is None


# Modified example https://www.python.org/dev/peps/pep-0525/
ASYNC_WITH_EXAMPLE = """
async def square_series(con, to):
    async with con.transaction():
        print(con)
"""


def test_async_with():
    result = compile_restricted_exec(
        ASYNC_WITH_EXAMPLE,
        policy=RestrictingAsyncNodeTransformer)
    assert result.errors == ('Line 3: AsyncWith statements are not allowed.',)
    assert result.code is None


# Modified example https://www.python.org/dev/peps/pep-0525/
ASYNC_FOR_EXAMPLE = """
async def read_rows(rows):
    async for row in rows:
        yield row
"""


def test_async_for():
    result = compile_restricted_exec(
        ASYNC_FOR_EXAMPLE,
        policy=RestrictingAsyncNodeTransformer)
    assert result.errors == ('Line 3: AsyncFor statements are not allowed.',)
    assert result.code is None
