from RestrictedPython import compile_restricted_exec


def test_1():
    source_code = """
g = None
leak = None

def test():
    global g, leak
    leak = g.gi_frame.f_back.f_back
    yield leak

g = test()
g.send(None)
os = leak.f_builtins.get('__import__')('os')

result = os.listdir('/')
"""
    result = compile_restricted_exec(source_code)
    assert result.errors == (
        'Line 7: "f_back" is a reserved inspect attribute name, '
        'that is forbidden to call in RestrictedPython',
        'Line 7: "f_back" is a reserved inspect attribute name, '
        'that is forbidden to call in RestrictedPython',
        'Line 7: "gi_frame" is a reserved inspect attribute name, '
        'that is forbidden to call in RestrictedPython',
        'Line 12: "f_builtins" is a reserved inspect attribute name, '
        'that is forbidden to call in RestrictedPython',
    )


def test_2():
    source_code = """
q = (q.gi_frame.f_back.f_back.f_back for _ in (1,))
result = [x for x in q][0].f_builtins['__import__']('os').listdir('/')
"""
    result = compile_restricted_exec(source_code)
    assert result.errors == (
        'Line 2: "f_back" is a reserved inspect attribute name, '
        'that is forbidden to call in RestrictedPython',
        'Line 2: "f_back" is a reserved inspect attribute name, '
        'that is forbidden to call in RestrictedPython',
        'Line 2: "f_back" is a reserved inspect attribute name, '
        'that is forbidden to call in RestrictedPython',
        'Line 2: "gi_frame" is a reserved inspect attribute name, '
        'that is forbidden to call in RestrictedPython',
        'Line 3: "f_builtins" is a reserved inspect attribute name, '
        'that is forbidden to call in RestrictedPython',
    )
