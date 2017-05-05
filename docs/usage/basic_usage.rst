Basic usage
-----------

The general workflow to execute Python code that is loaded within a Python program is:

.. testcode::

    source_code = """
    def do_something():
        pass
    """

    byte_code = compile(source_code, filename='<inline code>', mode='exec')
    exec(byte_code)
    do_something()

With RestrictedPython that workflow should be as straight forward as possible:

.. testcode::

    from RestrictedPython import compile_restricted

    source_code = """
    def do_something():
        pass
    """

    byte_code = compile_restricted(source_code,
                                   filename='<inline code>',
                                   mode='exec')
    exec(byte_code)
    do_something()

You might also use the replacement import:

.. testcode::

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
* ``utility_builtins``

So you normally end up using:

.. testcode::

    from RestrictedPython import compile_restricted

    from RestrictedPython import safe_builtins
    from RestrictedPython import limited_builtins
    from RestrictedPython import utility_builtins

    source_code = """
    def do_something():
        pass
    """

    try:
        byte_code = compile_restricted(source_code,
                                       filename='<inline code>',
                                       mode='exec')

        exec(byte_code, safe_builtins, None)
    except SyntaxError as e:
        pass

One common advanced usage would be to define an own restricted builtin dictionary.

Necessary setup
---------------

`RestrictedPython` requires some predefined names in globals in order to work
properly.

To use classes in Python 3
    ``__metaclass__`` must be set. Set it to ``type`` to use no custom metaclass.

To use ``for`` statements and comprehensions
    ``_iter_unpack_sequence_`` must point to :func:`RestrictedPython.Guards.guarded_iter_unpack_sequence`.

The usage of `RestrictedPython` in :mod:`AccessControl.ZopeGuards` can serve as example.
