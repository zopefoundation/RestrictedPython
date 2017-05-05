Grundlagen von RestrictedPython und der Sicherheitskonzepte von Zope2
=====================================================================


Motivation für RestrictedPython
-------------------------------

Python ist eine moderne und heute sehr beliebte Programmiersprache.
Viele Bereiche nutzen heute Python ganz selbstverständlich.
Waren am Anfang gerade Systemadministratoren die via  Python-Skripte ihre Systeme pflegten, ist heute die PyData Community eine der größten Nutzergruppen.
Auch wird Python gerne als Lehrsprache verwendet.

Ein Nutzungsbereich von Python unterscheidet sich fundamental: *Python-Web* bzw. *Applikations-Server die Fremdcode aufnehmen*.
Zope gehörte zu den ersten großen und erfolgreichen Python-Web-Projekten und hat sich mit als erster um dieses Thema gekümmert.

Während in der klassischen Software-Entwicklung aber auch in der Modelierung und Analyse von Daten drei Aspekte relevant sind:

* Verständlichkeit des Programms (--> Siehe PEP 20 "The Zen of Python" https://www.python.org/dev/peps/pep-0020/)
* die Effizienz der Programmiersprache und der Ausführungsumgebung
* Verfügbarkeit der Ausführungsumgebung

ist ein grundlegender Aspekt, die Mächtigkeit der Programmiersprache, selten von Relevanz.
Dies liegt auch daran, dass alle gängigen Programmiersprachen die gleiche Mächtigkeit besitzten: Turing-Vollständig.
Die Theoretische Informatik kennt mehrere Stufen der Mächtigkeit einer Programmiersprache, diese bilden die Grundlage der Berechenbarkeitstheorie.
Für klassische Software-Entwicklung ist eine Turing-vollständige Programmiersprache entsprechend die richtige Wahl.

In der klassischen Software-Welt gelten in der Regel folgende Bedingungen:

* man bekommt eine fertige Software und führt diese aus (Beispiel: Betriebssysteme, Anwendungen und Frameworks)
* man schreibt eine Software / Skript
* man verarbeitet Daten zur Berechung und Visualisierung, ohne ein vollumfängliches Programm zu entwickeln (Beispiel: MatLab, Jupyter-Notebooks)

Da hierbei erstmal keine Unterscheidung zwischen Open Source und Closed Source Software gemacht werden soll, da die relevante Frage eher eine Frage des Vertrauen ist.

Die zentrale Frage ist:

 Vertraue ich der Software, bzw. den Entwicklern der Software und führe diese aus.




Python ist eine Turing-vollständige Prgrammiersprache.
Somit haben Entwickler grundsätzlich erstmal keine Limitierungen beim programmieren.



und können somit potentiell die Applikation und den Server selber schaden.

RestrictedPython und AccessControl zielen auf diese Besonderheit und versuchen einen reduzierten Subset der Programmiersprache Python zur verfügung zu stellen.
Hierzu werden erstmal alle Funktionen die potentiel das System schaden können verboten.
Genauer gesagt muss jede Funktion, egal ob eine der Python ``__builtin__``-Funktionen, der Python Standard-Library oder beliebiger Zusatz-Modulen / (Python-Eggs) explizit freigegeben werden.
Wie sprechen hier von White-Listing.

Damit dies funktioniert, muss neben der ``restricted_compile``-Funktion auch eine API für die explizite Freigabe von Modulen und Funktionen existieren.
