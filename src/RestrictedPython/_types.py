import ast
import sys
import typing


_T = typing.TypeVar('_T')


def cast_not_none(var: _T | None) -> _T:
    return typing.cast(_T, var)


# T_pos_ast are subtypes of ast.AST that have a position
# (have attributes: lineno, end_lineno, col_offset, and end_col_offset).
#
# ast.type_param is a new type in python 3.12 that has a position.
# TODO: Remove `else` when Support for Python 3.11 is dropped.
if sys.version_info >= (3, 12):
    T_pos_ast: typing.TypeAlias = (
        ast.stmt | ast.expr | ast.excepthandler | ast.arg | ast.keyword
        | ast.alias | ast.pattern | ast.type_param)
else:
    T_pos_ast: typing.TypeAlias = (
        ast.stmt | ast.expr | ast.excepthandler | ast.arg | ast.keyword
        | ast.alias | ast.pattern)
