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
"""Restricted Python Expressions
"""
__rcs_id__='$Id: Eval.py,v 1.2 2001/04/27 20:27:51 shane Exp $'
__version__='$Revision: 1.2 $'[11:-2]

from string import translate, strip
import string
compile_restricted_eval = None

nltosp = string.maketrans('\r\n','  ')

def default_read_guard(ob):
    # No restrictions.
    return ob

PROFILE = 0

class RestrictionCapableEval:
    """A base class for restricted code.
    """
    globals = {'__builtins__': None}
    rcode = None  # restricted
    ucode = None  # unrestricted
    used = None

    def __init__(self, expr):
        """Create a restricted expression

        where:

          expr -- a string containing the expression to be evaluated.
        """
        expr = strip(expr)
        self.__name__ = expr
        expr = translate(expr, nltosp)
        self.expr = expr
        self.prepUnrestrictedCode()  # Catch syntax errors.

    def prepRestrictedCode(self):
        if self.rcode is None:
            global compile_restricted_eval
            if compile_restricted_eval is None:
                # Late binding because this will import the whole
                # compiler suite.
                from RestrictedPython import compile_restricted_eval

            if PROFILE:
                from time import clock
                start = clock()
            co, err, warn, used = compile_restricted_eval(
                self.expr, '<string>')
            if PROFILE:
                end = clock()
                print 'prepRestrictedCode: %d ms for %s' % (
                    (end - start) * 1000, `self.expr`)
            if err:
                raise SyntaxError, err[0]
            self.used = tuple(used.keys())
            self.rcode = co

    def prepUnrestrictedCode(self):
        if self.ucode is None:
            # Use the standard compiler.
            co = compile(self.expr, '<string>', 'eval')
            if self.used is None:
                # Examine the code object, discovering which names
                # the expression needs.
                names=list(co.co_names)
                used={}
                i=0
                code=co.co_code
                l=len(code)
                LOAD_NAME=101   
                HAVE_ARGUMENT=90        
                while(i < l):
                    c=ord(code[i])
                    if c==LOAD_NAME:
                        name=names[ord(code[i+1])+256*ord(code[i+2])]
                        used[name]=1
                        i=i+3
                    elif c >= HAVE_ARGUMENT: i=i+3
                    else: i=i+1
                self.used=tuple(used.keys())
            self.ucode=co

    def eval(self, mapping):
        # This default implementation is probably not very useful. :-(
        # This is meant to be overridden.
        self.prepRestrictedCode()
        code = self.rcode
        d = {'_read_': default_read_guard}
        d.update(self.globals)
        has_key = d.has_key
        for name in self.used:
            try:
                if not has_key(name):
                    d[name] = mapping[name]
            except KeyError:
                # Swallow KeyErrors since the expression
                # might not actually need the name.  If it
                # does need the name, a NameError will occur.
                pass
        return eval(code, d)

    def __call__(self, **kw):
        return self.eval(kw)

