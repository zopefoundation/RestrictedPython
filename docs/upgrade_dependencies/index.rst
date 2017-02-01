Upgrade dependencies
====================

Zope Core Packages that has RestrictedPython as dependencies
------------------------------------------------------------

The following Packages used in Zope2 for Plone depend on RestricedPython:

* AccessControl
* zope.untrustedpython
* DocumentTemplate
* Products.PageTemplates
* Products.PythonScripts
* Products.PluginIndexes
* five.pt (wrapping some functions and protection for Chameleon)

Upgrade path
------------

For packages that use RestrictedPython the upgrade path differs on the actual usage.
If it uses pure RestrictedPython without any additional checks it should be just to check the imports.
RestrictedPython did move some of the imports to the base namespace, so you should only import directly from ``RestrictedPython.__init__.py``.

* compile_restricted methods:

  * ``from RestrictedPython.compile import compile_restricted``
  * ``from RestrictedPython.compile import compile_restricted_eval``
  * ``from RestrictedPython.compile import compile_restricted_exec``
  * ``from RestrictedPython.compile import compile_restricted_function``
  * ``from RestrictedPython.compile import compile_restricted_single``

* predefined builtins:

  * ``from RestrictedPython.Guards import safe_builtins``
  * ``from RestrictedPython.Limits import limited_builtins``
  * ``from RestrictedPython.Utilities import utility_builtins``

* Helper methods

  * ``from RestrictedPython.PrintCollector import PrintCollector``

Any import from ``RestrictedPython.rcompile`` indicates that there have been advanced checks implemented.
Those advanced checks where implemented via ``MutatingWalker``'s.
Any check needs to be reimplemented as a subclass of RestrictingNodeTransformer.
