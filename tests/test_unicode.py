# -*- coding: utf-8 -*-
import ast


# Port of file: tests/testCompile.py

def test_unicode_source():
    """
    Test if the AST Parsing works with Unicode source.
    """
    # TODO: Review is that is really somethin we want to test this way.
    # ast.parse is a python core method and should be tested there.
    # RestrictedPython.RCompile _niceParse is not reimplemented.
    source = u"u'Ä väry nice säntänce with umlauts.'"

    assert isinstance(ast.parse(source, "test.py", "exec"), ast.Module)
    assert isinstance(ast.parse(source, "test.py", "single"), ast.Interactive)
    assert isinstance(ast.parse(source, "test.py", "eval"), ast.Expression)
