from .. import compile_restricted
from .. import safe_globals
from sys import version_info


def check_version(tversion, cmp=">="):
    """compare python version against target version *tversion*."""
    if isinstance(tversion, str):
        tversion = tversion.split(".")
    tversion = tuple(map(int, tversion))
    py_version = version_info[:len(tversion)]
    return eval("py_version %s tversion" % cmp, locals())


def compile_str(s, name="<unknown>"):
    """code and globals for *s*.

    *s* must be acceptable for ``compile_restricted`` (this is (especially) the
    case for an ``str`` or ``ast.Module``).

    *name* is a ``str`` used in error messages.
    """
    code = compile_restricted(s, name, 'exec')
    gs = safe_globals.copy()
    gs["__debug__"] = True  # assert active
    return code, gs
