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
* ``utility_builtins`` which provides access for standard modules math, random, string and for sets.

Guards
......

.. todo::

    Describe Guards and predefined guard methods in details

RestrictedPython predefines several guarded access and manipulation methods:

* ``guarded_setattr``
* ``guarded_delattr``
* ``guarded_iter_unpack_sequence``
* ``guarded_unpack_sequence``

Those and additional methods rely on a helper construct ``full_write_guard``, which is intended to help implement immutable and semi mutable objects and attributes.

.. todo::

    Describe full_write_guard more in detail and how it works.
