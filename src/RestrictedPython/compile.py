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
        globalize=None,  # List of globals (e.g. )
        flags=0,
        dont_inherit=False,
        policy=RestrictingNodeTransformer):
    """Compile a restricted code object for a function.

    The function can be reconstituted using the 'new' module:

    new.function(<code>, <globals>)  --> in Python 2 up to Python 2.7
    types.FunctionType(<code>, <globals> [, name [argdefs[, closure]]])  -->
    in Python 3 and Python 2.7
    it has the same signature.

    The globalize argument, if specified, is a list of variable names to be
    treated as globals (code is generated as if each name in the list
    appeared in a global statement at the top of the function).
    """
    # TODO: Special function not comparable with the other restricted_compile_* functions.  # NOQA

    # Parse the parameters and body, then combine them.
    wrapper_ast = ast.parse('def %s(%s): pass' % (name, p), '<func wrapper>', 'exec')

    body_ast = ast.parse(body, '<func code>', 'exec')
    wrapper_ast.body[0].body = body_ast.body

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
