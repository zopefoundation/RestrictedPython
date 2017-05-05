from RestrictedPython import PrintCollector
from RestrictedPython import safe_builtins
from tests import c_function
from types import FunctionType

import pytest


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

    safe_globals = {
        '__name__': 'script',
        '_getattr_': getattr,
        '_print_': PrintCollector
    }
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
    p = 'input1, input2'
    body = """
print(input1 + input2)
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
        '_print_': PrintCollector
    }
    safe_globals.update(safe_builtins)
    safe_locals = {}
    exec(result.code, safe_globals, safe_locals)
    hello_world = safe_locals['hello_world']
    assert type(hello_world) == FunctionType
    assert hello_world('Hello ', 'World!') == 'Hello World!\n'


@pytest.mark.parametrize(*c_function)
def test_compile_restricted_function_can_access_global_variables(c_function):
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


@pytest.mark.parametrize(*c_function)
def test_compile_restricted_function_pretends_the_code_is_executed_in_a_global_scope(c_function):  # NOQA: E501
    p = ''
    body = """output = output + 'bar'"""
    name = "hello_world"
    global_symbols = ['output']

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
        'output': 'foo',
    }
    # safe_globals.update(safe_builtins)
    safe_locals = {}
    exec(result.code, safe_globals, safe_locals)
    hello_world = safe_locals['hello_world']
    assert type(hello_world) == FunctionType
    hello_world()
    assert safe_globals['output'] == 'foobar'


@pytest.mark.parametrize(*c_function)
def test_compile_restricted_function_allows_invalid_python_identifiers_as_function_name(c_function):  # NOQA: E501
    p = ''
    body = """output = output + 'bar'"""
    name = "<foo>.bar.__baz__"
    global_symbols = ['output']

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
        'output': 'foo',
    }
    # safe_globals.update(safe_builtins)
    safe_locals = {}
    exec(result.code, safe_globals, safe_locals)
    generated_function = tuple(safe_locals.values())[0]
    assert type(generated_function) == FunctionType
    generated_function()
    assert safe_globals['output'] == 'foobar'
