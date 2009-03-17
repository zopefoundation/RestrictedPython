##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Run tests in README.txt
"""
import unittest

class UtilitiesTests(unittest.TestCase):

    def test_string_in_utility_builtins(self):
        import string
        from RestrictedPython.Utilities import utility_builtins
        self.failUnless(utility_builtins['string'] is string)

    def test_math_in_utility_builtins(self):
        import math
        from RestrictedPython.Utilities import utility_builtins
        self.failUnless(utility_builtins['math'] is math)

    def test_whrandom_in_utility_builtins(self):
        import random
        from RestrictedPython.Utilities import utility_builtins
        self.failUnless(utility_builtins['whrandom'] is random)

    def test_random_in_utility_builtins(self):
        import random
        from RestrictedPython.Utilities import utility_builtins
        self.failUnless(utility_builtins['random'] is random)

    def test_sets_in_utility_builtins_if_importable(self):
        import warnings
        from RestrictedPython.Utilities import utility_builtins
        _old_filters = warnings.filters[:]
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        try:
            try:
                import sets
            except ImportError:
                sets = None
        finally:
            warnings.filters[:] = _old_filters
        self.failUnless(utility_builtins['sets'] is sets)

    def test_DateTime_in_utility_builtins_if_importable(self):
        try:
            import DateTime
        except ImportError:
            pass
        else:
            from RestrictedPython.Utilities import utility_builtins
            self.failUnless('DateTime' in utility_builtins)

    def test_sequence_in_utility_builtins_if_importable(self):
        try:
            import DocumentTemplate.sequence
        except ImportError:
            pass
        else:
            from RestrictedPython.Utilities import utility_builtins
            self.failUnless('sequence' in utility_builtins)

    def test_same_type_in_utility_builtins(self):
        from RestrictedPython.Utilities import same_type
        from RestrictedPython.Utilities import utility_builtins
        self.failUnless(utility_builtins['same_type'] is same_type)

    def test_test_in_utility_builtins(self):
        from RestrictedPython.Utilities import test
        from RestrictedPython.Utilities import utility_builtins
        self.failUnless(utility_builtins['test'] is test)

    def test_reorder_in_utility_builtins(self):
        from RestrictedPython.Utilities import reorder
        from RestrictedPython.Utilities import utility_builtins
        self.failUnless(utility_builtins['reorder'] is reorder)

    def test_sametype_only_one_arg(self):
        from RestrictedPython.Utilities import same_type
        self.failUnless(same_type(object()))

    def test_sametype_only_two_args_same(self):
        from RestrictedPython.Utilities import same_type
        self.failUnless(same_type(object(), object()))

    def test_sametype_only_two_args_different(self):
        from RestrictedPython.Utilities import same_type
        class Foo(object):
            pass
        self.failIf(same_type(object(), Foo()))

    def test_sametype_only_multiple_args_same(self):
        from RestrictedPython.Utilities import same_type
        self.failUnless(same_type(object(), object(), object(), object()))

    def test_sametype_only_multipe_args_one_different(self):
        from RestrictedPython.Utilities import same_type
        class Foo(object):
            pass
        self.failIf(same_type(object(), object(), Foo()))

    def test_test_single_value_true(self):
        from RestrictedPython.Utilities import test
        self.failUnless(test(True))

    def test_test_single_value_False(self):
        from RestrictedPython.Utilities import test
        self.failIf(test(False))

    def test_test_even_values_first_true(self):
        from RestrictedPython.Utilities import test
        self.assertEqual(test(True, 'first', True, 'second'), 'first')

    def test_test_even_values_not_first_true(self):
        from RestrictedPython.Utilities import test
        self.assertEqual(test(False, 'first', True, 'second'), 'second')

    def test_test_odd_values_first_true(self):
        from RestrictedPython.Utilities import test
        self.assertEqual(test(True, 'first', True, 'second', False), 'first')

    def test_test_odd_values_not_first_true(self):
        from RestrictedPython.Utilities import test
        self.assertEqual(test(False, 'first', True, 'second', False), 'second')

    def test_test_odd_values_last_true(self):
        from RestrictedPython.Utilities import test
        self.assertEqual(test(False, 'first', False, 'second', 'third'),
                         'third')

    def test_test_odd_values_last_false(self):
        from RestrictedPython.Utilities import test
        self.assertEqual(test(False, 'first', False, 'second', False), False)

    def test_reorder_with__None(self):
        from RestrictedPython.Utilities import reorder
        before = ['a', 'b', 'c', 'd', 'e']
        without = ['a', 'c', 'e']
        after = reorder(before, without=without)
        self.assertEqual(after, [('b', 'b'), ('d', 'd')])

    def test_reorder_with__not_None(self):
        from RestrictedPython.Utilities import reorder
        before = ['a', 'b', 'c', 'd', 'e']
        with_ = ['a', 'd']
        without = ['a', 'c', 'e']
        after = reorder(before, with_=with_, without=without)
        self.assertEqual(after, [('d', 'd')])

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(UtilitiesTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

