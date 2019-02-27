from tests.helper import restricted_exec


def test_RestrictingNodeTransformer__test_ternary_if(
        mocker):
    src = 'x.y = y.a if y.z else y.b'
    _getattr_ = mocker.stub()
    _getattr_.side_effect = lambda ob, key: ob[key]
    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob

    glb = {
        '_getattr_': _getattr_,
        '_write_': _write_,
        'x': mocker.stub(),
        'y': {'a': 'a', 'b': 'b'},
    }

    glb['y']['z'] = True
    restricted_exec(src, glb)

    assert glb['x'].y == 'a'
    _write_.assert_called_once_with(glb['x'])
    _getattr_.assert_has_calls([
        mocker.call(glb['y'], 'z'),
        mocker.call(glb['y'], 'a')])

    _write_.reset_mock()
    _getattr_.reset_mock()

    glb['y']['z'] = False
    restricted_exec(src, glb)

    assert glb['x'].y == 'b'
    _write_.assert_called_once_with(glb['x'])
    _getattr_.assert_has_calls([
        mocker.call(glb['y'], 'z'),
        mocker.call(glb['y'], 'b')])
