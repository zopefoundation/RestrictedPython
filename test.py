#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Sample test script using zope.testing.testrunner

see zope.testing testrunner.txt

$Id$
"""

import os, sys

src = os.path.join(os.path.split(sys.argv[0])[0], 'src')
sys.path.insert(0, src) # put at beginning to avoid one in site_packages

from zope.testing import testrunner

defaults = [
    '--path', src,
    '--package', 'zope.i18nmessageid',
    '--tests-pattern', '^tests$',
    ]

sys.exit(testrunner.run(defaults))

