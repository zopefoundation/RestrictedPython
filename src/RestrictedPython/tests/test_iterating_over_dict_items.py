import pytest

from RestrictedPython import compile_restricted_exec
from RestrictedPython import safe_globals
from RestrictedPython.Eval import default_guarded_getiter
from RestrictedPython.Guards import guarded_iter_unpack_sequence


ITERATE_OVER_DICT_ITEMS = """
d = {'a': 'b'}
for k, v in d.items():
    pass
"""


def test_iterate_over_dict_items_plain():
    glb = {}
    result = compile_restricted_exec(ITERATE_OVER_DICT_ITEMS)
    assert result.code is not None
    assert result.errors == ()
    with pytest.raises(NameError) as excinfo:
        exec(result.code, glb, None)
    assert "name '_iter_unpack_sequence_' is not defined" in str(excinfo.value)


def test_iterate_over_dict_items_safe():
    glb = safe_globals.copy()
    glb['_getiter_'] = default_guarded_getiter
    glb['_iter_unpack_sequence_'] = guarded_iter_unpack_sequence
    result = compile_restricted_exec(ITERATE_OVER_DICT_ITEMS)
    assert result.code is not None
    assert result.errors == ()
    exec(result.code, glb, None)
