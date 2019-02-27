from tests.helper import restricted_eval


def test_UAdd():
    assert restricted_eval('+a', {'a': 42}) == 42


def test_USub():
    assert restricted_eval('-a', {'a': 2411}) == -2411
