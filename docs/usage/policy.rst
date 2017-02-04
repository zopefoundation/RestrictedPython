Policies & builtins
-------------------



Also RestrictedPython provides a way to define Policies, by redefining restricted versions of ``print``, ``getattr``, ``setattr``, ``import``, etc..
As shortcutes it offers three stripped down versions of Pythons ``__builtins__``:

* ``safe_builtins`` (by Guards.py)
* ``limited_builtins`` (by Limits.py), which provides restriced sequence types
* ``utilities_builtins`` (by Utilities.py), which provides access for standard modules math, random, string and for sets.

There is also a guard function for making attributes immutable --> ``full_write_guard`` (write and delete protected)
