Changes from Python 3.14 to Python 3.15
---------------------------------------

.. literalinclude:: ast/python3_15.ast
   :diff: ast/python3_14.ast

Security audit of the Python 3.15 changes
+++++++++++++++++++++++++++++++++++++++++

Lazy imports (:pep:`810`)
    ``lazy import`` statements do not introduce a new AST node.
    They only add a new field ``is_lazy`` to the existing ``Import`` and
    ``ImportFrom`` nodes, so the default-deny mechanism of
    ``RestrictingNodeTransformer.generic_visit`` does **not** apply to them.
    At run time a lazy import is resolved through the new ``__lazy_import__``
    builtin instead of ``__import__``, thus bypassing a guarded
    ``__import__``.
    Therefore lazy imports are explicitly not allowed.
    Assigning ``__lazy_modules__`` was already blocked by the rule denying
    names which start with an underscore.

Unpacking in comprehensions (:pep:`798`)
    ``[*x for x in seq]``, ``{*x for x in seq}``, ``(*x for x in seq)`` and
    ``{**x for x in seq}`` reuse the existing ``Starred`` node (resp. a
    ``DictComp`` node without a value), so they compiled silently.
    The unpacked value is iterated by the bytecode without calling the
    ``_getiter_`` guard — unlike the equivalent nested comprehension
    ``[y for x in seq for y in x]``.
    Therefore unpacking in comprehensions is explicitly not allowed.

Unary ``+`` in ``match`` literal patterns
    No action needed as the ``match`` statement is not allowed in
    RestrictedPython.

New builtins ``frozendict`` (:pep:`814`) and ``sentinel`` (:pep:`661`)
    No action needed as ``safe_builtins`` is an allow list, so the new
    builtins are not available in restricted code.

New ``inspect`` attributes ``gi_state``, ``cr_state`` and ``ag_state``
    They only reveal the state of a (async) generator resp. coroutine as a
    string, so they are treated like the other harmless attributes
    (e. g. ``gi_running``) and remain accessible.
    Reviewing ``INSPECT_ATTRIBUTES`` also revealed that the attributes of
    asynchronous generator objects (``ag_await``, ``ag_frame``, ``ag_code``)
    were missing from the list; they are now blocked.

Removed ``ast`` classes (``ast.Num``, ``ast.Str``, ``ast.Bytes``, ``ast.NameConstant``, ``ast.Ellipsis``)
    No action needed as they are no longer used by RestrictedPython.
