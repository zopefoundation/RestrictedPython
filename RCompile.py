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
"""Compiles restricted code using the compiler module from the
Python standard library.
"""

__version__='$Revision: 1.4 $'[11:-2]


from compiler import ast, parse, misc, syntax
from compiler.pycodegen import AbstractCompileMode, Expression, \
     Interactive, Module
from traceback import format_exception_only

import MutatingWalker
from RestrictionMutator import RestrictionMutator


def niceParse(source, filename, mode):
    try:
        return parse(source, mode)
    except:
        # Try to make a clean error message using
        # the builtin Python compiler.
        try:
            compile(source, filename, mode)
        except SyntaxError:
            raise
        # Some other error occurred.
        raise


class RestrictedCompileMode (AbstractCompileMode):

    def __init__(self, source, filename):
        self.rm = RestrictionMutator()
        AbstractCompileMode.__init__(self, source, filename)

    def parse(self):
        return niceParse(self.source, self.filename, self.mode)

    def _get_tree(self):
        tree = self.parse()
        rm = self.rm
        MutatingWalker.walk(tree, rm)
        if rm.errors:
            raise SyntaxError, rm.errors[0]
        misc.set_filename(self.filename, tree)
        syntax.check(tree)
        return tree


class RExpression(RestrictedCompileMode, Expression):
    mode = "eval"
    compile = Expression.compile


class RInteractive(RestrictedCompileMode, Interactive):
    mode = "single"
    compile = Interactive.compile


class RModule(RestrictedCompileMode, Module):
    mode = "exec"
    compile = Module.compile


class RFunction(RModule):
    """A restricted Python function built from parts.
    """

    def __init__(self, p, body, name, filename, globalize=None):
        self.params = p
        self.body = body
        self.name = name
        self.globalize = globalize
        RModule.__init__(self, None, filename)

    def parse(self):
        # Parse the parameters and body, then combine them.
        firstline = 'def f(%s): pass' % self.params
        tree = niceParse(firstline, '<function parameters>', 'exec')
        f = tree.node.nodes[0]
        body_code = niceParse(self.body, self.filename, 'exec')
        # Stitch the body code into the function.
        f.code.nodes = body_code.node.nodes
        f.name = self.name
        # Look for a docstring.
        stmt1 = f.code.nodes[0]
        if (isinstance(stmt1, ast.Discard) and
            isinstance(stmt1.expr, ast.Const) and
            type(stmt1.expr.value) is type('')):
            f.doc = stmt1.expr.value
        if self.globalize:
            f.code.nodes.insert(0, ast.Global(map(str, self.globalize)))
        return tree


def compileAndTuplize(gen):
    try:
        gen.compile()
    except SyntaxError, v:
        return None, (str(v),), gen.rm.warnings, gen.rm.used_names
    return gen.getCode(), (), gen.rm.warnings, gen.rm.used_names

def compile_restricted_function(p, body, name, filename, globalize=None):
    """Compiles a restricted code object for a function.

    The function can be reconstituted using the 'new' module:

    new.function(<code>, <globals>)
    """
    gen = RFunction(p, body, name, filename, globalize=globalize)
    return compileAndTuplize(gen)

def compile_restricted_exec(s, filename='<string>'):
    """Compiles a restricted code suite.
    """
    gen = RModule(s, filename)
    return compileAndTuplize(gen)

def compile_restricted_eval(s, filename='<string>'):
    """Compiles a restricted expression.
    """
    gen = RExpression(s, filename)
    return compileAndTuplize(gen)

def compile_restricted(source, filename, mode):
    """Replacement for the builtin compile() function.
    """
    if mode == "single":
        gen = RInteractive(source, filename)
    elif mode == "exec":
        gen = RModule(source, filename)
    elif mode == "eval":
        gen = RExpression(source, filename)
    else:
        raise ValueError("compile_restricted() 3rd arg must be 'exec' or "
                         "'eval' or 'single'")
    gen.compile()
    return gen.getCode()
