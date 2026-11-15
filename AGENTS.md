# AGENTS.md

## Zweck

Dieses Repository erzeugt pro Studienfach HTML-Lernblätter aus Vorlesungsfolien,
Übungen, Klausuren und Nutzer-Markierungen. Die Vorlesungsfolien sind die Ground
Truth. Eigene Beispiel-Lernblätter liefern nur den visuellen und sprachlichen Stil.

## Verzeichnisstruktur

```text
src/lernblatt/            Python-Paket mit der Kommandozeile `lernblatt`
  cli.py                  Einstieg: uv run lernblatt <befehl>
  paths.py                alle Pfade unter data/<Fach>/
  analysis/               extract, annotations, graph (Themenanalyse)
  sheet/                  slides, render, check, annotate, html (Lernblatt-Bau)
tests/                    pytest: Selbsttests und CLI
scripts/moodle/           PowerShell-Skripte für den Moodle-Download
data/<Fach>/              Kursdaten, nicht im Git (Layout: data/README.md)
  sources/                slides/, exercises/, exams/
  work/                   planning/, analyses/, build/, cache/
  output/                 fertige Lernblätter, Bilder unter output/bilder/
docs/                     Design-, Inhalts- und Prozessdokumentation
.claude/skills/           Projekt-Skills (Anleitungen für Agenten)
.claude/agents/           Projekt-Agenten, gespiegelt nach .pi/agents/
scratch/                  temporäre Skripte und Renderprüfungen, nicht im Git
tools/pdf-inspector/      Quelltext-Referenz des Parsers, v1.26.0 (installiert wird das PyPI-Paket)
```

Die Pfadlogik steht nur in `src/lernblatt/paths.py`. Liegen unter
`data/<Fach>/sources/` nur PDFs ohne Unterordner, gelten sie als Folien.

## Einrichtung

Das Projekt nutzt [uv](https://docs.astral.sh/uv/). Abhängigkeiten stehen in
`pyproject.toml`, die genauen Versionen in `uv.lock`, die Python-Version in
`.python-version`.

```bash
uv sync                    # legt .venv an, installiert alles und das Paket lernblatt
uv run lernblatt --help    # zeigt alle Befehle
uv add <paket>             # neue Abhängigkeit, aktualisiert uv.lock
```

- `pdf-inspector` (PyPI, Quelle: https://github.com/firecrawl/pdf-inspector)
  liefert den schnellen Text-Erstpass und die Folientitel.
- `pymupdf` liest Markierungen und rendert Crops.
- `pymupdf4llm` ist der OCR-Fallback. Er ruft Tesseract auf, wenn Sprachdaten
  für `eng` (und möglichst `deu`) unter `TESSDATA_PREFIX`,
  `%LOCALAPPDATA%/Tesseract-OCR/tessdata` oder
  `%PROGRAMFILES%/Tesseract-OCR/tessdata` liegen. Sonst nutzt er RapidOCR.
- Das Paket findet die Projektwurzel selbst über `pyproject.toml` und diese
  `AGENTS.md`. `LERNBLATT_ROOT` überschreibt sie, wenn die Kursdaten woanders liegen.

`data/<Fach>/work/cache/` ist wegwerfbar. `planning/`, `analyses/` und `build/`
bleiben erhalten.

## Arbeitsablauf

Arbeite in drei Stufen:

1. **Themenanalyse:** Extrakte, PDF-Markierungen, Übungen und Klausuren auswerten.
2. **Optionale Erweiterung:** Aus Prüfungsanforderungen fehlende Grundlagen,
   Beispiele und Transferwege ableiten, wenn dies freigegeben ist.
3. **Generator:** Freigegebene Themen reproduzierbar als HTML-Lernblatt bauen.

Übungs- und Klausurthemen liefern Grundlagen, Aufgabenformen und eigene Beispiele.
Aufgaben werden nicht wörtlich kopiert. Erweiterungen erscheinen nur bei aktiver
Freigabe und am passenden Ende eines Foliensatzes.

## Themenanalyse

```bash
uv run lernblatt extract "<Fach>"          # PDFs -> work/cache/text/, slide_titles.txt
uv run lernblatt annots "<Fach>"           # Markierungen -> work/cache/markierungen.md
uv run lernblatt graph "<Fach>" --init     # legt work/planning/terms.txt an
uv run lernblatt graph "<Fach>"            # Themengraph und Budget -> work/cache/graph.md
```

Automatische Analysedaten stehen unter `work/cache/`. Dauerhafte Berichte stehen
unter `work/analyses/`, und Nutzerfreigaben stehen unter `work/planning/`. Große
Folienextrakte nur kapitelweise lesen. Übungs- und Klausurmaterial vollständig lesen,
wenn es klein genug ist. Eine freigegebene `work/planning/themenliste.md` ist nicht
still zu überschreiben.

## Builds

Alle Befehle laufen aus der Projektwurzel, dem Ordner mit dieser `AGENTS.md`.
Ersetze `<Fach>` durch den Ordnernamen unter `data/`:

```bash
uv run python "data/<Fach>/work/build/build_lernblatt.py"
uv run python "data/<Fach>/work/build/build_quicknotes.py"
```

`build_quicknotes.py` ist optional und wird nur ausgeführt, wenn die Datei existiert.
Ein Build-Skript importiert den HTML-Builder aus dem Paket und schreibt nach `output/`:

```python
from lernblatt.paths import ausgabe
from lernblatt.sheet.html import LernblattHTML

lb = LernblattHTML("<Fach>", img_dir=ausgabe("<Fach>", "bilder"))
lb.h_deck("01 Einführung")
lb.pic("VL01-3.png", anteil=0.58)
lb.save(ausgabe("<Fach>", "Lernblatt_<Fach>.html"))
```

Die Builds schreiben die HTML-Dateien vollständig neu. Bilder liegen neben dem
HTML unter `output/bilder/` und werden relativ verlinkt, nicht als Base64
eingebettet.

## Crop-Workflow

1. Die finale Animationsstufe der Folie bestimmen.
2. Mit `lernblatt crop` nach `output/bilder/` rendern.
3. Rechteckwarnungen prüfen und jeden Crop allein verständlich machen.
4. `lernblatt check` über den vollständigen Bilderordner ausführen.
5. Das HTML neu bauen und im Browser prüfen.

Beispiel mit Platzhaltern:

```bash
uv run lernblatt crop --pdf "data/<Fach>/sources/slides/<datei>.pdf" \
  --pages 1,2 --out "data/<Fach>/output/bilder" --prefix VL01
uv run lernblatt check "data/<Fach>/output/bilder"
```

## Prüfungen

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest                  # Selbsttests aller Module und CLI-Tests
uv run lernblatt selftest      # dieselben Selbsttests ohne pytest
uv run lernblatt <befehl> --selftest   # ein Modul einzeln
uv run python -m py_compile "data/<Fach>/work/build/build_lernblatt.py"
```

Nach jedem Build zusätzlich prüfen:

1. Alle referenzierten Bildpfade existieren.
2. Jeder `h_topic`-Block beginnt direkt mit genau einem `kern()`.
3. HTML-Formeln verwenden `LernblattHTML.formel()` und natives MathML.
4. Folientext aus einem Crop wird nicht nochmals als HTML geschrieben.
5. Das HTML öffnet ohne Browserfehler.

Für eine Browserprüfung kann die Projektwurzel temporär dienen:

```bash
uv run python -m http.server 8765 --bind 127.0.0.1
```

Öffne danach `http://127.0.0.1:8765/data/<Fach>/output/<datei>.html`. Beende den
Server nach der Prüfung.

## Inhalts- und Stilregeln

- Markierte Kästen bestimmen den Inhalt. Textmarker verlangen eine Erklärung.
  Notizen sind Arbeitsaufträge. Unmarkierte Seiten bleiben ausgeschlossen.
- Ausgewählte Folientexte bleiben vollständig und inhaltlich 1:1.
- Jeder Topic-Block beginnt mit einer kurzen `kern()`-Zusammenfassung.
- Labels vor `:` und zentrale Schlüsselwörter werden fett gesetzt. Unterstreichung
  bleibt seltenen Merksignalen vorbehalten.
- Tabellenbegriffe und wichtige Begriffe werden zur Leseführung fett gesetzt.
- Formeln erscheinen über `formel()` als MathML, nie als sichtbarer LaTeX-Quelltext.
- Text aus Bildern wird nicht nochmals als HTML geschrieben.
- Echte Folien-Crops bevorzugen. Grafik-Crops müssen ohne die Folie verständlich sein.
- Bei Grafik-Kästen das Rechteck `mit Beschriftung` verwenden und ohne
  PDF-Annotationsebene rendern.
- Eigene Grafiken oder SVGs nicht erstellen. Nutzerbilder und externe Grafiken mit
  einer nachvollziehbaren Quellenangabe kennzeichnen.
- Das Lernblatt bietet nur den A4-Druckdialog, keine Endlos-PDF-Seite.
- Quicknotes bleiben ein separates, knappes HTML und ersetzen kein normales Lernblatt.

## Zusammenarbeit

`main` ist geschützt. Direkte Pushes sind gesperrt.

1. Erstelle einen Branch: `git switch -c <name>/<thema>`.
2. Pushe den Branch und öffne einen Pull Request.
3. Warte, bis die CI-Checks `checks` und `gitleaks` grün sind.
4. Lass den Pull Request von 1 Teammitglied freigeben.
5. Merge mit „Squash and merge“.

Der Check `checks` prüft: kein Kursmaterial im Commit, keine festen Projektpfade,
Spiegelung `.claude/agents/` und `.pi/agents/`, Ruff (Lint und Format), `pytest`
und `lernblatt selftest`. Vor dem Push lokal: `uv run ruff format .` und
`uv run ruff check --fix .`.

Der Check `gitleaks` sucht Schlüssel, Tokens und Passwörter in allen Commits.
Lokal: `gitleaks git .`. Ein Treffer im Commit bleibt in der Git-Historie, auch
nach dem Löschen. Mach den Schlüssel deshalb sofort ungültig und erzeuge einen
neuen. Trage einen echten Fehlalarm mit seinem Fingerprint in `.gitleaksignore` ein.

Dependabot öffnet jeden Montag gesammelte Update-PRs für die Python-Pakete
(`uv.lock`) und die GitHub Actions. Sie durchlaufen dieselbe CI und brauchen
dieselbe Freigabe.

## Änderungen

Ändere Build- und Kapitelquellen, nicht generierte HTML-Dateien. Halte relative
Bildpfade ein. Lies vor Inhaltsänderungen `docs/style-guide.md`,
`docs/html-style-guide.md` und `docs/markierungen.md`. Lies bei Crop-Änderungen
zusätzlich `docs/bild-zuschnitt.md`.

Neuer Code gehört in `src/lernblatt/`. Ein neuer Befehl bekommt einen Eintrag in
`BEFEHLE` in `src/lernblatt/cli.py`, ein Modul mit `_selftest()` einen Eintrag in
`SELBSTTESTS`. Kopiere eine geänderte Datei aus `.claude/agents/` nach `.pi/agents/`.
Pi liest die Skills direkt aus `.claude/skills/`.
