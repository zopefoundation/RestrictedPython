RestrictedPython 4+
===================

RestrictedPython 4.0.0 und aufwärts ist ein komplett Rewrite für Python 3 Kompatibilität.

Da das ``compiler`` Package in Python 2.6 als depricated erklärt und in 3.0 bereits entfernt wurde und somit in allen Python 3 Versionen nicht verfügbar ist, muss die Grundlage neu geschaffen werden.

Ziele des Rewrite
-----------------

Wir wollen RestrictedPython weiter führen, da es eine Core-Dependency für den Zope2 Applikations-Server ist und somit auch eine wichtige Grundlage für das CMS Plone.
Zope2 soll Python 3 kompatibel werden.

Eine der Kernfunktionalitäten von Zope2 und damit für Plone ist die Möglichkeit Python Skripte und Templates TTW (through the web) zu schreiben und zu modifizieren.



Targeted Versions to support
----------------------------

For the RestrictedPython 4 update we aim to support only current Python
versions (the ones that will have active `security support`_ after this update
will be completed):

* 2.7
* 3.4
* 3.5
* 3.6
* PyPy2.7

.. _`security support` : https://docs.python.org/devguide/index.html#branchstatus

Abhängigkeiten
--------------

Folgende Packete haben Abhägigkeiten zu RestrictedPython:

* AccessControl -->
* zope.untrustedpython --> SelectCompiler
* DocumentTemplate -->
* Products.PageTemplates -->
* Products.PythonScripts -->
* Products.PluginIndexes -->
* five.pt (wrapping some functions and procetion for Chameleon) -->

Zusätzlich sind in folgenden Add'ons Abhängigkeiten zu RestrictedPython
*
