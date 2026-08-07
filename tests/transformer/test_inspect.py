from RestrictedPython import compile_restricted_exec


def test_get_inspect_frame_on_generator():
    source_code = """
generator = (statement.gi_frame for _ in (1,))
generator_element = [elem for elem in generator][0]

"""
    result = compile_restricted_exec(source_code)
    assert result.errors == (
        'Line 2: "gi_frame" is a restricted name, '
        'that is forbidden to access in RestrictedPython.',
    )


def test_get_inspect_frame_back_on_generator():
    source_code = """
generator = (statement.gi_frame.f_back.f_back for _ in (1,))
generator_element = [elem for elem in generator][0]

"""
    result = compile_restricted_exec(source_code)
    assert result.errors == (
        'Line 2: "f_back" is a restricted name, '
        'that is forbidden to access in RestrictedPython.',
        'Line 2: "f_back" is a restricted name, '
        'that is forbidden to access in RestrictedPython.',
        'Line 2: "gi_frame" is a restricted name, '
        'that is forbidden to access in RestrictedPython.',
    )


def test_call_inspect_frame_on_generator():
    source_code = """
generator = None
frame = None

def test():
    global generator, frame
    frame = g.gi_frame.f_back.f_back
    yield frame

generator = test()
generator.send(None)
os = frame.f_builtins.get('__import__')('os')

result = os.listdir('/')
"""
    result = compile_restricted_exec(source_code)
    assert result.errors == (
        'Line 7: "f_back" is a restricted name, '
        'that is forbidden to access in RestrictedPython.',
        'Line 7: "f_back" is a restricted name, '
        'that is forbidden to access in RestrictedPython.',
        'Line 7: "gi_frame" is a restricted name, '
        'that is forbidden to access in RestrictedPython.',
        'Line 12: "f_builtins" is a restricted name, '
        'that is forbidden to access in RestrictedPython.',
    )
