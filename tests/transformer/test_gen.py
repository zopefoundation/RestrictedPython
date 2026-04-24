import ast

from RestrictedPython.transformer import RestrictingNodeTransformer


def test_RestrictingNodeTransformer__gen_none_node__1():
    node = RestrictingNodeTransformer().gen_none_node()
    assert node.value is None
    assert isinstance(node, ast.Constant)
