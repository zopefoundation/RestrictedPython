from RestrictedPython.RCompile import compile_restricted_function
from RestrictedPython import safe_builtins
from RestrictedPython import PrintCollector

import pytest

from types import FunctionType

def test_compile_restricted_function():
    p = ''
    body = """
print("Hello World!")
return printed
"""
    name = "hello_world"
    global_symbols = ['container', 'script']

    result = compile_restricted_function(
        p,  # parameters
        body,
        name,
        filename='<string>',
        globalize=global_symbols
    )

    assert result.code is not None
    assert result.errors == ()
    # import pdb; pdb.set_trace()
    safe_globals = {'__name__': 'script', '_print_': PrintCollector}
    safe_globals.update(safe_builtins)
    safe_locals = {}
    exec(result.code, safe_globals, safe_locals)
    hello_world = safe_locals['hello_world']
    assert type(hello_world) == FunctionType
    assert hello_world() == 'Hello World!\n'


def test_compile_restricted_function_with_arguments():
    p = 'input'
    body = """
print(input)
return printed
"""
    name = "hello_world"
    global_symbols = ['container', 'script']

    result = compile_restricted_function(
        p,  # parameters
        body,
        name,
        filename='<string>',
        globalize=global_symbols
    )

    assert result.code is not None
    assert result.errors == ()
    # import pdb; pdb.set_trace()
    safe_globals = {'__name__': 'script', '_print_': PrintCollector}
    safe_globals.update(safe_builtins)
    safe_locals = {}
    exec(result.code, safe_globals, safe_locals)
    hello_world = safe_locals['hello_world']
    assert type(hello_world) == FunctionType
    assert hello_world('Hello World!') == 'Hello World!\n'
