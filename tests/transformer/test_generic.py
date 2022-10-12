from RestrictedPython import RestrictingNodeTransformer

import ast


def test_RestrictingNodeTransformer__generic_visit__1():
    """It log an error if there is an unknown ast node visited."""
    class MyFancyNode(ast.AST):
        pass

    transformer = RestrictingNodeTransformer()
    transformer.visit(MyFancyNode())
    assert transformer.errors == [
        'Line None: MyFancyNode statements are not allowed.']
    assert transformer.warnings == [
        'Line None: MyFancyNode statement is not known to RestrictedPython']
