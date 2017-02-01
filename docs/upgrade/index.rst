Concept for a upgrade to Python 3
=================================

RestrictedPython is a classic approach of compiler construction to create a limited subset of an existing programming language.

Defining a programming language requires a regular grammar (Chomsky 3 / EBNF) definition.
This grammar will be implemented in an abstract syntax tree (AST), which will be passed on to a code generator to produce a machine-readable version.

As Python is a platform independent programming language, this machine readable version is a byte code which will be translated on the fly by an interpreter into machine code.
This machine code then gets executed on the specific CPU architecture, with the standard operating system restrictions.

The bytecode produced must be compatible with the execution environment that the Python interpreter is running in, so we do not generate the byte code directly from ``compile_restricted`` and the other ``compile_restricted_*`` methods manually, it may not match what the interpreter expects.

Thankfully, the Python ``compile()`` function introduced the capability to compile ``ast.AST`` code into byte code in Python 2.6, so we can return the platform-independent AST and keep bytecode generation delegated to the interpreter.

As the ``compiler`` module was deprecated in Python 2.6 and was removed before Python 3.0 was released it has never been avaliable for any Python 3 version.
So we need to move from ``compiler.ast`` to ``ast`` to support newer Python versions.

``compiler.ast`` --> ``ast``
----------------------------

From the point of view of compiler design, the concepts of the compiler module and the ast module are similar.
The ``compiler`` module predates several major improvements of the Python development like a generally applied style guide.
While ``compiler`` still uses the old `CamelCase`_ Syntax (``visitNode(self, node, walker)``) the ``ast.AST`` did now use the Python common ``visit_Node(self, node)`` syntax.
Also the names of classes have been changed, where ``compiler`` uses ``Walker`` and ``Mutator`` the corresponding elements in ``ast.AST`` are ``NodeVisitor`` and ``NodeTransformator``.


ast module (Abstract Syntax Trees)
----------------------------------

The ast module consists of four areas:

* AST (Basis of all Nodes) + all node class implementations
* NodeVisitor and NodeTransformer (tool to consume and modify the AST)
* Helper methods

  * parse
  * walk
  * dump

* Constants

  * PyCF_ONLY_AST


NodeVisitor & NodeTransformer
-----------------------------

A NodeVisitor is a class of a node / AST consumer, it reads the data by stepping through the tree without modifying it.
In contrast, a NodeTransformer (which inherits from a NodeVisitor) is allowed to modify the tree and nodes.


Links
-----

* Concept of Immutable Types and Python Example (https://en.wikipedia.org/wiki/Immutable_object#Python)
* Python 3 Standard Library Documentation on AST module ``ast`` (https://docs.python.org/3/library/ast.html)

  * AST Gramar of Python https://docs.python.org/3.5/library/ast.html#abstract-grammar https://docs.python.org/2.7/library/ast.html#abstract-grammar
  * NodeVistiors (https://docs.python.org/3.5/library/ast.html#ast.NodeVisitor)
  * NodeTransformer (https://docs.python.org/3.5/library/ast.html#ast.NodeTransformer)
  * dump (https://docs.python.org/3.5/library/ast.html#ast.dump)

* Indetail Documentation on the Python AST module ``ast`` (https://greentreesnakes.readthedocs.org/en/latest/)
* Example how to Instrumenting the Python AST (``ast.AST``) (http://www.dalkescientific.com/writings/diary/archive/2010/02/22/instrumenting_the_ast.html)
