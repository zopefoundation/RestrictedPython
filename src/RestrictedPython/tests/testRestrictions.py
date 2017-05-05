# Note that nothing should be imported from AccessControl, and in particular
# nothing from ZopeGuards.py.  Transformed code may need several wrappers
# in order to run at all, and most of the production wrappers are defined
# in ZopeGuards.  But RestrictedPython isn't supposed to depend on
# AccessControl, so we need to define throwaway wrapper implementations
# here instead.

from RestrictedPython import PrintCollector
from RestrictedPython.RCompile import compile_restricted
from RestrictedPython.RCompile import RFunction
from RestrictedPython.RCompile import RModule
from RestrictedPython.tests import restricted_module
from RestrictedPython.tests import verify

import os
import re
import sys
import unittest


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
    fn = os.path.join(_HERE, 'restricted_module.py')
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
    for name in ('map', 'reduce', 'int', 'pow', 'range', 'filter',
                 'len', 'chr', 'ord',
                 ):
        rmodule[name] = builtins[name]
    exec code in rmodule


class AccessDenied (Exception):
    pass

DisallowedObject = []


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


class RestrictionTests(unittest.TestCase):
    def execFunc(self, name, *args, **kw):
        func = rmodule[name]
        verify.verify(func.func_code)
        func.func_globals.update({'_getattr_': guarded_getattr,
                                  '_getitem_': guarded_getitem,
                                  '_write_': TestGuard,
                                  '_print_': PrintCollector,
        # I don't want to write something as involved as ZopeGuard's
        # SafeIter just for these tests.  Using the builtin list() function
        # worked OK for everything the tests did at the time this was added,
        # but may fail in the future.  If Python 2.1 is no longer an
        # interesting platform then, using 2.2's builtin iter() here should
        # work for everything.
                                  '_getiter_': list,
                                  '_apply_': apply_wrapper,
                                  '_inplacevar_': inplacevar_wrapper,
                                  })
        return func(*args, **kw)

    def test_Print(self):
        for i in range(2):
            res = self.execFunc('print%s' % i)
            self.assertEqual(res, 'Hello, world!')

    def test_PrintToNone(self):
        try:
            res = self.execFunc('printToNone')
        except AttributeError:
            # Passed.  "None" has no "write" attribute.
            pass
        else:
            self.fail(0, res)

    def test_PrintStuff(self):
        res = self.execFunc('printStuff')
        self.assertEqual(res, 'a b c')

    def test_PrintLines(self):
        res = self.execFunc('printLines')
        self.assertEqual(res, '0 1 2\n3 4 5\n6 7 8\n')

    def test_Primes(self):
        res = self.execFunc('primes')
        self.assertEqual(res, '[2, 3, 5, 7, 11, 13, 17, 19]')

    def test_AllowedSimple(self):
        res = self.execFunc('allowed_simple')
        self.assertEqual(res, 'abcabcabc')

    def test_AllowedRead(self):
        self.execFunc('allowed_read', RestrictedObject())

    def test_AllowedWrite(self):
        self.execFunc('allowed_write', RestrictedObject())

    def test_AllowedArgs(self):
        self.execFunc('allowed_default_args', RestrictedObject())

    def test_TryMap(self):
        res = self.execFunc('try_map')
        self.assertEqual(res, "[2, 3, 4]")

    def test_Apply(self):
        del apply_wrapper_called[:]
        res = self.execFunc('try_apply')
        self.assertEqual(apply_wrapper_called, ["yes"])
        self.assertEqual(res, "321")

    def test_Inplace(self):
        inplacevar_wrapper_called.clear()
        res = self.execFunc('try_inplace')
        self.assertEqual(inplacevar_wrapper_called['+='], (1, 3))

    def test_Denied(self):
        for k in rmodule.keys():
            if k[:6] == 'denied':
                try:
                    self.execFunc(k, RestrictedObject())
                except AccessDenied:
                    # Passed the test
                    pass
                else:
                    self.fail('%s() did not trip security' % k)

    def test_OrderOfOperations(self):
        res = self.execFunc('order_of_operations')
        self.assertEqual(res, 0)

    def test_Rot13(self):
        res = self.execFunc('rot13', 'Zope is k00l')
        self.assertEqual(res, 'Mbcr vf x00y')

    def test_NestedScopes1(self):
        res = self.execFunc('nested_scopes_1')
        self.assertEqual(res, 2)

    def test_StackSize(self):
        for k, rfunc in rmodule.items():
            if not k.startswith('_') and hasattr(rfunc, 'func_code'):
                rss = rfunc.func_code.co_stacksize
                ss = getattr(restricted_module, k).func_code.co_stacksize
                self.failUnless(
                    rss >= ss, 'The stack size estimate for %s() '
                    'should have been at least %d, but was only %d'
                    % (k, ss, rss))

    def _compile_file(self, name):
        path = os.path.join(_HERE, name)
        f = open(path, "r")
        source = f.read()
        f.close()

        co = compile_restricted(source, path, "exec")
        verify.verify(co)
        return co

    def test_UnpackSequence(self):
        co = self._compile_file("unpack.py")
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
        self.assert_(isinstance(calls[i], TypeError))
        expected[i] = calls[i]
        self.assertEqual(calls, expected)

    def test_UnpackSequenceExpression(self):
        co = compile_restricted("[x for x, y in [(1, 2)]]", "<string>", "eval")
        verify.verify(co)
        calls = []

        def getiter(s):
            calls.append(s)
            return list(s)
        globals = {"_getiter_": getiter}
        exec(co, globals, {})
        self.assertEqual(calls, [[(1, 2)], (1, 2)])

    def test_UnpackSequenceSingle(self):
        co = compile_restricted("x, y = 1, 2", "<string>", "single")
        verify.verify(co)
        calls = []

        def getiter(s):
            calls.append(s)
            return list(s)
        globals = {"_getiter_": getiter}
        exec(co, globals, {})
        self.assertEqual(calls, [(1, 2)])

    def test_Class(self):
        getattr_calls = []
        setattr_calls = []

        def test_getattr(obj, attr):
            getattr_calls.append(attr)
            return getattr(obj, attr)

        def test_setattr(obj):
            setattr_calls.append(obj.__class__.__name__)
            return obj

        co = self._compile_file("class.py")
        globals = {"_getattr_": test_getattr,
                   "_write_": test_setattr,
                   }
        exec(co, globals, {})
        # Note that the getattr calls don't correspond to the method call
        # order, because the x.set method is fetched before its arguments
        # are evaluated.
        self.assertEqual(getattr_calls,
                         ["set", "set", "get", "state", "get", "state"])
        self.assertEqual(setattr_calls, ["MyClass", "MyClass"])

    def test_Empty(self):
        rf = RFunction("", "", "issue945", "empty.py", {})
        rf.parse()
        rf2 = RFunction("", "# still empty\n\n# by", "issue945", "empty.py", {})
        rf2.parse()

    def test_SyntaxError(self):
        err = ("def f(x, y):\n"
               "    if x, y < 2 + 1:\n"
               "        return x + y\n"
               "    else:\n"
               "        return x - y\n")
        self.assertRaises(SyntaxError,
                          compile_restricted, err, "<string>", "exec")

    # these two tests test_ that source code with Windows line
    # endings still works.

    def test_LineEndingsRFunction(self):
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

    def test_LineEndingsRestrictedCompileMode(self):
        from RestrictedPython.RCompile import RestrictedCompileMode
        gen = RestrictedCompileMode(
            '# testing\r\nprint "testing"\r\nreturn printed\n',
            '<testing>'
        )
        gen.mode = 'exec'
        # if the source has any line ending other than \n by the time
        # parse() is called, then you'll get a syntax error.
        gen.parse()

    def test_Collector2295(self):
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


def test_suite():
    return unittest.makeSuite(RestrictionTests, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
