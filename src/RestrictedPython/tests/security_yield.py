# These are all supposed to raise a SyntaxError when using
# compile_restricted() but not when using compile().
# Each function in this module is compiled using compile_restricted().


def no_yield():
    yield 42
