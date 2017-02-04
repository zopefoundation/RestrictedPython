from RestrictedPython._compat import IS_PY2

import RestrictedPython


def _compile(compile_func, source):
    """Compile some source with a compile func."""
    result = compile_func(source)
    assert result.errors == (), result.errors
    assert result.code is not None
    return result.code


def _exec(compile_func):
    """Factory to create an execute function."""
    def _exec(source, glb=None):
        code = _compile(compile_func, source)
        if glb is None:
            glb = {}
        exec(code, glb)
        return glb
    return _exec


def _eval(compile_func):
    """Factory to create an eval function."""
    def _eval(source, glb=None):
        code = _compile(compile_func, source)
        if glb is None:
            glb = {}
        return eval(code, glb)
    return _eval


# Define the arguments for @pytest.mark.parametrize to be able to test both the
# old and the new implementation to be equal:
# Compile in `exec` mode.
c_exec = ('c_exec', [RestrictedPython.compile.compile_restricted_exec])
# Compile and execute in `exec` mode.
e_exec = ('e_exec', [_exec(RestrictedPython.compile.compile_restricted_exec)])
# Compile in `eval` mode.
c_eval = ('c_eval', [RestrictedPython.compile.compile_restricted_eval])
# Compile and execute in `eval` mode.
e_eval = ('e_eval', [_eval(RestrictedPython.compile.compile_restricted_eval)])

if IS_PY2:
    from RestrictedPython import RCompile
    c_exec[1].append(RCompile.compile_restricted_exec)
    c_eval[1].append(RCompile.compile_restricted_eval)
    e_exec[1].append(_exec(RCompile.compile_restricted_exec))
    e_eval[1].append(_eval(RCompile.compile_restricted_eval))
