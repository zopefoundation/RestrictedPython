##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Compiler selector.
"""

from compiler import ast
from compiler.consts import OP_APPLY
from compiler.consts import OP_ASSIGN
from compiler.consts import OP_DELETE
from compiler.transformer import parse
from RestrictedPython.RCompile import compile_restricted
from RestrictedPython.RCompile import compile_restricted_eval
from RestrictedPython.RCompile import compile_restricted_exec
from RestrictedPython.RCompile import compile_restricted_function

# Use the compiler from the standard library.
import compiler
