from RestrictedPython.transformer import RestrictingNodeTransformer
import ast


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
        return compile(source, filename, flags=flags, dont_inherit=dont_inherit)
    c_ast = ast.parse(source, filename, mode)
    r_ast = policy(errors, wanings, used_names).visit(c_ast)
    try:
        byte_code = compile(r_ast, filename, mode='eval', flags=flags,
                            dont_inherit=dont_inherit)
    except SyntaxError as v:
        byte_code = None
        errors.append(v)


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
        return compile(source, filename, flags=flags, dont_inherit=dont_inherit)
    c_ast = ast.parse(source, filename, mode)
    r_ast = policy(errors, wanings, used_names).visit(c_ast)
    try:
        byte_code = compile(r_ast, filename, mode='exec', flags=flags,
                            dont_inherit=dont_inherit)
    except SyntaxError as v:
        byte_code = None
        errors.append(v)


def compile_restricted_function(
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
        return compile(source, filename, flags=flags, dont_inherit=dont_inherit)
    c_ast = ast.parse(source, filename, mode)
    r_ast = policy(errors, wanings, used_names).visit(c_ast)
    try:
        byte_code = compile(r_ast, filename, mode='single', flags=flags,
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
    c_ast = ast.parse(source, filename, mode)
    r_ast = policy().visit(c_ast)
    return compile(r_ast, filename, mode, flags, dont_inherit)
