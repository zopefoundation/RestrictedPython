
def print0():
    print 'Hello, world!',
    return printed

def print1():
    print 'Hello,',
    print 'world!',
    return printed

def printStuff():
    print 'a', 'b', 'c',
    return printed

def printToNone():
    x = None
    print >>x, 'Hello, world!',
    return printed

def printLines():
    # This failed before Zope 2.4.0a2
    r = range(3)
    for n in r:
        for m in r:
            print m + n * len(r),
        print
    return printed

def primes():
    # Somewhat obfuscated code on purpose
    print filter(None,map(lambda y:y*reduce(lambda x,y:x*y!=0,
    map(lambda x,y=y:y%x,range(2,int(pow(y,0.5)+1))),1),range(2,20))),
    return printed

def allowed_read(ob):
    print ob.allowed
    print ob.s
    print ob[0]
    print ob[2]
    print ob[3:-1]
    print len(ob)
    return printed

def allowed_simple():
    q = {'x':'a'}
    q['y'] = 'b'
    q.update({'z': 'c'})
    r = ['a']
    r.append('b')
    r[2:2] = ['c']
    s = 'a'
    s = s[:100] + 'b'
    s += 'c'
    _ = q
    
    return q['x'] + q['y'] + q['z'] + r[0] + r[1] + r[2] + s

def allowed_write(ob):
    ob.writeable = 1
    #ob.writeable += 1
    [1 for ob.writeable in 1,2]
    ob['safe'] = 2
    #ob['safe'] += 2
    [1 for ob['safe'] in 1,2]

def denied_print(ob):
    print >> ob, 'Hello, world!',

def denied_getattr(ob):
    #ob.disallowed += 1
    ob.disallowed = 1
    return ob.disallowed

def denied_setattr(ob):
    ob.allowed = -1

def denied_setattr2(ob):
    #ob.allowed += -1
    ob.allowed = -1

def denied_setattr3(ob):
    [1 for ob.allowed in 1,2]

def denied_getitem(ob):
    ob[1]

def denied_getitem2(ob):
    #ob[1] += 1
    ob[1]
    
def denied_setitem(ob):
    ob['x'] = 2

def denied_setitem2(ob):
    #ob[0] += 2
    ob['x'] = 2

def denied_setitem3(ob):
    [1 for ob['x'] in 1,2]

def denied_setslice(ob):
    ob[0:1] = 'a'

def denied_setslice2(ob):
    #ob[0:1] += 'a'
    ob[0:1] = 'a'

def denied_setslice3(ob):
    [1 for ob[0:1] in 1,2]

##def strange_attribute():
##    # If a guard has attributes with names that don't start with an
##    # underscore, those attributes appear to be an attribute of
##    # anything.
##    return [].attribute_of_anything

def order_of_operations():
    return 3 * 4 * -2 + 2 * 12

def rot13(ss):
    mapping = {}
    orda = ord('a')
    ordA = ord('A')
    for n in range(13):
        c1 = chr(orda + n)
        c2 = chr(orda + n + 13)
        c3 = chr(ordA + n)
        c4 = chr(ordA + n + 13)
        mapping[c1] = c2
        mapping[c2] = c1
        mapping[c3] = c4
        mapping[c4] = c3
    del c1, c2, c3, c4, orda, ordA
    res = ''
    for c in ss:
        res = res + mapping.get(c, c)
    return res


