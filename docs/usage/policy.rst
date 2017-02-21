.. _policy_builtins:

Policies & builtins
-------------------

.. todo::

    Should be described in detail.
    Especially the difference between builtins and a policy which is a NodeTransformer.


RestrictedPython provides a way to define Policies, by redefining restricted versions of ``print``, ``getattr``, ``setattr``, ``import``, etc..
As shortcuts it offers three stripped down versions of Pythons ``__builtins__``:

.. _predefined_builtins:

Predefined builtins
...................

.. todo::

    Describe more in details

* ``safe_builtins`` a safe set of builtin modules and functions,
* ``limited_builtins`` which provides restricted sequence types,
* ``utilities_builtins`` which provides access for standard modules math, random, string and for sets.

Guards
......

.. todo::

    Describe Guards and predefined guard methods in details

There is also a guard function for making attributes immutable --> ``full_write_guard`` (write and delete protected)
