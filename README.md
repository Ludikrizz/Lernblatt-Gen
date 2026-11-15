# Lernblatt-Gen

GenAI-Pipeline für die Prüfungsvorbereitung: macht aus Vorlesungsfolien, Übungen,
Altklausuren und eigenen PDF-Markierungen quellengebundene HTML-Lernblätter.
Seminarprojekt im Kurs „Designing GenAI Systems for Education“.

## Schnellstart

Voraussetzungen: [uv](https://docs.astral.sh/uv/) und optional
[Tesseract](https://github.com/tesseract-ocr/tesseract) für die OCR.

```bash
uv sync
uv run lernblatt --help
uv run lernblatt selftest
```

Lege das Kursmaterial unter `data/<Fach>/sources/{slides,exercises,exams}/` ab.
Danach:

```bash
uv run lernblatt extract "<Fach>"
uv run lernblatt annots "<Fach>"
uv run lernblatt graph "<Fach>" --init
```

## Dokumentation

- [`AGENTS.md`](AGENTS.md): Struktur, Befehle, Regeln und Zusammenarbeit.
- [`data/README.md`](data/README.md): Layout der Kursdaten.
- [`docs/`](docs/): Stil, Markierungen, Bildzuschnitt und Skill-Design.

Kursmaterial ist urheberrechtlich geschützt und kommt nie ins Repo.
