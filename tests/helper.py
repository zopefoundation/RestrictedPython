from RestrictedPython import compile_restricted_eval

import RestrictedPython.Guards


def _compile(compile_func, source):
    """Compile some source with a compile func."""
    result = compile_func(source)
    assert result.errors == (), result.errors
    assert result.code is not None
    return result.code


def _execute(code, glb, exc_func):
    """Execute compiled code using `exc_func`.

    glb ... globals, gets injected with safe_builtins
    """
    if glb is None:
        glb = {}
    else:
        glb = glb.copy()
    glb['__builtins__'] = RestrictedPython.Guards.safe_builtins.copy()
    return eval(code, glb)


def restricted_eval(source, glb=None):
    """Call compile_restricted_eval and actually eval it."""
    code = _compile(compile_restricted_eval, source)
    return _execute(code, glb, eval)
