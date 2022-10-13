import RestrictedPython.Guards
from RestrictedPython import compile_restricted_eval
from RestrictedPython import compile_restricted_exec


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
    if '__builtins__' not in glb:
        glb['__builtins__'] = RestrictedPython.Guards.safe_builtins.copy()
    if exc_func == 'eval':
        return eval(code, glb)
    else:
        exec(code, glb)
        return glb


def restricted_eval(source, glb=None):
    """Call compile_restricted_eval and actually eval it."""
    code = _compile(compile_restricted_eval, source)
    return _execute(code, glb, 'eval')


def restricted_exec(source, glb=None):
    """Call compile_restricted_eval and actually exec it."""
    code = _compile(compile_restricted_exec, source)
    return _execute(code, glb, 'exec')
