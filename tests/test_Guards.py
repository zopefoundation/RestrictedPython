from RestrictedPython.Guards import safe_builtins
from tests import e_eval
from tests import e_exec

import pytest


@pytest.mark.parametrize(*e_eval)
def test_Guards__safe_builtins__1(e_eval):
    """It contains `slice()`."""
    restricted_globals = dict(__builtins__=safe_builtins)
    assert e_eval('slice(1)', restricted_globals) == slice(1)


CLASS_SOURCE = '''
class C:
    value = None
    def display(self):
        return str(self.value)

c1 = C()
c1.value = 2411
b = c1.display()
'''


@pytest.mark.parametrize(*e_exec)
def test_Guards__safe_builtins__2(e_exec):
    """It allows to define new classes by allowing `__build_class__`.

    `__build_class__` is only needed in Python 3.
    """
    restricted_globals = dict(
        __builtins__=safe_builtins, b=None,
        __name__='restricted_module',
        __metaclass__=type,
        _write_=lambda x: x,
        _getattr_=getattr)

    e_exec(CLASS_SOURCE, restricted_globals)
    assert restricted_globals['b'] == '2411'
