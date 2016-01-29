Notes on the Update Process to be Python 3 compatible
=====================================================

*Note, due to my English, I sometimes fall back to German on describing current state*

Current state
-------------

RestrictedPython is based on the Python 2 only standard library module `compiler https://docs.python.org/2.7/library/compiler.html`_.

RestrictedPython offers a replacement for the Python builtin function compile()

.. code:: Python

    compile(soure, filename, mode [, flags [, dont_inhearit]])

    compile_restricted(soure, filename, mode [, flags [, dont_inhearit]])

Also RestrictedPython



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
As Python is a Touring Complete programming language programmers don't have any limitation and could potentially harm the Application and Server itself.

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


Targeted Versions to support
............................

For a RestrictedPython 4.0.0+ Update we aim to support only current Python Versions:

* 2.6
* 2.7
* 3.2
* 3.3
* 3.4
* 3.5


Approach
--------

RestrictedPython is a classical approach of compiler construction to create a limited subset of an existing programming language.

As compiler construction do have basic concepts on how to build a Programming Language and Runtime Environment.
