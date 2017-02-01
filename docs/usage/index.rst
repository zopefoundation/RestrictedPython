Usage of RestrictedPython
=========================

Basics
------

RestrictedPython do have tree major scopes:

* compile_restricted methods

  * compile_restricted
  * compile_restricted_exec
  * compile_restricted_eval
  * compile_restricted_single
  * compile_restricted_function

* restricted builtins

  * safe_builtins
  * limited_builtins
  * utility_builtins

* Helper Moduls

  * PrintCollector

heading
-------

The general workflow to execute Python code that is loaded within a Python program is:

.. code:: Python

    source_code = """
    def do_something():
        pass
    """

    byte_code = compile(source_code, filename='<inline code>', mode='exec')
    exec(byte_code)
    do_something()

With RestrictedPython that workflow should be as straight forward as possible:

.. code:: Python

    from RestrictedPython import compile_restricted as compile

    source_code = """
    def do_something():
        pass
    """

    byte_code = compile(source_code, filename='<inline code>', mode='exec')
    exec(byte_code)
    do_something()

With that simple addition ``from RestrictedPython import compile_restricted as compile`` it uses a predefined policy that checks and modify the source code and checks against restricted subset of the Python language.
Execution of the compiled source code is still against the full avaliable set of library modules and methods.
