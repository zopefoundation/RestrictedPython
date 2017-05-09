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
"""RestrictedPython package."""

# flake8: NOQA: E401
# isort: skip

# This is a file to define public API in the base namespace of the package.
# use: isort:skip to supress all isort related warnings / errors,
# as this file should be logically grouped imports


# Old API --> Old Import Locations (Deprecated)
# from RestrictedPython.RCompile import compile_restricted
# from RestrictedPython.RCompile import compile_restricted_eval
# from RestrictedPython.RCompile import compile_restricted_exec
# from RestrictedPython.RCompile import compile_restricted_function

# RestrictedPython internal imports
# new API Style
# compile_restricted methods:
from RestrictedPython.compile import CompileResult
from RestrictedPython.compile import compile_restricted
from RestrictedPython.compile import compile_restricted_eval
from RestrictedPython.compile import compile_restricted_exec
from RestrictedPython.compile import compile_restricted_function
from RestrictedPython.compile import compile_restricted_single
#
from RestrictedPython.Eval import RestrictionCapableEval
# predefined builtins
from RestrictedPython.Guards import safe_builtins
from RestrictedPython.Limits import limited_builtins
# Helper Methods
from RestrictedPython.PrintCollector import PrintCollector
# Policy
from RestrictedPython.transformer import RestrictingNodeTransformer
from RestrictedPython.Utilities import utility_builtins
