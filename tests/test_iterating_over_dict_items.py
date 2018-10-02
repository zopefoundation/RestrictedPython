from RestrictedPython import safe_builtins
from RestrictedPython.Eval import default_guarded_getiter
from RestrictedPython.Guards import guarded_iter_unpack_sequence
from tests import c_exec

import pytest


ITERATE_OVER_DICT_ITEMS = """
d = {'a': 'b'}
for k, v in d.items():
    pass
"""


@pytest.mark.parametrize(*c_exec)
def test_iterate_over_dict_items_plain(c_exec):
    glb = {}
    result = c_exec(ITERATE_OVER_DICT_ITEMS)
    assert result.code is not None
    assert result.errors == ()
    with pytest.raises(NameError) as excinfo:
        exec(result.code, glb, None)
    assert "name '_iter_unpack_sequence_' is not defined" in str(excinfo.value)


@pytest.mark.parametrize(*c_exec)
def test_iterate_over_dict_items_safe(c_exec):
    glb = safe_builtins.copy()
    glb['_getiter_'] = default_guarded_getiter
    glb['_iter_unpack_sequence_'] = guarded_iter_unpack_sequence
    result = c_exec(ITERATE_OVER_DICT_ITEMS)
    assert result.code is not None
    assert result.errors == ()
    exec(result.code, glb, None)
