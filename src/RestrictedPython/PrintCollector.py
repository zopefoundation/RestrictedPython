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


class PrintCollector:
    """Collect written text, and return it when called."""

    def __init__(self, _getattr_=None):  # type: ignore[no-untyped-def]
        self.txt = []
        self._getattr_ = _getattr_

    def write(self, text: str) -> None:
        self.txt.append(text)

    def __call__(self) -> str:
        return ''.join(self.txt)

    def _call_print(self, *objects, **kwargs):  # type: ignore[no-untyped-def]
        if kwargs.get('file', None) is None:
            kwargs['file'] = self
        else:
            self._getattr_(kwargs['file'], 'write')

        print(*objects, **kwargs)
