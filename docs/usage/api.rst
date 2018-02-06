API overview
------------

RestrictedPython has tree major scopes:

1. ``compile_restricted`` methods:

.. py:method:: compile_restricted(source, filename, mode, flags, dont_inherit, policy)
    :module: RestrictedPython

    Compiles source code into interpretable byte code.

    :param source: (required). The source code that should be compiled
    :param filename: (optional).
    :param mode: (optional).
    :param flags: (optional).
    :param dont_inherit: (optional).
    :param policy: (optional).
    :type source: str or unicode text
    :type filename: str or unicode text
    :type mode: str or unicode text
    :type flags: int
    :type dont_inherit: int
    :type policy: RestrictingNodeTransformer class
    :return: Byte Code

.. py:method:: compile_restricted_exec(source, filename, flags, dont_inherit, policy)
    :module: RestrictedPython

    Compiles source code into interpretable byte code.

    :param source: (required). The source code that should be compiled
    :param filename: (optional).
    :param flags: (optional).
    :param dont_inherit: (optional).
    :param policy: (optional).
    :type source: str or unicode text
    :type filename: str or unicode text
    :type mode: str or unicode text
    :type flags: int
    :type dont_inherit: int
    :type policy: RestrictingNodeTransformer class
    :return: CompileResult (a namedtuple with code, errors, warnings, used_names)

.. py:method:: compile_restricted_eval(source, filename, flags, dont_inherit, policy)
    :module: RestrictedPython

    Compiles source code into interpretable byte code.

    :param source: (required). The source code that should be compiled
    :param filename: (optional).
    :param flags: (optional).
    :param dont_inherit: (optional).
    :param policy: (optional).
    :type source: str or unicode text
    :type filename: str or unicode text
    :type mode: str or unicode text
    :type flags: int
    :type dont_inherit: int
    :type policy: RestrictingNodeTransformer class
    :return: CompileResult (a namedtuple with code, errors, warnings, used_names)

.. py:method:: compile_restricted_single(source, filename, flags, dont_inherit, policy)
    :module: RestrictedPython

    Compiles source code into interpretable byte code.

    :param source: (required). The source code that should be compiled
    :param filename: (optional).
    :param flags: (optional).
    :param dont_inherit: (optional).
    :param policy: (optional).
    :type source: str or unicode text
    :type filename: str or unicode text
    :type mode: str or unicode text
    :type flags: int
    :type dont_inherit: int
    :type policy: RestrictingNodeTransformer class
    :return: CompileResult (a namedtuple with code, errors, warnings, used_names)

.. py:method:: compile_restricted_function(p, body, name, filename, globalize=None)
    :module: RestrictedPython

    Compiles source code into interpretable byte code.

    :param p: (required).
    :param body: (required).
    :param name: (required).
    :param filename: (required).
    :param globalize: (optional).
    :type p:
    :type body:
    :type name: str or unicode text
    :type filename: str or unicode text
    :type globalize:
    :return: byte code

    The globalize argument, if specified, is a list of variable names to be
    treated as globals (code is generated as if each name in the list
    appeared in a global statement at the top of the function).
    This allows to inject global variables into the generated function that
    feel like they are local variables, so the programmer who uses this doesn't
    have to understand that his code is executed inside a function scope
    instead of the global scope of a module.

    To actually get an executable function, you need to execute this code and
    pull out the defined function out of the locals like this:

    >>> from RestrictedPython import compile_restricted_function
    >>> compiled = compile_restricted_function('', 'pass', 'function_name')
    >>> safe_locals = {}
    >>> safe_globals = {}
    >>> exec(compiled.code, safe_globals, safe_locals)
    >>> compiled_function = safe_locals['function_name']
    >>> result = compiled_function(*[], **{})

    Then if you want to control the globals for a specific call to this
    function, you can regenerate the function like this:

    >>> my_call_specific_global_bindings = dict(foo='bar')
    >>> safe_globals = safe_globals.copy()
    >>> safe_globals.update(my_call_specific_global_bindings)
    >>> import types
    >>> new_function = types.FunctionType(
    ...     compiled_function.__code__,
    ...     safe_globals,
    ...     '<function_name>',
    ...     compiled_function.__defaults__ or ())
    >>> result = new_function(*[], **{})

2. restricted builtins

  * ``safe_builtins``
  * ``limited_builtins``
  * ``utility_builtins``

3. helper modules

  * ``PrintCollector``
