from RestrictedPython.transformer import RestrictingNodeTransformer

import ast


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
    # TODO: Should be an elif check if policy is subclass of
    # RestrictionNodeTransformer any other object passed in as policy might
    # throw an error or is a NodeVisitor subclass that could be initialized with
    # three params.
    # elif issubclass(policy, RestrictingNodeTransformer):
    else:
        c_ast = None
        try:
            c_ast = ast.parse(source, filename, mode)
        except SyntaxError as v:
            c_ast = None
            errors.append('Line {lineno}: {type}: {msg} in on statement: {statement}'.format(
                lineno=v.lineno,
                type=v.__class__.__name__,
                msg=v.msg,
                statement=v.text.strip()
            ))
        try:
            if c_ast:
                policy(errors, warnings, used_names).visit(c_ast)
                if not errors:
                    byte_code = compile(c_ast, filename, mode=mode  # ,
                                        #flags=flags,
                                        #dont_inherit=dont_inherit
                                        )
        except SyntaxError as v:
            byte_code = None
            errors.append(v)
        except TypeError as v:
            byte_code = None
            errors.append(v)
    # TODO: returning a named tuple should be considered
    return byte_code, tuple(errors), warnings, used_names


def compile_restricted_exec(
        source,
        filename='<string>',
        flags=0,
        dont_inherit=0,
        policy=RestrictingNodeTransformer):
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
    """Compiles a restricted code object for a function.

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
    # TODO: logging of warnings should be discussed and considered.
    return byte_code
