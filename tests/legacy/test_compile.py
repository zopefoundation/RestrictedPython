# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from RestrictedPython._compat import IS_PY2
from RestrictedPython._compat import IS_PY3

import pytest

if IS_PY2:
    from RestrictedPython.RCompile import _niceParse
    import compiler

pytestmark = pytest.mark.skipif(
    IS_PY3,
    reason="legacy tests against old implementation")


source = u"u'Ä väry nice säntänce with umlauts.'"


def test_unicode_source_exec():
    assert isinstance(_niceParse(source, "test.py", "exec"),
                      compiler.ast.Module)


def test_unicode_source_single():
    assert isinstance(_niceParse(source, "test.py", "single"),
                      compiler.ast.Module)


def test_unicode_source_eval():
    assert isinstance(_niceParse(source, "test.py", "eval"),
                      compiler.ast.Expression)
