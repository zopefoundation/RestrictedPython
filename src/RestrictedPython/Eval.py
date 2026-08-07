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
"""Restricted Python Expressions."""

import ast
import collections
import types
import typing

from RestrictedPython._types import cast_not_none
from RestrictedPython.compile import compile_restricted_eval


nltosp = str.maketrans('\r\n', '  ')

# No restrictions.
default_guarded_getattr = getattr

_T = typing.TypeVar('_T')
_TK = typing.TypeVar('_TK', contravariant=True)
_TV = typing.TypeVar('_TV', covariant=True)


class _GetItem(typing.Protocol[_TK, _TV]):
    def __getitem__(self, key: _TK) -> _TV: ...


def default_guarded_getitem(ob: _GetItem[_TK, _TV], index: _TK) -> _TV:
    # No restrictions.
    return ob[index]


def default_guarded_getiter(ob: _T) -> _T:
    # No restrictions.
    return ob


class RestrictionCapableEval:
    """A base class for restricted code."""

    globals: dict[str, typing.Any] = {'__builtins__': None}

    # restricted
    rcode: types.CodeType | None = None

    # unrestricted
    ucode: types.CodeType | None = None

    # Names used by the expression
    used: tuple[str, ...] | None = None

    def __init__(self, expr: str):
        """Create a restricted expression

        where:

          expr -- a string containing the expression to be evaluated.
        """
        expr = expr.strip()
        self.__name__ = expr
        expr = expr.translate(nltosp)
        self.expr = expr
        # Catch syntax errors.
        self.prepUnrestrictedCode()

    def prepRestrictedCode(self) -> None:
        if self.rcode is None:
            result = compile_restricted_eval(self.expr, '<string>')
            if result.errors:
                raise SyntaxError(result.errors[0])
            self.used = tuple(result.used_names)
            self.rcode = result.code

    def prepUnrestrictedCode(self) -> None:
        if self.ucode is None:
            exp_node = ast.parse(
                self.expr,
                '<string>',
                'eval')

            co = compile(exp_node, '<string>', 'eval')

            # Examine the ast to discover which names the expression needs.
            if self.used is None:
                used = set()
                for node in ast.walk(exp_node):
                    if isinstance(node, ast.Name):
                        if isinstance(node.ctx, ast.Load):
                            used.add(node.id)

                self.used = tuple(used)

            self.ucode = co

    def eval(self,
             mapping: collections.abc.Mapping[str,
                                              typing.Any]) -> typing.Any:
        # This default implementation is probably not very useful. :-(
        # This is meant to be overridden.
        self.prepRestrictedCode()

        global_scope = {
            '_getattr_': default_guarded_getattr,
            '_getitem_': default_guarded_getitem,
            '_getiter_': default_guarded_getiter,
        }

        global_scope.update(self.globals)

        for name in cast_not_none(self.used):
            if (name not in global_scope) and (name in mapping):
                global_scope[name] = mapping[name]

        return eval(cast_not_none(self.rcode), global_scope)

    def __call__(self, **kw: typing.Any) -> typing.Any:
        return self.eval(kw)
