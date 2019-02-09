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
            glb = {
                '__builtins__': RestrictedPython.Guards.safe_builtins.copy()}
        return eval(code, glb)
    return _eval


# Define the arguments for @pytest.mark.parametrize. This was used to be able
# to test both the old and the new implementation are equal. It can be
# refactored into fixtures.
# Compile and execute in `exec` mode.
e_exec = ('e_exec', [_exec(RestrictedPython.compile.compile_restricted_exec)])
# Compile and execute in `eval` mode.
e_eval = ('e_eval', [_eval(RestrictedPython.compile.compile_restricted_eval)])
#
c_single = ('c_single', [RestrictedPython.compile.compile_restricted_single])
