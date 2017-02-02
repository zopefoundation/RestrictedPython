Concept for a upgrade to Python 3
=================================

RestrictedPython is a classic approach of compiler construction to create a limited subset of an existing programming language.

Defining a programming language requires a regular grammar (`Chomsky 3`_ / `EBNF`_) definition.
This grammar will be implemented in an abstract syntax tree (AST), which will be passed on to a code generator to produce a machine-readable version.

.. _`_sec_code_generation`:

Code generation
---------------

As Python is a platform independent programming language, this machine readable version is a byte code which will be translated on the fly by an interpreter into machine code.
This machine code then gets executed on the specific CPU architecture, with the standard operating system restrictions.

The byte code produced must be compatible with the execution environment that the Python interpreter is running in, so we do not generate the byte code directly from ``compile_restricted`` and the other ``compile_restricted_*`` methods manually, it may not match what the interpreter expects.

Thankfully, the Python ``compile()`` function introduced the capability to compile ``ast.AST`` code into byte code in Python 2.6, so we can return the platform-independent AST and keep byte code generation delegated to the interpreter.

``compiler.ast`` --> ``ast``
----------------------------

As the ``compiler`` module was deprecated in Python 2.6 and was removed before Python 3.0 was released it has never been available for any Python 3 version.
Instead Python 2.6 / Python 3 introduced the new ``ast`` module, that is more widly supported.
So we need to move from ``compiler.ast`` to ``ast`` to support newer Python versions.

From the point of view of compiler design, the concepts of the ``compiler`` module and the ``ast`` module are similar.
The ``compiler`` module predates several major improvements of the Python development like a generally applied style guide.
While ``compiler`` still uses the old `CamelCase`_ Syntax (``visitNode(self, node, walker)``) the ``ast.AST`` did now use the Python common ``visit_Node(self, node)`` syntax.
Also the names of classes have been changed, where ``compiler`` uses ``Walker`` and ``Mutator`` the corresponding elements in ``ast.AST`` are ``NodeVisitor`` and ``NodeTransformator``.


``ast`` module (Abstract Syntax Trees)
--------------------------------------

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
.....................................

A ``NodeVisitor`` is a class of a node / AST consumer, it reads the data by stepping through the tree without modifying it.
In contrast, a ``NodeTransformer`` (which inherits from a ``NodeVisitor``) is allowed to modify the tree and nodes.

Modifying the AST
-----------------








Technical Backgrounds - Links to External Documentation
---------------------------------------------------------

* Concept of Immutable Types and Python Example (https://en.wikipedia.org/wiki/Immutable_object#Python)
* Python 3 Standard Library Documentation on AST module ``ast`` (https://docs.python.org/3/library/ast.html)

  * AST Grammar of Python

    * `Python 3.6 AST`_
    * `Python 3.5 AST`_
    * `Python 3.4 AST`_
    * `Python 3.3 AST`_
    * `Python 3.2 AST`_
    * `Python 3.1 AST`_
    * `Python 3.0 AST`_
    * `Python 2.7 AST`_
    * `Python 2.6 AST`_

  * ``NodeVistiors``  (https://docs.python.org/3.5/library/ast.html#ast.NodeVisitor)
  * ``NodeTransformer``  (https://docs.python.org/3.5/library/ast.html#ast.NodeTransformer)
  * ``dump`` (https://docs.python.org/3.5/library/ast.html#ast.dump)

* In detail Documentation on the Python AST module ``ast`` (Green Tree Snakes) (https://greentreesnakes.readthedocs.org/en/latest/)
* Example how to Instrumenting the Python AST (``ast.AST``) (http://www.dalkescientific.com/writings/diary/archive/2010/02/22/instrumenting_the_ast.html)

.. _`CamelCase`: https://en.wikipedia.org/wiki/Camel_case

.. _`EBNF`: https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form

.. _`Chomsky 3`: https://en.wikipedia.org/wiki/Chomsky_hierarchy#Type-3_grammars

.. _`Python 3.6 AST`: https://docs.python.org/3.6/library/ast.html#abstract-grammar

.. _`Python 3.5 AST`: https://docs.python.org/3.5/library/ast.html#abstract-grammar

.. _`Python 3.4 AST`: https://docs.python.org/3.4/library/ast.html#abstract-grammar

.. _`Python 3.3 AST`: https://docs.python.org/3.3/library/ast.html#abstract-grammar

.. _`Python 3.2 AST`: https://docs.python.org/3.2/library/ast.html#abstract-grammar

.. _`Python 3.1 AST`: https://docs.python.org/3.1/library/ast.html#abstract-grammar

.. _`Python 3.0 AST`: https://docs.python.org/3.0/library/ast.html#abstract-grammar

.. _`Python 2.7 AST`: https://docs.python.org/2.7/library/ast.html#abstract-grammar

.. _`Python 2.6 AST`: https://docs.python.org/2.6/library/ast.html#abstract-grammar
