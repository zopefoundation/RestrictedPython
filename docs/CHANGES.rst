Changes
=======

5.1 (unreleased)
----------------

- Drop install dependency on ``setuptools``.
  (`#189 <https://github.com/zopefoundation/RestrictedPython/issues/189>`_)


5.0 (2019-09-03)
----------------

Breaking changes
----------------

- Revert the Allowance of the ``...`` (Ellipsis) statement, as of 4.0. It is not needed to support Python 3.8.
  The security implications of the Ellipsis Statement is not 100 % clear and is not checked.
  ``...`` (Ellipsis) is disallowed again.

Features
--------

- Add support for f-strings in Python 3.6+.
  (`#123 <https://github.com/zopefoundation/RestrictedPython/issues/123>`_)


4.0 (2019-05-10)
----------------

Changes since 3.6.0:

Breaking changes
----------------

- The ``compile_restricted*`` functions now return a
  ``namedtuple CompileResult`` instead of a simple ``tuple``.

- Drop the old implementation of version 3.x: `RCompile.py`,
  `SelectCompiler.py`, `MutatingWorker.py`, `RestrictionMutator.py` and
  `tests/verify.py`.

- Drop support for long-deprecated ``sets`` module.

Security related issues
-----------------------

- RestrictedPython now ships with a default implementation for
  ``_getattr_`` which prevents from using the ``format()`` method on
  str/unicode as it is not safe, see:
  http://lucumr.pocoo.org/2016/12/29/careful-with-str-format/

  **Caution:** If you do not already have secured the access to this
  ``format()`` method in your ``_getattr_`` implementation use
  ``RestrictedPython.Guards.safer_getattr()`` in your implementation to
  benefit from this fix.

Features
--------

- Mostly complete rewrite based on Python AST module.
  [loechel (Alexander Loechel), icemac (Michael Howitz),
  stephan-hof (Stephan Hofmockel), tlotze (Thomas Lotze)]

- Add support for Python 3.5, 3.6, 3.7.

- Add preliminary support for Python 3.8. as of 3.8.0a3 is released.

- Warn when using another Python implementation than CPython as it is not safe
  to use RestrictedPython with other versions than CPyton.
  See https://bitbucket.org/pypy/pypy/issues/2653 for PyPy.

- Allow the ``...`` (Ellipsis) statement. It is needed to support Python 3.8.

- Allow `yield` and `yield from` statements.
  Generator functions would now work in RestrictedPython.

- Allow the following magic methods to be defined on classes.
  (`#104 <https://github.com/zopefoundation/RestrictedPython/issues/104>`_)
  They cannot be called directly but by the built-in way to use them (e. g.
  class instantiation, or comparison):

  + ``__init__``
  + ``__contains__``
  + ``__lt__``
  + ``__le__``
  + ``__eq__``
  + ``__ne__``
  + ``__gt__``
  + ``__ge__``

- Imports like ``from a import *`` (so called star imports) are now forbidden
  as they allow to import names starting with an underscore which could
  override protected build-ins.
  (`#102 <https://github.com/zopefoundation/RestrictedPython/issues/102>`_)

- Allow to use list comprehensions in the default implementation of
  ``RestrictionCapableEval.eval()``.

- Switch to pytest as test runner.

- Bring test coverage to 100 %.

Bug fixes
---------

- Improve `.Guards.safer_getattr` to prevent accessing names starting with
  underscore.
  (`#142 <https://github.com/zopefoundation/RestrictedPython/issues/142>`_)


3.6.0 (2010-07-09)
------------------

- Add name check for names assigned during imports using the
  ``from x import y`` format.

- Add test for name check when assigning an alias using multiple-context
  ``with`` statements in Python 2.7.

- Add tests for protection of the iterators for dict and set comprehensions
  in Python 2.7.

3.6.0a1 (2010-06-05)
--------------------

- Remove support for ``DocumentTemplate.sequence`` - this is handled in the
  DocumentTemplate package itself.

3.5.2 (2010-04-30)
------------------

- Remove a testing dependency on ``zope.testing``.

3.5.1 (2009-03-17)
------------------

- Add tests for ``Utilities`` module.

- Filter DeprecationWarnings when importing Python's ``sets`` module.

3.5.0 (2009-02-09)
------------------

- Drop legacy support for Python 2.1 / 2.2 (``__future__`` imports
  of ``nested_scopes`` / ``generators``.).

3.4.3 (2008-10-26)
------------------

- Fix deprecation warning: ``with`` is now a reserved keyword on
  Python 2.6. That means RestrictedPython should run on Python 2.6
  now. Thanks to Ranjith Kannikara, GSoC Student for the patch.

- Add tests for ternary if expression and for ``with`` keyword and
  context managers.

3.4.2 (2007-07-28)
------------------

- Changed homepage URL to the PyPI site

- Improve ``README.txt``.

3.4.1 (2007-06-23)
------------------

- Fix http://www.zope.org/Collectors/Zope/2295: Bare conditional in
  a Zope 2 PythonScript followed by a comment causes SyntaxError.

3.4.0 (2007-06-04)
------------------

- RestrictedPython now has its own release cycle as a separate project.

- Synchronized with RestrictedPython from Zope 2 tree.

3.2.0 (2006-01-05)
------------------

- Corresponds to the verison of the RestrictedPython package shipped
  as part of the Zope 3.2.0 release.

- No changes from 3.1.0.

3.1.0 (2005-10-03)
------------------

- Corresponds to the verison of the RestrictedPython package shipped
  as part of the Zope 3.1.0 release.

- Remove unused fossil module, ``SafeMapping``.

- Replaced use of deprecated ``whrandom`` module with ``random`` (aliased
  to ``whrandom`` for backward compatibility).

3.0.0 (2004-11-07)
------------------

- Corresponds to the verison of the RestrictedPython package shipped
  as part of the Zope X3.0.0 release.
