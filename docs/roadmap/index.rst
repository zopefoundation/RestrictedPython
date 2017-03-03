Roadmap for RestrictedPython
============================

RestrictedPython 4.0
--------------------

A feature complete rewrite of RestrictedPython using ``ast`` module instead of ``compile`` package.
RestrictedPython 4.0 should not add any new or remove restrictions.

A detailed documentation that support usage and further development.

Full code coverage tests.

.. todo::

    Complete documentation of all public API elements with docstyle comments
    https://www.python.org/dev/peps/pep-0257/
    http://www.sphinx-doc.org/en/stable/ext/autodoc.html
    http://thomas-cokelaer.info/tutorials/sphinx/docstring_python.html

.. todo::

    Resolve Discussion in https://github.com/zopefoundation/RestrictedPython/pull/39#issuecomment-283074699

    compile_restricted optional params flags and dont_inherit will not work as expected with the current implementation.

    stephan-hof did propose a solution, should be discussed and if approved implemented.


RestrictedPython 4.1+
---------------------

Enhance RestrictedPython, declare  deprecations and possible new restrictions.

RestrictedPython 5.0+
---------------------

* Python 3+ only, no more support for Python 2.7
* mypy - Static Code Analysis Annotations
