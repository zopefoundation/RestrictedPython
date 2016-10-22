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
"""
transformer module:

uses Python standard library ast module and its containing classes to transform
the parsed python code to create a modified AST for a byte code generation.
"""

# This package should follow the Plone Sytleguide for Python,
# which differ from PEP8:
# http://docs.plone.org/develop/styleguide/python.html


import ast
import sys


# if any of the ast Classes should not be whitelisted, please comment them out
# and add a comment why.
AST_WHITELIST = [
    # ast for Literals,
    ast.Num,
    ast.Str,
    ast.List,
    ast.Tuple,
    ast.Set,
    ast.Dict,
    ast.Ellipsis,
    #ast.NameConstant,
    # ast for Variables,
    ast.Name,
    ast.Load,
    ast.Store,
    ast.Del,
    # Expressions,
    ast.Expr,
    ast.UnaryOp,
    ast.UAdd,
    ast.USub,
    ast.Not,
    ast.Invert,
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.LShift,
    ast.RShift,
    ast.BitOr,
    ast.BitAnd,
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Is,
    ast.IsNot,
    ast.In,
    ast.NotIn,
    ast.Call,
    ast.keyword,
    ast.IfExp,
    ast.Attribute,
    # Subscripting,
    ast.Subscript,
    ast.Index,
    ast.Slice,
    ast.ExtSlice,
    # Comprehensions,
    ast.ListComp,
    ast.SetComp,
    ast.GeneratorExp,
    ast.DictComp,
    ast.comprehension,
    # Statements,
    ast.Assign,
    ast.AugAssign,
    ast.Raise,
    ast.Assert,
    ast.Delete,
    ast.Pass,
    # Imports,
    ast.Import,
    ast.ImportFrom,
    ast.alias,
    # Control flow,
    ast.If,
    ast.For,
    ast.While,
    ast.Break,
    ast.Continue,
    #ast.ExceptHanlder,  # We do not Support ExceptHanlders
    ast.With,
    #ast.withitem,
    # Function and class definitions,
    ast.FunctionDef,
    ast.Lambda,
    ast.arguments,
    #ast.arg,
    ast.Return,
    # ast.Yield, # yield is not supported
    #ast.YieldFrom,
    #ast.Global,
    #ast.Nonlocal,
    ast.ClassDef,
    ast.Module,
    ast.Param,
]


# For AugAssign the operator must be converted to a string.
IOPERATOR_TO_STR = {
    # Shared by python2 and python3
    ast.Add: '+=',
    ast.Sub: '-=',
    ast.Mult: '*=',
    ast.Div: '/=',
    ast.Mod: '%=',
    ast.Pow: '**=',
    ast.LShift: '<<=',
    ast.RShift: '>>=',
    ast.BitOr: '|=',
    ast.BitXor: '^=',
    ast.BitAnd: '&=',
    ast.FloorDiv: '//='
}


version = sys.version_info
if version >= (2, 7) and version < (2, 8):
    AST_WHITELIST.extend([
        ast.Print,
        #ast.TryFinally,  # TryFinally should not be supported
        #ast.TryExcept,  # TryExcept should not be supported
    ])

if version >= (3, 0):
    AST_WHITELIST.extend([
        ast.Bytes,
        ast.Starred,
        ast.arg,
        ast.Try,  # Try should not be supported
        ast.TryExcept,  # TryExcept should not be supported
        ast.NameConstant
    ])

if version >= (3, 4):
    AST_WHITELIST.extend([
    ])

if version >= (3, 5):
    IOPERATOR_TO_STR[ast.MatMult] = '@='

    AST_WHITELIST.extend([
        ast.MatMult,
        # Async und await,  # No Async Elements should be supported
        #ast.AsyncFunctionDef,  # No Async Elements should be supported
        #ast.Await,  # No Async Elements should be supported
        #ast.AsyncFor,  # No Async Elements should be supported
        #ast.AsyncWith,  # No Async Elements should be supported
    ])

if version >= (3, 6):
    AST_WHITELIST.extend([
    ])


# When new ast nodes are generated they have no 'lineno' and 'col_offset'.
# This function copies these two fields from the incoming node
def copy_locations(new_node, old_node):
    assert 'lineno' in new_node._attributes
    new_node.lineno = old_node.lineno

    assert 'col_offset' in new_node._attributes
    new_node.col_offset = old_node.col_offset

    ast.fix_missing_locations(new_node)




class RestrictingNodeTransformer(ast.NodeTransformer):

    def __init__(self, errors=[], warnings=[], used_names=[]):
        super(RestrictingNodeTransformer, self).__init__()
        self.errors = errors
        self.warnings = warnings
        self.used_names = used_names

        # Global counter to construct temporary variable names.
        self._tmp_idx = 0

    def gen_tmp_name(self):
        # 'check_name' ensures that no variable is prefixed with '_'.
        # => Its safe to use '_tmp..' as a temporary variable.
        name = '_tmp%i' % self._tmp_idx
        self._tmp_idx +=1
        return name

    def error(self, node, info):
        """Record a security error discovered during transformation."""
        lineno = getattr(node, 'lineno', None)
        self.errors.append('Line {lineno}: {info}'.format(lineno=lineno, info=info))

    def warn(self, node, info):
        """Record a security error discovered during transformation."""
        lineno = getattr(node, 'lineno', None)
        self.warnings.append('Line {lineno}: {info}'.format(lineno=lineno, info=info))

    def use_name(self, node, info):
        """Record a security error discovered during transformation."""
        lineno = getattr(node, 'lineno', None)
        self.used_names.append('Line {lineno}: {info}'.format(lineno=lineno, info=info))

    def guard_iter(self, node):
        """
        Converts:
            for x in expr
        to
            for x in _getiter_(expr)

        Also used for
        * list comprehensions
        * dict comprehensions
        * set comprehensions
        * generator expresions
        """
        node = self.generic_visit(node)

        new_iter = ast.Call(
            func=ast.Name("_getiter_", ast.Load()),
            args=[node.iter],
            keywords=[])

        copy_locations(new_iter, node.iter)
        node.iter = new_iter
        return node

    def gen_none_node(self):
        if version >= (3, 4):
            return ast.NameConstant(value=None)
        else:
            return ast.Name(id='None', ctx=ast.Load())

    def transform_slice(self, slice_):
        """Transforms slices into function parameters.

        ast.Slice nodes are only allowed within a ast.Subscript node.
        To use a slice as an argument of ast.Call it has to be converted.
        Conversion is done by calling the 'slice' function from builtins
        """

        if isinstance(slice_, ast.Index):
            return slice_.value

        elif isinstance(slice_, ast.Slice):
            # Create a python slice object.
            args = []

            if slice_.lower:
                args.append(slice_.lower)
            else:
                args.append(self.gen_none_node())

            if slice_.upper:
                args.append(slice_.upper)
            else:
                args.append(self.gen_none_node())

            if slice_.step:
                args.append(slice_.step)
            else:
                args.append(self.gen_none_node())

            return ast.Call(
                func=ast.Name('slice', ast.Load()),
                args=args,
                keywords=[])

        elif isinstance(slice_, ast.ExtSlice):
            dims = ast.Tuple([], ast.Load())
            for item in slice_.dims:
                dims.elts.append(self.transform_slice(item))
            return dims

        else:
            raise Exception("Unknown slice type: {0}".format(slice_))

    def check_name(self, node, name):
        if name is None:
            return

        if name.startswith('_') and name != '_':
            self.error(
                node,
                '"{name}" is an invalid variable name because it '
                'starts with "_"'.format(name=name))

        elif name.endswith('__roles__'):
            self.error(node, '"%s" is an invalid variable name because '
                       'it ends with "__roles__".' % name)

        # elif name == "printed":
        #     self.error(node, '"printed" is a reserved name.')

    def transform_seq_unpack(self, tpl):
        """Protects sequence unpacking with _getiter_"""

        assert isinstance(tpl, ast.Tuple)
        assert isinstance(tpl.ctx, ast.Store)

        # This name is used to feed the '_getiter_' method, so the *caller* of
        # this method has to ensure that the temporary name exsits and has the
        # correct value! Needed to support nested sequence unpacking and the
        # reason why this name is returned to the caller.
        my_name = self.gen_tmp_name()
        unpacks = []

        # Handle nested sequence unpacking.
        for idx, el in enumerate(tpl.elts):
            if isinstance(el, ast.Tuple):
                child = self.transform_seq_unpack(el)
                tpl.elts[idx] = ast.Name(child['name'], ast.Store())
                unpacks.append(child['body'])

        # The actual 'guarded' sequence unpacking.
        unpack = ast.Assign(
            targets=[tpl],
            value=ast.Call(
                func=ast.Name("_getiter_", ast.Load()),
                args=[ast.Name(my_name, ast.Load())],
                keywords=[]))

        unpacks.insert(0, unpack)

        # Delete the temporary variable from the scope.
        cleanup = ast.TryFinally(
            body=unpacks,
            finalbody=[
                ast.Delete(
                    targets=[ast.Name(my_name, ast.Del())])])

        return {'name': my_name, 'body': cleanup}

    # Special Functions for an ast.NodeTransformer

    def generic_visit(self, node):
        if node.__class__ not in AST_WHITELIST:
            self.error(
                node,
                '{0.__class__.__name__} statements are not allowed.'.format(
                    node))
        else:
            return super(RestrictingNodeTransformer, self).generic_visit(node)

    ##########################################################################
    # visti_*ast.ElementName* methods are used to eigther inspect special
    # ast Modules or modify the behaviour
    # therefore please have for all existing ast modules of all python versions
    # that should be supported included.
    # if nothing is need on that element you could comment it out, but please
    # let it remain in the file and do document why it is uncritical.
    # RestrictedPython is a very complicated peace of software and every
    # maintainer needs a way to understand why something happend here.
    # Longish code with lot of comments are better than ununderstandable code.
    ##########################################################################

    # ast for Literals

    def visit_Num(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Str(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Bytes(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_List(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Tuple(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Set(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Dict(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Ellipsis(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_NameConstant(self, node):
        """

        """
        return self.generic_visit(node)

    # ast for Variables

    def visit_Name(self, node):
        """

        """
        self.check_name(node, node.id)
        return self.generic_visit(node)

    def visit_Load(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Store(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Del(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Starred(self, node):
        """

        """
        return self.generic_visit(node)

    # Expressions

    def visit_UnaryOp(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_UAdd(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_USub(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Not(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Invert(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_BinOp(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Add(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Sub(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Div(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_FloorDiv(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Mod(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Pow(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_LShift(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_RShift(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_BitOr(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_BitAnd(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_MatMult(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_BoolOp(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_And(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Or(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Compare(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Eq(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_NotEq(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Lt(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_LtE(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Gt(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_GtE(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Is(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_IsNot(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_In(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_NotIn(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Call(self, node):
        """Checks calls with '*args' and '**kwargs'.

        Note: The following happens only if '*args' or '**kwargs' is used.

        Transfroms 'foo(<all the possible ways of args>)' into
        _apply_(foo, <all the possible ways for args>)

        The thing is that '_apply_' has only '*args', '**kwargs', so it gets
        Python to collapse all the myriad ways to call functions
        into one manageable from.

        From there, '_apply_()' wraps args and kws in guarded accessors,
        then calls the function, returning the value.
        """

        if isinstance(node.func, ast.Name):
            if node.func.id == 'exec':
                self.error(node, 'Exec calls are not allowed.')
            elif node.func.id == 'eval':
                self.error(node, 'Eval calls are not allowed.')

        needs_wrap = False

        # In python2.7 till python3.4 '*args', '**kwargs' have dedicated
        # attributes on the ast.Call node.
        # In python 3.5 and greater this has changed due to the fact that
        # multiple '*args' and '**kwargs' are possible.
        # '*args' can be detected by 'ast.Starred' nodes.
        # '**kwargs' can be deteced by 'keyword' nodes with 'arg=None'.

        if version < (3, 5):
            if (node.starargs is not None) or (node.kwargs is not None):
                needs_wrap = True
        else:
            for pos_arg in node.args:
                if isinstance(pos_arg, ast.Starred):
                    needs_wrap = True

            for keyword_arg in node.keywords:
                if keyword_arg.arg is None:
                    needs_wrap = True

        node = self.generic_visit(node)

        if not needs_wrap:
            return node

        node.args.insert(0, node.func)
        node.func = ast.Name('_apply_', ast.Load())
        copy_locations(node.func, node.args[0])
        return node

    def visit_keyword(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_IfExp(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Attribute(self, node):
        """Checks and mutates attribute access/assignment.

        'a.b' becomes '_getattr_(a, "b")'

        'a.b = c' becomes '_write_(a).b = c'
        The _write_ function should return a security proxy.
        """
        if node.attr.startswith('_') and node.attr != '_':
            self.error(
                node,
                '"{name}" is an invalid attribute name because it starts '
                'with "_".'.format(name=node.attr))

        if node.attr.endswith('__roles__'):
            self.error(
                node,
                '"{name}" is an invalid attribute name because it ends '
                'with "__roles__".'.format(name=node.attr))

        if isinstance(node.ctx, ast.Load):
            node = self.generic_visit(node)
            new_node = ast.Call(
                func=ast.Name('_getattr_', ast.Load()),
                args=[node.value, ast.Str(node.attr)],
                keywords=[])

            copy_locations(new_node, node)
            return new_node

        elif isinstance(node.ctx, ast.Store):
            node = self.generic_visit(node)
            new_value = ast.Call(
                func=ast.Name('_write_', ast.Load()),
                args=[node.value],
                keywords=[])

            copy_locations(new_value, node.value)
            node.value = new_value
            return node

        else:
            return self.generic_visit(node)

    # Subscripting

    def visit_Subscript(self, node):
        """Transforms all kinds of subscripts.

        'foo[bar]' becomes '_getitem_(foo, bar)'
        'foo[:ab]' becomes '_getitem_(foo, slice(None, ab, None))'
        'foo[ab:]' becomes '_getitem_(foo, slice(ab, None, None))'
        'foo[a:b]' becomes '_getitem_(foo, slice(a, b, None))'
        'foo[a:b:c]' becomes '_getitem_(foo, slice(a, b, c))'
        'foo[a, b:c] becomes '_getitem_(foo, (a, slice(b, c, None)))'
        'foo[a] = c' becomes '_write(foo)[a] = c'
        'del foo[a]' becomes 'del _write_(foo)[a]'

        The _write_ function should return a security proxy.
        """
        node = self.generic_visit(node)

        # 'AugStore' and 'AugLoad' are defined in 'Python.asdl' as possible
        # 'expr_context'. However, according to Python/ast.c
        # they are NOT used by the implementation => No need to worry here.
        # Instead ast.c creates 'AugAssign' nodes, which can be visited.

        if isinstance(node.ctx, ast.Load):
            new_node = ast.Call(
                func=ast.Name('_getitem_', ast.Load()),
                args=[node.value, self.transform_slice(node.slice)],
                keywords=[])

            copy_locations(new_node, node)
            return new_node

        elif isinstance(node.ctx, (ast.Del, ast.Store)):
            new_value = ast.Call(
                func=ast.Name('_write_', ast.Load()),
                args=[node.value],
                keywords=[])

            copy_locations(new_value, node)
            node.value = new_value
            return node

        else:
            return node

    def visit_Index(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Slice(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_ExtSlice(self, node):
        """

        """
        return self.generic_visit(node)

    # Comprehensions

    def visit_ListComp(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_SetComp(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_DictComp(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_comprehension(self, node):
        """

        """
        return self.guard_iter(node)

    # Statements

    def visit_Assign(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_AugAssign(self, node):
        """Forbid certain kinds of AugAssign

        According to the language reference (and ast.c) the following nodes
        are are possible:
        Name, Attribute, Subscript

        Note that although augmented assignment of attributes and
        subscripts is disallowed, augmented assignment of names (such
        as 'n += 1') is allowed.
        'n += 1' becomes 'n = _inplacevar_("+=", n, 1)'
        """

        node = self.generic_visit(node)

        if isinstance(node.target, ast.Attribute):
            self.error(
                node,
                "Augmented assignment of attributes is not allowed.")
            return node

        elif isinstance(node.target, ast.Subscript):
            self.error(
                node,
                "Augmented assignment of object items "
                "and slices is not allowed.")
            return node

        elif isinstance(node.target, ast.Name):
            new_node = ast.Assign(
                targets=[node.target],
                value=ast.Call(
                    func=ast.Name('_inplacevar_', ast.Load()),
                    args=[
                        ast.Str(IOPERATOR_TO_STR[type(node.op)]),
                        ast.Name(node.target.id, ast.Load()),
                        node.value
                    ],
                    keywords=[]))

            copy_locations(new_node, node)
            return new_node

        return node

    def visit_Print(self, node):
        """
        Fields:
        * dest (optional)
        * value --> List of Nodes
        * nl --> newline (True or False)
        """
        if node.dest is not None:
            self.error(
                node,
                'print statements with destination / chevron are not allowed.')

    def visit_Raise(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Assert(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Delete(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Pass(self, node):
        """

        """
        return self.generic_visit(node)

    # Imports

    def visit_Import(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_alias(self, node):
        """

        """
        return self.generic_visit(node)

    # Control flow

    def visit_If(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_For(self, node):
        """

        """
        return self.guard_iter(node)

    def visit_While(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Break(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Continue(self, node):
        """

        """
        return self.generic_visit(node)

#    def visit_Try(self, node):
#        """
#
#        """
#        return self.generic_visit(node)

#    def visit_TryFinally(self, node):
#        """
#
#        """
#        return self.generic_visit(node)

#    def visit_TryExcept(self, node):
#        """
#
#        """
#        return self.generic_visit(node)

#    def visit_ExceptHandler(self, node):
#        """
#
#        """
#        return self.generic_visit(node)

    def visit_With(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_withitem(self, node):
        """

        """
        return self.generic_visit(node)

    # Function and class definitions

    def visit_FunctionDef(self, node):
        """Checks a function defintion.

        Checks the name of the function and the arguments.
        """

        self.check_name(node, node.name)

        # In python3 arguments are always identifiers.
        # In python2 the 'Python.asdl' specifies expressions, but
        # the python grammer allows only identifiers or a tuple of
        # identifiers. If its a tuple 'tuple parameter unpacking' is used,
        # which is gone in python3.
        # See https://www.python.org/dev/peps/pep-3113/

        if version.major == 2:
            # Needed to handle nested 'tuple parameter unpacking'.
            # For example 'def foo((a, b, (c, (d, e)))): pass'
            to_check = list(node.args.args)
            while to_check:
                item = to_check.pop()
                if isinstance(item, ast.Tuple):
                    to_check.extend(item.elts)
                else:
                    self.check_name(node, item.id)

            self.check_name(node, node.args.vararg)
            self.check_name(node, node.args.kwarg)

        else:
            for arg in node.args.args:
                self.check_name(node, arg.arg)

            if node.args.vararg:
                self.check_name(node, node.args.vararg.arg)

            if node.args.kwarg:
                self.check_name(node, node.args.kwarg.arg)

            for arg in node.args.kwonlyargs:
                self.check_name(node, arg.arg)

        node = self.generic_visit(node)

        if version.major == 3:
            return node

        # Protect 'tuple parameter unpacking' with '_getiter_'.
        # Without this individual items from an arbitrary iterable are exposed.
        # _getiter_ applies security checks to each item the iterable delivers.
        # To apply these check to each item their container (the iterable) is
        # used. So a simple a = _guard(a) does not work.
        #
        # Here are two example how the code transformation looks like:
        # Example 1):
        #  def foo((a, b)): pass
        # is converted itno
        #  def foo(_tmp0):
        #      try:
        #          (a, b) = _getiter_(_tmp0)
        #      finally:
        #          del _tmp0
        #
        # Nested unpacking is also  supported:
        #  def foo((a, (b, c))): pass
        # is converted into
        #  def foo(_tmp0):
        #      try:
        #          (a, (_tmp1)) = _getiter_(_tmp0)
        #          try:
        #              (b, c) = _getiter_(_tmp1)
        #          finally:
        #              del _tmp1
        #      finally:
        #          del _tmp0

        unpacks = []
        for index, arg in enumerate(list(node.args.args)):
            if isinstance(arg, ast.Tuple):
                child = self.transform_seq_unpack(arg)

                # Replace the tuple with a single (temporary) parameter.
                node.args.args[index] = ast.Name(child['name'], ast.Param())

                copy_locations(node.args.args[index], node)
                copy_locations(child['body'], node)
                unpacks.append(child['body'])

        # Add the unpacks at the front of the body.
        # Keep the order, so that tuple one is unpacked first.
        node.body[0:0] = unpacks
        return node

    def visit_Lambda(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_arguments(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_arg(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Return(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Yield(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_YieldFrom(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Global(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Nonlocal(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_ClassDef(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Module(self, node):
        """

        """
        return self.generic_visit(node)

    # Async und await

    def visit_AsyncFunctionDef(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Await(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_AsyncFor(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_AsyncWith(self, node):
        """

        """
        return self.generic_visit(node)
