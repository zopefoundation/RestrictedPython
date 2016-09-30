from RestrictedPython import compile_restricted
from RestrictedPython import compile_restricted_eval
from RestrictedPython import compile_restricted_exec
from RestrictedPython import compile_restricted_function
from RestrictedPython.PrintCollector import PrintCollector
from RestrictedPython.PrintCollector import printed
from RestrictedPython.PrintCollector import safe_print

import pytest
import sys


ALLOWED_PRINT_STATEMENT = """\
print 'Hello World!'
"""

ALLOWED_PRINT_STATEMENT_WITH_NL = """\
print 'Hello World!',
"""

ALLOWED_MUKTI_PRINT_STATEMENT = """\
print 'Hello World!', 'Hello Earth!'
"""

DISSALOWED_PRINT_STATEMENT_WITH_CHEVRON = """\
print >> stream, 'Hello World!'
"""

DISSALOWED_PRINT_STATEMENT_WITH_CHEVRON_AND_NL = """\
print >> stream, 'Hello World!',
"""

ALLOWED_PRINT_FUNCTION = """\
print('Hello World!')
"""

ALLOWED_MULTI_PRINT_FUNCTION = """\
print('Hello World!', 'Hello Earth!')
"""

ALLOWED_FUTURE_PRINT_FUNCTION = """\
from __future import print_function

print('Hello World!')
"""

ALLOWED_FUTURE_MULTI_PRINT_FUNCTION = """\
from __future import print_function

print('Hello World!', 'Hello Earth!')
"""

ALLOWED_PRINT_FUNCTION = """\
print('Hello World!', end='')
"""

DISALLOWED_PRINT_FUNCTION_WITH_FILE = """\
print('Hello World!', file=sys.stderr)
"""


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in Python 3")
def test_print__simple_print_statement():
    code, err, warn, use = compile_restricted_exec(ALLOWED_PRINT_STATEMENT, '<undefined>')
    exec(code)
