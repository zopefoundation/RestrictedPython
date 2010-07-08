# These are all supposed to raise a SyntaxError when using
# compile_restricted() but not when using compile().
# Each function in this module is compiled using compile_restricted().

def dict_comp_bad_name():
    {y: y for _restricted_name in x}

def set_comp_bad_name():
    {y for _restricted_name in x}

def compound_with_bad_name():
    with a as b, c as _restricted_name:
        pass
