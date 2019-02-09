from tests.helper import restricted_eval


def test_Or():
    assert restricted_eval('False or True') is True


def test_And():
    assert restricted_eval('True and True') is True


def test_Not():
    assert restricted_eval('not False') is True
