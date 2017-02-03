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

# Need to be ported
from RestrictedPython.RCompile import _niceParse

import compiler.ast
import unittest


class CompileTests(unittest.TestCase):

    def testUnicodeSource(self):
        # We support unicode sourcecode.
        source = u"u'Ä väry nice säntänce with umlauts.'"

        parsed = _niceParse(source, "test.py", "exec")
        self.failUnless(isinstance(parsed, compiler.ast.Module))
        parsed = _niceParse(source, "test.py", "single")
        self.failUnless(isinstance(parsed, compiler.ast.Module))
        parsed = _niceParse(source, "test.py", "eval")
        self.failUnless(isinstance(parsed, compiler.ast.Expression))


def test_suite():
    return unittest.makeSuite(CompileTests)
