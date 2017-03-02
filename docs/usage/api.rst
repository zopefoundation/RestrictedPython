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



2. restricted builtins

  * ``safe_builtins``
  * ``limited_builtins``
  * ``utility_builtins``

3. helper modules

  * ``PrintCollector``
