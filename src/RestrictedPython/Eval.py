##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Restricted Python Expressions."""

import ast
from RestrictedPython.RCompile import compile_restricted_eval
from string import strip
from string import translate

import string


nltosp = string.maketrans('\r\n', '  ')

default_guarded_getattr = getattr  # No restrictions.


def default_guarded_getitem(ob, index):
    # No restrictions.
    return ob[index]


class RestrictionCapableEval(object):
    """A base class for restricted code."""

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
            co, err, warn, used = compile_restricted_eval(self.expr, '<string>')
            if err:
                raise SyntaxError(err[0])
            self.used = tuple(used.keys())
            self.rcode = co

    def prepUnrestrictedCode(self):
        if self.ucode is None:
            exp_node = compile(self.expr, '<string>', 'eval', ast.PyCF_ONLY_AST)
            co = compile(exp_node, '<string>', 'eval')

            # Examine the ast to discover which names the expression needs.
            if self.used is None:
                used = set()
                for node in ast.walk(exp_node):
                    if isinstance(node, ast.Name):
                        if isinstance(node.ctx, ast.Load):
                            used.add(node.id)

                self.used = tuple(used)

            self.ucode = co

    def eval(self, mapping):
        # This default implementation is probably not very useful. :-(
        # This is meant to be overridden.
        self.prepRestrictedCode()
        code = self.rcode
        d = {'_getattr_': default_guarded_getattr,
             '_getitem_': default_guarded_getitem}
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
