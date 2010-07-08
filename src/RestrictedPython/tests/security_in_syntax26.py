# These are all supposed to raise a SyntaxError when using
# compile_restricted() but not when using compile().
# Each function in this module is compiled using compile_restricted().

def with_as_bad_name():
    with x as _leading_underscore:
        pass

def relative_import_as_bad_name():
    from .x import y as _leading_underscore

def except_as_bad_name():
    try:
        1/0
    except Exception as _leading_underscore:
        pass
