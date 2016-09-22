from RestrictedPython.transformer import RestrictingNodeTransformer
import ast


def compile_restricted(
        source, filename='<unknown>', mode='exec', flags=0, dont_inherit=0):
    """Replacement for the built-in compile() function."""
    c_ast = ast.parse(source, filename, mode)
    r_ast = RestrictingNodeTransformer().visit(c_ast)
    return compile(r_ast, filename, mode, flags, dont_inherit)
