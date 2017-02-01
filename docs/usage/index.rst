Usage of RestrictedPython
=========================

API overview
------------

RestrictedPython do have tree major scopes:

* ``compile_restricted`` methods

  * ``compile_restricted``
  * ``compile_restricted_exec``
  * ``compile_restricted_eval``
  * ``compile_restricted_single``
  * ``compile_restricted_function``

* restricted builtins

  * ``safe_builtins``
  * ``limited_builtins``
  * ``utility_builtins``

* Helper Moduls

  * ``PrintCollector``

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
Execution of the compiled source code is still against the full available set of library modules and methods.

The ``exec()`` :ref:`Python ``exec()`` method <python3:meth:exec>` did take three params:

* ``code`` which is the compiled byte code
* ``globals`` which is global dictionary
* ``locals`` which is the local dictionary

By limiting the entries in globals and locals dictionary you restrict access to available library modules and methods.

So providing defined dictionaries for the ``exec()`` method should be used in context of RestrictedPython.

.. code:: Python

    byte_code = <code>
    exec(byte_code, { ... }, { ... })

Typically there is a defined set of allowed modules, methods and constants used in that context.
RestrictedPython did provide three predefined builtins for that:

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

.. _sec_usage_frameworks

Usage on frameworks and Zope
----------------------------

One major issue with using ``compile_restricted`` directly in a framework is, that you have to use try except statements to handle problems and it might be a bit harder to provide useful information to the user.
RestrictedPython did provide four specialized compile_restricted methods:

* ``compile_restricted_exec``
* ``compile_restricted_eval``
* ``compile_restricted_single``
* ``compile_restricted_function``

Those four methods return a tuple with four elements:

* ``byte_code`` <code> object or ``None`` if ``errors`` is not empty
* ``errors`` a tuple with error messages
* ``warnings`` a list with warnings
* ``used_names`` a set / dictionary with collected used names of library calls

Those three information "lists" could be used to provide the user with informations about its source code.

Typical uses cases for the four specialized methods:

* ``compile_restricted_exec`` --> Python Modules or Scripts that should be used or called by the framework itself or from user calls
* ``compile_restricted_eval`` --> Templates
* ``compile_restricted_single``
* ``compile_restricted_function``

Modifying the builtins is straight forward, it is just a dictionary containing access pointer to available library elements.
Modification is normally removing elements from existing builtins or adding allowed elements by copying from globals.

For frameworks it could possibly also be useful to change handling of specific Python language elements.
For that use case RestrictedPython provide the possibility to pass an own policy.
A policy is basically a special ``NodeTransformer`` that could be instantiated with three params for ``errors``, ``warnings`` and ``used_names``, it should be a subclass of RestrictingNodeTransformer (that subclassing will maybe later be enforced).

.. code:: Python

    OwnRestrictingNodeTransformer(errors=[], warnings=[], used_names=[])

One Special case (defined for non blocking other ports to Python 3 of the Zope Packages) is to actually use RestrictedPython in an unrestricted Mode, by providing a Null-Policy (None).

All ``compile_restricted*`` methods do have a optional param policy, where a specific policy could be provided.

.. code:: Python

    source_code = """<demo code>"""

    policy = OwnRestrictingNodeTransformer

    byte_code = compile(source_code, filename='<inline code>', mode='exec', policy=policy)
    exec(byte_code, { ... }, { ... })

The Special case "unrestricted RestrictedPython" would be:

.. code:: Python

    source_code = """<demo code>"""

    byte_code = compile(source_code, filename='<inline code>', mode='exec', policy=None)
    exec(byte_code, globals(), None)
