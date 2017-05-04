from RestrictedPython.PrintCollector import PrintCollector

import RestrictedPython


# The old 'RCompile' has no clue about the print function.
compiler = RestrictedPython.compile.compile_restricted_exec


ALLOWED_PRINT_FUNCTION = """
from __future__ import print_function
print ('Hello World!')
"""

ALLOWED_PRINT_FUNCTION_WITH_END = """
from __future__ import print_function
print ('Hello World!', end='')
"""

ALLOWED_PRINT_FUNCTION_MULTI_ARGS = """
from __future__ import print_function
print ('Hello World!', 'Hello Earth!')
"""

ALLOWED_PRINT_FUNCTION_WITH_SEPARATOR = """
from __future__ import print_function
print ('a', 'b', 'c', sep='|', end='!')
"""

PRINT_FUNCTION_WITH_NONE_SEPARATOR = """
from __future__ import print_function
print ('a', 'b', sep=None)
"""


PRINT_FUNCTION_WITH_NONE_END = """
from __future__ import print_function
print ('a', 'b', end=None)
"""


PRINT_FUNCTION_WITH_NONE_FILE = """
from __future__ import print_function
print ('a', 'b', file=None)
"""


def test_print_function__simple_prints():
    glb = {'_print_': PrintCollector, '_getattr_': None}

    code, errors = compiler(ALLOWED_PRINT_FUNCTION)[:2]
    assert errors == ()
    assert code is not None
    exec(code, glb)
    assert glb['_print']() == 'Hello World!\n'

    code, errors = compiler(ALLOWED_PRINT_FUNCTION_WITH_END)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == 'Hello World!'

    code, errors = compiler(ALLOWED_PRINT_FUNCTION_MULTI_ARGS)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == 'Hello World! Hello Earth!\n'

    code, errors = compiler(ALLOWED_PRINT_FUNCTION_WITH_SEPARATOR)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == "a|b|c!"

    code, errors = compiler(PRINT_FUNCTION_WITH_NONE_SEPARATOR)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == "a b\n"

    code, errors = compiler(PRINT_FUNCTION_WITH_NONE_END)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == "a b\n"

    code, errors = compiler(PRINT_FUNCTION_WITH_NONE_FILE)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == "a b\n"


ALLOWED_PRINT_FUNCTION_WITH_STAR_ARGS = """
from __future__ import print_function
to_print = (1, 2, 3)
print(*to_print)
"""


def test_print_function_with_star_args(mocker):
    _apply_ = mocker.stub()
    _apply_.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)

    glb = {
        '_print_': PrintCollector,
        '_getattr_': None,
        "_apply_": _apply_
    }

    code, errors = compiler(ALLOWED_PRINT_FUNCTION_WITH_STAR_ARGS)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == "1 2 3\n"
    _apply_.assert_called_once_with(glb['_print']._call_print, 1, 2, 3)


ALLOWED_PRINT_FUNCTION_WITH_KWARGS = """
from __future__ import print_function
to_print = (1, 2, 3)
kwargs = {'sep': '-', 'end': '!', 'file': None}
print(*to_print, **kwargs)
"""


def test_print_function_with_kw_args(mocker):
    _apply_ = mocker.stub()
    _apply_.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)

    glb = {
        '_print_': PrintCollector,
        '_getattr_': None,
        "_apply_": _apply_
    }

    code, errors = compiler(ALLOWED_PRINT_FUNCTION_WITH_KWARGS)[:2]
    assert code is not None
    assert errors == ()
    exec(code, glb)
    assert glb['_print']() == "1-2-3!"
    _apply_.assert_called_once_with(
        glb['_print']._call_print,
        1,
        2,
        3,
        end='!',
        file=None,
        sep='-')


PROTECT_WRITE_ON_FILE = """
from __future__ import print_function
print ('a', 'b', file=stream)
"""


def test_print_function__protect_file(mocker):
    _getattr_ = mocker.stub()
    _getattr_.side_effect = getattr
    stream = mocker.stub()
    stream.write = mocker.stub()

    glb = {
        '_print_': PrintCollector,
        '_getattr_': _getattr_,
        'stream': stream
    }

    code, errors = compiler(PROTECT_WRITE_ON_FILE)[:2]
    assert code is not None
    assert errors == ()

    exec(code, glb)

    _getattr_.assert_called_once_with(stream, 'write')
    stream.write.assert_has_calls([
        mocker.call('a'),
        mocker.call(' '),
        mocker.call('b'),
        mocker.call('\n')
    ])


# 'printed' is scope aware.
# => on a new function scope a new printed is generated.
INJECT_PRINT_COLLECTOR_NESTED = """
from __future__ import print_function
def f2():
    return 'f2'

def f1():
    print ('f1')

    def inner():
        print ('inner')
        return printed

    return inner() + printed + f2()

def main():
    print ('main')
    return f1() + printed
"""


def test_print_function__nested_print_collector():
    code, errors = compiler(INJECT_PRINT_COLLECTOR_NESTED)[:2]

    glb = {"_print_": PrintCollector, '_getattr_': None}
    exec(code, glb)

    ret = glb['main']()
    assert ret == 'inner\nf1\nf2main\n'


WARN_PRINTED_NO_PRINT = """
def foo():
    return printed
"""


def test_print_function__with_printed_no_print():
    code, errors, warnings = compiler(WARN_PRINTED_NO_PRINT)[:3]

    assert code is not None
    assert errors == ()
    assert warnings == ["Line 2: Doesn't print, but reads 'printed' variable."]


WARN_PRINTED_NO_PRINT_NESTED = """
from __future__ import print_function
print ('a')
def foo():
    return printed
printed
"""


def test_print_function__with_printed_no_print_nested():
    code, errors, warnings = compiler(WARN_PRINTED_NO_PRINT_NESTED)[:3]

    assert code is not None
    assert errors == ()
    assert warnings == ["Line 4: Doesn't print, but reads 'printed' variable."]


WARN_PRINT_NO_PRINTED = """
from __future__ import print_function
def foo():
    print (1)
"""


def test_print_function__with_print_no_printed():
    code, errors, warnings = compiler(WARN_PRINT_NO_PRINTED)[:3]

    assert code is not None
    assert errors == ()
    assert warnings == ["Line 3: Prints, but never reads 'printed' variable."]


WARN_PRINT_NO_PRINTED_NESTED = """
from __future__ import print_function
print ('a')
def foo():
    print ('x')
printed
"""


def test_print_function__with_print_no_printed_nested():
    code, errors, warnings = compiler(WARN_PRINT_NO_PRINTED_NESTED)[:3]

    assert code is not None
    assert errors == ()
    assert warnings == ["Line 4: Prints, but never reads 'printed' variable."]


# python generates a new frame/scope for:
# modules, functions, class, lambda, all the comprehensions
# For class, lambda and comprehensions *no* new print collector scope should be
# generated.

NO_PRINT_SCOPES = """
from __future__ import print_function
def class_scope():
    class A:
        print ('a')
    return printed

def lambda_scope():
    func = lambda x: print(x)
    func(1)
    func(2)
    return printed

def comprehension_scope():
    [print(1) for _ in range(2)]
    return printed
"""


def test_print_function_no_new_scope():
    code, errors = compiler(NO_PRINT_SCOPES)[:2]
    glb = {
        '_print_': PrintCollector,
        '__metaclass__': type,
        '_getattr_': None,
        '_getiter_': lambda ob: ob
    }
    exec(code, glb)

    ret = glb['class_scope']()
    assert ret == 'a\n'

    ret = glb['lambda_scope']()
    assert ret == '1\n2\n'

    ret = glb['comprehension_scope']()
    assert ret == '1\n1\n'


PASS_PRINT_FUNCTION = """
from __future__ import print_function
def main():
    def do_stuff(func):
        func(1)
        func(2)

    do_stuff(print)
    return printed
"""


def test_print_function_pass_print_function():
    code, errors = compiler(PASS_PRINT_FUNCTION)[:2]
    glb = {'_print_': PrintCollector, '_getattr_': None}
    exec(code, glb)

    ret = glb['main']()
    assert ret == '1\n2\n'


CONDITIONAL_PRINT = """
from __future__ import print_function
def func(cond):
    if cond:
        print(1)
    return printed
"""


def test_print_function_conditional_print():
    code, errors = compiler(CONDITIONAL_PRINT)[:2]
    glb = {'_print_': PrintCollector, '_getattr_': None}
    exec(code, glb)

    assert glb['func'](True) == '1\n'
    assert glb['func'](False) == ''
