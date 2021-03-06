The idea behind RestrictedPython
================================

Python is a `Turing complete <https://en.wikipedia.org/wiki/Turing_completeness>`_ programming language.
To offer a Python interface for users in web context is a potential security risk.
Web frameworks and Content Management Systems (CMS) want to offer their users as much extensibility as possible through the web (TTW).
This also means to have permissions to add functionality via a Python script.

There should be additional preventive measures taken to ensure integrity of the application and the server itself, according to information security best practice and unrelated to RestrictedPython.

RestrictedPython defines a safe subset of the Python programming language.
This is a common approach for securing a programming language.
The `Ada Ravenscar profile <https://en.wikipedia.org/wiki/Ravenscar_profile>`_ is another example of such an approach.

Defining a secure subset of the language involves restricting the `EBNF <https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form>`_ elements and explicitly allowing or disallowing language features.
Much of the power of a programming language derives from its standard and contributed libraries, so any calling of these methods must also be checked and potentially restricted.
RestrictedPython generally disallows calls to any library that is not explicit whitelisted.

As Python is a scripting language that is executed by an interpreter any Python code that should be executed has to be explicitly checked before executing the generated byte code by the interpreter.

Python itself offers three methods that provide such a workflow:

* ``compile()`` which compiles source code to byte code
* ``exec`` / ``exec()`` which executes the byte code in the interpreter
* ``eval`` / ``eval()`` which executes a byte code expression

Therefore RestrictedPython offers a replacement for the python builtin function ``compile()`` (`Python 2 <https://docs.python.org/2/library/functions.html#compile>`_ / `Python 3 <https://docs.python.org/3/library/functions.html#compile>`_).
This Python function is defined as following:

.. code-block:: python

    compile(source, filename, mode [, flags [, dont_inherit]])

The definition of the ``compile()`` method has changed over time, but its relevant parameters ``source`` and ``mode`` still remain.

There are three valid string values for ``mode``:

* ``'exec'``
* ``'eval'``
* ``'single'``

For RestrictedPython this ``compile()`` method is replaced by:

.. code-block:: python

    RestrictedPython.compile_restricted(source, filename, mode [, flags [, dont_inherit]])

The primary parameter ``source`` has to be a string or ``ast.AST`` instance.
Both methods either return compiled byte code that the interpreter can execute or raise exceptions if the provided source code is invalid.

As ``compile`` and ``compile_restricted`` just compile the provided source code to byte code it is not sufficient as a sandbox environment, as all calls to libraries are still available.

The two methods / statements:

* ``exec`` / ``exec()``
* ``eval`` / ``eval()``

have two parameters:

* ``globals``
* ``locals``

which are references to the Python builtins.

By modifying and restricting the available modules, methods and constants from ``globals`` and ``locals`` we can limit the possible calls.

Additionally RestrictedPython offers a way to define a policy which allows developers to protect access to attributes.
This works by defining a restricted version of:

* ``print``
* ``getattr``
* ``setattr``
* ``import``

Also RestrictedPython provides three predefined, limited versions of Python's ``__builtins__``:

* ``safe_builtins`` (by Guards.py)
* ``limited_builtins`` (by Limits.py), which provides restricted sequence types
* ``utilities_builtins`` (by Utilities.py), which provides access for standard modules math, random, string and for sets.

One special shortcut:

* ``safe_globals`` for ``{'__builtins__': safe_builtins}`` (by Guards.py)

Additional there exist guard functions to make attributes of Python objects immutable --> ``full_write_guard`` (write and delete protected).
