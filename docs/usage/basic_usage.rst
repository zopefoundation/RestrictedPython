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

With RestrictedPython that workflow should be as straight forward as possible:

.. code:: Python

    from RestrictedPython import compile_restricted as compile

    source_code = """
    def do_something():
        pass
    """

    byte_code = compile(source_code, filename='<inline code>', mode='exec')
    exec(byte_code)
    do_something()

With that simple addition:

.. code:: Python

    from RestrictedPython import compile_restricted as compile

it uses a predefined policy that checks and modify the source code and checks against a restricted subset of the Python language.
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
RestrictedPython provides three predefined built-ins for that:

* ``safe_builtins``
* ``limited_builtins``
* ``utilities_builtins``

So you normally end up using:

.. code:: Python

    from RestrictedPython import ..._builtins
    from RestrictedPython import compile_restricted as compile

    source_code = """<demo code>"""

    try:
        byte_code = compile(source_code, filename='<name>', mode='exec')

        used_builtins = ..._builtins + { <additionl elems> }
        exec(byte_code, used_buildins, None)
    except SyntaxError as e:
        ...

One common advanced usage would be to define an own restricted builtin dictionary.
