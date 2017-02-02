from RestrictedPython._compat import IS_PY2

import RestrictedPython


def _execute(compile_func):
    """Factory to create an execute function."""
    def _execute(source):
        code, errors = compile_func(source)[:2]
        assert errors == (), errors
        assert code is not None
        glb = {}
        exec(code, glb)
        return glb
    return _execute


# Define the arguments for @pytest.mark.parametrize to be able to test both the
# old and the new implementation to be equal:
compile = ('compile', [RestrictedPython.compile.compile_restricted_exec])
execute = ('execute',
           [_execute(RestrictedPython.compile.compile_restricted_exec)])
if IS_PY2:
    from RestrictedPython import RCompile
    compile[1].append(RCompile.compile_restricted_exec)
    execute[1].append(_execute(RCompile.compile_restricted_exec))
