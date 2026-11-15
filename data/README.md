# `data/`: Kursdaten pro Fach

Jedes Fach hat einen eigenen Ordner `data/<Fach>/`. Git ignoriert alles in
`data/` außer dieser Datei, weil Kursmaterial urheberrechtlich geschützt ist.

```text
data/<Fach>/
  sources/                 Kursmaterial, unverändert
    slides/                Vorlesungsfolien (Präfix VL)
    exercises/             Übungen und Lösungen (Präfix UE)
    exams/                 Alt- und Probeklausuren (Präfix KL)
    Syllabus.txt           Kursüberblick, optional
  work/                    Arbeitsdaten der Pipeline
    planning/              manuell gepflegt und freigegeben
      terms.txt            Suchbegriffe für den Themengraphen
      themenliste.md       freigegebene Themen und Quicknotes-Zuordnung
    analyses/              dauerhafte Auswertungen
      material.md          Quellenlage und Materialprüfung, optional
      themen.md            verdichtete Themenstruktur, optional
      aufgaben.md          Übungs- und Klausuraufgaben
      markierungen.md      dauerhafte Auswertung der PDF-Markierungen
      erweiterungen_quellen.md
    build/                 reproduzierbare Generatorquellen
      build_lernblatt.py
      build_quicknotes.py  optional
      chapters/            Kapitelquellen des Lernblatts
    cache/                 vollständig wegwerfbar
      text/                PDF-Extrakte (lernblatt extract)
      slide_titles.txt     Folientitel (lernblatt extract)
      markierungen.md      PDF-Markierungen (lernblatt annots)
      graph.md             Themengraph und Budget (lernblatt graph)
      review/              temporäre Render- und Sichtprüfungen
  output/                  fertige Lernmaterialien
    bilder/                Folien-Crops, relativ verlinkt
```

## Regeln

1. Lege Kursmaterial unter `sources/` ab. Ändere es nicht.
2. Speichere Nutzerfreigaben und manuelle Suchbegriffe unter `work/planning/`.
3. Speichere dauerhafte Befunde und Aufgabeninventare unter `work/analyses/`.
4. Speichere ausführbare Generatorquellen unter `work/build/`.
5. Speichere nur reproduzierbare Zwischenstände unter `work/cache/`.

Fertige Lernblätter, Quicknotes und Probeklausuren liegen unter `output/`, nie
unter `work/`. Neue Produkte nutzen dasselbe Muster, zum Beispiel
`work/build/build_quiz.py` und `work/build/build_probeklausur.py`.

Liegen unter `sources/` nur PDFs ohne Unterordner, gelten sie als Folien. Das
hilft bei einem laufenden Kurs, dessen Material noch nicht sortiert ist.

`LERNBLATT_ROOT` setzt eine andere Projektwurzel. Die Kursdaten liegen dann unter
`$LERNBLATT_ROOT/data/<Fach>/`.
