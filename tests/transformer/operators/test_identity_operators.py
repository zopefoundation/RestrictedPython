from tests.helper import restricted_eval


def test_Is():
    assert restricted_eval('True is True') is True


def test_NotIs():
    assert restricted_eval('1 is not True') is True
