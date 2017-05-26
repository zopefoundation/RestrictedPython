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

# flake8: NOQA: 401
# isort: skip
# TODO: Drop whole file on getting rid of old implementation.

from compiler import ast
from compiler.consts import OP_APPLY
from compiler.consts import OP_ASSIGN
from compiler.consts import OP_DELETE
from compiler.transformer import parse
from RCompile import compile_restricted
from RCompile import compile_restricted_eval
from RCompile import compile_restricted_exec
from RCompile import compile_restricted_function

import compiler  # Use the compiler from the standard library.
import warnings


warnings.warn(
    "This Module (RestrictedPython.SelectCompiler) is deprecated"
    "and will be gone soon.",
    category=PendingDeprecationWarning,
    stacklevel=1
)
