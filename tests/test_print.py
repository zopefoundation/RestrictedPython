from RestrictedPython import compile_restricted
from RestrictedPython import compile_restricted_exec
import pytest
import sys





ALLOWED_PRINT = """\
print 'Hello World!'
"""

ALLOWED_PRINT_WITH_NL = """\
print 'Hello World!',
"""

DISSALOWED_PRINT_WITH_CHEVRON = """\
print >> stream, 'Hello World!'
"""


def test_print__simple_print_statement():
    code, err, warn, use = compile_restricted_exec(ALLOWED_PRINT, '<undefined>')
    exec(code)
    assert 'code' == code
