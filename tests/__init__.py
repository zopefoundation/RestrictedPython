from RestrictedPython._compat import IS_PY2

import RestrictedPython


def _compile(compile_func, source):
    """Compile some source with a compile func."""
    result = compile_func(source)
    assert result.errors == (), result.errors
    assert result.code is not None
    return result.code


def _execute(compile_func):
    """Factory to create an execute function."""
    def _execute(source, glb=None):
        code = _compile(compile_func, source)
        if glb is None:
            glb = {}
        exec(code, glb)
        return glb
    return _execute


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
compile = ('compile', [RestrictedPython.compile.compile_restricted_exec])
compile_eval = ('compile_eval',
                [RestrictedPython.compile.compile_restricted_eval])
execute = ('execute',
           [_execute(RestrictedPython.compile.compile_restricted_exec)])
r_eval = ('r_eval',
          [_eval(RestrictedPython.compile.compile_restricted_eval)])

if IS_PY2:
    from RestrictedPython import RCompile
    compile[1].append(RCompile.compile_restricted_exec)
    compile_eval[1].append(RCompile.compile_restricted_eval)
    execute[1].append(_execute(RCompile.compile_restricted_exec))
    r_eval[1].append(_eval(RCompile.compile_restricted_eval))
