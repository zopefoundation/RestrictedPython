
# These are all supposed to raise a SyntaxError when using
# compile_restricted() but not when using compile().
# Each function in this module is compiled using compile_restricted().

def overrideGuardWithFunction():
    def _guard(o): return o

def overrideGuardWithLambda():
    lambda o, _guard=None: o

def overrideGuardWithClass():
    class _guard:
        pass

def overrideGuardWithName():
    _guard = None

def overrideGuardWithArgument():
    def f(_guard=None):
        pass

def reserved_names():
    printed = ''

def bad_name():
    __ = 12

def bad_attr():
    some_ob._some_attr = 15

def no_exec():
    exec 'q = 1'
