##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
from __future__ import nested_scopes

__version__='$Revision: 1.5 $'[11:-2]

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
    def guard(ob, write=None):
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
    def guard(ob):
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




