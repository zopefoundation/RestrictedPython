##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
__doc__='''Read-only Mapping class based on MultiMapping

$Id$'''
__version__='$Revision: 1.3 $'[11:-2]

from MultiMapping import MultiMapping

_marker = []

class SafeMapping(MultiMapping):
    '''Mapping with security declarations and limited method exposure.

    Since it subclasses MultiMapping, this class can be used to wrap
    one or more mapping objects.  Restricted Python code will not be
    able to mutate the SafeMapping or the wrapped mappings, but will be
    able to read any value.
    '''
    __allow_access_to_unprotected_subobjects__ = 1
    push = pop = None
    def _push(self, ob):
        MultiMapping.push(self, ob)
    def _pop(self, *args):
        if args:
            return apply(MultiMapping.pop, (self,) + args)
        else:
            return MultiMapping.pop(self)
    def has_get(self, key):
        v = self.get(key, _marker)
        if v is _marker:
            return 0, None
        else:
            return 1, v
