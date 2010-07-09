##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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

# dictionary and set comprehensions

def simple_dict_comprehension_before():
    x = {y: y for y in whatever if y}

def simple_dict_comprehension_after():
    x = {y: y for y in _getiter_(whatever) if y}

def dict_comprehension_attrs_before():
    x = {y: y.q for y in whatever.z if y.q}

def dict_comprehension_attrs_after():
    x = {y: _getattr_(y, 'q') for y in _getiter_(_getattr_(whatever, 'z')) if _getattr_(y, 'q')}

def simple_set_comprehension_before():
    x = {y for y in whatever if y}

def simple_set_comprehension_after():
    x = {y for y in _getiter_(whatever) if y}
