---
name: lernblatt-erweiterung
description: >-
  Leitet aus besonders wichtigen Übungs- und Klausurthemen die nötigen Grundlagen
  und Verständnisbrücken für ein Lernblatt ab. Nutze diesen Skill nach der
  Themenanalyse und vor dem Lernblatt-Generator, wenn ein Thema mit
  `Erweiterung: ja` markiert ist oder wenn Übungen und Klausuren Voraussetzungen
  erklären, die in den Folien knapp oder verteilt stehen. Übernimm Übungen und
  Klausuren nie 1:1. Schreibe eigene Erklärungen, Definitionen, Beispiele und
  geprüfte Transferlösungen. Erstelle am Ende des zugehörigen Foliensatzes einen
  sichtbar markierten Erweiterungsabschnitt. Nutze bei Bedarf Web-Recherche und
  externe, belegte Grafiken.
---

# Lernblatt-Erweiterung

## Zweck

Die Vorlesungsfolien bleiben die Quelle des behandelten Inhalts. Übungen und
Klausuren zeigen, **welche Grundlagen zum Lösen gebraucht werden** und welche
Aufgabenformen sicher beherrscht werden müssen. Dieser Skill baut daraus eine
verständliche Ergänzung. Er kopiert keine Aufgabenblätter und ersetzt keinen
Folientext.

## Eingaben

Lies:

1. `_derived/<Fach>/planung/themenliste.md`, besonders `Erweiterung: ja`, Aufgabentyp,
   Einbauort und Quellen.
2. `_derived/<Fach>/analysen/aufgaben.md` oder die entsprechende Aufgabenliste.
3. Den vollständigen relevanten Folienextrakt und den bestehenden Kapitelquelltext.
4. Die zugehörigen Übungs- und Klausuraufgaben mit Lösungen.
5. `docs/style-guide.md`, `docs/markierungen.md` und `docs/bild-zuschnitt.md`.

## Ableitung statt Kopie

Arbeite pro wichtigem Thema diese Kette ab:

1. **Aufgabenform:** Was soll der Nutzer rechnen, erklären, modellieren oder
   entscheiden?
2. **Voraussetzungen:** Welche Begriffe, Regeln, Formeln oder Zwischenschritte
   braucht man dafür?
3. **Erklärung:** Schreibe diese Voraussetzungen in eigener, klarer Prosa.
4. **Beispiel:** Baue ein neues kleines Beispiel oder erkläre das Folienbeispiel.
5. **Transfer:** Zeige bei einer Transferaufgabe einen geprüften Lösungsweg, ohne
   die Übungsaufgabe wörtlich abzuschreiben.
6. **Abgrenzung:** Trenne Folientext, eigene Erklärung und Prüfungsübertragung
   sichtbar.

Übernimm Zahlen oder Randbedingungen nur, wenn sie für die Erklärung nötig sind.
Prüfe jede Rechnung und jede fachliche Aussage selbst. Erfinde keine Quelle und
keine zusätzliche Kursanforderung.

## Position und Markierung

Füge den Abschnitt **nach allen normalen Themen eines Foliensatzes und vor dem
nächsten `h_deck`** ein. Verwende eine sichtbare Überschrift, zum Beispiel:

```python
lb.h_topic("Erweiterung: Gradient Descent für Klausuraufgaben")
lb.kern(
    "Die Erweiterung verbindet Lernrate, Ableitung und Update-Schritt zu einem prüfbaren Rechenablauf."
)
lb.sublabel("Prüfungs- und Übungserweiterung:")
lb.glossar("Lernrate", "...")
lb.formel("...", "...")
lb.para("Eigenes Beispiel: ...")
```

Die Überschrift muss mit `Erweiterung:` beginnen. Der `kern()`-Satz steht direkt
danach. Setze die Erweiterung nicht zwischen normale Folienthemen und verstecke
sie nicht in einem bestehenden Bullet. Verweise bei Bedarf auf die Quelle im
Build-Kommentar oder im Quellenledger, nicht als lange Literaturangabe im
Lernblatt.

## Web-Recherche und Grafiken

Recherchiere nur, wenn die Folien und Kursmaterialien eine Erklärung nicht tragen
oder eine Grafik das Verständnis deutlich verbessert. Nutze dafür eine nennbare,
verlässliche Quelle und halte sie in `_derived/<Fach>/analysen/erweiterungen_quellen.md` fest.
Externe Grafiken erhalten `pic(hinweis="Quelle: ...")`. Erstelle keine eigene SVG,
Skizze oder Grafik. Bei einer gewünschten Grafik prüfe zuerst passende Folien-Crops,
dann eine externe Quelle. Bleibt nur eine eigene Zeichnung, frage den Nutzer.

## Abschlussprüfung

- Jedes `Erweiterung: ja`-Thema hat genau einen markierten Endabschnitt.
- Die Erweiterung steht vor dem nächsten Foliensatz.
- Keine Übung oder Klausur ist wörtlich kopiert.
- Voraussetzungen, Definitionen, Beispiele und Transferlösungen sind verständlich.
- Jede Rechnung ist geprüft.
- Jede externe Aussage und Grafik steht im Quellenledger.
- Der normale Folientext bleibt vollständig und 1:1.
- Der Generator kann den Abschnitt reproduzierbar aus dem Build-Skript erzeugen.
