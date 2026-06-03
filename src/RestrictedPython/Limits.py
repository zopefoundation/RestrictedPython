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
import collections.abc
import typing


limited_builtins: dict[str, typing.Any] = {}


@typing.overload
def limited_range(iFirst: int) -> collections.abc.Sequence[int]: ...


@typing.overload
def limited_range(iStart: int, iEnd: int, /
                  ) -> collections.abc.Sequence[int]: ...


@typing.overload
def limited_range(iStart: int, iEnd: int, iStep: int, /
                  ) -> collections.abc.Sequence[int]: ...


def limited_range(iFirst: int, *args: int) -> collections.abc.Sequence[int]:
    # limited range function from Martijn Pieters
    RANGELIMIT = 1000
    if not len(args):
        iStart, iEnd, iStep = 0, iFirst, 1
    elif len(args) == 1:
        iStart, iEnd, iStep = iFirst, args[0], 1
    elif len(args) == 2:
        iStart, iEnd, iStep = iFirst, args[0], args[1]
    else:
        raise AttributeError('range() requires 1-3 int arguments')
    if iStep == 0:
        raise ValueError('zero step for range()')
    iLen = int((iEnd - iStart) / iStep)
    if iLen < 0:
        iLen = 0
    if iLen >= RANGELIMIT:
        raise ValueError(
            'To be created range() object would be to large, '
            'in RestrictedPython we only allow {limit} '
            'elements in a range.'.format(limit=str(RANGELIMIT)),
        )
    return range(iStart, iEnd, iStep)


limited_builtins['range'] = limited_range

_T = typing.TypeVar('_T')


def limited_list(seq: collections.abc.Iterable[_T]) -> list[_T]:
    if isinstance(seq, str):
        raise TypeError('cannot convert string to list')
    return list(seq)


limited_builtins['list'] = limited_list


def limited_tuple(seq: collections.abc.Iterable[_T]) -> tuple[_T, ...]:
    if isinstance(seq, str):
        raise TypeError('cannot convert string to tuple')
    return tuple(seq)


limited_builtins['tuple'] = limited_tuple
