##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""

def simple_generator_expression_before():
    x = (y**2 for y in whatever if y > 3)

def simple_generator_expression_after():
    x = (y**2 for y in _getiter_(whatever) if y > 3)

def nested_generator_expression_before():
    x = (x**2 + y**2 for x in whatever1 if x >= 0
                     for y in whatever2 if y >= x)

def nested_generator_expression_after():
    x = (x**2 + y**2 for x in _getiter_(whatever1) if x >= 0
                     for y in _getiter_(whatever2) if y >= x)
