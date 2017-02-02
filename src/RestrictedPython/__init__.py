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

# Old API --> Old Import Locations
# from RestrictedPython.RCompile import compile_restricted
# from RestrictedPython.RCompile import compile_restricted_eval
# from RestrictedPython.RCompile import compile_restricted_exec
# from RestrictedPython.RCompile import compile_restricted_function

# new API Style
from RestrictedPython.compile import compile_restricted
from RestrictedPython.compile import compile_restricted_eval
from RestrictedPython.compile import compile_restricted_exec
from RestrictedPython.compile import compile_restricted_function
from RestrictedPython.compile import compile_restricted_single
from RestrictedPython.compile import CompileResult
from RestrictedPython.Guards import safe_builtins
from RestrictedPython.Limits import limited_builtins
from RestrictedPython.PrintCollector import PrintCollector
from RestrictedPython.Utilities import utility_builtins


# from RestrictedPython.Eval import RestrictionCapableEval
