##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Restricted Python transformation examples

This module contains pairs of functions. Each pair has a before and an
after function.  The after function shows the source code equivalent
of the before function after it has been modified by the restricted
compiler.

These examples are actually used in the testRestrictions.py
checkBeforeAndAfter() unit tests, which verifies that the restricted compiler
actually produces the same output as would be output by the normal compiler
for the after function.

$Id: before_and_after24.py 76322 2007-06-04 17:40:03Z philikon $
"""

def simple_context_before():
    with whatever as x:
        x.y = z

def simple_context_after():
    with whatever as x:
        _write_(x).y = z

def simple_context_assign_attr_before():
    with whatever as x.y:
        x.y = z

def simple_context_assign_attr_after():
    with whatever as _write_(x).y:
        _write_(x).y = z

def simple_context_load_attr_before():
    with whatever.w as z:
        x.y = z

def simple_context_load_attr_after():
    with _getattr_(whatever, 'w') as z:
        _write_(x).y = z
