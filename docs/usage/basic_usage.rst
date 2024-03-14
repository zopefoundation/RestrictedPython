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

    byte_code = compile_restricted(
        source_code,
        filename='<inline code>',
        mode='exec'
    )
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

.. code-block:: python

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
        byte_code = compile_restricted(
            source_code,
            filename='<inline code>',
            mode='exec'
        )
        exec(byte_code, {'__builtins__': safe_builtins}, None)
    except SyntaxError as e:
        pass

One common advanced usage would be to define an own restricted builtin dictionary.

There is a shortcut for ``{'__builtins__': safe_builtins}`` named ``safe_globals`` which can be imported from ``RestrictedPython``.

Other Usages
------------

RestrictedPython has similar to normal Python multiple modes:

* exec
* eval
* single
* function

you can use it by:

.. testcode::

    from RestrictedPython import compile_restricted

    source_code = """
    def do_something():
        pass
    """

    byte_code = compile_restricted(
        source_code,
        filename='<inline code>',
        mode='exec'
    )
    exec(byte_code)
    do_something()

.. testcode::

    from RestrictedPython import compile_restricted

    byte_code = compile_restricted(
        "2 + 2",
        filename='<inline code>',
        mode='eval'
    )
    eval(byte_code)


.. testcode:: single

    from RestrictedPython import compile_restricted

    byte_code = compile_restricted(
        "2 + 2",
        filename='<inline code>',
        mode='single'
    )
    exec(byte_code)

.. testoutput:: single

    4

Necessary setup
---------------

`RestrictedPython` requires some predefined names in globals in order to work
properly.

To use classes in Python 3
    * ``__metaclass__`` must be set. Set it to ``type`` to use no custom metaclass.
    * ``__name__`` must be set. As classes need a namespace to be defined in.
      It is the name of the module the class is defined in. You might set it to
      an arbitrary string.

To use ``for`` statements and comprehensions:
    * ``_getiter_`` must point to an ``iter`` implementation. As an unguarded variant you might use
      :func:`RestrictedPython.Eval.default_guarded_getiter`.

    *  ``_iter_unpack_sequence_`` must point to :func:`RestrictedPython.Guards.guarded_iter_unpack_sequence`.

To use ``getattr``
    you have to provide an implementation for it.
    :func:`RestrictedPython.Guards.safer_getattr` can be a starting point.

The usage of `RestrictedPython` in :mod:`AccessControl.ZopeGuards` can serve as example.
