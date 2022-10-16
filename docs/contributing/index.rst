Contributing
============

.. toctree::

Contributing to RestrictedPython
--------------------------------

Legal requirements to contribute to RestrictedPython
++++++++++++++++++++++++++++++++++++++++++++++++++++

The projects under the zopefoundation GitHub organization, and therefore RestrictedPython, are open source.
We welcome contributions in different forms:

* bug reports
* code improvements and bug fixes
* documentation improvements
* pull request reviews

For any changes in the repository besides trivial typo fixes, you are required to sign the contributor agreement.
See https://www.zope.dev/developer/becoming-a-committer.html for details.

Please visit our `Developer Guidelines`_ if you'd like to contribute code changes and our `guidelines for reporting bugs`_ if you want to file a bug report.


.. _`Developer Guidelines`: https://www.zope.dev/developer/guidelines.html
.. _`guidelines for reporting bugs`: https://www.zope.dev/developer/reporting-bugs.html

Preperations for Contributing
+++++++++++++++++++++++++++++

If you want to contribute to this package, please prepare a development environment that includes ``git``, ``tox``, and several Python versions available through a Python manager such as ``pyenv``.
Please read the part of `Understanding How RestrictedPython works internally`_ first.

For all commits, please run the tests locally (with ``tox``) before pushing the the central repository.

.. code-block:: console

    tox

Preperations for a new Python version
+++++++++++++++++++++++++++++++++++++

RestrictedPython should be updated for each new Version of Python.
To do so, please read the Changelog (`What's new in Python`_) and copy and adjust the new AST Grammar (can be found under: `Python 3 AST`_) to ``/docs/contributing/ast/python<version>.ast`` and add a new ``changes_from<old_version>to<new_version>.rst to /docs/contributing`` and add those to ``index.rst``.

For each new *AST Node* please add a ``visit_<AST Node>`` to ``/src/RestrictedPython/transformer.py`` and add tests to ``/tests/``.

If the new AST Node should be disabled by default, please add a ``visit_<AST Node>`` methode like:

.. code-block:: python

    def visit_<AST Node>(self, node):
        """`<AST Node>` expression currently not allowed."""
        self.not_allowed(node)

Please note, that for all AST Nodes that has no explicite ``visit_<AST Node>`` method a default applies, that denies the usage of this expression / functionality.

If the new AST Node should be enabled by default, with out any modification, please add a ``visit_<AST Node>`` method like:

.. code-block:: python

    def visit_<AST Node>(self, node):
        """Allow `<AST Node>` expressions."""
        return self.node_contents_visit(node)

Add a corresponding changelog entry.

Additionally modify ``.meta.toml`` and run the ``meta/config`` script to update the following files:

* ``/setup.py`` <-- please check afterwards the *classifiers* list if it contains the new Python Version as a ``"Programming Language :: Python :: <Version>",`` element, and if ``python_requires`` is correctly updated.
* ``/tox.ini`` <-- please check that a testenv entry is added to the general ``envlist`` statement
* ``/.github/workflows/tests.yml`` <-- check if a corresponding python version entry is added to the matrix definition.

Run the test via ``tox``.

Create a Pull Request.


Enable a Python Feature in RestrictedPython
+++++++++++++++++++++++++++++++++++++++++++

To enable a certain functionality in RestrictedPython, please follow the folloing steps:

#. Add a feature request on GitHub
#. Create a Pull-Request on Github
  * In ``/src/RestrictedPython/transformer.py`` change the corresponding ``visit_<AST Node>`` method
  * In ``/tests/`` add / change the corresponding tests for this functionality
  * Add a changelog entry
  * request a review by a core maintainer, e.g.:

    * icemac
    * loechel


Todos
-----

.. todolist::

.. _Understanding How RestrictedPython works internally:

Understanding How RestrictedPython works internally
---------------------------------------------------

RestrictedPython is a classic approach of compiler construction to create a limited subset of an existing programming language.

Defining a programming language requires a regular grammar (`Chomsky 3`_ / `EBNF`_) definition.
This grammar will be implemented in an abstract syntax tree (AST), which will be passed on to a code generator to produce a machine-readable version.

.. _`_sec_code_generation`:

Code generation
+++++++++++++++

As Python is a platform independent programming language, this machine readable version is a byte code which will be translated on the fly by an interpreter into machine code.
This machine code then gets executed on the specific CPU architecture, with the standard operating system restrictions.

The byte code produced must be compatible with the execution environment that the Python interpreter is running in, so we do not generate the byte code directly from ``compile_restricted`` and the other ``compile_restricted_*`` methods manually, it may not match what the interpreter expects.

Thankfully, the Python ``compile()`` function introduced the capability to compile ``ast.AST`` code into byte code in Python 2.6, so we can return the platform-independent AST and keep byte code generation delegated to the interpreter.

``ast`` module (Abstract Syntax Trees)
++++++++++++++++++++++++++++++++++++++

The ``ast`` module consists of four areas:

* ``AST`` (Basis of all Nodes) + all node class implementations
* ``NodeVisitor`` and ``NodeTransformer`` (tool to consume and modify the AST)
* Helper methods

  * ``parse``
  * ``walk``
  * ``dump``

* Constants

  * ``PyCF_ONLY_AST``


``NodeVisitor`` & ``NodeTransformer``
+++++++++++++++++++++++++++++++++++++

A ``NodeVisitor`` is a class of a node / AST consumer, it reads the data by stepping through the tree without modifying it.
In contrast, a ``NodeTransformer`` (which inherits from a ``NodeVisitor``) is allowed to modify the tree and nodes.


Technical Backgrounds - Links to External Documentation
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

* `Concept of Immutable Types and Python Example`_
* `Python 3 Standard Library Documentation on AST module`_

  * AST Grammar of Python

    * `Python 3.12 AST`_ (development branch - EOL 2028-10)
    * `Python 3.11 AST`_ (in bugfix phase - EOL 2027-10)
    * `Python 3.10 AST`_ (in bugfix phase - EOL 2026-10)
    * `Python 3.9 AST`_ (in security phase - EOL 2025-10)
    * `Python 3.8 AST`_ (in security phase - EOL 2024-10)
    * `Python 3.7 AST`_ (in security phase - EOL 2023-06-27)
    * `Python 3.6 AST`_ (obsolete - EOL 2021-12-23)
    * `Python 3.5 AST`_ (obsolete - EOL 2020-09-30)
    * `Python 3.4 AST`_ (obsolete - EOL 2019-03-18)
    * `Python 3.3 AST`_ (obsolete - EOL 2017-09-29)
    * `Python 3.2 AST`_ (obsolete - EOL 2016-02-20)
    * `Python 3.1 AST`_ (obsolete - EOL 2012-04-09)
    * `Python 3.0 AST`_ (obsolete - EOL 2009-06-27)
    * `Python 2.7 AST`_ (obsolete - EOL 2020-01-01)
    * `Python 2.6 AST`_ (obsolete - EOL 2013-10.29)

  * `AST NodeVistiors Class`_  (https://docs.python.org/3.9/library/ast.html#ast.NodeVisitor)
  * `AST NodeTransformer Class`_  (https://docs.python.org/3.9/library/ast.html#ast.NodeTransformer)
  * `AST dump method`_ (https://docs.python.org/3.9/library/ast.html#ast.dump)

* `In detail Documentation on the Python AST module (Green Tree Snakes)`_
* `Example how to Instrumenting the Python AST`_
* `Status of Python Versions`_

Differences between different Python versions
---------------------------------------------

A (modified style) Copy of all Abstract Grammar Definitions for the Python versions does live in this Documentation (ast Subfolder) to help finding difference quicker by comparing files.

.. toctree::
   :maxdepth: 2

   changes_from26to27
   changes_from30to31
   changes_from31to32
   changes_from32to33
   changes_from33to34
   changes_from34to35
   changes_from35to36
   changes_from36to37
   changes_from37to38
   changes_from38to39
   changes_from39to310
   changes_from310to311
   changes_from311to312

.. Links

.. _`What's new in Python`: https://docs.python.org/3/whatsnew/

.. _`What's new in Python 3.12`: https://docs.python.org/3.11/whatsnew/3.12.html

.. _`What's new in Python 3.11`: https://docs.python.org/3.11/whatsnew/3.11.html

.. _`What's new in Python 3.10`: https://docs.python.org/3.10/whatsnew/3.10.html

.. _`What's new in Python 3.9`: https://docs.python.org/3.9/whatsnew/3.9.html

.. _`What's new in Python 3.8`: https://docs.python.org/3.8/whatsnew/3.8.html

.. _`What's new in Python 3.7`: https://docs.python.org/3.7/whatsnew/3.7.html

.. _`What's new in Python 3.6`: https://docs.python.org/3.6/whatsnew/3.6.html

.. _`What's new in Python 3.5`: https://docs.python.org/3.5/whatsnew/3.5.html

.. _`What's new in Python 3.4`: https://docs.python.org/3.4/whatsnew/3.4.html

.. _`What's new in Python 2.7`: https://docs.python.org/2.7/whatsnew/2.7.html

.. _`Status of Python Versions`: https://devguide.python.org/versions/

.. _`Concept of Immutable Types and Python Example`: https://en.wikipedia.org/wiki/Immutable_object#Python

.. _`Python 3 Standard Library Documentation on AST module`: https://docs.python.org/3/library/ast.html

.. _`CamelCase`: https://en.wikipedia.org/wiki/Camel_case

.. _`EBNF`: https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form

.. _`Chomsky 3`: https://en.wikipedia.org/wiki/Chomsky_hierarchy#Type-3_grammars

.. _`Python 3 AST`: https://docs.python.org/3/library/ast.html#abstract-grammar

.. _`Python 3.12 AST`: https://docs.python.org/3.12/library/ast.html#abstract-grammar

.. _`Python 3.11 AST`: https://docs.python.org/3.11/library/ast.html#abstract-grammar

.. _`Python 3.10 AST`: https://docs.python.org/3.10/library/ast.html#abstract-grammar

.. _`Python 3.9 AST`: https://docs.python.org/3.9/library/ast.html#abstract-grammar

.. _`Python 3.8 AST`: https://docs.python.org/3.8/library/ast.html#abstract-grammar

.. _`Python 3.7 AST`: https://docs.python.org/3.7/library/ast.html#abstract-grammar

.. _`Python 3.6 AST`: https://docs.python.org/3.6/library/ast.html#abstract-grammar

.. _`Python 3.5 AST`: https://docs.python.org/3.5/library/ast.html#abstract-grammar

.. _`Python 3.4 AST`: https://docs.python.org/3.4/library/ast.html#abstract-grammar

.. _`Python 3.3 AST`: https://docs.python.org/3.3/library/ast.html#abstract-grammar

.. _`Python 3.2 AST`: https://docs.python.org/3.2/library/ast.html#abstract-grammar

.. _`Python 3.1 AST`: https://docs.python.org/3.1/library/ast.html#abstract-grammar

.. _`Python 3.0 AST`: https://docs.python.org/3.0/library/ast.html#abstract-grammar

.. _`Python 2.7 AST`: https://docs.python.org/2.7/library/ast.html#abstract-grammar

.. _`Python 2.6 AST`: https://docs.python.org/2.6/library/ast.html#abstract-grammar

.. _`AST NodeVistiors Class`: https://docs.python.org/3.5/library/ast.html#ast.NodeVisitor

.. _`AST NodeTransformer Class`: https://docs.python.org/3.5/library/ast.html#ast.NodeTransformer

.. _`AST dump method`: https://docs.python.org/3.5/library/ast.html#ast.dump

.. _`In detail Documentation on the Python AST module (Green Tree Snakes)`: https://greentreesnakes.readthedocs.org/en/latest/

.. _`Example how to Instrumenting the Python AST`: http://www.dalkescientific.com/writings/diary/archive/2010/02/22/instrumenting_the_ast.html
