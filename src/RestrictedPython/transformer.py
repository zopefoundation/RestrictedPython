
import ast
import sys

AST_WHITELIST = [
    ast.Call,  # see visit_Call for restrictions
    ast.Expr,
    ast.FunctionDef,
    ast.List,
    ast.Load,
    ast.Module,
    ast.Name,
    ast.Num,
    ast.Str,
]

version = sys.version_info
if version <= (2, 8):
    AST_WHITELIST.extend([
        ast.Print
    ])
elif version >= (3, 5):
    AST_WHITELIST.extend([
        ast.AsyncFunctionDef
    ])


class RestrictingNodeTransformer(ast.NodeTransformer):

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, node, info):
        """Record a security error discovered during transformation."""
        lineno = getattr(node, 'lineno', None)
        self.errors.append('Line {}: {}'.format(lineno, info))

    # Special Functions for an ast.NodeTransformer

    def visit(self, node):
        import ipdb; ipdb.set_trace()
        code = super(RestrictingNodeTransformer, self).visit(node)
        if self.errors:
            raise SyntaxError('\n'.join(self.errors))
        return code

    def generic_visit(self, node):
        if node.__class__ not in AST_WHITELIST:
            self.error(
                node,
                '{0.__class__.__name__} statements are not allowed.'.format(
                    node))
        else:
            return super(RestrictingNodeTransformer, self).generic_visit(node)

    ## ast for Literals

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

    ## ast for Variables

    def visit_Name(self, node):
        """

        """
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

    ## Expressions

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











    def visit_Call(self, node):
        if node.func.id == 'exec':
            self.error(node, 'Exec statements are not allowed.')
        else:
            return self.generic_visit(node)

    def visit_Print(self, node):
        if node.dest is not None:
            self.error(
                node,
                'print statements with destination / chevron are not allowed.')
        else:
            return self.generic_visit(node)
