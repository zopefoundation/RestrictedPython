from collections import namedtuple
from RestrictedPython._compat import IS_PY2
from RestrictedPython.transformer import RestrictingNodeTransformer

import ast
import warnings


CompileResult = namedtuple(
    'CompileResult', 'code, errors, warnings, used_names')
syntax_error_template = (
    'Line {lineno}: {type}: {msg} in on statement: {statement}')


def _compile_restricted_mode(
        source,
        filename='<string>',
        mode="exec",
        flags=0,
        dont_inherit=False,
        policy=RestrictingNodeTransformer):
    byte_code = None
    errors = []
    warnings = []
    used_names = {}
    if policy is None:
        # Unrestricted Source Checks
        byte_code = compile(source, filename, mode=mode, flags=flags,
                            dont_inherit=dont_inherit)
    elif issubclass(policy, RestrictingNodeTransformer):
        c_ast = None
        allowed_source_types = [str, ast.Module]
        if IS_PY2:
            allowed_source_types.append(unicode)
        if not issubclass(type(source), tuple(allowed_source_types)):
            raise TypeError('Not allowed source type: '
                            '"{0.__class__.__name__}".'.format(source))
        c_ast = None
        # workaround for pypy issue https://bitbucket.org/pypy/pypy/issues/2552
        if isinstance(source, ast.Module):
            c_ast = source
        else:
            try:
                c_ast = ast.parse(source, filename, mode)
            except (TypeError, ValueError) as e:
                errors.append(str(e))
            except SyntaxError as v:
                errors.append(syntax_error_template.format(
                    lineno=v.lineno,
                    type=v.__class__.__name__,
                    msg=v.msg,
                    statement=v.text.strip()
                ))
        if c_ast:
            policy(errors, warnings, used_names).visit(c_ast)
            if not errors:
                byte_code = compile(c_ast, filename, mode=mode  # ,
                                    # flags=flags,
                                    # dont_inherit=dont_inherit
                                    )
    else:
        raise TypeError('Unallowed policy provided for RestrictedPython')
    return CompileResult(byte_code, tuple(errors), warnings, used_names)


def compile_restricted_exec(
        source,
        filename='<string>',
        flags=0,
        dont_inherit=False,
        policy=RestrictingNodeTransformer):
    """Compile restricted for the mode `exec`."""
    return _compile_restricted_mode(
        source,
        filename=filename,
        mode='exec',
        flags=flags,
        dont_inherit=dont_inherit,
        policy=policy)


def compile_restricted_eval(
        source,
        filename='<string>',
        flags=0,
        dont_inherit=False,
        policy=RestrictingNodeTransformer):
    """Compile restricted for the mode `eval`."""
    return _compile_restricted_mode(
        source,
        filename=filename,
        mode='eval',
        flags=flags,
        dont_inherit=dont_inherit,
        policy=policy)


def compile_restricted_single(
        source,
        filename='<string>',
        flags=0,
        dont_inherit=False,
        policy=RestrictingNodeTransformer):
    """Compile restricted for the mode `single`."""
    return _compile_restricted_mode(
        source,
        filename=filename,
        mode='single',
        flags=flags,
        dont_inherit=dont_inherit,
        policy=policy)


def compile_restricted_function(
        p,  # parameters
        body,
        name,
        filename='<string>',
        globalize=None,  # List of globals (e.g. ['here', 'context', ...])
        flags=0,
        dont_inherit=False,
        policy=RestrictingNodeTransformer):
    """Compile a restricted code object for a function.

    The globalize argument, if specified, is a list of variable names to be
    treated as globals (code is generated as if each name in the list
    appeared in a global statement at the top of the function).
    This allows to inject global variables into the generated function that
    feel like they are local variables, so the programmer who uses this doesn't
    have to understand that his code is executed inside a function scope
    instead of the global scope of a module.

    To actually get an executable function, you need to execute this code and
    pull out the defined function out of the locals like this:

    >>> compiled = compile_restricted_function('', 'pass', 'function_name')
    >>> safe_locals = {}
    >>> safe_globals = {}
    >>> exec(compiled.code, safe_globals, safe_locals)
    >>> compiled_function = safe_locals['function_name']
    >>> result = compiled_function(*[], **{})

    Then if you want to controll the globals for a specific call to this
    function, you can regenerate the function like this:

    >>> my_call_specific_global_bindings = dict(foo='bar')
    >>> safe_globals = safe_globals.copy()
    >>> safe_globals.update(my_call_specific_global_bindings)
    >>> import types
    >>> new_function = types.FunctionType(compiled_function.__code__, \
                                          safe_globals, \
                                          '<function_name>', \
                                          compiled_function.__defaults__ or \
                                          () \
                                          )
    >>> result = new_function(*[], **{})
    """
    # Parse the parameters and body, then combine them.
    body_ast = ast.parse(body, '<func code>', 'exec')

    # The compiled code is actually executed inside a function
    # (that is called when the code is called) so reading and assigning to a
    # global variable like this`printed += 'foo'` would throw an
    # UnboundLocalError.
    # We don't want the user to need to understand this.
    if globalize:
        body_ast.body.insert(0, ast.Global(globalize))
    wrapper_ast = ast.parse('def masked_function_name(%s): pass' % p,
                            '<func wrapper>', 'exec')
    # In case the name you chose for your generated function is not a
    # valid python identifier we set it after the fact
    function_ast = wrapper_ast.body[0]
    assert isinstance(function_ast, ast.FunctionDef)
    function_ast.name = name

    wrapper_ast.body[0].body = body_ast.body
    wrapper_ast = ast.fix_missing_locations(wrapper_ast)

    result = _compile_restricted_mode(
        wrapper_ast,
        filename=filename,
        mode='exec',
        flags=flags,
        dont_inherit=dont_inherit,
        policy=policy)

    return result


def compile_restricted(
        source,
        filename='<unknown>',
        mode='exec',
        flags=0,
        dont_inherit=False,
        policy=RestrictingNodeTransformer):
    """Replacement for the built-in compile() function.

    policy ... `ast.NodeTransformer` class defining the restrictions.

    """
    if mode in ['exec', 'eval', 'single', 'function']:
        result = _compile_restricted_mode(
            source,
            filename=filename,
            mode=mode,
            flags=flags,
            dont_inherit=dont_inherit,
            policy=policy)
    else:
        raise TypeError('unknown mode %s', mode)
    for warning in result.warnings:
        warnings.warn(
            warning,
            SyntaxWarning
        )
    if result.errors:
        raise SyntaxError(result.errors)
    return result.code
