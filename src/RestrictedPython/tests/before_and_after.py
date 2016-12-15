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

# this, and all slices, won't work in these tests because the before code
# parses the slice as a slice object, while the after code can't generate a
# slice object in this way.  The after code as written below
# is parsed as a call to the 'slice' name, not as a slice object.
# XXX solutions?

# Assignment stmts in Python can be very complicated.  The "no_unpack"
# test makes sure we're not doing unnecessary rewriting.
def no_unpack_before():
    x = y
    x = [y]
    x = y,
    x = (y, (y, y), [y, (y,)], x, (x, y))
    x = y = z = (x, y, z)

no_unpack_after = no_unpack_before    # that is, should be untouched

"""
