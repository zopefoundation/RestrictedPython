Changes
=======

4.0a3 (2017-06-20)
------------------

- Fix install problem caused by an invisible non-ASCII character in
  `README.rst`.

- Update configurations to give better feedback and helpful reports.



4.0a2 (2017-05-26)
------------------

- Modified README and setup.py to provide a better desciption test for PyPI.
  [loechel]

- Drop support for long-deprecated ``sets`` module.
  [tseaver]


4.0a1 (2017-05-05)
------------------

- Mostly complete rewrite based on Python AST module.
  [loechel (Alexander Loechel), icemac (Michael Howitz), stephan-hof (Stephan Hofmockel), tlotze (Thomas Lotze)]

- switch to pytest

- The ``compile_restricted*`` functions now return a
  ``namedtuple CompileResult`` instead of a simple ``tuple``.


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
