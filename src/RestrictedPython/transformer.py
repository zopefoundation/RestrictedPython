
import ast
import sys

AST_WHITELIST = [
    ast.Assign,
    ast.Call,  # see visit_Call for restrictions
    ast.Expr,
    ast.FunctionDef,
    ast.List,
    ast.Load,
    ast.Module,
    ast.Name,  # see visit_Name for restrictions
    ast.Num,
    ast.Store,
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

    def error(self, node, info):
        """Record a security error discovered during transformation."""
        lineno = getattr(node, 'lineno', None)
        self.errors.append('Line {}: {}'.format(lineno, info))

    def visit(self, node):
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

    def visit_arguments(self, node):
        return node

    def visit_Call(self, node):
        if node.func.id == 'exec':
            self.error(node, 'Exec statements are not allowed.')
        else:
            return self.generic_visit(node)

    def visit_Name(self, node):
        if node.id.startswith('__'):
            self.error(node, 'Names starting with "__" are not allowed.')
        else:
            return self.generic_visit(node)
