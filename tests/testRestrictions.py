
from string import rfind
import sys, os

if __name__=='__main__':
    sys.path.append(os.path.join(os.pardir, os.pardir))

import unittest
from RestrictedPython import compile_restricted, PrintCollector
from RestrictedPython.Eval import RestrictionCapableEval
from RestrictedPython.tests import restricted_module, security_in_syntax
from types import FunctionType

if __name__=='__main__':
    sys.path.append(os.path.join(os.pardir, os.pardir))
    here = os.curdir
else:
    from App.Common import package_home
    from RestrictedPython import tests
    here = package_home(tests.__dict__)

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

def create_rmodule():
    global rmodule
    fn = os.path.join(here, 'restricted_module.py')
    f = open(fn, 'r')
    source = f.read()
    f.close()
    # Sanity check
    compile(source, fn, 'exec')
    # Now compile it for real
    code = compile_restricted(source, fn, 'exec')
    rmodule = {'__builtins__':{'__import__':__import__, 'None':None}}
    builtins = getattr(__builtins__, '__dict__', __builtins__)
    for name in ('map', 'reduce', 'int', 'pow', 'range', 'filter',
                 'len', 'chr', 'ord',
                 ):
        rmodule[name] = builtins[name]
    exec code in rmodule

create_rmodule()

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

##    attribute_of_anything = 98.6

class RestrictionTests(unittest.TestCase):
    def execFunc(self, name, *args, **kw):
        func = rmodule[name]
        func.func_globals.update({'_getattr_': guarded_getattr,
                                  '_getitem_': guarded_getitem,
                                  '_write_': TestGuard,
                                  '_print_': PrintCollector})
        return func(*args, **kw)

    def checkPrint(self):
        for i in range(2):
            res = self.execFunc('print%s' % i)
            assert res == 'Hello, world!', res

    def checkPrintToNone(self):
        try:
            res = self.execFunc('printToNone')
        except AttributeError:
            # Passed.  "None" has no "write" attribute.
            pass
        else:
            assert 0, res

    def checkPrintStuff(self):
        res = self.execFunc('printStuff')
        assert res == 'a b c', res

    def checkPrintLines(self):
        res = self.execFunc('printLines')
        assert res == '0 1 2\n3 4 5\n6 7 8\n', res

    def checkPrimes(self):
        res = self.execFunc('primes')
        assert res == '[2, 3, 5, 7, 11, 13, 17, 19]', res

    def checkAllowedSimple(self):
        res = self.execFunc('allowed_simple')
        assert res == 'abcabcabc', res

    def checkAllowedRead(self):
        self.execFunc('allowed_read', RestrictedObject())

    def checkAllowedWrite(self):
        self.execFunc('allowed_write', RestrictedObject())

    def checkAllowedArgs(self):
        self.execFunc('allowed_default_args', RestrictedObject())

    def checkDenied(self):
        for k in rmodule.keys():
            if k[:6] == 'denied':
                try:
                    self.execFunc(k, RestrictedObject())
                except AccessDenied:
                    # Passed the test
                    pass
                else:
                    raise AssertionError, '%s() did not trip security' % k

    def checkSyntaxSecurity(self):
        # Ensures that each of the functions in security_in_syntax.py
        # throws a SyntaxError when using compile_restricted.
        fn = os.path.join(here, 'security_in_syntax.py')
        f = open(fn, 'r')
        source = f.read()
        f.close()
        # Unrestricted compile.
        code = compile(source, fn, 'exec')
        m = {'__builtins__':None}
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
                    raise AssertionError, '%s should not have compiled' % k

##    def checkStrangeAttribute(self):
##        res = self.execFunc('strange_attribute')
##        assert res == 98.6, res

    def checkOrderOfOperations(self):
        res = self.execFunc('order_of_operations')
        assert (res == 0), res

    def checkRot13(self):
        res = self.execFunc('rot13', 'Zope is k00l')
        assert (res == 'Mbcr vf x00y'), res

    def checkNestedScopes1(self):
        res = self.execFunc('nested_scopes_1')
        assert (res == 2), res

    def checkUnrestrictedEval(self):
        expr = RestrictionCapableEval("{'a':[m.pop()]}['a'] + [m[0]]")
        v = [12, 34]
        expect = v[:]
        expect.reverse()
        res = expr.eval({'m':v})
        assert res == expect, res
        v = [12, 34]
        res = expr(m=v)
        assert res == expect

    def checkStackSize(self):
        for k, rfunc in rmodule.items():
            if not k.startswith('_') and hasattr(rfunc, 'func_code'):
                rss = rfunc.func_code.co_stacksize
                ss = getattr(restricted_module, k).func_code.co_stacksize
                self.failUnless(
                    rss >= ss, 'The stack size estimate for %s() '
                    'should have been at least %d, but was only %d'
                    % (k, ss, rss))

def test_suite():
    return unittest.makeSuite(RestrictionTests, 'check')

def main():
    alltests=test_suite()
    runner = unittest.TextTestRunner()
    runner.run(alltests)

def debug():
   test_suite().debug()

def pdebug():
    import pdb
    pdb.run('debug()')

if __name__=='__main__':
    if len(sys.argv) > 1:
        globals()[sys.argv[1]]()
    else:
        main()
