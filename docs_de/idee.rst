Die Idee von RestrictedPython
=============================

Python ist ein Turing-vollständige Programmiersprache (https://de.wikipedia.org/wiki/Turing-Vollst%C3%A4ndigkeit).
Eine Python-Schnittstelle im Web-Kontext für den User anzubieten ist ein potentielles Sicherheitsrisiko.
Als Web-Framework (Zope) und CMS (Plone) möchte man den Nutzern eine größt mögliche Erweiterbarkeit auch Through the Web (TTW) ermöglichen, hierzu zählt es auch via Python Scripts Funtionalität hinzuzufügen.

Aus Gründen der IT-Sicherheit muss hier aber zusätzliche Sicherungsmaßnahmen ergriffen werden um die Integrität der Anwendung und des Servers zu wahren.

RestrictedPython wählt den Weg über eine Beschränkung / explizietes Whitelisting von Sprachelementen und Programmbibliotheken.

Hierzu bietet RestrictedPython einen Ersatz für die Python eigene (builtin) Funktion ``compile()`` (Python 2: https://docs.python.org/2/library/functions.html#compile bzw.  Python 3 https://docs.python.org/3/library/functions.html#compile).
Dies Methode ist wie folgt definiert:

.. code:: Python

    compile(source, filename, mode [, flags [, dont_inherit]])

Die Definition von ``comile()`` hat sich mit der Zeit verändert, aber die relevanten Parameter ``source`` und ``mode`` sind geblieben.
``mode`` hat drei erlaubte Werte, die durch folgende String Paramter angesprochen werden:

* ``'exec'``
* ``'eval'``
* ``'single'``

Diese ist für RestrictedPython durch folgende Funktion ersetzt:
.. code:: Python

    compile_restriced(source, filename, mode [, flags [, dont_inherit]])


The primary param ``source`` has been restriced to be an ASCII string or ``unicode`` string.



Also RestrictedPython provides a way to define Policies, by redefining restricted versions of ``print``, ``getattr``, ``setattr``, ``import``, etc..
As shortcutes it offers three stripped down versions of Pythons ``__builtins__``:

* ``safe_builtins`` (by Guards.py)
* ``limited_builtins`` (by Limits.py), which provides restriced sequence types
* ``utilities_builtins`` (by Utilities.py), which provides access for standard modules math, random, string and for sets.

There is also a guard function for making attributes immutable --> ``full_write_guard`` (write and delete protected)
