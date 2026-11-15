"""Kommandozeile: uv run lernblatt <befehl> [argumente].

Jeder Befehl reicht seine Argumente unverändert an das zuständige Modul weiter.
`lernblatt <befehl> --selftest` startet den eingebauten Selbsttest des Moduls.
"""

import importlib
import io
import sys

from lernblatt import __version__

# befehl: (modul, funktion, kurzbeschreibung)
BEFEHLE = {
    "extract": (
        "lernblatt.analysis.extract",
        "cli",
        "PDFs eines Fachs nach Markdown, Folientitel nach work/cache/",
    ),
    "annots": (
        "lernblatt.analysis.annotations",
        "cli",
        "eigene PDF-Markierungen nach work/cache/markierungen.md",
    ),
    "graph": (
        "lernblatt.analysis.graph",
        "cli",
        "Themengraph und Budget; --init legt work/planning/terms.txt an",
    ),
    "crop": (
        "lernblatt.sheet.render",
        "main",
        "Folienseiten rendern und auf den Inhalt zuschneiden",
    ),
    "check": (
        "lernblatt.sheet.check",
        "cli",
        "gerenderte Ausschnitte auf Zuschnittfehler prüfen",
    ),
    "annotate": (
        "lernblatt.sheet.annotate",
        "main",
        "Text und Kästen in einen Folien-Screenshot schreiben",
    ),
}

SELBSTTESTS = [
    "lernblatt.paths",
    "lernblatt.analysis.extract",
    "lernblatt.analysis.annotations",
    "lernblatt.analysis.graph",
    "lernblatt.sheet.slides",
    "lernblatt.sheet.check",
    "lernblatt.sheet.html",
]


def _hilfe():
    zeilen = [f"lernblatt {__version__}", "", "Aufruf: uv run lernblatt <befehl> [argumente]", ""]
    breite = max(len(b) for b in BEFEHLE) + 2
    for name, (_, _, text) in BEFEHLE.items():
        zeilen.append(f"  {name:<{breite}}{text}")
    zeilen.append(f"  {'selftest':<{breite}}alle eingebauten Selbsttests ausführen")
    zeilen += ["", "Hilfe zu einem Befehl: uv run lernblatt <befehl> --help"]
    return "\n".join(zeilen)


def selftest():
    for name in SELBSTTESTS:
        importlib.import_module(name)._selftest()


def main(argv=None):
    # Umlaute auch in einer Windows-Konsole mit cp1252. reconfigure statt eines
    # neuen TextIOWrapper, der beim Aufraeumen den geteilten Puffer schliessen wuerde.
    if isinstance(sys.stdout, io.TextIOWrapper) and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    argv = sys.argv[1:] if argv is None else list(argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(_hilfe())
        return 0
    if argv[0] in ("-V", "--version"):
        print(__version__)
        return 0
    befehl, rest = argv[0], argv[1:]
    if befehl == "selftest":
        selftest()
        return 0
    if befehl not in BEFEHLE:
        print(f"Unbekannter Befehl: {befehl}\n\n{_hilfe()}", file=sys.stderr)
        return 2
    modul, funktion, text = BEFEHLE[befehl]
    if rest in (["-h"], ["--help"]) and funktion == "cli":
        mod = importlib.import_module(modul)
        print(f"lernblatt {befehl}: {text}\n\n{mod.cli.__doc__}")
        return 0
    getattr(importlib.import_module(modul), funktion)(rest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
