from RestrictedPython import PrintCollector
from RestrictedPython.test_helper import verify

import os
import pytest
import re
import sys


if sys.version_info.major > 2:
    from RestrictedPython.compile import compile_restricted
else:
    from RestrictedPython.RCompile import RFunction
    from RestrictedPython.Eval import RestrictionCapableEval
    from RestrictedPython.RCompile import compile_restricted
    from RestrictedPython.tests import restricted_module

try:
    __file__
except NameError:
    __file__ = os.path.abspath(sys.argv[1])
_FILEPATH = os.path.abspath(__file__)
_HERE = os.path.dirname(_FILEPATH)


def _getindent(line):
    """Returns the indentation level of the given line."""
    indent = 0
    for c in line:
        if c == ' ':
            indent = indent + 1
        elif c == '\t':
            indent = indent + 8
        else:
            break
    return indent


def find_source(fn, func):
    """Given a func_code object, this function tries to find and return
    the python source code of the function.
    Originally written by
    Harm van der Heijden (H.v.d.Heijden@phys.tue.nl)"""
    f = open(fn, "r")
    for i in range(func.co_firstlineno):
        line = f.readline()
    ind = _getindent(line)
    msg = ""
    while line:
        msg = msg + line
        line = f.readline()
        # the following should be <= ind, but then we get
        # confused by multiline docstrings. Using == works most of
        # the time... but not always!
        if _getindent(line) == ind:
            break
    f.close()
    return fn, msg


def get_source(func):
    """Less silly interface to find_source"""
    file = func.func_globals['__file__']
    if file.endswith('.pyc'):
        file = file[:-1]
    source = find_source(file, func.func_code)[1]
    assert source.strip(), "Source should not be empty!"
    return source


def create_rmodule():
    global rmodule
    if sys.version_info.major > 2:
        fn = os.path.join(_HERE, 'fixtures', 'restricted_module_py3.py')
    else:
        fn = os.path.join(_HERE, 'fixtures', 'restricted_module.py')

    f = open(fn, 'r')
    source = f.read()
    f.close()
    # Sanity check
    compile(source, fn, 'exec')
    # Now compile it for real
    code = compile_restricted(source, fn, 'exec')
    rmodule = {'__builtins__': {'__import__': __import__,
                                'None': None,
                                '__name__': 'restricted_module'
                                }
               }

    builtins = getattr(__builtins__, '__dict__', __builtins__)
    words = ('map', 'int', 'pow', 'range', 'filter',
             'len', 'chr', 'ord', 'print')
    for name in words:
        rmodule[name] = builtins[name]

    if sys.version_info.major < 3:
        rmodule['reduce'] = builtins['reduce']

    exec(code, rmodule)


class AccessDenied (Exception):
    pass

DisallowedObject = []


class TestGuard:
    '''A guard class'''
    def __init__(self, _ob, write=None):
        self.__dict__['_ob'] = _ob

    # Write guard methods

    def __setattr__(self, name, value):
        _ob = self.__dict__['_ob']
        writeable = getattr(_ob, '__writeable_attrs__', ())
        if name not in writeable:
            raise AccessDenied
        if name[:5] == 'func_':
            raise AccessDenied
        setattr(_ob, name, value)

    def __setitem__(self, index, value):
        _ob = self.__dict__['_ob']
        _ob[index] = value

    def __setslice__(self, lo, hi, value):
        _ob = self.__dict__['_ob']
        _ob[lo:hi] = value

# A wrapper for _apply_.
apply_wrapper_called = []


def apply_wrapper(func, *args, **kws):
    apply_wrapper_called.append('yes')
    return func(*args, **kws)

inplacevar_wrapper_called = {}


def inplacevar_wrapper(op, x, y):
    inplacevar_wrapper_called[op] = x, y
    # This is really lame.  But it's just a test. :)
    globs = {'x': x, 'y': y}
    exec('x' + op + 'y', globs)
    return globs['x']


class RestrictedObject:
    disallowed = DisallowedObject
    allowed = 1
    _ = 2
    __ = 3
    _some_attr = 4
    __some_other_attr__ = 5
    s = 'Another day, another test...'
    __writeable_attrs__ = ('writeable',)

    def __getitem__(self, idx):
        if idx == 'protected':
            raise AccessDenied
        elif idx == 0 or idx == 'safe':
            return 1
        elif idx == 1:
            return DisallowedObject
        else:
            return self.s[idx]

    def __getslice__(self, lo, hi):
        return self.s[lo:hi]

    def __len__(self):
        return len(self.s)

    def __setitem__(self, idx, v):
        if idx == 'safe':
            self.safe = v
        else:
            raise AccessDenied

    def __setslice__(self, lo, hi, value):
        raise AccessDenied

    write = DisallowedObject


def guarded_getattr(ob, name):
    v = getattr(ob, name)
    if v is DisallowedObject:
        raise AccessDenied
    return v

SliceType = type(slice(0))


def guarded_getitem(ob, index):
    if type(index) is SliceType and index.step is None:
        start = index.start
        stop = index.stop
        if start is None:
            start = 0
        if stop is None:
            v = ob[start:]
        else:
            v = ob[start:stop]
    else:
        v = ob[index]
    if v is DisallowedObject:
        raise AccessDenied
    return v


def minimal_import(name, _globals, _locals, names):
    if name != "__future__":
        raise ValueError("Only future imports are allowed")
    import __future__
    return __future__


def exec_func(name, *args, **kw):
    func = rmodule[name]
    func_dict = {'_getattr_': guarded_getattr,
                 '_getitem_': guarded_getitem,
                 '_write_': TestGuard,
                 '_print_': PrintCollector,
                 '_getiter_': iter,
                 '_apply_': apply_wrapper,
                 '_inplacevar_': inplacevar_wrapper,
                 }
    if sys.version_info.major < 3:
        verify(func.func_code)
        func.func_globals.update(func_dict)
    else:
        verify(func.__code__)
        func.__globals__.update(func_dict)
    return func(*args, **kw)


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in python 3")
def test_print():
    for i in range(2):
        res = exec_func('print%s' % i)
        assert res == 'Hello, world!'


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in python 3")
def test_print_to_None():
    try:
        res = exec_func('printToNone')
    except AttributeError:
        # Passed.  "None" has no "write" attribute.
        pass
    else:
        raise AssertionError(res)


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in python 3")
def test_print_stuff():
    res = exec_func('printStuff')
    assert res == 'a b c'


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in python 3")
def test_print_lines():
    res = exec_func('printLines')
    assert res == '0 1 2\n3 4 5\n6 7 8\n'


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in python 3")
def test_primes():
    res = exec_func('primes')
    assert res == '[2, 3, 5, 7, 11, 13, 17, 19]'


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in python 3")
def test_allowed_simple():
    res = exec_func('allowed_simple')
    assert res == 'abcabcabc'


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in python 3")
def test_allowed_read():
    res = exec_func('allowed_read', RestrictedObject())


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in python 3")
def test_allowed_write():
    res = exec_func('allowed_write', RestrictedObject())


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in python 3")
def test_allowed_args():
    res = exec_func('allowed_default_args', RestrictedObject())


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in python 3")
def test_try_map():
    res = exec_func('try_map')
    assert res == "[2, 3, 4]"


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="print statement no longer exists in python 3")
def test_apply():
    del apply_wrapper_called[:]
    res = exec_func("try_apply")
    assert apply_wrapper_called == ["yes"]
    assert res == "321"


def test_inplace():
    inplacevar_wrapper_called.clear()
    exec_func('try_inplace')
    inplacevar_wrapper_called['+='] == (1, 3)


def test_denied():
    for k in [k for k in rmodule.keys() if k.startswith("denied")]:
        try:
            exec_func(k, RestrictedObject())

        except (AccessDenied, TypeError):
            # Passed the test
            # TODO: TypeError is not 100% correct ...
            # remove this and fixed `denied`
            pass
        else:
            raise AssertionError('%s() did not trip security' % k)


def test_syntax_security():
    # Ensures that each of the functions in security_in_syntax.py
    # throws a SyntaxError when using compile_restricted.
    fn = os.path.join(_HERE, 'fixtures', 'security_in_syntax.py')
    f = open(fn, 'r')
    source = f.read()
    f.close()
    # Unrestricted compile.
    code = compile(source, fn, 'exec')
    m = {'__builtins__': {'__import__': minimal_import}}
    exec(code, m)
    for k, v in m.items():
        if hasattr(v, 'func_code'):
            filename, source = find_source(fn, v.func_code)
            # Now compile it with restrictions
            try:
                code = compile_restricted(source, filename, 'exec')
            except SyntaxError:
                # Passed the test.
                pass
            else:
                raise AssertionError('%s should not have compiled' % k)


def test_order_of_operations():
    res = exec_func('order_of_operations')
    assert res == 0


def test_rot13():
    res = exec_func('rot13', 'Zope is k00l')
    assert res == 'Mbcr vf x00y'


def test_nested_scopes1():
    res = exec_func('nested_scopes_1')
    assert res == 2

# TODO: check if this need py3 love
@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="compiler no longer exists in python 3")
def test_unrestricted_eval():
    expr = RestrictionCapableEval("{'a':[m.pop()]}['a'] + [m[0]]")
    v = [12, 34]
    expect = v[:]
    expect.reverse()
    res = expr.eval({'m': v})
    assert res == expect
    v = [12, 34]
    res = expr(m=v)
    assert res == expect


def test_stacksize():
    for k, rfunc in rmodule.items():
        if not k.startswith('_') and hasattr(rfunc, 'func_code'):
            rss = rfunc.func_code.co_stacksize
            ss = getattr(restricted_module, k).func_code.co_stacksize

            if not rss >= ss:
                raise AssertionError(
                    'The stack size estimate for %s() '
                    'should have been at least %d, but was only %d'
                    % (k, ss, rss))


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="compiler no longer exists in python 3")
def test_before_and_after():
    from RestrictedPython.RCompile import RModule
    from RestrictedPython.tests import before_and_after
    from compiler import parse

    defre = re.compile(r'def ([_A-Za-z0-9]+)_(after|before)\(')

    beforel = [name for name in before_and_after.__dict__
               if name.endswith("_before")]

    for name in beforel:
        before = getattr(before_and_after, name)
        before_src = get_source(before)
        before_src = re.sub(defre, r'def \1(', before_src)
        rm = RModule(before_src, '')
        tree_before = rm._get_tree()

        after = getattr(before_and_after, name[:-6] + 'after')
        after_src = get_source(after)
        after_src = re.sub(defre, r'def \1(', after_src)
        tree_after = parse(after_src)

        assert str(tree_before) == str(tree_after)

        rm.compile()
        verify(rm.getCode())


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="compiler no longer exists in python 3")
def _test_before_and_after(mod):
    from RestrictedPython.RCompile import RModule
    from compiler import parse

    defre = re.compile(r'def ([_A-Za-z0-9]+)_(after|before)\(')

    beforel = [name for name in mod.__dict__
               if name.endswith("_before")]

    for name in beforel:
        before = getattr(mod, name)
        before_src = get_source(before)
        before_src = re.sub(defre, r'def \1(', before_src)
        rm = RModule(before_src, '')
        tree_before = rm._get_tree()

        after = getattr(mod, name[:-6] + 'after')
        after_src = get_source(after)
        after_src = re.sub(defre, r'def \1(', after_src)
        tree_after = parse(after_src)

        assert str(tree_before) == str(tree_after)

        rm.compile()
        verify(rm.getCode())


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="compiler no longer exists in python 3")
def test_BeforeAndAfter24():
    from RestrictedPython.tests import before_and_after24
    _test_before_and_after(before_and_after24)


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="compiler no longer exists in python 3")
def test_BeforeAndAfter25():
    from RestrictedPython.tests import before_and_after25
    _test_before_and_after(before_and_after25)


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="compiler no longer exists in python 3")
def test_BeforeAndAfter26():
    from RestrictedPython.tests import before_and_after26
    _test_before_and_after(before_and_after26)


@pytest.mark.skipif(sys.version_info >= (3, 0),
                    reason="compiler no longer exists in python 3")
def test_BeforeAndAfter27():
    from RestrictedPython.tests import before_and_after27
    _test_before_and_after(before_and_after27)


def _compile_file(name):
    path = os.path.join(_HERE, 'fixtures', name)
    f = open(path, "r")
    source = f.read()
    f.close()

    co = compile_restricted(source, path, "exec")
    verify(co)
    return co


def test_unpack_sequence():
    if sys.version_info.major > 2:
        co = _compile_file("unpack_py3.py")
    else:
        co = _compile_file("unpack.py")

    calls = []

    def getiter(seq):
        calls.append(seq)
        return list(seq)
    globals = {"_getiter_": getiter, '_inplacevar_': inplacevar_wrapper}
    exec(co, globals, {})
    # The comparison here depends on the exact code that is
    # contained in unpack.py.
    # The test doing implicit unpacking in an "except:" clause is
    # a pain, because there are two levels of unpacking, and the top
    # level is unpacking the specific TypeError instance constructed
    # by the test.  We have to worm around that one.
    ineffable = "a TypeError instance"
    expected = [[1, 2],
                (1, 2),
                "12",
                [1],
                [1, [2, 3], 4],
                [2, 3],
                (1, (2, 3), 4),
                (2, 3),
                [1, 2, 3],
                2,
                ('a', 'b'),
                ((1, 2), (3, 4)), (1, 2),
                ((1, 2), (3, 4)), (3, 4),
                ineffable, [42, 666],
                [[0, 1], [2, 3], [4, 5]], [0, 1], [2, 3], [4, 5],
                ([[[1, 2]]], [[[3, 4]]]), [[[1, 2]]], [[1, 2]], [1, 2],
                                          [[[3, 4]]], [[3, 4]], [3, 4],
                ]
    i = expected.index(ineffable)
    assert isinstance(calls[i], TypeError) is True
    expected[i] = calls[i]
    assert calls == expected


def test_unpack_sequence_expression():
    co = compile_restricted("[x for x, y in [(1, 2)]]", "<string>", "eval")
    verify(co)
    calls = []

    def getiter(s):
        calls.append(s)
        return list(s)
    globals = {"_getiter_": getiter}
    exec(co, globals, {})
    assert calls == [[(1, 2)], (1, 2)]


def test_unpack_sequence_single():
    co = compile_restricted("x, y = 1, 2", "<string>", "single")
    verify(co)
    calls = []

    def getiter(s):
        calls.append(s)
        return list(s)
    globals = {"_getiter_": getiter}
    exec(co, globals, {})
    assert calls == [(1, 2)]


def test_class():
    getattr_calls = []
    setattr_calls = []

    def test_getattr(obj, attr):
        getattr_calls.append(attr)
        return getattr(obj, attr)

    def test_setattr(obj):
        setattr_calls.append(obj.__class__.__name__)
        return obj

    co = _compile_file("class.py")
    globals = {"_getattr_": test_getattr,
               "_write_": test_setattr,
               }
    exec(co, globals, {})
    # Note that the getattr calls don't correspond to the method call
    # order, because the x.set method is fetched before its arguments
    # are evaluated.
    assert getattr_calls == ["set", "set", "get", "state", "get", "state"]
    assert setattr_calls == ["MyClass", "MyClass"]


def test_lambda():
    co = _compile_file("lambda.py")
    exec(co, {}, {})


def test_empty():
    rf = RFunction("", "", "issue945", "empty.py", {})
    rf.parse()
    rf2 = RFunction("", "# still empty\n\n# by", "issue945", "empty.py", {})
    rf2.parse()


def test_SyntaxError():
    err = ("def f(x, y):\n"
           "    if x, y < 2 + 1:\n"
           "        return x + y\n"
           "    else:\n"
           "        return x - y\n")
    with pytest.raises(SyntaxError):
        compile_restricted(err, "<string>", "exec")


def test_line_endings_RFunction():
    from RestrictedPython.RCompile import RFunction
    gen = RFunction(
        p='',
        body='# testing\r\nprint "testing"\r\nreturn printed\n',
        name='test',
        filename='<test>',
        globals=(),
    )
    gen.mode = 'exec'
    # if the source has any line ending other than \n by the time
    # parse() is called, then you'll get a syntax error.
    gen.parse()


def test_line_endings_RestrictedCompileMode():
    from RestrictedPython.RCompile import RestrictedCompileMode
    gen = RestrictedCompileMode(
        '# testing\r\nprint "testing"\r\nreturn printed\n',
        '<testing>'
    )
    gen.mode = 'exec'
    # if the source has any line ending other than \n by the time
    # parse() is called, then you'll get a syntax error.
    gen.parse()


def test_Collector2295():
    from RestrictedPython.RCompile import RestrictedCompileMode
    gen = RestrictedCompileMode(
        'if False:\n  pass\n# Me Grok, Say Hi',
        '<testing>'
    )
    gen.mode = 'exec'
    # if the source has any line ending other than \n by the time
    # parse() is called, then you'll get a syntax error.
    gen.parse()


create_rmodule()
