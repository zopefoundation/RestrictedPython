RestrictedPython 4+
===================

RestrictedPython 4.0.0 and upwords is a complete rewrite for Python 3 compatibility.

As the ``compiler`` module has been declared deprecated in Python 2.6 and already been removed in Python 3.0 it has never been avaliable for any Python 3 version.


Goals for a rewrite
-------------------

RestrictedPython is a core dependency for the Zope2 application server and therefore implicit for the content management system Plone.
The Zope & Plone community want to continue their projects and as Python 2 is announced end of life by 2020, and will be ultimately replaced by Python 3 or higher.
Zope and Plone should become Python 3 compatible.

One of the core features of Zope 2 and therefore Plone is the possibility to implement and modify Python scripts and templates through the web (TTW) without harming the application or server itself.


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

We explicitly exclude Python 3.3 and PyPy3 (which is based on the Python 3.3 specification) at the moment, because the changes from 3.4 upwords are huge and Python 3.3 is end of life by September 2017.

Dependencies
------------

The following packages / modules have hard dependencies on RestrictedPython:

* AccessControl -->
* zope.untrustedpython --> SelectCompiler
* DocumentTemplate -->
* Products.PageTemplates -->
* Products.PythonScripts -->
* Products.PluginIndexes -->
* five.pt (wrapping some functions and procetion for Chameleon) -->

Additionally the folowing add ons have dependencies on RestrictedPython

* None
