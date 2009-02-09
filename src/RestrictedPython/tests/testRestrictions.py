import os
import re
import sys
import unittest

# Note that nothing should be imported from AccessControl, and in particular
# nothing from ZopeGuards.py.  Transformed code may need several wrappers
# in order to run at all, and most of the production wrappers are defined
# in ZopeGuards.  But RestrictedPython isn't supposed to depend on
# AccessControl, so we need to define throwaway wrapper implementations
# here instead.

from RestrictedPython import compile_restricted, PrintCollector
from RestrictedPython.Eval import RestrictionCapableEval
from RestrictedPython.tests import restricted_module, verify
from RestrictedPython.RCompile import RModule, RFunction

try:
    __file__
except NameError:
    __file__ = os.path.abspath(sys.argv[1])
_FILEPATH = os.path.abspath( __file__ )
_HERE = os.path.dirname( _FILEPATH )

def _getindent(line):
    """Returns the indentation level of the given line."""
    indent = 0
    for c in line:
        if c == ' ': indent = indent + 1
        elif c == '\t': indent = indent + 8
        else: break
    return indent

def find_source(fn, func):
    """Given a func_code object, this function tries to find and return
    the python source code of the function.  Originally written by
    Harm van der Heijden (H.v.d.Heijden@phys.tue.nl)"""
    f = open(fn,"r")
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
        if _getindent(line) == ind: break
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
    rmodule = {'__builtins__':{'__import__':__import__, 'None':None,
                               '__name__': 'restricted_module'}}
    builtins = getattr(__builtins__, '__dict__', __builtins__)
    for name in ('map', 'reduce', 'int', 'pow', 'range', 'filter',
                 'len', 'chr', 'ord',
                 ):
        rmodule[name] = builtins[name]
    exec code in rmodule

class AccessDenied (Exception): pass

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
        raise ValueError, "Only future imports are allowed"
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
    exec 'x'+op+'y' in globs
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

    def checkPrint(self):
        for i in range(2):
            res = self.execFunc('print%s' % i)
            self.assertEqual(res, 'Hello, world!')

    def checkPrintToNone(self):
        try:
            res = self.execFunc('printToNone')
        except AttributeError:
            # Passed.  "None" has no "write" attribute.
            pass
        else:
            self.fail(0, res)

    def checkPrintStuff(self):
        res = self.execFunc('printStuff')
        self.assertEqual(res, 'a b c')

    def checkPrintLines(self):
        res = self.execFunc('printLines')
        self.assertEqual(res,  '0 1 2\n3 4 5\n6 7 8\n')

    def checkPrimes(self):
        res = self.execFunc('primes')
        self.assertEqual(res, '[2, 3, 5, 7, 11, 13, 17, 19]')

    def checkAllowedSimple(self):
        res = self.execFunc('allowed_simple')
        self.assertEqual(res, 'abcabcabc')

    def checkAllowedRead(self):
        self.execFunc('allowed_read', RestrictedObject())

    def checkAllowedWrite(self):
        self.execFunc('allowed_write', RestrictedObject())

    def checkAllowedArgs(self):
        self.execFunc('allowed_default_args', RestrictedObject())

    def checkTryMap(self):
        res = self.execFunc('try_map')
        self.assertEqual(res, "[2, 3, 4]")

    def checkApply(self):
        del apply_wrapper_called[:]
        res = self.execFunc('try_apply')
        self.assertEqual(apply_wrapper_called, ["yes"])
        self.assertEqual(res, "321")

    def checkInplace(self):
        inplacevar_wrapper_called.clear()
        res = self.execFunc('try_inplace')
        self.assertEqual(inplacevar_wrapper_called['+='], (1, 3))

    def checkDenied(self):
        for k in rmodule.keys():
            if k[:6] == 'denied':
                try:
                    self.execFunc(k, RestrictedObject())
                except AccessDenied:
                    # Passed the test
                    pass
                else:
                    self.fail('%s() did not trip security' % k)

    def checkSyntaxSecurity(self):
        self._checkSyntaxSecurity('security_in_syntax.py')
        if sys.version_info >= (2, 6):
            self._checkSyntaxSecurity('security_in_syntax26.py')

    def _checkSyntaxSecurity(self, mod_name):
        # Ensures that each of the functions in security_in_syntax.py
        # throws a SyntaxError when using compile_restricted.
        fn = os.path.join(_HERE, 'security_in_syntax.py')
        f = open(fn, 'r')
        source = f.read()
        f.close()
        # Unrestricted compile.
        code = compile(source, fn, 'exec')
        m = {'__builtins__': {'__import__':minimal_import}}
        exec code in m
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
                    self.fail('%s should not have compiled' % k)

    def checkOrderOfOperations(self):
        res = self.execFunc('order_of_operations')
        self.assertEqual(res, 0)

    def checkRot13(self):
        res = self.execFunc('rot13', 'Zope is k00l')
        self.assertEqual(res, 'Mbcr vf x00y')

    def checkNestedScopes1(self):
        res = self.execFunc('nested_scopes_1')
        self.assertEqual(res, 2)

    def checkUnrestrictedEval(self):
        expr = RestrictionCapableEval("{'a':[m.pop()]}['a'] + [m[0]]")
        v = [12, 34]
        expect = v[:]
        expect.reverse()
        res = expr.eval({'m':v})
        self.assertEqual(res, expect)
        v = [12, 34]
        res = expr(m=v)
        self.assertEqual(res, expect)

    def checkStackSize(self):
        for k, rfunc in rmodule.items():
            if not k.startswith('_') and hasattr(rfunc, 'func_code'):
                rss = rfunc.func_code.co_stacksize
                ss = getattr(restricted_module, k).func_code.co_stacksize
                self.failUnless(
                    rss >= ss, 'The stack size estimate for %s() '
                    'should have been at least %d, but was only %d'
                    % (k, ss, rss))


    def checkBeforeAndAfter(self):
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

            after = getattr(before_and_after, name[:-6]+'after')
            after_src = get_source(after)
            after_src = re.sub(defre, r'def \1(', after_src)
            tree_after = parse(after_src)

            self.assertEqual(str(tree_before), str(tree_after))

            rm.compile()
            verify.verify(rm.getCode())

    def _checkBeforeAndAfter(self, mod):
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

                after = getattr(mod, name[:-6]+'after')
                after_src = get_source(after)
                after_src = re.sub(defre, r'def \1(', after_src)
                tree_after = parse(after_src)

                self.assertEqual(str(tree_before), str(tree_after))

                rm.compile()
                verify.verify(rm.getCode())

    if sys.version_info[:2] >= (2, 4):
        def checkBeforeAndAfter24(self):
            from RestrictedPython.tests import before_and_after24
            self._checkBeforeAndAfter(before_and_after24)

    if sys.version_info[:2] >= (2, 5):
        def checkBeforeAndAfter25(self):
            from RestrictedPython.tests import before_and_after25
            self._checkBeforeAndAfter(before_and_after25)

    if sys.version_info[:2] >= (2, 6):
        def checkBeforeAndAfter26(self):
            from RestrictedPython.tests import before_and_after26
            self._checkBeforeAndAfter(before_and_after26)

    def _compile_file(self, name):
        path = os.path.join(_HERE, name)
        f = open(path, "r")
        source = f.read()
        f.close()

        co = compile_restricted(source, path, "exec")
        verify.verify(co)
        return co

    def checkUnpackSequence(self):
        co = self._compile_file("unpack.py")
        calls = []
        def getiter(seq):
            calls.append(seq)
            return list(seq)
        globals = {"_getiter_": getiter, '_inplacevar_': inplacevar_wrapper}
        exec co in globals, {}
        # The comparison here depends on the exact code that is
        # contained in unpack.py.
        # The test doing implicit unpacking in an "except:" clause is
        # a pain, because there are two levels of unpacking, and the top
        # level is unpacking the specific TypeError instance constructed
        # by the test.  We have to worm around that one.
        ineffable =  "a TypeError instance"
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

    def checkUnpackSequenceExpression(self):
        co = compile_restricted("[x for x, y in [(1, 2)]]", "<string>", "eval")
        verify.verify(co)
        calls = []
        def getiter(s):
            calls.append(s)
            return list(s)
        globals = {"_getiter_": getiter}
        exec co in globals, {}
        self.assertEqual(calls, [[(1,2)], (1, 2)])

    def checkUnpackSequenceSingle(self):
        co = compile_restricted("x, y = 1, 2", "<string>", "single")
        verify.verify(co)
        calls = []
        def getiter(s):
            calls.append(s)
            return list(s)
        globals = {"_getiter_": getiter}
        exec co in globals, {}
        self.assertEqual(calls, [(1, 2)])

    def checkClass(self):
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
        exec co in globals, {}
        # Note that the getattr calls don't correspond to the method call
        # order, because the x.set method is fetched before its arguments
        # are evaluated.
        self.assertEqual(getattr_calls,
                         ["set", "set", "get", "state", "get", "state"])
        self.assertEqual(setattr_calls, ["MyClass", "MyClass"])

    def checkLambda(self):
        co = self._compile_file("lambda.py")
        exec co in {}, {}

    def checkEmpty(self):
        rf = RFunction("", "", "issue945", "empty.py", {})
        rf.parse()
        rf2 = RFunction("", "# still empty\n\n# by", "issue945", "empty.py", {})
        rf2.parse()

    def checkSyntaxError(self):
        err = ("def f(x, y):\n"
               "    if x, y < 2 + 1:\n"
               "        return x + y\n"
               "    else:\n"
               "        return x - y\n")
        self.assertRaises(SyntaxError,
                          compile_restricted, err, "<string>", "exec")

    # these two tests check that source code with Windows line
    # endings still works.

    def checkLineEndingsRFunction(self):
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

    def checkLineEndingsRestrictedCompileMode(self):
        from RestrictedPython.RCompile import RestrictedCompileMode
        gen = RestrictedCompileMode(
            '# testing\r\nprint "testing"\r\nreturn printed\n',
            '<testing>'
            )
        gen.mode='exec'
        # if the source has any line ending other than \n by the time
        # parse() is called, then you'll get a syntax error.
        gen.parse()

    def checkCollector2295(self):
        from RestrictedPython.RCompile import RestrictedCompileMode
        gen = RestrictedCompileMode(
            'if False:\n  pass\n# Me Grok, Say Hi',
            '<testing>'
            )
        gen.mode='exec'
        # if the source has any line ending other than \n by the time
        # parse() is called, then you'll get a syntax error.
        gen.parse()

        
create_rmodule()

def test_suite():
    return unittest.makeSuite(RestrictionTests, 'check')

if __name__=='__main__':
    unittest.main(defaultTest="test_suite")
