from tests import e_exec

import pytest


DICT_COMPREHENSION_WITH_ATTRS = """
def call(seq):
    return {y.k: y.v for y in seq.z if y.k}
"""


@pytest.mark.parametrize(*e_exec)
def test_dict_comprehension_with_attrs(e_exec, mocker):
    _getattr_ = mocker.Mock()
    _getattr_.side_effect = getattr

    _getiter_ = mocker.Mock()
    _getiter_.side_effect = lambda ob: ob

    glb = {'_getattr_': _getattr_, '_getiter_': _getiter_}
    e_exec(DICT_COMPREHENSION_WITH_ATTRS, glb)

    z = [mocker.Mock(k=0, v='a'), mocker.Mock(k=1, v='b')]
    seq = mocker.Mock(z=z)

    ret = glb['call'](seq)
    assert ret == {1: 'b'}

    _getiter_.assert_called_once_with(z)
    _getattr_.assert_has_calls([
        mocker.call(seq, 'z'),
        mocker.call(z[0], 'k'),
        mocker.call(z[1], 'k'),
        mocker.call(z[1], 'v'),
        mocker.call(z[1], 'k')
    ])
