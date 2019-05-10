Upgrade from 3.x
----------------

For packages that use RestrictedPython the upgrade path differs on the actual usage.
If it uses pure RestrictedPython without any additional checks it should be enough to check the imports.
RestrictedPython did move some of the imports to the base namespace, so you should only import directly from ``RestrictedPython``.

* compile_restricted methods:

  * ``from RestrictedPython import compile_restricted``
  * ``from RestrictedPython import compile_restricted_eval``
  * ``from RestrictedPython import compile_restricted_exec``
  * ``from RestrictedPython import compile_restricted_function``
  * ``from RestrictedPython import compile_restricted_single``

* predefined built-ins:

  * ``from RestrictedPython import safe_globals``
  * ``from RestrictedPython import safe_builtins``
  * ``from RestrictedPython import limited_builtins``
  * ``from RestrictedPython import utility_builtins``

* helper methods:

  * ``from RestrictedPython import PrintCollector``

Any import from ``RestrictedPython.RCompile`` indicates that there have been advanced checks implemented.
Those advanced checks where implemented via a ``MutatingWalker``.
Any checks needs to be reimplemented as a subclass of
``RestrictingNodeTransformer``.
