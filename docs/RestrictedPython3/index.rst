RestrictedPython 3.6.x and before
=================================


Technical foundation of RestrictedPython
........................................

RestrictedPython is based on the Python 2 only standard library module ``compiler`` (https://docs.python.org/2.7/library/compiler.html).
RestrictedPython based on the

* ``compiler.ast``
* ``compiler.parse``
* ``compiler.pycodegen``

With Python 2.6 the compiler module with all its sub modules has been declared deprecated with no direct upgrade Path or recommendations for a replacement.


Version Support of RestrictedPython 3.6.x
.........................................

RestrictedPython 3.6.x aims on supporting Python versions:

* 2.0
* 2.1
* 2.2
* 2.3
* 2.4
* 2.5
* 2.6
* 2.7

Even if the README claims that Compatibility Support is form Python 2.3 - 2.7 I found some Code in RestrictedPython and related Packages which test if Python 1 is used.

Due to this approach to support all Python 2 Versions the code uses only statements that are compatible with all of those versions.

So old style classes and new style classes are mixed,

The following language elements are statements and not functions:

* exec
* print
