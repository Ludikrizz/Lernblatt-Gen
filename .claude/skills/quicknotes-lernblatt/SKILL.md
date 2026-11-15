---
name: quicknotes-lernblatt
description: >-
  Erstellt eine separate, extrem knappe Quicknotes- und Karteikartenfassung aus
  markierten Wiederholungsfolien, Quicknotes-Anweisungen oder Lernzettel-Begriffen.
  Jede Definition oder jedes Konzept erhält 1–2 kurze deutsche Sätze. Nutze diesen
  Skill immer, wenn der Nutzer Quicknotes, Karteikarten, Wiederholungsfolien,
  Kurzdefinitionen oder eine schnelle Auswendiglernfassung aus Vorlesungsfolien
  verlangt, auch wenn er den Skill nicht ausdrücklich nennt. Vermische Quicknotes
  nie mit dem normalen erklärenden Lernblatt.
---

# Quicknotes-Lernblatt

Erstelle eine eigene Kurzfassung für schnelles Wiederholen. Sie ist kein Ersatz für
das normale Lernblatt und enthält keine langen Herleitungen.

## Eingabe

1. Lies `_derived/<Fach>/planung/themenliste.md` und die Quicknotes-Zuordnung.
2. Lies `_derived/<Fach>/cache/markierungen.md` für die exakten Notizen und markierten
   Wiederholungsfolien.
3. Lies die zugehörigen Folienextrakte aus `_derived/<Fach>/cache/text/` nur kapitelweise.
4. Nutze die Vorlesungsfolien als Ground Truth. Beispiel-Lernblätter liefern nur den Stil.

## Auswahl

- Übernimm nur Begriffe und Konzepte aus Quicknotes-Blöcken oder ausdrücklichen
  Quicknotes-Anweisungen.
- Nimm keine unmarkierten Detailthemen aus dem normalen Lernblatt hinzu.
- Löse eine Quicknotes-Anweisung in einzelne Begriffe auf.
- Wenn ein Begriff in den Folien nicht erklärt wird, schreibe `Quelle fehlt` statt
  eine Erklärung zu erfinden und melde den Punkt dem Nutzer.

## Form

- Schreibe pro Begriff oder Konzept **1–2 Sätze**.
- Erkläre zuerst, was es ist, dann wozu es dient oder worin der Unterschied liegt.
- Nutze deutsche Sätze. Lasse etablierte englische Fachbegriffe in Klammern stehen.
- Schreibe keine Quellenangaben, Foliennummern oder Meta-Kommentare in das Blatt.
- Nutze eine kompakte Tabelle oder Glossarzeilen, wenn sie schneller scannbar sind.
- Setze Begriffe vor einem Doppelpunkt, zentrale Schlüsselwörter und Kernaussagen
  zur Leseführung fett. Unterstreiche nur seltene besondere Merksignale.
- Setze wichtige Tabellenbegriffe fett.
- Setze mathematische Formeln mit `LernblattHTML.formel()` als MathML.
- Nutze keine Screenshots, außer eine markierte Grafik ist ohne Bild nicht verständlich.
- Trenne Begriffe mit ähnlicher Bedeutung nicht künstlich auf.
- Ergänze neue Inhalte nur, wenn eine Notiz das verlangt. Kennzeichne Ergänzungen kurz.

## Ausgabe

Erstelle den Quelltext unter `_derived/<Fach>/build/build_quicknotes.py` und die Ausgabe unter
`Vorlesungen/<Fach>/Lernblaetter/Quicknotes_<Fach>.html`.

Nutze `LernblattHTML` aus
`.claude/skills/lernblatt-generator/scripts/lernblatt_html.py`, damit die Ausgabe
offline funktioniert und druckbar bleibt. Verwende `h_deck` für die Foliensätze und
`glossar` oder kompakte Tabellen für die Begriffe. Bilder gehören in den vorhandenen
`bilder/`-Ordner neben dem normalen Lernblatt.

Das Build-Skript bleibt die Quelle. Ändere beim nächsten Lauf nur die betroffenen
Quicknotes-Blöcke und schreibe die HTML-Datei vollständig neu.

## Abschlussprüfung

Prüfe vor der Ausgabe:

- Jede Quicknotes-Anweisung ist abgedeckt.
- Jeder Eintrag hat höchstens 2 kurze Sätze.
- Kein normaler Lernblatt-Abschnitt ist unbemerkt hineingerutscht.
- Fehlende Quellen sind sichtbar markiert und im Chat genannt.
