Contributing
============


Contributing to RestrictedPython
--------------------------------

Legal requirements to contribute to RestrictedPython
++++++++++++++++++++++++++++++++++++++++++++++++++++

The projects under the zopefoundation GitHub organization are open source, including RestrictedPython.
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
Please read the section :ref:`understand` first.

For all commits, use ``tox`` to run tests and lint, and build the docs, before pushing your commit to the remote repository.

.. _new_python_version:

Preperations for a new Python version
+++++++++++++++++++++++++++++++++++++

RestrictedPython should be updated for each new version of Python.
To do so:

* Read the changelog (`What's new in Python`_).
* Copy and adjust the new AST Grammar (found under: `Python 3 AST`_) to ``/docs/contributing/ast/python<version>.ast``.
* Add a new file ``changes_from<old_version>to<new_version>.rst`` in the directory ``/docs/contributing/``.
  If the changes are significant, especially if related to security, then add a description of the changes in that file.
* Add those files to the ``toctree`` directive in ``index.rst``.
* For each new **AST Node** or functionality:

  * Add tests to ``/tests/``.
  * Add a ``visit_<AST Node>`` to ``/src/RestrictedPython/transformer.py``.

    If the new AST Node should be enabled by default, with or without any modification, please add a ``visit_<AST Node>`` method such as the following:

    .. code-block:: python

        def visit_<AST Node>(self, node):
            """Allow `<AST Node>` expressions."""
            ...  # modifications
            return self.node_contents_visit(node)

    All AST Nodes without an explicit ``visit_<AST Node>`` method, are denied by default.
    So the usage of this expression and functionality is not allowed.

* Check the documentation for `inspect <https://docs.python.org/3/library/inspect.html>`_ and adjust the ``transformer.py:INSPECT_ATTRIBUTES`` list.
* Add a corresponding changelog entry.
* Additionally modify ``.meta.toml`` and run the ``meta/config`` script (for details see: https://github.com/mgedmin/check-python-versions) to update the following files:

  * ``/setup.py`` - Check that the new Python version classifier has been added ``"Programming Language :: Python :: <version>",``, and that the ``python_requires`` section has been updated correctly.
  * ``/tox.ini`` - Check that a ``testenv`` entry is added to the general ``envlist`` statement.
  * ``/.github/workflows/tests.yml`` - Check that a corresponding Python version entry has been added to the matrix definition.
  * ``/docs/conf.py`` - Add the Python version to the ``intersphinx_mapping`` list.

* On your local environment, use ``tox`` to run tests and lint, and build the docs, before pushing your commit to the remote repository.
* Create a pull request.

Enable a Python Feature in RestrictedPython
+++++++++++++++++++++++++++++++++++++++++++

To enable a certain functionality in RestrictedPython, do the following:

* `Create a new issue on GitHub <https://github.com/zopefoundation/RestrictedPython/issues/new/choose>`__, requesting the new feature, for discussion.
* In ``/src/RestrictedPython/transformer.py``, change the corresponding ``visit_<AST Node>`` method.
* In ``/tests/``, add or change the corresponding tests for this functionality.
* Add a changelog entry.
* On your local environment, use ``tox`` to run tests and lint, and build the docs, before pushing your commit to the remote repository.
* Create a pull request and request a review by a core maintainer, e.g.:

  * icemac
  * loechel

Differences between Python versions
-----------------------------------

A (modified style) Copy of all Abstract Grammar Definitions for the Python versions does live in this Documentation (ast Subfolder) to help finding difference quicker by comparing files.

.. toctree::
   :maxdepth: 2

   changes_from37to38
   changes_from38to39
   changes_from39to310
   changes_from310to311
   changes_from311to312
   changes_from312to313

.. _understand:

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

Technical decisions on how to implement / maintain RestrictedPython (Design, Structure, Tools, ...)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

RestrictedPython is a core Package of the Zope & Plone Stack.
Until Version 3.6 RestrictedPython was Python 2 only, and a critical blocker for Zope & Plone.
With RestrictedPython 4.0 an API compatible rewrite has happened, which supports modern Python Versions.

* Use modern python tool stack for maintenance and tests

  * tox
  * pytest
  * black
  * linting tools: flake8

* Use clear package Structure

  * ``/src`` - Source Code
  * ``/tests`` - separated tests
  * ``/docs`` - Documentation

  Tests and documentation are distributed within released packages.

.. todo::

  Resolve discussion about how RestrictedPython should be treat new expressions / ``ast.Nodes``.
  This belongs to :ref:`new_python_version`.

  **Option 1 - reduce maintenance burden (preferred by icemac)**


  All AST Nodes without an explicit ``visit_<AST Node>`` method, are denied by default.
  So the usage of this expression and functionality is not allowed.

  *This is currently the promoted version.*

  **Option 2 - be as explicit as possible (preferred by loechel)**

  If the new AST Node should be disabled by default, add a ``visit_<AST Node>`` method such as the following:

  .. code-block:: python

      def visit_<AST Node>(self, node):
          """`<AST Node>` expression currently not allowed."""
          self.not_allowed(node)

  Please note, that for all AST Nodes without an explicit ``visit_<AST Node>`` method, a default applies which denies the usage of this expression and functionality.
  As we try to be **as explicit as possible**, all language features should have a corresponding ``visit_<AST Node>``.

  That follows the Zen of Python:

  .. code-block:: pycon
      :emphasize-lines: 5

      >>> import this
      The Zen of Python, by Tim Peters

      Beautiful is better than ugly.
      Explicit is better than implicit.
      Simple is better than complex.
      Complex is better than complicated.
      Flat is better than nested.
      Sparse is better than dense.
      Readability counts.
      Special cases aren't special enough to break the rules.
      Although practicality beats purity.
      Errors should never pass silently.
      Unless explicitly silenced.
      In the face of ambiguity, refuse the temptation to guess.
      There should be one-- and preferably only one --obvious way to do it.
      Although that way may not be obvious at first unless you're Dutch.
      Now is better than never.
      Although never is often better than *right* now.
      If the implementation is hard to explain, it's a bad idea.
      If the implementation is easy to explain, it may be a good idea.
      Namespaces are one honking great idea -- let's do more of those!


Technical Backgrounds - Links to External Documentation
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

* `Concept of Immutable Types and Python Example`_
* `Python 3 Standard Library Documentation on AST module`_

  * AST Grammar of Python (`Status of Python Versions`_)

    * `Python 3.12 AST`_ (EOL 2028-10)
    * `Python 3.11 AST`_ (EOL 2027-10)
    * `Python 3.10 AST`_ (EOL 2026-10)
    * `Python 3.9 AST`_ (EOL 2025-10)
    * `Python 3.8 AST`_ (EOL 2024-10)
    * `Python 3.7 AST`_ (EOL 2023-06-27)

  * `AST NodeVistiors Class`_
  * `AST NodeTransformer Class`_
  * `AST dump method`_

* `In detail Documentation on the Python AST module (Green Tree Snakes)`_
* `Example how to Instrumenting the Python AST`_

Todos
-----

.. todolist::

.. Links:

.. _`What's new in Python`: https://docs.python.org/3/whatsnew/

.. _`What's new in Python 3.12`: https://docs.python.org/3.12/whatsnew/3.12.html

.. _`What's new in Python 3.11`: https://docs.python.org/3.11/whatsnew/3.11.html

.. _`What's new in Python 3.10`: https://docs.python.org/3.10/whatsnew/3.10.html

.. _`What's new in Python 3.9`: https://docs.python.org/3.9/whatsnew/3.9.html

.. _`What's new in Python 3.8`: https://docs.python.org/3.8/whatsnew/3.8.html

.. _`What's new in Python 3.7`: https://docs.python.org/3.7/whatsnew/3.7.html

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

.. _`AST NodeVistiors Class`: https://docs.python.org/3/library/ast.html#ast.NodeVisitor

.. _`AST NodeTransformer Class`: https://docs.python.org/3/library/ast.html#ast.NodeTransformer

.. _`AST dump method`: https://docs.python.org/3/library/ast.html#ast.dump

.. _`In detail Documentation on the Python AST module (Green Tree Snakes)`: https://greentreesnakes.readthedocs.org/en/latest/

.. _`Example how to Instrumenting the Python AST`: http://www.dalkescientific.com/writings/diary/archive/2010/02/22/instrumenting_the_ast.html
