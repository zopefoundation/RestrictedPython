Konzept für das Update auf Python 3
===================================



RestrictedPython is a classical approach of compiler construction to create a limited subset of an existing programming language.

As compiler construction do have basic concepts on how to build a Programming Language and Runtime Environment.

Defining a Programming Language means to define a regular grammar (Chomsky 3 / EBNF) first.
This grammar will be implemented in an abstract syntax tree (AST), which will be passed on to a code generator to produce a machine understandable version.

As Python is a plattform independend programming / scripting language, this machine understandable version is a byte code which will be translated on the fly by an interpreter into machine code.
This machine code then gets executed on the specific CPU architecture, with all Operating System restriction.

Produced byte code has to compatible with the execution environment, the Python Interpreter within this code is called.
So we must not generate the byte code that has to be returned from ``compile_restricted`` and the other ``compile_restricted_*`` methods manually, as this might harm the interpreter.
We actually don't even need that.
The Python ``compile()`` function introduced the capability to compile ``ast.AST`` code into byte code.


compiler.ast --> ast.AST
------------------------

Aus Sicht des Compilerbaus sind die Konzepte der Module compiler und ast vergleichbar, bzw. ähnlich.
Primär hat sich mit der Entwicklung von Python ein Styleguide gebildet wie bestimmte Sachen ausgezeichnet werden sollen.
Während compiler eine alte CamelCase Syntax (``visitNode(self, node, walker)``) nutzt ist in AST die Python übliche ``visit_Node(self, node)`` Syntax heute üblich.
Auch habe sich die Namen genändert, wärend compiler von ``Walker`` und ``Mutator`` redet heissen die im AST kontext ``NodeVisitor`` und ``NodeTransformator``


ast Modul (Abstract Syntax Trees)
---------------------------------

Das ast Modul besteht aus drei(/vier) Bereichen:

* AST (Basis aller Nodes) + aller Node Classen Implementierungen
* NodeVisitor und NodeTransformer (Tools zu Ver-/Bearbeiten des AST)
* Helper-Methoden

  * parse
  * walk
  * dump

* Constanten

  * PyCF_ONLY_AST


NodeVisitor & NodeTransformer
-----------------------------

Ein NodeVisitor ist eine Klasse eines Node / AST Konsumenten beim durchlaufen des AST-Baums.
Ein Visitor liest Daten aus dem Baum verändert aber nichts am Baum, ein Transformer - vom Visitor abgeleitet - erlaubt modifikationen am Baum, bzw. den einzelnen Knoten.



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
