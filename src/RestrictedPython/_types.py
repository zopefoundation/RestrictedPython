import ast
import sys
import typing


_T = typing.TypeVar('_T')


def cast_not_none(var: _T | None) -> _T:
    return typing.cast(_T, var)


if sys.version_info >= (3, 12):
    T_pos_ast: typing.TypeAlias = (
        ast.stmt | ast.expr | ast.excepthandler | ast.arg | ast.keyword
        | ast.alias | ast.pattern | ast.type_param)
else:
    T_pos_ast: typing.TypeAlias = (
        ast.stmt | ast.expr | ast.excepthandler | ast.arg | ast.keyword
        | ast.alias | ast.pattern)
