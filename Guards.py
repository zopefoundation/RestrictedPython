##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
from __future__ import nested_scopes

__version__='$Revision: 1.7 $'[11:-2]

import new

safe_builtins = {}
for name in ('None', 'abs', 'chr', 'divmod', 'float', 'hash', 'hex', 'int',
             'len', 'max', 'min', 'oct', 'ord', 'round', 'str', 'pow',
             'apply', 'callable', 'cmp', 'complex', 'isinstance',
             'issubclass', 'long', 'repr', 'range', 'list', 'tuple',
             'unichr', 'unicode',
             'Exception',
             'ArithmeticError', 'AssertionError', 'AttributeError',
             'EOFError', 'EnvironmentError', 'FloatingPointError',
             'IOError', 'ImportError', 'IndexError', 'KeyError',
             'LookupError', 'NameError', 'OSError', 'OverflowError',
             'RuntimeError', 'StandardError', 'SyntaxError',
             'TypeError', 'ValueError', 'ZeroDivisionError',):
    safe_builtins[name] = __builtins__[name]


def _full_read_guard(g_attr, g_item):
    # Nested scope abuse!
    # The arguments are used by class Wrapper
    # safetype variable is used by guard()
    safetype = {type(()): 1, type([]): 1, type({}): 1, type(''): 1}.has_key
    def guard(ob, write=None, safetype=safetype):
        # Don't bother wrapping simple types, or objects that claim to
        # handle their own read security.
        if safetype(type(ob)) or getattr(ob, '_guarded_reads', 0):
            return ob
        # ob is shared by class Wrapper, so the class instance wraps it.
        class Wrapper:
            def __len__(self):
                # Required for slices with negative bounds
                return len(ob)
            def __getattr__(self, name):
                return g_attr(ob, name)
            def __getitem__(self, i):
                # Must handle both item and slice access.
                return g_item(ob, i)
            # Optional, for combined read/write guard
            def __setitem__(self, index, val):
                write(ob)[index] = val
            def __setattr__(self, attr, val):
                setattr(write(ob), attr, val)
        return Wrapper()
    return guard 


def _write_wrapper():
    # Construct the write wrapper class
    def _handler(secattr, error_msg):
        # Make a class method.
        def handler(self, *args):
            try:
                f = getattr(self.ob, secattr)
            except AttributeError:
                raise TypeError, error_msg
            f(*args)
        return handler
    class Wrapper:
        def __len__(self):
            # Required for slices with negative bounds.
            return len(self.ob)
        def __init__(self, ob):
            self.__dict__['ob'] = ob
        __setitem__ = _handler('__guarded_setitem__',
          'object does not support item or slice assignment')
        __delitem__ = _handler('__guarded_delitem__',
          'object does not support item or slice assignment')
        __setattr__ = _handler('__guarded_setattr__',
          'attribute-less object (assign or del)')
        __delattr__ = _handler('__guarded_delattr__',
          'attribute-less object (assign or del)')
    return Wrapper

def _full_write_guard():
    # Nested scope abuse!
    # safetype and Wrapper variables are used by guard()
    safetype = {type([]): 1, type({}): 1}.has_key
    Wrapper = _write_wrapper()
    def guard(ob, safetype=safetype, Wrapper=Wrapper):
        # Don't bother wrapping simple types, or objects that claim to
        # handle their own write security.
        if safetype(type(ob)) or hasattr(ob, '_guarded_writes'):
            return ob
        # Hand the object to the Wrapper instance, then return the instance.
        return Wrapper(ob)
    return guard 
full_write_guard = _full_write_guard()

def guarded_setattr(object, name, value):
    setattr(full_write_guard(object), name, value)
safe_builtins['setattr'] = guarded_setattr

def guarded_delattr(object, name):
    delattr(full_write_guard(object), name)
safe_builtins['delattr'] = guarded_delattr




