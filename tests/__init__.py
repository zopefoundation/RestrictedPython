from RestrictedPython._compat import IS_PY2

import RestrictedPython


# Define the arguments for @pytest.mark.parametrize to be able to test both the
# old and the new implementation to be equal:
compile = ('compile', [RestrictedPython.compile.compile_restricted_exec])
if IS_PY2:
    from RestrictedPython import RCompile
    compile[1].append(RCompile.compile_restricted_exec)
