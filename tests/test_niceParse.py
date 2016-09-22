# -*- coding: utf-8 -*-

from RestrictedPython.RCompile import niceParse
import pytest

import compiler.ast

SOURCE = u"u'Ä väry nice säntänce with umlauts.'"


def test_niceParse_exec_UnicodeSource():
    parsed = niceParse(SOURCE, "test.py", "exec")
    assert isinstance(parsed, compiler.ast.Module)


def test_niceParse_single_UnicodeSource():
    parsed = niceParse(SOURCE, "test.py", "single")
    assert isinstance(parsed, compiler.ast.Module)


def test_niceParse_eval_UnicodeSource():
    parsed = niceParse(SOURCE, "test.py", "eval")
    assert isinstance(parsed, compiler.ast.Expression)
