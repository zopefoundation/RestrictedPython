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
'''
RestrictionMutator modifies a tree produced by
compiler.transformer.Transformer, restricting and enhancing the
code in various ways before sending it to pycodegen.
'''
__version__='$Revision: 1.5 $'[11:-2]

from compiler import ast
from compiler.transformer import parse
from compiler.consts import OP_ASSIGN, OP_DELETE, OP_APPLY

# These utility functions allow us to generate AST subtrees without
# line number attributes.  These trees can then be inserted into other
# trees without affecting line numbers shown in tracebacks, etc.
def rmLineno(node):
    '''Strip lineno attributes from a code tree'''
    if node.__dict__.has_key('lineno'):
        del node.lineno
    for child in node.getChildren():
        if isinstance(child, ast.Node):
            rmLineno(child)

def stmtNode(txt):
    '''Make a "clean" statement node'''
    node = parse(txt).node.nodes[0]
    rmLineno(node)
    return node

def exprNode(txt):
    '''Make a "clean" expression node'''
    return stmtNode(txt).expr

# There should be up to four objects in the global namespace.
# If a wrapper function or print target is needed in a particular
# module or function, it is obtained from one of these objects.
# It is stored in a variable with the same name as the global
# object, but without a single trailing underscore.  This variable is
# local, and therefore efficient to access, in function scopes.
_print_target_name = ast.Name('_print')
_getattr_name = ast.Name('_getattr')
_getitem_name = ast.Name('_getitem')
_write_guard_name = ast.Name('_write')

# Constants.
_None_const = ast.Const(None)
_write_const = ast.Const('write')

# Example prep code:
#
# global _getattr_
# _getattr = _getattr_
_prep_code = {}
for _n in ('getattr', 'getitem', 'write', 'print'):
    _prep_code[_n] = [ast.Global(['_%s_' % _n]),
                      stmtNode('_%s = _%s_' % (_n, _n))]
# Call the global _print instead of copying it.
_prep_code['print'][1] = stmtNode('_print = _print_()')

_printed_expr = exprNode('_print()')


# Keep track of which restrictions have been applied in a given scope.
class FuncInfo:
    _print_used = 0
    _printed_used = 0
    _getattr_used = 0
    _getitem_used = 0
    _write_used = 0


class RestrictionMutator:
    def __init__(self):
        self.funcinfo = FuncInfo()
        self.warnings = []
        self.errors = []
        self.used_names = {}

    def error(self, node, info):
        lineno = getattr(node, 'lineno', None)
        if lineno is not None and lineno > 0:
            self.errors.append('Line %d: %s' % (lineno, info))
        else:
            self.errors.append(info)

    def checkName(self, node, name):
        if len(name) > 1 and name[0] == '_':
            # Note: "_" *is* allowed.
            self.error(node, '"%s" is an invalid variable name because'
                       ' it starts with "_"' % name)
        if name == 'printed':
            self.error(node, '"printed" is a reserved name.')

    def checkAttrName(self, node):
        # This prevents access to protected attributes of guards
        # and is thus essential regardless of the security policy,
        # unless some other solution is devised.
        name = node.attrname
        if len(name) > 1 and name[0] == '_':
            # Note: "_" *is* allowed.
            self.error(node, '"%s" is an invalid attribute name '
                       'because it starts with "_".' % name)

    def prepBody(self, body):
        info = self.funcinfo
        if info._print_used or info._printed_used:
            # Add code at top for creating _print_target
            body[0:0] = _prep_code['print']
            if not info._printed_used:
                self.warnings.append(
                    "Prints, but never reads 'printed' variable.")
            elif not info._print_used:
                self.warnings.append(
                    "Doesn't print, but reads 'printed' variable.")
        if info._getattr_used:
            body[0:0] = _prep_code['getattr']
        if info._getitem_used:
            body[0:0] = _prep_code['getitem']
        if info._write_used:
            body[0:0] = _prep_code['write']

    def visitFunction(self, node, walker):
        self.checkName(node, node.name)
        for argname in node.argnames:
            self.checkName(node, argname)

        former_funcinfo = self.funcinfo
        self.funcinfo = FuncInfo()
        node = walker.defaultVisitNode(node)
        self.prepBody(node.code.nodes)
        self.funcinfo = former_funcinfo
        return node

    def visitLambda(self, node, walker):
        for argname in node.argnames:
            self.checkName(node, argname)
        return walker.defaultVisitNode(node)

    def visitPrint(self, node, walker):
        node = walker.defaultVisitNode(node)
        self.funcinfo._print_used = 1
        if node.dest is None:
            node.dest = _print_target_name
        else:
            self.funcinfo._getattr_used = 1
            # Pre-validate access to the "write" attribute.
            # "print >> ob, x" becomes
            # "print >> (_getattr(ob, 'write') and ob), x"
            node.dest = ast.And([
                ast.CallFunc(_getattr_name, [node.dest, _write_const]),
                node.dest])
        return node

    visitPrintnl = visitPrint

    def visitName(self, node, walker):
        if node.name == 'printed':
            # Replace name lookup with an expression.
            self.funcinfo._printed_used = 1
            return _printed_expr
        self.checkName(node, node.name)
        self.used_names[node.name] = 1
        return node

    def visitAssName(self, node, walker):
        self.checkName(node, node.name)
        return node

    def visitGetattr(self, node, walker):
        self.checkAttrName(node)
        node = walker.defaultVisitNode(node)
        if getattr(node, 'in_aug_assign', 0):
            # We're in an augmented assignment
            # We might support this later...
            self.error(node, 'Augmented assignment of '
                       'attributes is not allowed.')
            #expr.append(_write_guard_name)
            #self.funcinfo._write_used = 1
        self.funcinfo._getattr_used = 1
        return ast.CallFunc(_getattr_name,
                            [node.expr, ast.Const(node.attrname)])

    def visitSubscript(self, node, walker):
        node = walker.defaultVisitNode(node)
        if node.flags == OP_APPLY:
            # get subscript or slice
            if getattr(node, 'in_aug_assign', 0):
                # We're in an augmented assignment
                # We might support this later...
                self.error(node, 'Augmented assignment of '
                           'object items and slices is not allowed.')
                #expr.append(_write_guard_name)
                #self.funcinfo._write_used = 1
            self.funcinfo._getitem_used = 1
            if hasattr(node, 'subs'):
                # Subscript.
                subs = node.subs
                if len(subs) > 1:
                    # example: ob[1,2]
                    subs = ast.Tuple(subs)
                else:
                    # example: ob[1]
                    subs = subs[0]
            else:
                # Slice.
                # example: obj[0:2]
                lower = node.lower
                if lower is None:
                    lower = _None_const
                upper = node.upper
                if upper is None:
                    upper = _None_const
                subs = ast.Sliceobj([lower, upper])
            return ast.CallFunc(_getitem_name, [node.expr, subs])
        elif node.flags in (OP_DELETE, OP_ASSIGN):
            # set or remove subscript or slice
            node.expr = ast.CallFunc(_write_guard_name, [node.expr])
            self.funcinfo._write_used = 1
        return node

    visitSlice = visitSubscript

    def visitAssAttr(self, node, walker):
        self.checkAttrName(node)
        node = walker.defaultVisitNode(node)
        node.expr = ast.CallFunc(_write_guard_name, [node.expr])
        self.funcinfo._write_used = 1
        return node

    def visitExec(self, node, walker):
        self.error(node, 'Exec statements are not allowed.')

    def visitClass(self, node, walker):
        # Should classes be allowed at all??
        self.checkName(node, node.name)
        return walker.defaultVisitNode(node)

    def visitModule(self, node, walker):
        node = walker.defaultVisitNode(node)
        self.prepBody(node.node.nodes)
        return node

    def visitAugAssign(self, node, walker):
        node.node.in_aug_assign = 1
        return walker.defaultVisitNode(node)

