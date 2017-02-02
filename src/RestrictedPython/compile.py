from collections import namedtuple
from RestrictedPython.transformer import RestrictingNodeTransformer

import ast


CompileResult = namedtuple(
    'CompileResult', 'code, errors, warnings, used_names')
syntax_error_template = (
    'Line {lineno}: {type}: {msg} in on statement: {statement}')


def _compile_restricted_mode(
        source,
        filename='<string>',
        mode="exec",
        flags=0,
        dont_inherit=0,
        policy=RestrictingNodeTransformer):
    byte_code = None
    errors = []
    warnings = []
    used_names = {}
    if policy is None:
        # Unrestricted Source Checks
        byte_code = compile(source, filename, mode=mode, flags=flags,
                            dont_inherit=dont_inherit)
    else:
        c_ast = None
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
    return CompileResult(byte_code, tuple(errors), warnings, used_names)


def compile_restricted_exec(
        source,
        filename='<string>',
        flags=0,
        dont_inherit=0,
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
        dont_inherit=0,
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
        dont_inherit=0,
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
        source,
        filename='<string>',
        flags=0,
        dont_inherit=0,
        policy=RestrictingNodeTransformer):
    """Compile a restricted code object for a function.

    The function can be reconstituted using the 'new' module:

    new.function(<code>, <globals>)

    The globalize argument, if specified, is a list of variable names to be
    treated as globals (code is generated as if each name in the list
    appeared in a global statement at the top of the function).

    TODO: Special function not comparable with the other restricted_compile_*
    functions.
    """
    return _compile_restricted_mode(
        source,
        filename=filename,
        mode='function',
        flags=flags,
        dont_inherit=dont_inherit,
        policy=policy)


def compile_restricted(
        source,
        filename='<unknown>',
        mode='exec',
        flags=0,
        dont_inherit=0,
        policy=RestrictingNodeTransformer):
    """Replacement for the built-in compile() function.

    policy ... `ast.NodeTransformer` class defining the restrictions.

    """
    byte_code, errors, warnings, used_names = None, None, None, None
    if mode in ['exec', 'eval', 'single', 'function']:
        byte_code, errors, warnings, used_names = _compile_restricted_mode(
            source,
            filename=filename,
            mode=mode,
            flags=flags,
            dont_inherit=dont_inherit,
            policy=policy)
    else:
        raise TypeError('unknown mode %s', mode)
    if errors:
        raise SyntaxError(errors)
    return byte_code
