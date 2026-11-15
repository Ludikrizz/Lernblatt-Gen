"""Wo was liegt. Eine Stelle, damit die Module nicht auseinanderlaufen.

Alle Kursdaten liegen unter data/<Fach>/ (nicht im Git):

  sources/         Kursmaterial, unverändert
    slides/        Vorlesungsfolien (Präfix VL)
    exercises/     Übungen und Lösungen (UE)
    exams/         Alt- und Probeklausuren (KL)
  work/            Arbeitsdaten der Pipeline
    planning/      Handarbeit und Nutzerfreigaben. Nie automatisch löschen.
    analyses/      dauerhafte Befunde und Aufgabeninventare.
    build/         reproduzierbare Generator- und Kapitelquellen.
    cache/         maschinell erzeugt. Löschen ist folgenlos.
  output/          fertige Lernblätter, Quicknotes, Probeklausuren
    bilder/        gerenderte Folien-Crops, relativ verlinkt

Die Projektwurzel ist der erste Elternordner mit pyproject.toml und AGENTS.md.
LERNBLATT_ROOT überschreibt sie, z.B. wenn Kursdaten außerhalb des Repos liegen.
Die Pfade werden bei jedem Aufruf neu bestimmt, damit Tests die Variable setzen
können.
"""

import os
from pathlib import Path

QUELLEN = [("slides", "VL"), ("exercises", "UE"), ("exams", "KL")]


def root():
    """Projektwurzel als String mit Vorwärts-Schrägstrichen."""
    env = os.environ.get("LERNBLATT_ROOT")
    if env:
        return env.replace("\\", "/").rstrip("/")
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").is_file() and (d / "AGENTS.md").is_file():
            return d.as_posix()
    raise RuntimeError(
        "Projektwurzel nicht gefunden (pyproject.toml + AGENTS.md). LERNBLATT_ROOT setzen."
    )


def kursordner(fach):
    """data/<Fach>/ ohne Anlegen."""
    return f"{root()}/data/{fach}"


def _anlegen(basis, teile):
    p = os.path.join(basis, *teile)
    os.makedirs(os.path.dirname(p) if teile else p, exist_ok=True)
    return p.replace("\\", "/")


def cache(fach, *teile):
    """Pfad unter data/<Fach>/work/cache/. Legt den Ordner an."""
    return _anlegen(f"{kursordner(fach)}/work/cache", teile)


def fest(fach, *teile):
    """Dauerhafter Pfad unter data/<Fach>/work/ (planning, analyses, build)."""
    return _anlegen(f"{kursordner(fach)}/work", teile)


def ausgabe(fach, *teile):
    """Pfad unter data/<Fach>/output/. Legt den Ordner an."""
    return _anlegen(f"{kursordner(fach)}/output", teile)


def prefix_fuer_datei(name, prefix):
    """Ordnet eine Klausur-Zusammenfassung im Folienordner als KL ein."""
    lower = name.lower()
    if prefix == "VL" and "zusammenfassung" in lower and "klausur" in lower:
        return "KL"
    return prefix


def quellen(fach):
    """[(Ordner, Präfix)] mit den PDFs des Fachs.

    Standard sind die drei Unterordner von data/<Fach>/sources/. Liegen dort
    nur flache PDFs (laufender Kurs, noch nicht sortiert), gelten sie als Folien.
    """
    src = f"{kursordner(fach)}/sources"
    if not os.path.isdir(src):
        return []
    unter = [(f"{src}/{u}", p) for u, p in QUELLEN if os.path.isdir(f"{src}/{u}")]
    if unter:
        return unter
    if any(n.lower().endswith(".pdf") for n in os.listdir(src)):
        return [(src, "VL")]
    return []


def pdfs(fach):
    """(Präfix, Dateiname, Pfad) für jedes PDF des Fachs."""
    for d, pre in quellen(fach):
        for name in sorted(os.listdir(d)):
            if name.lower().endswith(".pdf"):
                yield prefix_fuer_datei(name, pre), name, f"{d}/{name}"


def _selftest():
    import tempfile

    alt = os.environ.get("LERNBLATT_ROOT")
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["LERNBLATT_ROOT"] = tmp
        try:
            assert cache("X", "text", "a.md").endswith("data/X/work/cache/text/a.md")
            assert fest("X", "planning", "terms.txt").endswith("data/X/work/planning/terms.txt")
            assert ausgabe("X", "bilder", "a.png").endswith("data/X/output/bilder/a.png")
            assert quellen("X") == [], "ohne sources/ keine Quellen"
            for u in ("slides", "exercises"):
                os.makedirs(f"{tmp}/data/X/sources/{u}")
            open(f"{tmp}/data/X/sources/slides/01.pdf", "w").close()
            open(f"{tmp}/data/X/sources/slides/Klausur_Zusammenfassung.pdf", "w").close()
            assert [p for _, p in quellen("X")] == ["VL", "UE"], quellen("X")
            assert [p for p, _, _ in pdfs("X")] == ["VL", "KL"], list(pdfs("X"))
        finally:
            if alt is None:
                os.environ.pop("LERNBLATT_ROOT", None)
            else:
                os.environ["LERNBLATT_ROOT"] = alt
    print("selftest ok - data/<Fach>/ mit sources/, work/, output/")


if __name__ == "__main__":
    _selftest()
