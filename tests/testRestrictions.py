
from string import rfind
import sys, os

if __name__=='__main__':
    sys.path.append(os.path.join(os.pardir, os.pardir))

import unittest
from RestrictedPython import compile_restricted, PrintCollector
from RestrictedPython.Eval import RestrictionCapableEval
import security_in_syntax
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
    rmodule = {'__builtins__':None}
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


class TestGuard:
    '''A guard class'''
    def __init__(self, _ob, write=None):
        self.__dict__['_ob'] = _ob

    # Read guard methods
    def __len__(self):
        return len(self.__dict__['_ob'])

    def __getattr__(self, name):
        _ob = self.__dict__['_ob']
        v = getattr(_ob, name)
        if v is DisallowedObject:
            raise AccessDenied
        return v

    def __getitem__(self, index):
        # Can receive an Ellipsis or "slice" instance.
        _ob = self.__dict__['_ob']
        v = _ob[index]
        if v is DisallowedObject:
            raise AccessDenied
        return v

    def __getslice__(self, lo, hi):
        _ob = self.__dict__['_ob']
        return _ob[lo:hi]

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

    attribute_of_anything = 98.6

class RestrictionTests(unittest.TestCase):
    def execFunc(self, name, *args, **kw):
        func = rmodule[name]
        func.func_globals.update({'_read_': TestGuard,
                                  '_write_': TestGuard,
                                  '_print_': PrintCollector})
        return func(*args, **kw)

    def checkPrint(self):
        for i in range(3):
            res = self.execFunc('print%s' % i)
            assert res == 'Hello, world!', res

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

    def checkStrangeAttribute(self):
        res = self.execFunc('strange_attribute')
        assert res == 98.6, res

    def checkOrderOfOperations(self):
        res = self.execFunc('order_of_operations')
        assert (res == 0), res

    def checkRot13(self):
        res = self.execFunc('rot13', 'Zope is k00l')
        assert (res == 'Mbcr vf x00y'), res

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
