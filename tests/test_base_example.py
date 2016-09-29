from RestrictedPython import compile_restricted


SRC = """\
def hello_world():
    return "Hello World!"
"""


def test_base_example_unrestricted_compile():
    code = compile(SRC, '<string>', 'exec')
    exec(code)
    result = hello_world()
    assert result == 'Hello World!'


def test_base_example_restricted_compile():
    code = compile_restricted(SRC, '<string>', 'exec')
    exec(code)
    assert hello_world() == 'Hello World!'


PRINT_STATEMENT = """\
print("Hello World!")
"""


def test_base_example_catched_stdout():
    from RestrictedPython.PrintCollector import PrintCollector
    _print_ = PrintCollector
    code = compile_restricted(PRINT_STATEMENT, '<string>', 'exec')
    exec(code)
