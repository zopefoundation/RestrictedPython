from tests.helper import restricted_exec


DICT_COMPREHENSION_WITH_ATTRS = """
def call(seq):
    return {y.k: y.v for y in seq.z if y.k}
"""


def test_dict_comprehension_with_attrs(mocker):
    _getattr_ = mocker.Mock()
    _getattr_.side_effect = getattr

    _getiter_ = mocker.Mock()
    _getiter_.side_effect = lambda ob: ob

    glb = {'_getattr_': _getattr_, '_getiter_': _getiter_}
    restricted_exec(DICT_COMPREHENSION_WITH_ATTRS, glb)

    z = [mocker.Mock(k=0, v='a'), mocker.Mock(k=1, v='b')]
    seq = mocker.Mock(z=z)

    ret = glb['call'](seq)
    assert ret == {1: 'b'}

    _getiter_.assert_called_once_with(z)

    calls = [mocker.call(seq, 'z')]

    calls.extend([
        mocker.call(z[0], 'k'),
        mocker.call(z[1], 'k'),
        mocker.call(z[1], 'k'),
        mocker.call(z[1], 'v'),
    ])

    _getattr_.assert_has_calls(calls)
