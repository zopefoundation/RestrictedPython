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

from RestrictedPython.RCompile import compile_restricted
from RestrictedPython.RCompile import compile_restricted_eval
from RestrictedPython.RCompile import compile_restricted_exec
from RestrictedPython.RCompile import compile_restricted_function
from RestrictedPython.PrintCollector import PrintCollector

from RestrictedPython.Eval import RestrictionCapableEval

from RestrictedPython.Guards import safe_builtins
from RestrictedPython.Utilities import utility_builtins
from RestrictedPython.Limits import limited_builtins

from zope.deprecation import deprecation

compile_restricted_eval = deprecation.deprecated(compile_restricted_eval, 'compile_restricted_eval is deprecated, please use compile_restricted(source, filename, mode="eval") instead')
compile_restricted_exec = deprecation.deprecated(compile_restricted_exec, 'compile_restricted_exec is deprecated, please use compile_restricted(source, filename, mode="exec") instead')
compile_restricted_function = deprecation.deprecated(compile_restricted_function, 'compile_restricted_function is deprecated, please use compile_restricted(source, filename, mode="single") instead')
RestrictionCapableEval = deprecation.deprecated(RestrictionCapableEval, 'RestrictionCapableEval is deprecated, please use instead.')

# new API Style
#from RestrictedPython.compiler import compile_restricted
