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

__version__='$Revision: 1.5 $'[11:-2]

import string, math, random, whrandom
import DocumentTemplate.sequence

utility_builtins = {}

utility_builtins['string'] = string
utility_builtins['math'] = math
utility_builtins['random'] = random
utility_builtins['whrandom'] = whrandom
utility_builtins['sequence'] = DocumentTemplate.sequence

try:
    import DateTime
    utility_builtins['DateTime']= DateTime.DateTime
except: pass

def same_type(arg1, *args):
    '''Compares the class or type of two or more objects.'''
    t = getattr(arg1, '__class__', type(arg1))
    for arg in args:
        if getattr(arg, '__class__', type(arg)) is not t:
            return 0
    return 1
utility_builtins['same_type'] = same_type

def test(*args):
    l=len(args)
    for i in range(1, l, 2):
        if args[i-1]: return args[i]

    if l%2: return args[-1]
utility_builtins['test'] = test

def reorder(s, with=None, without=()):
    # s, with, and without are sequences treated as sets.
    # The result is subtract(intersect(s, with), without),
    # unless with is None, in which case it is subtract(s, without).
    if with is None: with=s
    d={}
    tt=type(())
    for i in s:
        if type(i) is tt and len(i)==2: k, v = i
        else:                           k= v = i
        d[k]=v
    r=[]
    a=r.append
    h=d.has_key

    for i in without:
        if type(i) is tt and len(i)==2: k, v = i
        else:                           k= v = i
        if h(k): del d[k]
        
    for i in with:
        if type(i) is tt and len(i)==2: k, v = i
        else:                           k= v = i
        if h(k):
            a((k,d[k]))
            del d[k]

    return r
utility_builtins['reorder'] = reorder
