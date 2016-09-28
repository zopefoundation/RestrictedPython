from RestrictedPython.transformer import RestrictingNodeTransformer

import ast


def compile_restricted_exec(
        source,
        filename='<string>',
        flags=0,
        dont_inherit=0,
        policy=RestrictingNodeTransformer):
    byte_code = None
    errors = []
    warnings = []
    used_names = []
    if policy is None:
        # Unrestricted Source Checks
        return compile(source, filename, mode='exec', flags=flags, dont_inherit=dont_inherit)
    c_ast = ast.parse(source, filename, 'exec')
    r_ast = policy(errors, warnings, used_names).visit(c_ast)
    if r_ast is None:
        raise SyntaxError('AST parse fehlgeschlagen')
    try:
        byte_code = compile(r_ast, filename, mode='exec'  # ,
                            #flags=flags,
                            #dont_inherit=dont_inherit
                            )
    except SyntaxError as v:
        byte_code = None
        errors.append(v)
    return byte_code, errors, warnings, used_names


def compile_restricted_eval(
        source,
        filename='<string>',
        flags=0,
        dont_inherit=0,
        policy=RestrictingNodeTransformer):
    byte_code = None
    errors = []
    warnings = []
    used_names = []
    if policy is None:
        # Unrestricted Source Checks
        return compile(source, filename, mode='eval', flags=flags, dont_inherit=dont_inherit)
    c_ast = ast.parse(source, filename, 'eval')
    r_ast = policy(errors, warnings, used_names).visit(c_ast)
    try:
        byte_code = compile(r_ast, filename, mode='eval', flags=flags,
                            dont_inherit=dont_inherit)
    except SyntaxError as v:
        byte_code = None
        errors.append(v)
    return byte_code, errors, warnings, used_names


def compile_restricted_single(
        source,
        filename='<string>',
        flags=0,
        dont_inherit=0,
        policy=RestrictingNodeTransformer):
    byte_code = None
    errors = []
    warnings = []
    used_names = []
    if policy is None:
        # Unrestricted Source Checks
        return compile(source, filename, mode='single', flags=flags, dont_inherit=dont_inherit)
    c_ast = ast.parse(source, filename, 'single')
    r_ast = policy(errors, warnings, used_names).visit(c_ast)
    try:
        byte_code = compile(r_ast, filename, mode='single', flags=flags,
                            dont_inherit=dont_inherit)
    except SyntaxError as v:
        byte_code = None
        errors.append(v)
    return byte_code, errors, warnings, used_names


def compile_restricted_function(
        source,
        filename='<string>',
        flags=0,
        dont_inherit=0,
        policy=RestrictingNodeTransformer):
    """Compiles a restricted code object for a function.

    The function can be reconstituted using the 'new' module:

    new.function(<code>, <globals>)

    The globalize argument, if specified, is a list of variable names to be
    treated as globals (code is generated as if each name in the list
    appeared in a global statement at the top of the function).

    TODO: Special function not comparable with the other restricted_compile_*
    functions.
    """
    byte_code = None
    errors = []
    warnings = []
    used_names = []
    if policy is None:
        # Unrestricted Source Checks
        return compile(source, filename, flags=flags, dont_inherit=dont_inherit)
    c_ast = ast.parse(source, filename, mode)
    r_ast = policy(errors, warnings, used_names).visit(c_ast)
    try:
        byte_code = compile(r_ast, filename, mode='', flags=flags,
                            dont_inherit=dont_inherit)
    except SyntaxError as v:
        byte_code = None
        errors.append(v)
    return byte_code, errors, warnings, used_names


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
    if mode == 'exec':
        byte_code, errors, warnings, used_names = compile_restricted_exec(
            source, filename=filename, flags=flags, dont_inherit=dont_inherit,
            policy=policy)
    elif mode == 'eval':
        byte_code, errors, warnings, used_names = compile_restricted_eval(
            source, filename=filename, flags=flags, dont_inherit=dont_inherit,
            policy=policy)
    elif mode == 'single':
        byte_code, errors, warnings, used_names = compile_restricted_single(
            source, filename=filename, flags=flags, dont_inherit=dont_inherit,
            policy=policy)
    elif mode == 'function':
        byte_code, errors, warnings, used_names = compile_restricted_function(
            source, filename=filename, flags=flags, dont_inherit=dont_inherit,
            policy=policy)
    else:
        raise TypeError('unknown mode %s', mode)
    if errors:
        raise SyntaxError(errors)
    return byte_code
