================
RestrictedPython
================

RestrictedPython is a tool that helps to define a subset of the Python language which allows to provide a program input into a trusted environment.
RestrictedPython is not a sandbox system or a secured environment, but it helps to define a trusted environment and execute untrusted code inside of it.

For full documentation please see http://restrictedpython.readthedocs.io/ or the local ``docs/index``.

Example
=======

To give a basic understanding what RestrictedPython does here two examples:

An unproblematic code example
-----------------------------

Python allows you to execute a large set of commands.
This would not harm any system.

    >>> from RestrictedPython import compile_restricted
    >>> from RestrictedPython import safe_builtins
    >>>
    >>> source_code = """
    ... def example():
    ...     return 'Hello World!'
    ... """
    >>>
    >>> loc = {}
    >>> byte_code = compile_restricted(source_code, '<inline>', 'exec')
    >>> exec(byte_code, safe_builtins, loc)
    >>>
    >>> loc['example']()
    'Hello World!'

Problematic code example
------------------------

This example directly executed in Python could harm your system.

  >>> from RestrictedPython import compile_restricted
  >>> from RestrictedPython import safe_builtins
  >>>
  >>> source_code = """
  ... import os
  ...
  ... os.listdir('/')
  ... """
  >>> byte_code = compile_restricted(source_code, '<inline>', 'exec')
  >>> # exec(byte_code, safe_builtins, {})
