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


# apply() variations.  Native apply() is unsafe because, e.g.,
#
#     def f(a, b, c):
#         whatever
#
#     apply(f, two_element_sequence, dict_with_key_c)
#
# or (different spelling of the same thing)
#
#     f(*two_element_sequence, **dict_with_key_c)
#
# makes the elements of two_element_sequence visible to f via its 'a' and
# 'b' arguments, and the dict_with_key_c['c'] value visible via its 'c'
# argument.  That is, it's a devious way to extract values without going
# thru security checks.

def star_call_before():
    foo(*a)


def star_call_after():
    _apply_(foo, *a)


def star_call_2_before():
    foo(0, *a)


def star_call_2_after():
    _apply_(foo, 0, *a)


def starstar_call_before():
    foo(**d)


def starstar_call_after():
    _apply_(foo, **d)


def star_and_starstar_call_before():
    foo(*a, **d)


def star_and_starstar_call_after():
    _apply_(foo, *a, **d)


def positional_and_star_and_starstar_call_before():
    foo(b, *a, **d)


def positional_and_star_and_starstar_call_after():
    _apply_(foo, b, *a, **d)


def positional_and_defaults_and_star_and_starstar_call_before():
    foo(b, x=y, w=z, *a, **d)


def positional_and_defaults_and_star_and_starstar_call_after():
    _apply_(foo, b, x=y, w=z, *a, **d)


def lambda_with_getattr_in_defaults_before():
    f = lambda x=y.z: x


def lambda_with_getattr_in_defaults_after():
    f = lambda x=_getattr_(y, "z"): x


# augmented operators
# Note that we don't have to worry about item, attr, or slice assignment,
# as they are disallowed. Yay!
#
# def inplace_id_add_before():
#     x += y+z
#
# def inplace_id_add_after():
#     x = _inplacevar_('+=', x, y+z)
