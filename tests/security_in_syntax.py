# These are all supposed to raise a SyntaxError when using
# compile_restricted() but not when using compile().
# Each function in this module is compiled using compile_restricted().

def overrideGuardWithFunction():
    def _getattr(o): return o

def overrideGuardWithLambda():
    lambda o, _getattr=None: o

def overrideGuardWithClass():
    class _getattr:
        pass

def overrideGuardWithName():
    _getattr = None

def overrideGuardWithArgument():
    def f(_getattr=None):
        pass

def reserved_names():
    printed = ''

def bad_name():
    __ = 12

def bad_attr():
    some_ob._some_attr = 15

def no_exec():
    exec 'q = 1'
