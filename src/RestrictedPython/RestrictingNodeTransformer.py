
import ast
import sys

AST_WHITELIST = [
    ast.Module,
    ast.FunctionDef,
    ast.Expr,
    ast.Num,
]

version = sys.version_info
if sys.version_info <= (2, 7):
    AST_WHITELIST.extend([
        ast.Print
    ])

elif sys.version <= (3, 0):
    AST_WHITELIST

elif sys.version <= (3, 6):
    AST_WHITELIST.extend([
        ast.AsyncFunctionDef
    ])


class RestrictingNodeTransformer(ast.NodeTransformer):

    def generic_visit(self, node):
        if node.__class__ not in AST_WHITELIST:
            raise SyntaxError(
                'Node {0.__class__.__name__!r} not allowed.'.format(node))
        else:
            return super(RestrictingNodeTransformer, self).generic_visit(node)

    def visit_arguments(self, node):
        return node
