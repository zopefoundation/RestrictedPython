.. _sec_usage_frameworks:

Usage in frameworks and Zope
----------------------------

One major issue with using ``compile_restricted`` directly in a framework is, that you have to use try-except statements to handle problems and it might be a bit harder to provide useful information to the user.
RestrictedPython provides four specialized compile_restricted methods:

* ``compile_restricted_exec``
* ``compile_restricted_eval``
* ``compile_restricted_single``
* ``compile_restricted_function``

Those four methods return a named tuple (``CompileResult``) with four elements:

* ``code`` ``<code>`` object or ``None`` if ``errors`` is not empty
* ``errors`` a tuple with error messages
* ``warnings`` a list with warnings
* ``used_names`` a set / dictionary with collected used names of library calls

Those three information "lists" could be used to provide the user with informations about the compiled source code.

Typical uses cases for the four specialized methods:

* ``compile_restricted_exec`` --> Python Modules or Scripts that should be used or called by the framework itself or from user calls
* ``compile_restricted_eval`` --> Templates
* ``compile_restricted_single``
* ``compile_restricted_function``

Modifying the builtins is straight forward, it is just a dictionary containing access pointers to available library elements.
Modification is normally removing elements from existing builtins or adding allowed elements by copying from globals.

For frameworks it could possibly also be useful to change handling of specific Python language elements.
For that use case RestrictedPython provides the possibility to pass an own policy.

A policy is basically a special ``NodeTransformer`` that could be instantiated with three params for ``errors``, ``warnings`` and ``used_names``, it should be a subclass of RestrictedPython.RestrictingNodeTransformer.

.. testcode:: own_policy

    from RestrictedPython import compile_restricted
    from RestrictedPython import RestrictingNodeTransformer

    class OwnRestrictingNodeTransformer(RestrictingNodeTransformer):
        pass

    policy_instance = OwnRestrictingNodeTransformer(errors=[],
                                                    warnings=[],
                                                    used_names=[])

All ``compile_restricted*`` methods do have a optional parameter ``policy``, where a specific policy could be provided.

.. testcode:: own_policy

    source_code = """
    def do_something():
        pass
    """

    policy = OwnRestrictingNodeTransformer

    byte_code = compile_restricted(source_code,
                                   filename='<inline code>',
                                   mode='exec',
                                   policy=policy # Policy Class
                                   )
    exec(byte_code, globals(), None)

One special case "unrestricted RestrictedPython" (defined to unblock ports of Zope Packages to Python 3) is to actually use RestrictedPython in an unrestricted mode, by providing a Null-Policy (aka ``None``).
That special case would be written as:

.. testcode::

    from RestrictedPython import compile_restricted

    source_code = """
    def do_something():
        pass
    """

    byte_code = compile_restricted(source_code,
                                   filename='<inline code>',
                                   mode='exec',
                                   policy=None # Null-Policy -> unrestricted
                                   )
    exec(byte_code, globals(), None)
