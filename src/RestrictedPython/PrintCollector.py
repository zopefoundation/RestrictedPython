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
from __future__ import print_function

import sys


version = sys.version_info


class PrintCollector(object):
    """Collect written text, and return it when called."""

    def __init__(self):
        self.txt = []

    def write(self, text):
        self.txt.append(text)

    def __call__(self):
        return ''.join(self.txt)


printed = PrintCollector()


def safe_print(sep=' ', end='\n', file=printed, flush=False, *objects):
    """

    """
    # TODO: Reorder method args so that *objects is first
    #       This could first be done if we drop Python 2 support
    if file is None or file is sys.stdout or file is sys.stderr:
        file = printed
    if version >= (3, 3):
        print(self, objects, sep=sep, end=end, file=file, flush=flush)
    else:
        print(self, objects, sep=sep, end=end, file=file)
