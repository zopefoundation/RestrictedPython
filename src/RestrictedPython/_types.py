import typing


_T = typing.TypeVar('_T')


def _cast_not_none(var: _T | None) -> _T:
    return var  # type: ignore[return-value]
