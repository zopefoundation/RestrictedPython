from tests.helper import restricted_exec


SIMPLE_SUBSCRIPTS = """
def simple_subscript(a):
    return a['b']
"""


def test_read_simple_subscript(mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    restricted_exec(SIMPLE_SUBSCRIPTS, glb)

    assert (value, 'b') == glb['simple_subscript'](value)


VAR_SUBSCRIPT = """
def simple_subscript(a, b):
    return a[b]
"""


def test_read_subscript_with_variable(mocker):
    value = [1]
    idx = 0
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    restricted_exec(VAR_SUBSCRIPT, glb)

    assert (value, 0) == glb['simple_subscript'](value, idx)


TUPLE_SUBSCRIPTS = """
def tuple_subscript(a):
    return a[1, 2]
"""


def test_tuple_subscript(mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    restricted_exec(TUPLE_SUBSCRIPTS, glb)

    assert (value, (1, 2)) == glb['tuple_subscript'](value)


SLICE_SUBSCRIPT_NO_UPPER_BOUND = """
def slice_subscript_no_upper_bound(a):
    return a[1:]
"""


def test_read_slice_subscript_no_upper_bound(mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    restricted_exec(SLICE_SUBSCRIPT_NO_UPPER_BOUND, glb)

    assert (value, slice(1, None, None)) == glb['slice_subscript_no_upper_bound'](value)  # NOQA: E501


SLICE_SUBSCRIPT_NO_LOWER_BOUND = """
def slice_subscript_no_lower_bound(a):
    return a[:1]
"""


def test_read_slice_subscript_no_lower_bound(mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    restricted_exec(SLICE_SUBSCRIPT_NO_LOWER_BOUND, glb)

    assert (value, slice(None, 1, None)) == glb['slice_subscript_no_lower_bound'](value)  # NOQA: E501


SLICE_SUBSCRIPT_NO_STEP = """
def slice_subscript_no_step(a):
    return a[1:2]
"""


def test_read_slice_subscript_no_step(mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    restricted_exec(SLICE_SUBSCRIPT_NO_STEP, glb)

    assert (value, slice(1, 2, None)) == glb['slice_subscript_no_step'](value)


SLICE_SUBSCRIPT_WITH_STEP = """
def slice_subscript_with_step(a):
    return a[1:2:3]
"""


def test_read_slice_subscript_with_step(mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    restricted_exec(SLICE_SUBSCRIPT_WITH_STEP, glb)

    assert (value, slice(1, 2, 3)) == glb['slice_subscript_with_step'](value)


EXTENDED_SLICE_SUBSCRIPT = """

def extended_slice_subscript(a):
    return a[0, :1, 1:, 1:2, 1:2:3]
"""


def test_read_extended_slice_subscript(mocker):
    value = None
    _getitem_ = mocker.stub()
    _getitem_.side_effect = lambda ob, index: (ob, index)
    glb = {'_getitem_': _getitem_}
    restricted_exec(EXTENDED_SLICE_SUBSCRIPT, glb)
    ret = glb['extended_slice_subscript'](value)
    ref = (
        value,
        (
            0,
            slice(None, 1, None),
            slice(1, None, None),
            slice(1, 2, None),
            slice(1, 2, 3)
        )
    )

    assert ref == ret


WRITE_SUBSCRIPTS = """
def assign_subscript(a):
    a['b'] = 1
"""


def test_write_subscripts(
        mocker):
    value = {'b': None}
    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob
    glb = {'_write_': _write_}
    restricted_exec(WRITE_SUBSCRIPTS, glb)

    glb['assign_subscript'](value)
    assert value['b'] == 1


DEL_SUBSCRIPT = """
def del_subscript(a):
    del a['b']
"""


def test_del_subscripts(
        mocker):
    value = {'b': None}
    _write_ = mocker.stub()
    _write_.side_effect = lambda ob: ob
    glb = {'_write_': _write_}
    restricted_exec(DEL_SUBSCRIPT, glb)
    glb['del_subscript'](value)

    assert value == {}
