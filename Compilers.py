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

__version__='$Revision: 1.2 $'[11:-2]

import sys
from traceback import format_exception_only

def getSyntaxError(source, mode):
    try:
        compile(source, '<string>', mode)
    except SyntaxError:
        err = format_exception_only(SyntaxError, sys.exc_info()[1])
        err = [line.rstrip() for line in err]
    else:
        err = ['Unknown parser error.']
    return None, err, [], {}

from parser import ParserError
from compiler.transformer import Transformer

def tryParsing(source, mode):
    if mode == 'eval':
        parser = Transformer().parseexpr
    else:
        parser = Transformer().parsesuite
    try:
        return parser(source), None
    except ParserError:
        return None, getSyntaxError(source, mode)

import MutatingWalker
from RestrictionMutator import RestrictionMutator
from compiler import ast, visitor, pycodegen

def compile_restricted_function(p, body, name, filename):
    '''Compile a restricted code object for a function.

    The function can be reconstituted using the 'new' module:

    new.function(<code>, <globals>)
    '''
    rm = RestrictionMutator()
    # Parse the parameters and body, then combine them.
    tree, err = tryParsing('def f(%s): pass' % p, 'exec')
    if err:
        if len(err) > 1:
            # Drop the first line of the error and adjust the next two.
            err[1].pop(0) 
            err[1][0] = 'parameters: %s\n' % err[1][0][10:-8]
            err[1][1] = '  ' + err[1][1]
        return err
    f = tree.node.nodes[0]
    btree, err = tryParsing(body, 'exec')
    if err: return err
    f.code.nodes = btree.node.nodes
    f.name = name
    # Look for a docstring
    stmt1 = f.code.nodes[0]
    if (isinstance(stmt1, ast.Discard) and
        isinstance(stmt1.expr, ast.Const) and
        type(stmt1.expr.value) is type('')):
        f.doc = stmt1.expr.value
    MutatingWalker.walk(tree, rm)
    if rm.errors:
        return None, rm.errors, rm.warnings, rm.used_names
    gen = pycodegen.NestedScopeModuleCodeGenerator(filename)
    visitor.walk(tree, gen)
    return gen.getCode(), (), rm.warnings, rm.used_names

def compile_restricted_exec(s, filename='<string>', nested_scopes=1):
    '''Compile a restricted code suite.'''
    rm = RestrictionMutator()
    tree, err = tryParsing(s, 'exec')
    if err: return err
    MutatingWalker.walk(tree, rm)
    if rm.errors:
        return None, rm.errors, rm.warnings, rm.used_names
    if nested_scopes:
        gen = pycodegen.NestedScopeModuleCodeGenerator(filename)
    else:
        gen = pycodegen.ModuleCodeGenerator(filename)
    visitor.walk(tree, gen)
    return gen.getCode(), (), rm.warnings, rm.used_names

if 1:
  def compile_restricted_eval(s, filename='<string>', nested_scopes=1):
    '''Compile a restricted expression.'''
    r = compile_restricted_exec('def f(): return \\\n' + s, filename,
                                nested_scopes)
    err = r[1]
    if err:
        if len(err) > 1:
            err.pop(0) # Discard first line of error
    else:
        # Extract the code object representing the function body
        r = (r[0].co_consts[1],) + r[1:]
    return r

else:

  def compile_restricted_eval(s, filename='<string>'):
    '''Compile a restricted expression.'''
    rm = RestrictionMutator()
    tree, err = tryParsing(s, 'eval')
    if err:
        err[1].pop(0) # Discard first line of error
        return err
    MutatingWalker.walk(tree, rm)
    if rm.errors:
        return None, rm.errors, rm.warnings, rm.used_names
    # XXX No "EvalCodeGenerator" exists
    # so here's a hack that gets around it.
    gen = pycodegen.ModuleCodeGenerator(filename)
    gen.emit('SET_LINENO', 0)
    visitor.walk(tree, gen)
    gen.emit('RETURN_VALUE')
    return gen.getCode(), (), rm.warnings, rm.used_names

DEBUG = 0
def compile_restricted(source, filename, mode):
    '''Returns restricted compiled code. The signature of this
    function should match the signature of the builtin compile.'''
    if DEBUG:
        from time import clock
        start = clock()

    if mode == 'eval':
        r = compile_restricted_eval(source, filename)
    elif mode == 'exec':
        r = compile_restricted_exec(source, filename)
    else:
        raise ValueError, "compile_restricted() arg 3 must be 'exec' or 'eval'"

    if DEBUG:
        end = clock()
        print 'compile_restricted: %d ms for %s' % (
            (end - start) * 1000, repr(filename))
    code, errors, warnings, used_names = r
    if errors:
        raise SyntaxError, errors[0]
    return code
