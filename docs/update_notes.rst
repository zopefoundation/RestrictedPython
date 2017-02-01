Notes on the Update Process to be Python 3 compatible
=====================================================


Also RestrictedPython provides a way to define Policies, by redefining restricted versions of ``print``, ``getattr``, ``setattr``, ``import``, etc..
As shortcutes it offers three stripped down versions of Pythons ``__builtins__``:

* ``safe_builtins`` (by Guards.py)
* ``limited_builtins`` (by Limits.py), which provides restriced sequence types
* ``utilities_builtins`` (by Utilities.py), which provides access for standard modules math, random, string and for sets.

There is also a guard function for making attributes immutable --> ``full_write_guard`` (write and delete protected)



Technical foundation of RestrictedPython
........................................

RestrictedPython is based on the Python 2 only standard library module ``compiler`` (https://docs.python.org/2.7/library/compiler.html).
RestrictedPython based on the

* compiler.ast
* compiler.parse
* compiler.pycodegen

With Python 2.6 the compiler module with all its sub modules has been declared deprecated with no direct upgrade Path or recommendations for a replacement.


Approach
--------

RestrictedPython is a classical approach of compiler construction to create a limited subset of an existing programming language.

As compiler construction do have basic concepts on how to build a Programming Language and Runtime Environment.

Defining a Programming Language means to define a regular grammar (Chomsky 3 / EBNF) first.
This grammar will be implemented in an abstract syntax tree (AST), which will be passed on to a code generator to produce a machine understandable version.

As Python is a plattform independend programming / scripting language, this machine understandable version is a byte code which will be translated on the fly by an interpreter into machine code.
This machine code then gets executed on the specific CPU architecture, with all Operating System restriction.

Produced byte code has to compatible with the execution environment, the Python Interpreter within this code is called.
So we must not generate the byte code that has to be returned from ``compile_restricted`` and the other ``compile_restricted_*`` methods manually, as this might harm the interpreter.
We actually don't even need that.
The Python ``compile()`` function introduced the capability to compile ``ast.AST`` code into byte code.
