.. _security_considerations:

Security considerations
-----------------------

RestrictedPython restricts the *language*: it compiles a subset of Python and
rewrites the compiled code to route certain operations through guard functions
you supply.
It does not restrict the *environment*.
That environment — the ``globals`` and ``__builtins__`` you pass to ``exec()`` —
decides what restricted code can reach, and you write it yourself.

.. _guards_only_cover_restricted_source:

Guards only cover the restricted source code
............................................

``compile_restricted`` rewrites attribute access **written in the restricted
source** into calls to ``_getattr_``.
It cannot rewrite anything else.
So when restricted code calls a function that looks up the attribute itself,
that lookup runs in ordinary CPython and never reaches your guard.

``operator.attrgetter`` shows the difference.
Write the access directly and the guard runs:

.. code-block:: python

    # `_getattr_` runs; `safer_getattr` refuses the leading underscore
    some_function.__globals__

Route the same access through ``attrgetter`` and it succeeds, because
``attrgetter`` calls ``getattr()`` itself, in C:

.. code-block:: python

    # no `_getattr_` call, so the guard never runs
    operator.attrgetter('__globals__')(some_function)

``operator.itemgetter`` and ``operator.methodcaller`` work the same way, as does
any other callable that looks up attributes, invokes arbitrary callables or
executes code on behalf of its caller.

So **exposing an object exposes everything reachable through it.**
You gain more by auditing what you put into ``globals`` and ``__builtins__``
than by relying on the guards.
The guards are a second line of defence, not the boundary.

.. _providing_import:

Providing ``__import__`` moves the boundary out of RestrictedPython
...................................................................

.. warning::

    RestrictedPython deliberately ships **no** ``__import__`` implementation.
    ``safe_builtins`` omits it, so by default restricted code cannot import
    anything and fails with ``ImportError: __import__ not found``.

    Add an ``__import__`` to ``__builtins__`` and you take over the security
    boundary.
    Every module restricted code can then import becomes part of your trusted
    computing base.
    No guard that RestrictedPython ships can make up for a permissive import
    policy.

One unrestricted import is enough on its own; no exotic technique is required:

.. code-block:: python

    import os

    os.listdir('/')

Denylisting individual modules, types or methods does not work: the set of
dangerous modules is open-ended, and a module that restricted code reaches
indirectly is just as dangerous as one it imports directly.
**Allowlist the modules you need and reject everything else.**

Modules that must not be reachable
..................................

Each of the modules below is enough on its own to break out of restricted code.
The list is illustrative, not exhaustive — which is why only an allowlist works:

``os``, ``subprocess``, ``sys``, ``shutil``
    Direct access to the process, the file system and the operating system.
``operator``
    ``attrgetter``, ``itemgetter`` and ``methodcaller`` look up attributes and
    call methods in C, bypassing ``_getattr_`` entirely
    (see :ref:`guards_only_cover_restricted_source`).
``functools``
    ``partial`` and ``reduce`` invoke arbitrary callables, so restricted code
    can make calls it cannot write directly.
``ctypes``
    Arbitrary native calls and direct memory access.
``inspect``, ``gc``
    General purpose introspection.
    ``gc.get_referrers()`` walks from any restricted object to unrestricted
    ones.
``importlib``, ``pkgutil``, ``runpy``
    They import modules themselves, so whatever restriction you place on
    ``__import__`` no longer applies.
``pickle``, ``marshal``, ``shelve``
    Construct arbitrary objects and execute code while deserializing.
``builtins``
    Restores everything ``safe_builtins`` left out.
``string``
    ``string.Formatter`` walks attributes and items on its arguments without
    consulting ``_getattr_``.
    ``utility_builtins['string']`` therefore hands out a delegator that
    withholds ``Formatter``, and ``safer_getattr`` blocks the traversal methods.
    A plain ``import string`` bypasses both of those protections.

Allowing ``import x`` exposes **all** of ``x``: on the imported module only
``_getattr_`` still filters attribute access, and it merely rejects underscore
names.
If restricted code needs a handful of names rather than a whole module, do not
allow the import at all — put those specific objects into ``globals`` instead,
the way :ref:`utility_builtins <predefined_builtins>` does.

An allowlisting import hook
...........................

The hook below is a starting point, not a finished policy:

.. testcode:: guarded_import

    from RestrictedPython import compile_restricted
    from RestrictedPython import safe_globals

    ALLOWED_MODULES = frozenset(['math'])

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level != 0:
            raise ImportError('relative imports are not allowed')
        if name not in ALLOWED_MODULES:
            raise ImportError(f'{name!r} may not be imported')
        return __import__(name, globals, locals, fromlist, level)

    # Copy before modifying: `safe_globals` and `safe_builtins` are shared.
    restricted_globals = dict(safe_globals)
    restricted_globals['__builtins__'] = dict(safe_globals['__builtins__'])
    restricted_globals['__builtins__']['__import__'] = guarded_import

    source_code = """
    import math

    result = math.floor(3.7)
    """

    byte_code = compile_restricted(source_code, '<inline>', 'exec')
    loc = {}
    exec(byte_code, restricted_globals, loc)
    print(loc['result'])

.. testoutput:: guarded_import

    3

The hook refuses anything outside the allowlist:

.. testcode:: guarded_import

    source_code = """
    import os
    """

    byte_code = compile_restricted(source_code, '<inline>', 'exec')
    try:
        exec(byte_code, restricted_globals, {})
    except ImportError as e:
        print(e)

.. testoutput:: guarded_import

    'os' may not be imported

Zope's own hook, :func:`AccessControl.ZopeGuards.guarded_import`, is the
reference implementation.
It resolves imports against a registry of explicitly published modules and names
rather than a flat set, so study it before writing your own.
