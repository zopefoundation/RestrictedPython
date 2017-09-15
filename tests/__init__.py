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


def _single(compile_func):
    """Factory to create an single function."""
    def _single(source, glb=None):
        code = _compile(compile_func, source)
        if glb is None:
            glb = {}
        exec(code, glb)
        return glb
    return _single


def _function(compile_func):
    """Factory to create a function object."""
    def _function(source, glb=None):
        code = _compile(compile_func, source)
        if glb is None:
            glb = {}
        exec(code, glb)
        return glb
    return _function


# Define the arguments for @pytest.mark.parametrize. This was used to be able
# to test both the old and the new implementation are equal. It can be
# refactored into fixtures.
# Compile in `exec` mode.
c_exec = ('c_exec', [RestrictedPython.compile.compile_restricted_exec])
# Compile and execute in `exec` mode.
e_exec = ('e_exec', [_exec(RestrictedPython.compile.compile_restricted_exec)])
# Compile in `eval` mode.
c_eval = ('c_eval', [RestrictedPython.compile.compile_restricted_eval])
# Compile and execute in `eval` mode.
e_eval = ('e_eval', [_eval(RestrictedPython.compile.compile_restricted_eval)])
#
c_function = ('c_function', [RestrictedPython.compile.compile_restricted_function])  # NOQA: E501
e_function = ('e_function', [_function(RestrictedPython.compile.compile_restricted_function)])  # NOQA: E501

c_single = ('c_single', [RestrictedPython.compile.compile_restricted_single])
e_single = ('e_single', [_single(RestrictedPython.compile.compile_restricted_single)])  # NOQA: E501
