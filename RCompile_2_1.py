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

__version__='$Revision: 1.4 $'[11:-2]

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
from compiler_2_1.transformer import Transformer

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
from compiler_2_1 import ast, visitor, pycodegen

def compile_restricted_function(p, body, name, filename, globalize=None):
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
    if globalize is not None:
        btree.node.nodes.insert(0, ast.Global(map(str, globalize)))
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
