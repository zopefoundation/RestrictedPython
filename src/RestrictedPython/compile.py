from __future__ import annotations

import ast
import collections.abc
import os
import types
import typing
import warnings

from RestrictedPython._compat import IS_CPYTHON
from RestrictedPython._types import cast_not_none
from RestrictedPython.transformer import RestrictingNodeTransformer
from RestrictedPython.transformer import copy_locations


# Temporary workaround for missing _typeshed
ReadableBuffer: typing.TypeAlias = bytes | bytearray


class CompileResult(typing.NamedTuple):
    code: types.CodeType | None
    errors: collections.abc.Sequence[str]
    warnings: collections.abc.Sequence[str]
    used_names: collections.abc.Mapping[str, bool]


syntax_error_template = (
    'Line {lineno}: {type}: {msg} at statement: {statement!r}'
)

NOT_CPYTHON_WARNING = (
    'RestrictedPython is only supported on CPython: use on other Python '
    'implementations may create security issues.'
)

_T_ast_compilable: typing.TypeAlias = (
    ast.Module | ast.Expression | ast.Interactive)
_T_source: typing.TypeAlias = str | ReadableBuffer | _T_ast_compilable


def _compile_restricted_mode(
        source: _T_source,
        filename: str | bytes | os.PathLike[typing.Any] = '<string>',
        mode: typing.Literal["exec", "eval", "single"] = "exec",
        flags: int = 0,
        dont_inherit: bool = False,
        policy: type[ast.NodeTransformer] | None = RestrictingNodeTransformer,
) -> CompileResult:

    if not IS_CPYTHON:
        warnings.warn_explicit(
            NOT_CPYTHON_WARNING, RuntimeWarning, 'RestrictedPython', 0)

    byte_code = None
    collected_errors: list[str] = []
    collected_warnings: list[str] = []
    used_names: dict[str, bool] = {}
    if policy is None:
        # Unrestricted Source Checks
        byte_code = compile(source, filename, mode=mode, flags=flags,
                            dont_inherit=dont_inherit)
    elif issubclass(policy, RestrictingNodeTransformer):
        allowed_source_types = [
            str,
            bytes,
            bytearray,
            ast.Module,
            ast.Expression,
            ast.Interactive]
        if not issubclass(type(source), tuple(allowed_source_types)):
            raise TypeError('Not allowed source type: '
                            '"{0.__class__.__name__}".'.format(source))
        c_ast: _T_ast_compilable | None = None
        # workaround for pypy issue https://bitbucket.org/pypy/pypy/issues/2552
        if isinstance(source, (ast.Module, ast.Expression, ast.Interactive)):
            c_ast = source
        else:
            try:
                c_ast = typing.cast(
                    _T_ast_compilable, ast.parse(
                        source, filename, mode))
            except (TypeError, ValueError) as e:
                collected_errors.append(str(e))
            except SyntaxError as v:
                collected_errors.append(syntax_error_template.format(
                    lineno=v.lineno,
                    type=v.__class__.__name__,
                    msg=v.msg,
                    statement=v.text.strip() if v.text else None
                ))
        if c_ast:
            policy_instance = policy(
                collected_errors, collected_warnings, used_names)
            policy_instance.visit(c_ast)
            if not collected_errors:
                byte_code = compile(c_ast, filename, mode=mode  # ,
                                    # flags=flags,
                                    # dont_inherit=dont_inherit
                                    )
    else:
        raise TypeError('Unallowed policy provided for RestrictedPython')
    return CompileResult(
        byte_code,
        tuple(collected_errors),
        collected_warnings,
        used_names)


def compile_restricted_exec(
        source: _T_source,
        filename: str | bytes | os.PathLike[typing.Any] = '<string>',
        flags: int = 0,
        dont_inherit: bool = False,
        policy: type[ast.NodeTransformer] | None = RestrictingNodeTransformer,
) -> CompileResult:
    """Compile restricted for the mode `exec`."""
    return _compile_restricted_mode(
        source,
        filename=filename,
        mode='exec',
        flags=flags,
        dont_inherit=dont_inherit,
        policy=policy)


def compile_restricted_eval(
        source: _T_source,
        filename: str | bytes | os.PathLike[typing.Any] = '<string>',
        flags: int = 0,
        dont_inherit: bool = False,
        policy: type[ast.NodeTransformer] | None = RestrictingNodeTransformer,
) -> CompileResult:
    """Compile restricted for the mode `eval`."""
    return _compile_restricted_mode(
        source,
        filename=filename,
        mode='eval',
        flags=flags,
        dont_inherit=dont_inherit,
        policy=policy)


def compile_restricted_single(
        source: _T_source,
        filename: str | bytes | os.PathLike[typing.Any] = '<string>',
        flags: int = 0,
        dont_inherit: bool = False,
        policy: type[ast.NodeTransformer] | None = RestrictingNodeTransformer,
) -> CompileResult:
    """Compile restricted for the mode `single`."""
    return _compile_restricted_mode(
        source,
        filename=filename,
        mode='single',
        flags=flags,
        dont_inherit=dont_inherit,
        policy=policy)


def compile_restricted_function(
        p: str,  # parameters
        body: _T_source,
        name: str,
        filename: str | bytes | os.PathLike[typing.Any] = '<string>',
        # List of globals (e.g. ['here', 'context', ...])
        globalize: list[str] | None = None,
        flags: int = 0,
        dont_inherit: bool = False,
        policy: type[ast.NodeTransformer] | None = RestrictingNodeTransformer,
) -> CompileResult:
    """Compile a restricted code object for a function.

    Documentation see:
    http://restrictedpython.readthedocs.io/en/latest/usage/index.html#RestrictedPython.compile_restricted_function
    """
    # Parse the parameters and body, then combine them.
    body_ast: list[ast.stmt]
    if isinstance(body, ast.Expression):
        _body_ast = ast.Expr(body.body)
        copy_locations(_body_ast, body.body)
        body_ast = [_body_ast]
    elif isinstance(body, (ast.Module, ast.Interactive)):
        body_ast = body.body
    else:
        try:
            body_ast = ast.parse(body, '<func code>', 'exec').body
        except SyntaxError as v:
            error = syntax_error_template.format(
                lineno=v.lineno,
                type=v.__class__.__name__,
                msg=v.msg,
                statement=v.text.strip() if v.text else None)
            return CompileResult(
                code=None, errors=(error,), warnings=(), used_names={})

    # The compiled code is actually executed inside a function
    # (that is called when the code is called) so reading and assigning to a
    # global variable like this`printed += 'foo'` would throw an
    # UnboundLocalError.
    # We don't want the user to need to understand this.
    if globalize:
        body_ast.insert(0, ast.Global(globalize))
    wrapper_ast = ast.parse('def masked_function_name(%s): pass' % p,
                            '<func wrapper>', 'exec')
    # In case the name you chose for your generated function is not a
    # valid python identifier we set it after the fact
    function_ast = wrapper_ast.body[0]
    assert isinstance(function_ast, ast.FunctionDef)
    function_ast.name = name

    function_ast.body = body_ast
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
        source: _T_source,
        filename: str | bytes | os.PathLike[typing.Any] = '<unknown>',
        mode: typing.Literal["exec", "eval", "single"] = 'exec',
        flags: int = 0,
        dont_inherit: bool = False,
        policy: type[ast.NodeTransformer] | None = RestrictingNodeTransformer,
) -> types.CodeType:
    """Replacement for the built-in compile() function.

    policy ... `ast.NodeTransformer` class defining the restrictions.

    """
    if mode in ['exec', 'eval', 'single']:
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
    return cast_not_none(result.code)
