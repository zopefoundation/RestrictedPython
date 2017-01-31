Concept for a Upgrade to Python 3
=================================

RestrictedPython is a classical approach of compiler construction to create a limited subset of an existing programming language.

As compiler construction do have basic concepts on how to build a Programming Language and Runtime Environment.

Defining a Programming Language means to define a regular grammar (Chomsky 3 / EBNF) first.
This grammar will be implemented in an abstract syntax tree (AST), which will be passed on to a code generator to produce a machine understandable version.

As Python is a plattform independend programming / scripting language, this machine understandable version is a byte code which will be translated on the fly by an interpreter into machine code.
This machine code then gets executed on the specific CPU architecture, with all Operating System restriction.

Produced byte code has to compatible with the execution environment, the Python Interpreter within this code is called.
So we must not generate the byte code that has to be returned from ``compile_restricted`` and the other ``compile_restricted_*`` methods manually, as this might harm the interpreter.
We actually don't even need that.
The Python ``compile()`` function introduced the capability to compile ``ast.AST`` code into byte code in Python 2.6.

We do need to move from ``compiler.ast`` to ``ast``.

``compiler.ast`` --> ``ast``
----------------------------

From the point of view of compiler design the concepts of the compiler module and the ast module are similar.
The ``compiler`` module seems to be a very old module of the Python history.
There have happened several improvements of the Python development like a generally applied style guide.
While ``compiler`` still uses the old `CamelCase`_ Syntax (``visitNode(self, node, walker)``) the ``ast.AST`` did now use the Python common ``visit_Node(self, node)`` syntax.
Also the names have been changed, while ``compiler`` did talk about ``Walker`` and ``Mutator`` the corresponding elements in ``ast.AST`` are ``NodeVisitor`` and ``NodeTransformator``.


ast Modul (Abstract Syntax Trees)
---------------------------------

The ast module consists of four areas:

* AST (Basis of all Nodes) + all node class implementations
* NodeVisitor and NodeTransformer (tool to consume and modify the AST)
* Helper-Methods

  * parse
  * walk
  * dump

* Constants

  * PyCF_ONLY_AST


NodeVisitor & NodeTransformer
-----------------------------

A NodeVisitor is a class of a node / AST consumer, it just reads the data by steping through the tree but does not modify the tree.
In oposite a NodeTransformer which inherits from a NodeVisitor is allowed to modify the tree and nodes.


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
