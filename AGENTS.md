# AGENTS.md

## Zweck

Dieses Repository erzeugt pro Studienfach HTML-Lernblätter aus Vorlesungsfolien,
Übungen, Klausuren und Nutzer-Markierungen. Die Vorlesungsfolien sind die Ground
Truth. Eigene Beispiel-Lernblätter liefern nur den visuellen und sprachlichen Stil.

## Verzeichnisstruktur

```text
Examples/<Fach>/
  Vorlesungsfolien/       Folien-PDFs
  Uebungen/               Übungen und Lösungen
  Klausuren/              Alt- und Probeklausuren
  Syllabus.txt            Kursüberblick
  Lernblaetter/           generierte HTML-Ausgaben

Vorlesungen/<Fach>/       laufender Kurs mit derselben möglichen Unterstruktur
_derived/<Fach>/
  planung/                manuelle Begriffe und Nutzerfreigaben
  analysen/               dauerhafte Analyseergebnisse
  build/                  reproduzierbare Generatorquellen und Kapitel
  cache/                  automatisch erzeugte Extrakte, Graphen und Renderprüfungen

.claude/skills/           Projekt-Skills und Generator-Skripte
.pi/agents/               Laufzeitspiegelung der Projekt-Agenten
Scratchpad/               temporäre Skripte und Renderprüfungen
docs/                     Design-, Inhalts- und Prozessdokumentation
tools/pdf-inspector/      Quelltext-Referenz des Parsers, v1.26.0 (installiert wird das PyPI-Paket)
```

`Examples/<Fach>/` ist die bevorzugte Struktur für sortierte Quellen. Während ein
Kurs läuft, kann `Vorlesungen/<Fach>/` verwendet werden. Die Pfadlogik in
`.claude/skills/themen-analyse/scripts/pfade.py` unterstützt beide Varianten.

## Einrichtung

Das Projekt nutzt [uv](https://docs.astral.sh/uv/). Abhängigkeiten stehen in
`pyproject.toml`, die genauen Versionen in `uv.lock`, die Python-Version in
`.python-version`.

```bash
uv sync                 # legt .venv an und installiert alles
uv run python <skript>  # führt ein Skript in dieser Umgebung aus
uv add <paket>          # neue Abhängigkeit, aktualisiert uv.lock
```

- `pdf-inspector` (PyPI, Quelle: https://github.com/firecrawl/pdf-inspector)
  liefert den schnellen Text-Erstpass und die Folientitel.
- `pymupdf` liest Markierungen und rendert Crops.
- `pymupdf4llm` ist der OCR-Fallback. Er ruft Tesseract auf, wenn Sprachdaten
  für `eng` (und möglichst `deu`) unter `TESSDATA_PREFIX`,
  `%LOCALAPPDATA%/Tesseract-OCR/tessdata` oder
  `%PROGRAMFILES%/Tesseract-OCR/tessdata` liegen. Sonst nutzt er RapidOCR.
- Die Skripte finden die Projektwurzel selbst über diese `AGENTS.md`.
  `LERNBLATT_ROOT` überschreibt sie, wenn das Kursmaterial woanders liegt.

`_derived/<Fach>/cache/` ist wegwerfbar. `planung/`, `analysen/` und `build/`
bleiben erhalten. Das genaue Layout steht in `_derived/README.md`.

## Arbeitsablauf

Arbeite in drei Stufen:

1. **Themenanalyse:** Extrakte, PDF-Markierungen, Übungen und Klausuren auswerten.
2. **Optionale Erweiterung:** Aus Prüfungsanforderungen fehlende Grundlagen,
   Beispiele und Transferwege ableiten, wenn dies freigegeben ist.
3. **Generator:** Freigegebene Themen reproduzierbar als HTML-Lernblatt bauen.

Übungs- und Klausurthemen liefern Grundlagen, Aufgabenformen und eigene Beispiele.
Aufgaben werden nicht wörtlich kopiert. Erweiterungen erscheinen nur bei aktiver
Freigabe und am passenden Ende eines Foliensatzes.

## Builds

Alle Befehle laufen aus der Projektwurzel, dem Ordner mit dieser `AGENTS.md`. Ersetze `<Fach>` durch
den Ordnernamen des Fachs:

```bash
uv run python "_derived/<Fach>/build/build_lernblatt.py"
uv run python "_derived/<Fach>/build/build_quicknotes.py"
```

`build/build_quicknotes.py` ist optional und wird nur ausgeführt, wenn die Datei existiert.
Die Builds schreiben die HTML-Dateien vollständig neu. Bilder liegen neben dem
HTML unter `Lernblaetter/bilder/` und werden relativ verlinkt, nicht als Base64
eingebettet.

## Prüfungen

Es gibt keinen `pytest`-Lauf. Nutze Ruff und die vorhandenen Selbsttests und
Artefaktprüfungen:

```bash
uv run ruff check .
uv run ruff format --check .
uv run python -m py_compile "_derived/<Fach>/build/build_lernblatt.py" "_derived/<Fach>/build/chapters/"*.py
uv run python .claude/skills/lernblatt-generator/scripts/lernblatt_html.py --selftest
uv run python .claude/skills/lernblatt-generator/scripts/slides.py --selftest
uv run python .claude/skills/lernblatt-generator/scripts/check_crops.py --selftest
uv run python .claude/skills/themen-analyse/scripts/extract_and_map.py --selftest
uv run python .claude/skills/themen-analyse/scripts/annots.py --selftest
uv run python .claude/skills/themen-analyse/scripts/graph.py --selftest
uv run python .claude/skills/lernblatt-generator/scripts/check_crops.py "Vorlesungen/<Fach>/Lernblaetter/bilder"
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

Öffne danach die erzeugte HTML-Datei unter
`http://127.0.0.1:8765/<Ausgabepfad>`. Beende den Server nach der Prüfung.

## Themenanalyse

Typische Befehle für ein Fach sind:

```bash
uv run python .claude/skills/themen-analyse/scripts/extract_and_map.py <Fach>
uv run python .claude/skills/themen-analyse/scripts/annots.py <Fach>
uv run python .claude/skills/themen-analyse/scripts/graph.py <Fach>
```

Automatische Analysedaten stehen unter `_derived/<Fach>/cache/`. Dauerhafte Berichte
stehen unter `analysen/`, und Nutzerfreigaben stehen unter `planung/`. Große
Folienextrakte nur kapitelweise lesen. Übungs- und Klausurmaterial vollständig lesen,
wenn es klein genug ist. Eine freigegebene `planung/themenliste.md` ist nicht still
zu überschreiben.

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

## Crop-Workflow

1. Die finale Animationsstufe der Folie bestimmen.
2. Mit `render_crop.py` nach `<Ausgabe>/bilder/` rendern.
3. Rechteckwarnungen prüfen und jeden Crop allein verständlich machen.
4. `check_crops.py` über den vollständigen Bilderordner ausführen.
5. Das HTML neu bauen und im Browser prüfen.

Beispiel mit Platzhaltern:

```bash
uv run python .claude/skills/lernblatt-generator/scripts/render_crop.py \
  --pdf "Vorlesungen/<Fach>/Vorlesungsfolien/<datei>.pdf" \
  --pages 1,2 --out "Vorlesungen/<Fach>/Lernblaetter/bilder" --prefix VL01
```

## Zusammenarbeit

`main` ist geschützt. Direkte Pushes sind gesperrt.

1. Erstelle einen Branch: `git switch -c <name>/<thema>`.
2. Pushe den Branch und öffne einen Pull Request.
3. Warte, bis der CI-Check `checks` grün ist.
4. Lass den Pull Request von 1 Teammitglied freigeben.
5. Merge mit „Squash and merge“.

Der CI-Check prüft: kein Kursmaterial im Commit, keine festen Projektpfade,
Spiegelung `.claude/` und `.pi/`, Ruff (Lint und Format), Kompilieren und die
Selbsttests. Vor dem Push lokal: `uv run ruff format .` und `uv run ruff check --fix .`.

## Änderungen

Ändere Build- und Kapitelquellen, nicht generierte HTML-Dateien. Halte relative
Bildpfade ein. Lies vor Inhaltsänderungen `docs/style-guide.md`,
`docs/html-style-guide.md` und `docs/markierungen.md`. Lies bei Crop-Änderungen
zusätzlich `docs/bild-zuschnitt.md`.

Bei Änderungen an einem Skill oder Laufzeit-Agenten die entsprechende Spiegelung
unter `.pi/` beziehungsweise `.claude/` synchron halten.
