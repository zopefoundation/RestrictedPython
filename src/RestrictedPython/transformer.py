
import ast
import sys

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
    #ast.Starred,
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
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.LShift,
    ast.RShift,
    ast.BitOr,
    ast.BitAnd,
    #ast.MatMult,
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
    ast.With,
    #ast.withitem,
    # Function and class definitions,
    ast.FunctionDef,
    ast.Lambda,
    ast.arguments,
    #ast.arg,
    ast.Return,
    #ast.Yield,
    #ast.YieldFrom,
    #ast.Global,
    #ast.Nonlocal,
    ast.ClassDef,
    ast.Module,
]

version = sys.version_info
if version >= (2, 7) and version <= (2, 8):
    AST_WHITELIST.extend([
        ast.Print,
    ])

if version >= (3, 0):
    AST_WHITELIST.extend([
        ast.Bytes,
    ])

if version >= (3, 5):
    AST_WHITELIST.extend([
        # Async und await,  # No Async Elements
        #ast.AsyncFunctionDef,  # No Async Elements
        #ast.Await,  # No Async Elements
        #ast.AsyncFor,  # No Async Elements
        #ast.AsyncWith,  # No Async Elements
    ])


class RestrictingNodeTransformer(ast.NodeTransformer):

    def __init__(self, errors=[], warnings=[], used_names=[]):
        super(RestrictingNodeTransformer, self).__init__()
        self.errors = errors
        self.warnings = warnings
        self.used_names = used_names

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

    # Special Functions for an ast.NodeTransformer

    def generic_visit(self, node):
        if node.__class__ not in AST_WHITELIST:
            self.error(
                node,
                '{0.__class__.__name__} statements are not allowed.'.format(
                    node))
        else:
            return super(RestrictingNodeTransformer, self).generic_visit(node)

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
        if node.id.startswith('_'):
            self.error(node, '"{name}" is an invalid variable name because it starts with "_"'.format(name=node.id))
            self.error(node, 'Attribute names starting with "_" are not allowed.')
        else:
            return self.generic_visit(node)
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

    def visit_Expr(self, node):
        """

        """
        return self.generic_visit(node)

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
        """
        func, args, keywords, starargs, kwargs
        """
        if node.func.id == 'exec':
            self.error(node, 'Exec statements are not allowed.')
        elif node.func.id == 'eval':
            self.error(node, 'Eval functions are not allowed.')
        else:
            return self.generic_visit(node)

    def visit_keyword(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_IfExp(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr.startswith('_'):
            self.error(
                node, '"{name}" is an invalid attribute name because it starts with "_".'.format(name=node.attr))
        else:
            return self.generic_visit(node)

    # Subscripting

    def visit_Subscript(self, node):
        """

        """
        return self.generic_visit(node)

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
        return self.generic_visit(node)

    # Statements

    def visit_Assign(self, node):
        """

        """
        return self.generic_visit(node)

    def visit_AugAssign(self, node):
        """

        """
        return self.generic_visit(node)

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
        return self.generic_visit(node)

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
        """

        """
        return self.generic_visit(node)

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
