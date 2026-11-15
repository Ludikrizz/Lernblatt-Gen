# `_derived`-Struktur

`_derived/<Fach>/` enthält Arbeitsdaten und reproduzierbare Quellen. Fertige HTML-Dateien und Bilder liegen weiterhin im Fachordner.

```text
_derived/<Fach>/
  planung/                 manuell gepflegt und freigegeben
    terms.txt              Suchbegriffe für den Themen-Graphen
    themenliste.md         freigegebene Themen und Quicknotes-Zuordnung
  analysen/                dauerhafte Auswertungen
    material.md            Quellenlage und Materialprüfung, falls vorhanden
    themen.md              verdichtete Themenstruktur, falls vorhanden
    aufgaben.md            Übungs- und Klausuraufgaben
    markierungen.md        dauerhafte Auswertung der PDF-Markierungen
    erweiterungen_quellen.md
  build/                   reproduzierbare Generatorquellen
    build_lernblatt.py
    build_quicknotes.py    optional
    chapters/              Kapitelquellen des normalen Lernblatts
  cache/                   vollständig wegwerfbar
    text/                  PDF-Extrakte
    slide_titles.txt
    markierungen.md
    graph.md
    review/                temporäre Render- und Sichtprüfungen
```

## Regeln

1. Speichere Nutzerfreigaben und manuelle Suchbegriffe unter `planung/`.
2. Speichere dauerhafte Befunde und Aufgabeninventare unter `analysen/`.
3. Speichere ausführbare Generatorquellen unter `build/`.
4. Speichere nur reproduzierbare Zwischenstände unter `cache/`.
5. Speichere fertige Lernmaterialien nie unter `_derived/`.

Für neue Produkte gilt dasselbe Muster. Quizzes nutzen später `build/build_quiz.py`, und Probeklausuren nutzen `build/build_probeklausur.py`.
