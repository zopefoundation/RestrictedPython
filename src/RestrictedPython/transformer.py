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
import contextlib
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
    ast.Param
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
        ast.Raise,
        ast.TryExcept,
        ast.TryFinally,
        ast.ExceptHandler,
    ])

if version >= (3, 0):
    AST_WHITELIST.extend([
        ast.Bytes,
        ast.Starred,
        ast.arg,
        ast.Try,
        ast.ExceptHandler,
    ])

if version >= (3, 4):
    AST_WHITELIST.extend([
        ast.NameConstant,
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


class PrintInfo(object):
    def __init__(self):
        self.print_used = False
        self.printed_used = False

    @contextlib.contextmanager
    def new_print_scope(self):
        old_print_used = self.print_used
        old_printed_used = self.printed_used

        self.print_used = False
        self.printed_used = False

        try:
            yield
        finally:
            self.print_used = old_print_used
            self.printed_used = old_printed_used


class RestrictingNodeTransformer(ast.NodeTransformer):

    def __init__(self, errors=[], warnings=[], used_names=[]):
        super(RestrictingNodeTransformer, self).__init__()
        self.errors = errors
        self.warnings = warnings
        self.used_names = used_names

        # Global counter to construct temporary variable names.
        self._tmp_idx = 0

        self.print_info = PrintInfo()

    def gen_tmp_name(self):
        # 'check_name' ensures that no variable is prefixed with '_'.
        # => Its safe to use '_tmp..' as a temporary variable.
        name = '_tmp%i' % self._tmp_idx
        self._tmp_idx += 1
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

        if isinstance(node.target, ast.Tuple):
            spec = self.gen_unpack_spec(node.target)
            new_iter = ast.Call(
                func=ast.Name('_iter_unpack_sequence_', ast.Load()),
                args=[node.iter, spec, ast.Name('_getiter_', ast.Load())],
                keywords=[])
        else:
            new_iter = ast.Call(
                func=ast.Name("_getiter_", ast.Load()),
                args=[node.iter],
                keywords=[])

        copy_locations(new_iter, node.iter)
        node.iter = new_iter
        return node

    def is_starred(self, ob):
        if version.major == 3:
            return isinstance(ob, ast.Starred)
        else:
            return False

    def gen_unpack_spec(self, tpl):
        """Generate a specification for 'guarded_unpack_sequence'.

        This spec is used to protect sequence unpacking.
        The primary goal of this spec is to tell which elements in a sequence
        are sequences again. These 'child' sequences have to be protected again.

        For example there is a sequence like this:
            (a, (b, c), (d, (e, f))) = g

        On a higher level the spec says:
            - There is a sequence of len 3
            - The element at index 1 is a sequence again with len 2
            - The element at index 2 is a sequence again with len 2
              - The element at index 1 in this subsequence is a sequence again
                with len 2

        With this spec 'guarded_unpack_sequence' does something like this for
        protection (len checks are omitted):

            t = list(_getiter_(g))
            t[1] = list(_getiter_(t[1]))
            t[2] = list(_getiter_(t[2]))
            t[2][1] = list(_getiter_(t[2][1]))
            return t

        The 'real' spec for the case above is then:
            spec = {
                'min_len': 3,
                'childs': (
                    (1, {'min_len': 2, 'childs': ()}),
                    (2, {
                            'min_len': 2,
                            'childs': (
                                (1, {'min_len': 2, 'childs': ()})
                            )
                        }
                    )
                )
            }

        So finally the assignment above is converted into:
            (a, (b, c), (d, (e, f))) = guarded_unpack_sequence(g, spec)
        """
        spec = ast.Dict(keys=[], values=[])

        spec.keys.append(ast.Str('childs'))
        spec.values.append(ast.Tuple([], ast.Load()))

        # starred elements in a sequence do not contribute into the min_len.
        # For example a, b, *c = g
        # g must have at least 2 elements, not 3. 'c' is empyt if g has only 2.
        min_len = len([ob for ob in tpl.elts if not self.is_starred(ob)])
        offset = 0

        for idx, val in enumerate(tpl.elts):
            # After a starred element specify the child index from the back.
            # Since it is unknown how many elements from the sequence are
            # consumed by the starred element.
            # For example a, *b, (c, d) = g
            # Then (c, d) has the index '-1'
            if self.is_starred(val):
                offset = min_len + 1

            elif isinstance(val, ast.Tuple):
                el = ast.Tuple([], ast.Load())
                el.elts.append(ast.Num(idx - offset))
                el.elts.append(self.gen_unpack_spec(val))
                spec.values[0].elts.append(el)

        spec.keys.append(ast.Str('min_len'))
        spec.values.append(ast.Num(min_len))

        return spec

    def protect_unpack_sequence(self, target, value):
        spec = self.gen_unpack_spec(target)
        return ast.Call(
            func=ast.Name('_unpack_sequence_', ast.Load()),
            args=[value, spec, ast.Name('_getiter_', ast.Load())],
            keywords=[])

    def gen_none_node(self):
        if version >= (3, 4):
            return ast.NameConstant(value=None)
        else:
            return ast.Name(id='None', ctx=ast.Load())

    def gen_lambda(self, args, body):
        return ast.Lambda(
            args=ast.arguments(args=args, vararg=None, kwarg=None, defaults=[]),
            body=body)

    def gen_del_stmt(self, name_to_del):
        return ast.Delete(targets=[ast.Name(name_to_del, ast.Del())])

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

        elif name == "printed":
            self.error(node, '"printed" is a reserved name.')

        elif name == 'print':
            # Assignments to 'print' would lead to funny results.
            self.error(node, '"print" is a reserved name.')

    def check_function_argument_names(self, node):
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

    def check_import_names(self, node):
        """Check the names being imported.

        This is a protection against rebinding dunder names like
        _getitem_, _write_ via imports.

        => 'from _a import x' is ok, because '_a' is not added to the scope.
        """
        for alias in node.names:
            self.check_name(node, alias.name)
            if alias.asname:
                self.check_name(node, alias.asname)

        return self.generic_visit(node)

    def inject_print_collector(self, node, position=0):
        print_used = self.print_info.print_used
        printed_used = self.print_info.printed_used

        if print_used or printed_used:
            # Add '_print = _print_(_getattr_)' add the top of a function/module.
            _print = ast.Assign(
                targets=[ast.Name('_print', ast.Store())],
                value=ast.Call(
                    func=ast.Name("_print_", ast.Load()),
                    args=[ast.Name("_getattr_", ast.Load())],
                    keywords=[]))

            if isinstance(node, ast.Module):
                _print.lineno = position
                _print.col_offset = position
                ast.fix_missing_locations(_print)
            else:
                copy_locations(_print, node)

            node.body.insert(position, _print)

            if not printed_used:
                self.warn(node, "Prints, but never reads 'printed' variable.")

            elif not print_used:
                self.warn(node, "Doesn't print, but reads 'printed' variable.")

    def gen_attr_check(self, node, attr_name):
        """Check if 'attr_name' is allowed on the object in node.

        It generates (_getattr_(node, attr_name) and node).
        """

        call_getattr = ast.Call(
            func=ast.Name('_getattr_', ast.Load()),
            args=[node, ast.Str(attr_name)],
            keywords=[])

        return ast.BoolOp(op=ast.And(), values=[call_getattr, node])

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
        """Prevents access to protected names.

        Converts use of the name 'printed' to this expression: '_print()'
        """

        node = self.generic_visit(node)

        if isinstance(node.ctx, ast.Load):
            if node.id == 'printed':
                self.print_info.printed_used = True
                new_node = ast.Call(
                    func=ast.Name("_print", ast.Load()),
                    args=[],
                    keywords=[])

                copy_locations(new_node, node)
                return new_node

            elif node.id == 'print':
                self.print_info.print_used = True
                new_node = ast.Attribute(
                    value=ast.Name('_print', ast.Load()),
                    attr="_call_print",
                    ctx=ast.Load())

                copy_locations(new_node, node)
                return new_node

        self.check_name(node, node.id)
        return node

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

        node = self.generic_visit(node)

        if not any(isinstance(t, ast.Tuple) for t in node.targets):
            return node

        # Handle sequence unpacking.
        # For briefness this example omits cleanup of the temporary variables.
        # Check 'transform_tuple_assign' how its done.
        #
        # - Single target (with nested support)
        # (a, (b, (c, d))) = <exp>
        # is converted to
        # (a, t1) = _getiter_(<exp>)
        # (b, t2) = _getiter_(t1)
        # (c, d) = _getiter_(t2)
        #
        # - Multi targets
        # (a, b) = (c, d) = <exp>
        # is converted to
        # (c, d) = _getiter_(<exp>)
        # (a, b) = _getiter_(<exp>)
        # Why is this valid ? The original bytecode for this multi targets
        # behaves the same way.

        # ast.NodeTransformer works with list results.
        # He injects it at the right place of the node's parent statements.
        new_nodes = []

        # python fills the right most target first.
        for target in reversed(node.targets):
            if isinstance(target, ast.Tuple):
                wrapper = ast.Assign(
                    targets=[target],
                    value=self.protect_unpack_sequence(target, node.value))
                new_nodes.append(wrapper)
            else:
                new_node = ast.Assign(targets=[target], value=node.value)
                new_nodes.append(new_node)

        for new_node in new_nodes:
            copy_locations(new_node, node)

        return new_nodes

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
        """Checks and mutates a print statement.

        Adds a target to all print statements.  'print foo' becomes
        'print >> _print, foo', where _print is the default print
        target defined for this scope.

        Alternatively, if the untrusted code provides its own target,
        we have to check the 'write' method of the target.
        'print >> ob, foo' becomes
        'print >> (_getattr_(ob, 'write') and ob), foo'.
        Otherwise, it would be possible to call the write method of
        templates and scripts; 'write' happens to be the name of the
        method that changes them.
        """

        self.print_info.print_used = True

        node = self.generic_visit(node)
        if node.dest is None:
            node.dest = ast.Name('_print', ast.Load())
        else:
            # Pre-validate access to the 'write' attribute.
            node.dest = self.gen_attr_check(node.dest, 'write')

        copy_locations(node.dest, node)
        return node

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
        """ """
        return self.check_import_names(node)

    def visit_ImportFrom(self, node):
        """ """
        return self.check_import_names(node)

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

    def visit_ExceptHandler(self, node):
        """Protects tuple unpacking on exception handlers.

        try:
            .....
        except Exception as (a, b):
            ....

        becomes

        try:
            .....
        except Exception as tmp:
            try:
                (a, b) = _getiter_(tmp)
            finally:
                del tmp
        """

        node = self.generic_visit(node)

        if version.major == 3:
            return node

        if not isinstance(node.name, ast.Tuple):
            return node

        # Generate a tmp name to replace the tuple with.
        tmp_name = self.gen_tmp_name()

        # Generates an expressions which protects the unpack.
        converter = self.protect_unpack_sequence(
            node.name,
            ast.Name(tmp_name, ast.Load()))

        # Assign the expression to the original names.
        # Cleanup the temporary variable.
        cleanup = ast.TryFinally(
            body=[ast.Assign(targets=[node.name], value=converter)],
            finalbody=[self.gen_del_stmt(tmp_name)]

        )

        # Repalce the tuple with the temporary variable.
        node.name = ast.Name(tmp_name, ast.Store())

        copy_locations(cleanup, node)
        copy_locations(node.name, node)
        node.body.insert(0, cleanup)

        return node

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
        self.check_function_argument_names(node)

        with self.print_info.new_print_scope():
            node = self.generic_visit(node)
            self.inject_print_collector(node)

        if version.major == 3:
            return node

        # Protect 'tuple parameter unpacking' with '_getiter_'.

        unpacks = []
        for index, arg in enumerate(list(node.args.args)):
            if isinstance(arg, ast.Tuple):
                tmp_name = self.gen_tmp_name()

                # converter looks like wrapper(tmp_name).
                # Wrapper takes care to protect
                # sequence unpacking with _getiter_
                converter = self.protect_unpack_sequence(
                        arg,
                        ast.Name(tmp_name, ast.Load()))

                # Generates:
                # try:
                #     # converter is 'wrapper(tmp_name)'
                #     arg = converter
                # finally:
                #     del tmp_arg
                cleanup = ast.TryFinally(
                    body=[ast.Assign(targets=[arg], value=converter)],
                    finalbody=[self.gen_del_stmt(tmp_name)]
                )

                # Replace the tuple with a single (temporary) parameter.
                node.args.args[index] = ast.Name(tmp_name, ast.Param())

                copy_locations(node.args.args[index], node)
                copy_locations(cleanup, node)
                unpacks.append(cleanup)

        # Add the unpacks at the front of the body.
        # Keep the order, so that tuple one is unpacked first.
        node.body[0:0] = unpacks
        return node

    def visit_Lambda(self, node):
        """Checks a lambda definition."""
        self.check_function_argument_names(node)

        node = self.generic_visit(node)

        if version.major == 3:
            return node

        # Check for tuple parameters which need _getiter_ protection
        if not any(isinstance(arg, ast.Tuple) for arg in node.args.args):
            return node

        # Wrap this lambda function with another. Via this wrapping it is
        # possible to protect the 'tuple arguments' with _getiter_
        outer_params = []
        inner_args = []

        for arg in node.args.args:
            if isinstance(arg, ast.Tuple):
                tmp_name = self.gen_tmp_name()
                converter = self.protect_unpack_sequence(
                    arg,
                    ast.Name(tmp_name, ast.Load()))

                outer_params.append(ast.Name(tmp_name, ast.Param()))
                inner_args.append(converter)

            else:
                outer_params.append(arg)
                inner_args.append(ast.Name(arg.id, ast.Load()))

        body = ast.Call(func=node, args=inner_args, keywords=[])
        new_node = self.gen_lambda(outer_params, body)

        if node.args.vararg:
            new_node.args.vararg = node.args.vararg
            body.starargs = ast.Name(node.args.vararg, ast.Load())

        if node.args.kwarg:
            new_node.args.kwarg = node.args.kwarg
            body.kwargs = ast.Name(node.args.kwarg, ast.Load())

        copy_locations(new_node, node)
        return new_node

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
        """Check the name of a class definition."""

        self.check_name(node, node.name)
        return self.generic_visit(node)

    def visit_Module(self, node):
        """Adds the print_collector (only if print is used) at the top."""

        node = self.generic_visit(node)

        # Inject the print collector after 'from __future__ import ....'
        position = 0
        for position, child in enumerate(node.body):
            if not isinstance(child, ast.ImportFrom):
                break

            if not child.module == '__future__':
                break

        self.inject_print_collector(node, position)
        return node

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
