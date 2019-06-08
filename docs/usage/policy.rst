.. _policy_builtins:

Policies & builtins
-------------------

RestrictedPython provides a way to define policies, by redefining restricted versions of ``print``, ``getattr``, ``setattr``, ``import``, etc..
As shortcuts it offers three stripped down versions of Python's ``__builtins__``:

.. _predefined_builtins:

Predefined builtins
...................

``safe_builtins``
    a safe set of builtin modules and functions
``limited_builtins``
    restricted sequence types (e. g. ``range``, ``list`` and ``tuple``)
``utility_builtins``
    access to standard modules like math, random, string and set.

``safe_globals`` is a shortcut for ``{'__builtins__': safe_builtins}`` as this
is the way globals have to be provided to the `exec` function to actually
restrict the access to the builtins provided by Python.

Guards
......

.. todo::

    Describe Guards and predefined guard methods in details

RestrictedPython predefines several guarded access and manipulation methods:

* ``safer_getattr``
* ``guarded_setattr``
* ``guarded_delattr``
* ``guarded_iter_unpack_sequence``
* ``guarded_unpack_sequence``

Those and additional methods rely on a helper construct ``full_write_guard``, which is intended to help implement immutable and semi mutable objects and attributes.

.. todo::

    Describe full_write_guard more in detail and how it works.

Implementing a policy
---------------------

RestrictedPython only provides the raw material for restricted execution.
To actually enforce any restrictions, you need to supply a policy
implementation by providing restricted versions of ``print``,
``getattr``, ``setattr``, ``import``, etc.  These restricted
implementations are hooked up by providing a set of specially named
objects in the global dict that you use for execution of code.
Specifically:

1. ``_print_`` is a callable object that returns a handler for print
   statements.  This handler must have a ``write()`` method that
   accepts a single string argument, and must return a string when
   called. ``RestrictedPython.PrintCollector.PrintCollector`` is a
   suitable implementation.

2. ``_write_`` is a guard function taking a single argument.  If the
   object passed to it may be written to, it should be returned,
   otherwise the guard function should raise an exception.  ``_write_``
   is typically called on an object before a ``setattr`` operation.

3. ``_getattr_`` and ``_getitem_`` are guard functions, each of which
   takes two arguments.  The first is the base object to be accessed,
   while the second is the attribute name or item index that will be
   read.  The guard function should return the attribute or subitem,
   or raise an exception.
   RestrictedPython ships with a default implementation
   for ``_getattr_`` which prevents the following actions:

   * accessing an attribute whose name start with an underscore
   * accessing the format method of strings as this is considered harmful.

4. ``__import__`` is the normal Python import hook, and should be used
   to control access to Python packages and modules.

5. ``__builtins__`` is the normal Python builtins dictionary, which
   should be weeded down to a set that cannot be used to get around
   your restrictions.  A usable "safe" set is
   ``RestrictedPython.Guards.safe_builtins``.

To help illustrate how this works under the covers, here's an example
function:

.. code-block:: python

    def f(x):
        x.foo = x.foo + x[0]
        print x
        return printed

and (sort of) how it looks after restricted compilation:

.. code-block:: python

    def f(x):
        # Make local variables from globals.
        _print = _print_()
        _write = _write_
        _getattr = _getattr_
        _getitem = _getitem_

        # Translation of f(x) above
        _write(x).foo = _getattr(x, 'foo') + _getitem(x, 0)
        print >>_print, x
        return _print()

Examples
--------

``print``
.........

To support the ``print`` statement in restricted code, we supply a
``_print_`` object (note that it's a *factory*, e.g. a class or a
callable, from which the restricted machinery will create the object):

.. code-block:: pycon

    >>> from RestrictedPython.PrintCollector import PrintCollector
    >>> _print_ = PrintCollector
    >>> _getattr_ = getattr

    >>> src = '''
    ... print("Hello World!")
    ... '''
    >>> code = compile_restricted(src, '<string>', 'exec')
    >>> exec(code)

As you can see, the text doesn't appear on stdout.  The print
collector collects it.  We can have access to the text using the
``printed`` variable, though:

.. code-block:: pycon

    >>> src = '''
    ... print("Hello World!")
    ... result = printed
    ... '''
    >>> code = compile_restricted(src, '<string>', 'exec')
    >>> exec(code)

    >>> result
    'Hello World!\n'

Built-ins
.........

By supplying a different ``__builtins__`` dictionary, we can rule out
unsafe operations, such as opening files:

.. code-block:: pycon

    >>> from RestrictedPython.Guards import safe_builtins
    >>> restricted_globals = dict(__builtins__=safe_builtins)

    >>> src = '''
    ... open('/etc/passwd')
    ... '''
    >>> code = compile_restricted(src, '<string>', 'exec')
    >>> exec(code, restricted_globals)
    Traceback (most recent call last):
      ...
    NameError: name 'open' is not defined

Guards
......

Here's an example of a write guard that never lets restricted code
modify (assign, delete an attribute or item) except dictionaries and
lists:

.. code-block:: pycon

    >>> from RestrictedPython.Guards import full_write_guard
    >>> _write_ = full_write_guard
    >>> _getattr_ = getattr

    >>> class BikeShed(object):
    ...     colour = 'green'
    ...
    >>> shed = BikeShed()

Normally accessing attributes works as expected, because we're using
the standard ``getattr`` function for the ``_getattr_`` guard:

.. code-block:: pycon

    >>> src = '''
    ... print(shed.colour)
    ... result = printed
    ... '''
    >>> code = compile_restricted(src, '<string>', 'exec')
    >>> exec(code)

    >>> result
    'green\n'

However, changing an attribute doesn't work:

.. code-block:: pycon

    >>> src = '''
    ... shed.colour = 'red'
    ... '''
    >>> code = compile_restricted(src, '<string>', 'exec')
    >>> exec(code)
    Traceback (most recent call last):
      ...
    TypeError: attribute-less object (assign or del)

As said, this particular write guard (``full_write_guard``) will allow
restricted code to modify lists and dictionaries:

.. code-block:: pycon

    >>> fibonacci = [1, 1, 2, 3, 4]
    >>> transl = dict(one=1, two=2, tres=3)
    >>> src = '''
    ... # correct mistake in list
    ... fibonacci[-1] = 5
    ... # one item doesn't belong
    ... del transl['tres']
    ... '''
    >>> code = compile_restricted(src, '<string>', 'exec')
    >>> exec(code)

    >>> fibonacci
    [1, 1, 2, 3, 5]

    >>> sorted(transl.keys())
    ['one', 'two']
