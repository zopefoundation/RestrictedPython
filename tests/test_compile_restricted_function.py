from RestrictedPython import safe_builtins
from RestrictedPython import PrintCollector
from tests import c_function
import operator

import pytest

from types import FunctionType


@pytest.mark.parametrize(*c_function)
def test_compile_restricted_function(c_function):
    p = ''
    body = """
print("Hello World!")
return printed
"""
    name = "hello_world"
    global_symbols = []

    result = c_function(
        p,  # parameters
        body,
        name,
        filename='<string>',
        globalize=global_symbols
    )

    assert result.code is not None
    assert result.errors == ()
    # import pdb; pdb.set_trace()
    safe_globals = {'__name__': 'script', '_getattr_': getattr, '_print_': PrintCollector}
    safe_globals.update(safe_builtins)
    safe_locals = {}
    exec(result.code, safe_globals, safe_locals)
    hello_world = safe_locals['hello_world']
    assert type(hello_world) == FunctionType
    assert hello_world() == 'Hello World!\n'


@pytest.mark.parametrize(*c_function)
def test_compile_restricted_function_func_wrapped(c_function):
    p = ''
    body = """
print("Hello World!")
return printed
"""
    name = "hello_world"
    global_symbols = []

    result = c_function(
        p,  # parameters
        body,
        name,
        filename='<string>',
        globalize=global_symbols
    )

    assert result.code is not None
    assert result.errors == ()
    safe_globals = {
        '__name__': 'script',
        '_getattr_': getattr,
        '_print_': PrintCollector,
    }
    safe_globals.update(safe_builtins)

    func = FunctionType(result.code, safe_globals)
    func()
    assert 'hello_world' in safe_globals
    hello_world = safe_globals['hello_world']
    assert hello_world() == 'Hello World!\n'


@pytest.mark.parametrize(*c_function)
def test_compile_restricted_function_with_arguments(c_function):
    p = 'input'
    body = """
print(input)
return printed
"""
    name = "hello_world"
    global_symbols = []

    result = c_function(
        p,  # parameters
        body,
        name,
        filename='<string>',
        globalize=global_symbols
    )

    assert result.code is not None
    assert result.errors == ()

    safe_globals = {'__name__': 'script', '_getattr_': getattr, '_print_': PrintCollector}
    safe_globals.update(safe_builtins)
    safe_locals = {}
    exec(result.code, safe_globals, safe_locals)
    hello_world = safe_locals['hello_world']
    assert type(hello_world) == FunctionType
    assert hello_world('Hello World!') == 'Hello World!\n'

@pytest.mark.parametrize(*c_function)
def test_compile_restricted_function_with_global_variables(c_function):
    p = ''
    body = """
print(input)
return printed
"""
    name = "hello_world"
    global_symbols = ['input']

    result = c_function(
        p,  # parameters
        body,
        name,
        filename='<string>',
        globalize=global_symbols
    )

    assert result.code is not None
    assert result.errors == ()

    safe_globals = {
        '__name__': 'script',
        '_getattr_': getattr,
        'input': 'Hello World!',
        '_print_': PrintCollector
    }
    safe_globals.update(safe_builtins)
    safe_locals = {}
    exec(result.code, safe_globals, safe_locals)
    hello_world = safe_locals['hello_world']
    assert type(hello_world) == FunctionType
    assert hello_world() == 'Hello World!\n'
