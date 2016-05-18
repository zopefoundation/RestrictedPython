Notes on the Update Process to be Python 3 compatible
=====================================================

*Note, due to my English, I sometimes fall back to German on describing my ideas and learnings.*

Current state
-------------

Idea of RestrictedPython
........................

RestrictedPython offers a replacement for the Python builtin function ``compile()`` (https://docs.python.org/2/library/functions.html#compile) which is defined as:

.. code:: Python
    :caption: compile()

    compile(source, filename, mode [, flags [, dont_inherit]])

The definition of compile has changed over the time, but the important element is the param ``mode``, there are three allowed values for this string param:

* ``'exec'``
* ``'eval'``
* ``'single'``

RestrictedPython has it origin in the time of Python 1 and early Python 2.
The optional params ``flags`` and ``dont_inherit`` has been added to Python's ``compile()`` function with Version Python 2.3.
RestrictedPython never added those new parameters to implementation.
The definition of

.. code:: Python

    compile_restricted(source, filename, mode)


The primary param ``source`` has been restriced to be an ASCII string or ``unicode`` string.



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


Version Support of RestrictedPython 3.6.x
.........................................

RestrictedPython 3.6.x aims on supporting Python versions:

* 2.0
* 2.1
* 2.2
* 2.3
* 2.4
* 2.5
* 2.6
* 2.7

Even if the README claims that Compatibility Support is form Python 2.3 - 2.7 I found some Code in RestricedPython and related Packages which test if Python 1 is used.

Due to this approach to support all Python 2 Versions the code uses only statements that are compatible with all of those versions.

So oldstyle classes and newstyle classes are mixed,

The following language elements are statements and not functions:

* exec
* print



Goals for Rewrite
-----------------

We want to rewrite RestrictedPython as it is one of the core dependencies for the Zope2 Application Server which is the base for the CMS Plone.
Zope2 should become Python3 compatible.

One of the core features of Zope2 and therefore Plone is the capability to write and modify Code and Templates TTW (through the web).
As Python is a Turing Complete programming language programmers don't have any limitation and could potentially harm the Application and Server itself.

RestrictedPython and AccessControl aims on this topic to provide a reduced subset of the Python Programming language, where all functions that could harm the system are permitted by default.

Therefore RestrictedPython provide a way to define Policies and





Zope2 Core Packages that has RestrictedPython as dependencies
.............................................................

The following Packages used in Zope2 for Plone depend on RestricedPython:

* AccessControl
* zope.untrustedpython
* DocumentTemplate
* Products.PageTemplates
* Products.PythonScripts
* Products.PluginIndexes
* five.pt (wrapping some functions and procetion for Chameleon)

Targeted Versions to support
............................

For a RestrictedPython 4.0.0+ Update we aim to support only current Python Versions (under active Security Support):

* 2.6
* 2.7
* 3.2
* 3.3
* 3.4
* 3.5

Targeted API
............


.. code:: Python

    compile(source, filename, mode [, flags [, dont_inherit]])
    compile_restricted(source, filename, mode [, flags [, dont_inherit]])


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

Technical Backgrounds
.....................

https://docs.python.org/3.5/library/ast.html#abstract-grammar

NodeVistiors (https://docs.python.org/3.5/library/ast.html#ast.NodeVisitor)

NodeTransformer (https://docs.python.org/3.5/library/ast.html#ast.NodeTransformer)

dump (https://docs.python.org/3.5/library/ast.html#ast.dump)






Links
-----

* Concept of Immutable Types and Python Example (https://en.wikipedia.org/wiki/Immutable_object#Python)
* Python 3 Standard Library Documentation on AST module ``ast`` (https://docs.python.org/3/library/ast.html)
* Indetail Documentation on the Python AST module ``ast`` (https://greentreesnakes.readthedocs.org/en/latest/)
* Example how to Instrumenting the Python AST (``ast.AST``) (http://www.dalkescientific.com/writings/diary/archive/2010/02/22/instrumenting_the_ast.html)
