from RestrictedPython import compile_restricted_exec


def test_call_breakpoint():
    """The Python3.7+ builtin function breakpoint should not
    be used and is forbidden in RestrictedPython.
    """
    result = compile_restricted_exec('breakpoint()')
    assert result.errors == ('Line 1: "breakpoint" is a reserved name.',)
    assert result.code is None
