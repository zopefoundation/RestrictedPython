from RestrictedPython.transformer import RestrictingNodeTransformer
import ast


def compile_restricted(
        source, filename='<unknown>', mode='exec', flags=0, dont_inherit=0,
        policy=RestrictingNodeTransformer):
    """Replacement for the built-in compile() function.

    policy ... `ast.NodeTransformer` class defining the restrictions.

    """
    c_ast = ast.parse(source, filename, mode)
    r_ast = policy().visit(c_ast)
    return compile(r_ast, filename, mode, flags, dont_inherit)
