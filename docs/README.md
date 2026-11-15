# docs/ — Design & Entscheidungen

Projekt: automatische Lernblatt-Generierung pro Studienfach aus Vorlesungsfolien,
Übungen und Klausuren, im Stil der eigenen Beispiel-Lernblätter.

- [style-guide.md](style-guide.md) — fachunabhängige **inhaltliche** Stil-Spez (aus
  3 Beispiel-Lernblättern: CyberSec, Datascience 1, POIS).
- [html-style-guide.md](html-style-guide.md) — **HTML-Layout** der Ausgabe (eine
  scrollbare Datei pro Fach, zentriert, A4-Marker, Druck-CSS) + Code-Snippets.
- [skill-design.md](skill-design.md) — festgelegte Entscheidungen für die drei
  Skills `themen-analyse`, `lernblatt-erweiterung` und `lernblatt-generator`.
- `../.claude/skills/lernblatt-erweiterung/SKILL.md` — leitet aus besonders
  wichtigen Übungs- und Klausurthemen markierte Erweiterungen ab.
- [bild-zuschnitt.md](bild-zuschnitt.md) — **welcher Ausschnitt ins Blatt kommt**.
  Text, der zur Grafik gehört, wird mitfotografiert statt abgeschrieben; fünf
  belegte Fehlschnitte und die zwei Prüfskripte dagegen.
- [markierungen.md](markierungen.md) — **Vertrag für eigene PDF-Markierungen**:
  Kasten = Inhalt übernehmen, Textmarker = Begriff erklären, Notiz = Anweisung
  befolgen, unmarkierte Folienseite = weglassen. Übungs- und Klausurthemen bleiben
  eine freigegebene Ergänzung. Gilt für alle drei Skills.

Siehe auch `../CLAUDE.md` (Projekt-Überblick) und `../.claude/skills/` (Skills).
