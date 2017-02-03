.. _sec_usage_frameworks:

Usage in frameworks and Zope
----------------------------

One major issue with using ``compile_restricted`` directly in a framework is, that you have to use try-except statements to handle problems and it might be a bit harder to provide useful information to the user.
RestrictedPython provides four specialized compile_restricted methods:

* ``compile_restricted_exec``
* ``compile_restricted_eval``
* ``compile_restricted_single``
* ``compile_restricted_function``

Those four methods return a tuple with four elements:

* ``byte_code`` <code> object or ``None`` if ``errors`` is not empty
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
For that use case RestrictedPython provide the possibility to pass an own policy.
A policy is basically a special ``NodeTransformer`` that could be instantiated with three params for ``errors``, ``warnings`` and ``used_names``, it should be a subclass of RestrictingNodeTransformer (that subclassing will maybe later be enforced).

.. code:: Python

    OwnRestrictingNodeTransformer(errors=[], warnings=[], used_names=[])

One special case (defined to unblock ports of Zope Packages to Python 3) is to actually use RestrictedPython in an unrestricted mode, by providing a Null-Policy (aka ``None``).

All ``compile_restricted*`` methods do have a optional parameter ``policy``, where a specific policy could be provided.

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
