#!/usr/bin/env python3
"""Wo was liegt. Eine Stelle, damit die Skripte nicht auseinanderlaufen.

_derived/<Fach>/ hat vier klar getrennte Bereiche:

  planung/        Handarbeit und Nutzerfreigaben. Nie automatisch loeschen.
  analysen/       dauerhafte Befunde und Aufgabeninventare.
  build/          reproduzierbare Generator- und Kapitelquellen.
  cache/          maschinell erzeugt. Loeschen ist folgenlos; die Analyse-
                  skripte stellen die Daten wieder her.

Gerenderte Bilder liegen NICHT hier, sondern neben dem Lernblatt
(<Ausgabeordner>/bilder/). Sie gehoeren zum Artefakt und sollen mit ihm umziehen.
"""

import os


def _projektwurzel():
    """Projektwurzel = erster Elternordner mit AGENTS.md. LERNBLATT_ROOT
    ueberschreibt das, z.B. wenn Kursmaterial ausserhalb des Repos liegt."""
    env = os.environ.get("LERNBLATT_ROOT")
    if env:
        return env.replace("\\", "/").rstrip("/")
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isfile(os.path.join(d, "AGENTS.md")):
            return d.replace("\\", "/")
        oben = os.path.dirname(d)
        if oben == d:
            raise RuntimeError(
                "Projektwurzel nicht gefunden (keine AGENTS.md "
                "ueber diesem Skript). LERNBLATT_ROOT setzen."
            )
        d = oben


ROOT = _projektwurzel()
UNTER = [("Vorlesungsfolien", "VL"), ("Uebungen", "UE"), ("Klausuren", "KL")]


def cache(fach, *teile):
    """Pfad unter _derived/<Fach>/cache/. Legt den Ordner an."""
    p = os.path.join(f"{ROOT}/_derived/{fach}/cache", *teile)
    os.makedirs(os.path.dirname(p) if teile else p, exist_ok=True)
    return p.replace("\\", "/")


def fest(fach, *teile):
    """Dauerhafter Pfad unter _derived/<Fach>/. Legt Unterordner an."""
    p = os.path.join(f"{ROOT}/_derived/{fach}", *teile)
    os.makedirs(os.path.dirname(p) if teile else p, exist_ok=True)
    return p.replace("\\", "/")


def prefix_fuer_datei(name, prefix):
    """Ordnet eine Klausur-Zusammenfassung im Folienordner als KL ein."""
    lower = name.lower()
    if prefix == "VL" and "zusammenfassung" in lower and "klausur" in lower:
        return "KL"
    return prefix


def quellen(fach):
    """[(Ordner, Praefix)] mit den PDFs des Fachs.

    Neue Kurse liegen unter Vorlesungen/<Fach>/. Examples/<Fach>/ bleibt als
    Rückfall für alte Bestände erhalten. Laufende Kurse dürfen die drei
    Unterordner oder flache Folien direkt im Fachordner verwenden.
    """
    lauf = f"{ROOT}/Vorlesungen/{fach}"
    alt = f"{ROOT}/Examples/{fach}"
    namen = {"Vorlesungsfolien": ("Vorlesungsfolien", "Vorlesungfolien")}
    for root in (lauf, alt):
        if not os.path.isdir(root):
            continue
        unter = []
        for u, p in UNTER:
            kandidaten = namen.get(u, (u,))
            gefunden = next(
                (f"{root}/{name}" for name in kandidaten if os.path.isdir(f"{root}/{name}")), None
            )
            if gefunden:
                unter.append((gefunden, p))
        if unter:
            return unter
        if root == lauf and any(
            os.path.isfile(f"{root}/{name}") and name.lower().endswith(".pdf")
            for name in os.listdir(root)
        ):
            return [(root, "VL")]
    return []


def pdfs(fach):
    """(Praefix, Dateiname, Pfad) fuer jedes PDF des Fachs."""
    for d, pre in quellen(fach):
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.lower().endswith(".pdf"):
                yield prefix_fuer_datei(name, pre), name, f"{d}/{name}"


def _selftest():
    assert cache("X", "text", "a.md").endswith("_derived/X/cache/text/a.md")
    assert fest("X", "planung", "terms.txt").endswith("_derived/X/planung/terms.txt")
    assert "cache" not in fest("X", "planung", "terms.txt")
    q = quellen("GenAi")
    assert {"VL", "UE"} <= {prefix for _, prefix in q}, q
    assert quellen("Gibtsnicht") == []
    n = len(list(pdfs("GenAi")))
    assert n > 0, n
    import shutil

    shutil.rmtree(f"{ROOT}/_derived/X", ignore_errors=True)
    print(f"selftest ok - {n} PDFs in 'GenAi', Layout planung/ + analysen/ + build/ + cache/")


if __name__ == "__main__":
    _selftest()
