RestrictedPython 4+
===================

RestrictedPython 4 is a complete rewrite for Python 3 compatibility.

Goals for a rewrite
-------------------

RestrictedPython is a core dependency for the Zope2 application server and therefore for the content management system Plone.
The Zope & Plone community want to continue their projects and as Python 2 will reach its end-of-life by 2020, to be replaced by Python 3.
Zope and Plone should become Python 3 compatible.

One of the core features of Zope 2 and therefore Plone is the possibility to implement and modify Python scripts and templates through the web (TTW) without harming the application or server itself.

As Python is a `Turing complete`_ programming language programmers don't have any limitation and could potentially harm the Application and Server itself.

RestrictedPython and AccessControl aims on this topic to provide a reduced subset of the Python Programming language, where all functions that could harm the system are permitted by default.

Targeted Versions to support
----------------------------

For the RestrictedPython 4 update we aim to support only current Python
versions (the ones that will have active `security support`_ after this update
will be completed):

* 2.7
* 3.4
* 3.5
* 3.6
* PyPy2.7

.. _`security support` : https://docs.python.org/devguide/index.html#branchstatus
.. _`Turing complete`: https://en.wikipedia.org/wiki/Turing_completeness

We explicitly excluded Python 3.3 and PyPy3 (which is based on the Python 3.3 specification) as the changes in Python 3.4 are significant and the Python 3.3 is nearing the end of its supported lifetime.

Dependencies
------------

The following packages / modules have hard dependencies on RestrictedPython:

* AccessControl -->
* zope.untrustedpython --> SelectCompiler
* DocumentTemplate -->
* Products.PageTemplates -->
* Products.PythonScripts -->
* Products.PluginIndexes -->
* five.pt (wrapping some functions and protection for Chameleon) -->

Additionally the following add ons have dependencies on RestrictedPython

* None

How RestrictedPython 4+ works internally
----------------------------------------

RestrictedPython's core functions are split over several files:

* __init__.py --> It exports the API directly in the ``RestrictedPython`` namespace. It should be not necessary to import from any other module inside the package.
* compile.py --> It contains the ``compile_restricted`` functions where internally ``_compile_restricted_mode`` is the important one
* transformer.py --> Home of the ``RestrictingNodeTransformer``

``RestrictingNodeTransformer``
..............................

The ``RestrictingNodeTransformer`` is one of the core elements of RestrictedPython.
