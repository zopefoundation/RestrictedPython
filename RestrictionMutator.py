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
'''
RestrictionMutator modifies a tree produced by
compiler.transformer.Transformer, restricting and enhancing the
code in various ways before sending it to pycodegen.
'''
__version__='$Revision: 1.12 $'[11:-2]

from SelectCompiler import ast, parse, OP_ASSIGN, OP_DELETE, OP_APPLY

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

# There should be up to four objects in the global namespace.  If a
# wrapper function or print target is needed in a particular module or
# function, it is obtained from one of these objects.  There is a
# local and a global binding for each object: the global name has a
# trailing underscore, while the local name does not.
_print_target_name = ast.Name('_print')
_getattr_name = ast.Name('_getattr')
_getattr_name_expr = ast.Name('_getattr_')
_getitem_name = ast.Name('_getitem')
_getitem_name_expr = ast.Name('_getitem_')
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
    _is_suite = 0  # True for modules and functions, false for expressions


class RestrictionMutator:

    def __init__(self):
        self.funcinfo = FuncInfo()
        self.warnings = []
        self.errors = []
        self.used_names = {}

    def error(self, node, info):
        """Records a security error discovered during compilation.
        """
        lineno = getattr(node, 'lineno', None)
        if lineno is not None and lineno > 0:
            self.errors.append('Line %d: %s' % (lineno, info))
        else:
            self.errors.append(info)

    def checkName(self, node, name):
        """Verifies that a name being assigned is safe.

        This is to prevent people from doing things like:

          __metatype__ = mytype (opens up metaclasses, a big unknown
                                 in terms of security)
          __path__ = foo        (could this confuse the import machinery?)
          _getattr = somefunc   (not very useful, but could open a hole)

        Note that assigning a variable is not the only way to assign
        a name.  def _badname, class _badname, import foo as _badname,
        and perhaps other statements assign names.  Special case:
        '_' is allowed.
        """
        if len(name) > 1 and name[0] == '_':
            # Note: "_" *is* allowed.
            self.error(node, '"%s" is an invalid variable name because'
                       ' it starts with "_"' % name)
        if name == 'printed':
            self.error(node, '"printed" is a reserved name.')

    def checkAttrName(self, node):
        """Verifies that an attribute name does not start with _.

        As long as guards (security proxies) have underscored names,
        this underscore protection is important regardless of the
        security policy.  Special case: '_' is allowed.
        """
        name = node.attrname
        if len(name) > 1 and name[0] == '_':
            # Note: "_" *is* allowed.
            self.error(node, '"%s" is an invalid attribute name '
                       'because it starts with "_".' % name)

    def prepBody(self, body):
        """Prepends preparation code to a code suite.

        For example, if a code suite uses getattr operations,
        this places the following code at the beginning of the suite:

            global _getattr_
            _getattr = _getattr_

        Similarly for _getitem_, _print_, and _write_.
        """
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
        """Checks and mutates a function definition.

        Checks the name of the function and the argument names using
        checkName().  It also calls prepBody() to prepend code to the
        beginning of the code suite.
        """
        self.checkName(node, node.name)
        for argname in node.argnames:
            self.checkName(node, argname)
        walker.visitSequence(node.defaults)

        former_funcinfo = self.funcinfo
        self.funcinfo = FuncInfo()
        self.funcinfo._is_suite = 1
        node = walker.defaultVisitNode(node, exclude=('defaults',))
        self.prepBody(node.code.nodes)
        self.funcinfo = former_funcinfo
        return node

    def visitLambda(self, node, walker):
        """Checks and mutates an anonymous function definition.

        Checks the argument names using checkName().  It also calls
        prepBody() to prepend code to the beginning of the code suite.
        """
        for argname in node.argnames:
            self.checkName(node, argname)
        return walker.defaultVisitNode(node)

    def visitPrint(self, node, walker):
        """Checks and mutates a print statement.

        Adds a target to all print statements.  'print foo' becomes
        'print >> _print, foo', where _print is the default print
        target defined for this scope.

        Alternatively, if the untrusted code provides its own target,
        we have to check the 'write' method of the target.
        'print >> ob, foo' becomes
        'print >> (_getattr(ob, 'write') and ob), foo'.
        Otherwise, it would be possible to call the write method of
        templates and scripts; 'write' happens to be the name of the
        method that changes them.
        """
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
        """Prevents access to protected names as defined by checkName().

        Also converts use of the name 'printed' to an expression.
        """
        if node.name == 'printed':
            # Replace name lookup with an expression.
            self.funcinfo._printed_used = 1
            return _printed_expr
        self.checkName(node, node.name)
        self.used_names[node.name] = 1
        return node

    def visitAssName(self, node, walker):
        """Checks a name assignment using checkName().
        """
        self.checkName(node, node.name)
        return node

    def visitGetattr(self, node, walker):
        """Converts attribute access to a function call.

        'foo.bar' becomes '_getattr(foo, "bar")'.

        Also prevents augmented assignment of attributes, which would
        be difficult to support correctly.
        """
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
        if self.funcinfo._is_suite:
            # Use the local function _getattr().
            ga = _getattr_name
        else:
            # Use the global function _getattr_().
            ga = _getattr_name_expr
        return ast.CallFunc(ga, [node.expr, ast.Const(node.attrname)])

    def visitSubscript(self, node, walker):
        """Checks all kinds of subscripts.

        'foo[bar] += baz' is disallowed.
        'a = foo[bar, baz]' becomes 'a = _getitem(foo, (bar, baz))'.
        'a = foo[bar]' becomes 'a = _getitem(foo, bar)'.
        'a = foo[bar:baz]' becomes 'a = _getitem(foo, slice(bar, baz))'.
        'a = foo[:baz]' becomes 'a = _getitem(foo, slice(None, baz))'.
        'a = foo[bar:]' becomes 'a = _getitem(foo, slice(bar, None))'.
        'del foo[bar]' becomes 'del _write(foo)[bar]'.
        'foo[bar] = a' becomes '_write(foo)[bar] = a'.

        The _write function returns a security proxy.
        """
        node = walker.defaultVisitNode(node)
        if node.flags == OP_APPLY:
            # Set 'subs' to the node that represents the subscript or slice.
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
            if self.funcinfo._is_suite:
                gi = _getitem_name
            else:
                gi = _getitem_name_expr
            return ast.CallFunc(gi, [node.expr, subs])
        elif node.flags in (OP_DELETE, OP_ASSIGN):
            # set or remove subscript or slice
            node.expr = ast.CallFunc(_write_guard_name, [node.expr])
            self.funcinfo._write_used = 1
        return node

    visitSlice = visitSubscript

    def visitAssAttr(self, node, walker):
        """Checks and mutates attribute assignment.

        'a.b = c' becomes '_write(a).b = c'.
        The _write function returns a security proxy.
        """
        self.checkAttrName(node)
        node = walker.defaultVisitNode(node)
        node.expr = ast.CallFunc(_write_guard_name, [node.expr])
        self.funcinfo._write_used = 1
        return node

    def visitExec(self, node, walker):
        self.error(node, 'Exec statements are not allowed.')

    def visitYield(self, node, walker):
        self.error(node, 'Yield statements are not allowed.')

    def visitClass(self, node, walker):
        """Checks the name of a class using checkName().

        Should classes be allowed at all?  They don't cause security
        issues, but they aren't very useful either since untrusted
        code can't assign instance attributes.
        """
        self.checkName(node, node.name)
        return walker.defaultVisitNode(node)

    def visitModule(self, node, walker):
        """Adds prep code at module scope.

        Zope doesn't make use of this.  The body of Python scripts is
        always at function scope.
        """
        self.funcinfo._is_suite = 1
        node = walker.defaultVisitNode(node)
        self.prepBody(node.node.nodes)
        return node

    def visitAugAssign(self, node, walker):
        """Makes a note that augmented assignment is in use.

        Note that although augmented assignment of attributes and
        subscripts is disallowed, augmented assignment of names (such
        as 'n += 1') is allowed.

        This could be a problem if untrusted code got access to a
        mutable database object that supports augmented assignment.
        """
        node.node.in_aug_assign = 1
        return walker.defaultVisitNode(node)

    def visitImport(self, node, walker):
        """Checks names imported using checkName().
        """
        for name, asname in node.names:
            self.checkName(node, name)
            if asname:
                self.checkName(node, asname)
        return node

