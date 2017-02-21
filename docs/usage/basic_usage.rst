Basic usage
-----------

The general workflow to execute Python code that is loaded within a Python program is:

.. code:: Python

    source_code = """
    def do_something():
        pass
    """

    byte_code = compile(source_code, filename='<inline code>', mode='exec')
    exec(byte_code)
    do_something()

.. doctest::
    :hide:

    >>> source_code = """
    ... def do_something():
    ...     pass
    ... """
    >>> byte_code = compile(source_code, filename='<inline code>', mode='exec')
    >>> exec(byte_code)
    >>> do_something()


With RestrictedPython that workflow should be as straight forward as possible:

.. code:: Python

    from RestrictedPython import compile_restricted

    source_code = """
    def do_something():
        pass
    """

    byte_code = compile_restricted(source_code, filename='<inline code>', mode='exec')
    exec(byte_code)
    do_something()


.. doctest::
    :hide:

    >>> from RestrictedPython import compile_restricted
    >>> source_code = """
    ... def do_something():
    ...     pass
    ... """
    >>> byte_code = compile_restricted(source_code, filename='<inline code>', mode='exec')
    >>> exec(byte_code)
    >>> do_something()

You might also use the replacement import:

.. code:: Python

    from RestrictedPython import compile_restricted as compile

``compile_restricted`` uses a predefined policy that checks and modify the source code and checks against a restricted subset of the Python language.
The compiled source code is still executed against the full available set of library modules and methods.

The Python :py:func:`exec` takes three parameters:

* ``code`` which is the compiled byte code
* ``globals`` which is global dictionary
* ``locals`` which is the local dictionary

By limiting the entries in the ``globals`` and ``locals`` dictionaries you
restrict the access to the available library modules and methods.

Providing defined dictionaries for ``exec()`` should be used in context of RestrictedPython.

.. code:: Python

    byte_code = <code>
    exec(byte_code, { ... }, { ... })

Typically there is a defined set of allowed modules, methods and constants used in that context.
RestrictedPython provides three predefined built-ins for that (see :ref:`predefined_builtins` for details):

* ``safe_builtins``
* ``limited_builtins``
* ``utilities_builtins``

So you normally end up using:

.. code:: Python

    #from RestrictedPython import ..._builtins
    from RestrictedPython import safe_builtins
    from RestrictedPython import limited_builtins
    from RestrictedPython import utilities_builtins
    from RestrictedPython import compile_restricted

    source_code = """<demo code>"""

    try:
        byte_code = compile_restricted(source_code, filename='<name>', mode='exec')

        #used_builtins = ..._builtins + { <additionl elems> } # Whitelisting additional elements
        used_builtins = safe_builtins
        exec(byte_code, used_buildins, None)
    except SyntaxError as e:
        ...

One common advanced usage would be to define an own restricted builtin dictionary.
