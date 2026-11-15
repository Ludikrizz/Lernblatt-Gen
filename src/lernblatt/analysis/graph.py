"""Zaehlt Themen-Treffer und Themen-Kopplungen in den data/<Fach>/work/cache/-Extrakten.
Token-sparsam: laedt nichts in den Context, schreibt data/<Fach>/work/cache/graph.md.

    uv run lernblatt graph "<Fach>" --init  # Starter unter work/planning/terms.txt
    uv run lernblatt graph "<Fach>"         # liest work/planning/terms.txt, schreibt graph.md

terms.txt: eine Zeile je Thema, 'Thema: suchwort, suchwort, ...'.
Die Suchwoerter kommen vom Modell (Synonyme, engl. Begriffe, Abkuerzungen) —
ohne sie findet der Abgleich nur woertliche Titel-Treffer.

Zwei Themen auf derselben Seite = eine Kante. Kantengewicht nach Quelle
(Klausur > Uebung > Folien). Grad = Summe der Kanten eines Themas: viel
verbunden + klausurnah = wichtig.
"""

import glob
import io
import os
import re
import sys
from collections import defaultdict
from itertools import combinations

from lernblatt.paths import cache, fest, kursordner

# ponytail: Knopf. Klausurnaehe hoeher drehen, wenn die Rangliste zu folienlastig wird.
GEWICHT = {"KL": 3, "UE": 2, "VL": 1}
TOP_KANTEN = 4  # je Thema in der Tabelle gezeigte staerkste Nachbarn
# Eine Seite, die halb so viele Themen nennt, ist ein Inhaltsverzeichnis, keine
# inhaltliche Kopplung. Sie zaehlt als Treffer, aber erzeugt keine Kanten —
# sonst verklebt die Themenuebersicht der Klausur alles zu einer Clique.
MAX_KLIQUE = 12  # ponytail: Knopf, falls echte Uebersichtsfolien wegfallen


def _pat(s):
    """Regex mit Wortgrenze, damit 'SQL' nicht in 'SQLite' trifft."""
    s = s.strip()
    b0 = r"\b" if s[:1].isalnum() else ""
    b1 = r"\b" if s[-1:].isalnum() else ""
    return re.compile(b0 + re.escape(s) + b1, re.I)


def _ohne_grenze(p):
    """Dasselbe Pattern ohne Wortgrenzen — findet Plural und Beugung."""
    return re.compile(p.pattern.replace(r"\b", ""), re.I)


def load_terms(path):
    """[(Thema, [Pattern])] aus 'Thema: syn1, syn2'-Zeilen."""
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            thema, syns = line.split(":", 1)
            pats = [_pat(s) for s in syns.split(",") if s.strip()]
            out.append((thema.strip(), pats or [_pat(thema)]))
    return out


def split_pages(text):
    """[(Seitennr, Seitentext)] aus den <!-- Seite N -->-Markern."""
    parts = re.split(r"<!-- Seite (\d+) -->", text)
    return [(int(n), t) for n, t in zip(parts[1::2], parts[2::2])]


def pages(fach):
    """(Quelle 'VL'/'UE'/'KL', Datei, Seitennr, Text) ueber alle Extrakte."""
    d = cache(fach, "text")
    for name in sorted(os.listdir(d)):
        if not name.endswith(".md") or name[:2] not in GEWICHT:
            continue
        with open(f"{d}/{name}", encoding="utf-8") as fh:
            for nr, txt in split_pages(fh.read()):
                yield name[:2], name[3:-3], nr, txt


def scan(fach, terms):
    """(treffer, kanten, fundstellen, index, stumme Decks) je Thema/Quelle."""
    treffer = defaultdict(lambda: defaultdict(int))
    kanten = defaultdict(int)
    fund = defaultdict(list)
    decks, getroffen = set(), set()
    index = 0
    for src, datei, nr, txt in pages(fach):
        da = [th for th, pats in terms if any(p.search(txt) for p in pats)]
        if src == "VL":
            decks.add(datei)
            if da:
                getroffen.add(datei)
        for th in da:
            treffer[th][src] += 1
            if src != "VL" and len(fund[th]) < 6:
                fund[th].append(f"{datei} p{nr}")
        if len(da) > MAX_KLIQUE:  # Uebersichtsseite, keine Kopplung
            index += 1
            continue
        for a, b in combinations(sorted(da), 2):
            kanten[(a, b)] += GEWICHT[src]
    return treffer, kanten, fund, index, sorted(decks - getroffen)


def titel_themen(fach):
    """Summe der Themen aus den Kopfzeilen von slide_titles.txt."""
    p = cache(fach, "slide_titles.txt")
    if not os.path.exists(p):
        return 0
    with open(p, encoding="utf-8") as fh:
        return sum(int(n) for n in re.findall(r", (\d+) Themen\)", fh.read()))


def budget(fach, themen_gesamt):
    """(Seiten, Themen-Budget, Quelle) — wieviele Themen `rein` Platz haben.

    Gemessen an drei eigenen Lernblaettern: 2,4-3,0 Themen je Seite
    (125/42 S., 90/30 S., 84/35 S.) -> 2,5 als Richtwert.
    Ohne eigenes Blatt als Referenz ist die Seitenzahl ~1/10 der Folien-Themen
    (gemessen 7,2 / 12,4 / 12,7 Folien-Themen je Blattseite).
    """
    treffer = glob.glob(f"{kursordner(fach)}/sources/**/[Ll]ernblatt*.pdf", recursive=True)
    if treffer:
        try:
            import pymupdf

            seiten = pymupdf.open(treffer[0]).page_count
            return seiten, round(seiten * 2.5), os.path.basename(treffer[0])
        except Exception:  # kein fitz oder PDF kaputt -> schaetzen
            pass
    seiten = max(1, round(themen_gesamt / 10))
    return seiten, round(seiten * 2.5), "geschaetzt, kein eigenes Lernblatt gefunden"


def write_report(fach, terms, treffer, kanten, fund, stumm):
    nachbarn = defaultdict(list)
    for (a, b), w in kanten.items():
        nachbarn[a].append((w, b))
        nachbarn[b].append((w, a))
    grad = {th: sum(w for w, _ in nachbarn[th]) for th, _ in terms}

    gesamt = titel_themen(fach)
    seiten, platz, quelle = budget(fach, gesamt)
    zeilen = sorted(terms, key=lambda t: -grad[t[0]])
    dest = cache(fach, "graph.md")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(
            f"# Themen-Graph {fach}\n\nSeiten-Treffer je Quelle, Grad = Summe "
            f"der Kantengewichte (KL{GEWICHT['KL']}/UE{GEWICHT['UE']}/"
            f"VL{GEWICHT['VL']} je gemeinsamer Seite).\n\n"
        )
        fh.write(
            f"**Umfang:** {gesamt} Folien-Themen · Ziel {seiten} Blattseiten "
            f"({quelle}) · **Budget rund {platz} Themen mit Empfehlung `rein`** "
            f"(2,5 Themen je Seite). Mehr Themen heisst nicht mehr Punkte — was "
            f"ueber dem Budget liegt, kommt auf `optional`.\n\n"
        )
        if stumm:
            fh.write(
                f"**WARN stumme Decks** (kein Thema aus `terms.txt` trifft dort): "
                f"{', '.join(stumm)}. Entweder fehlen Suchwoerter, oder ein "
                f"ganzer Foliensatz fehlt in der Themenliste.\n\n"
            )
        # Nachbarn nur fuer die obere Haelfte. Bei einem Thema mit Grad 2
        # entscheidet Kopplung ohnehin nichts, und die Spalte macht knapp die
        # Haelfte der Datei aus (gemessen: 11,8 von 25 KB) — die liest das Modell
        # bei jedem Lauf mit.
        mitte = sorted(grad.values())[len(grad) // 2] if grad else 0
        fh.write("| Thema | KL | UE | VL | Grad | staerkste Kopplungen |\n")
        fh.write("|---|---|---|---|---|---|\n")
        for th, _ in zeilen:
            t = treffer[th]
            top = (
                ", ".join(f"{b} ({w})" for w, b in sorted(nachbarn[th], reverse=True)[:TOP_KANTEN])
                if grad[th] >= mitte
                else ""
            )
            fh.write(f"| {th} | {t['KL']} | {t['UE']} | {t['VL']} | {grad[th]} | {top} |\n")
        fh.write("\n## Fundstellen in Uebung/Klausur\n")
        for th, _ in zeilen:
            if fund[th]:
                fh.write(f"- **{th}**: {', '.join(fund[th])}\n")
        leer = [th for th, _ in terms if not sum(treffer[th].values())]
        if leer:
            fh.write("\n## Ohne Treffer (Suchwoerter pruefen oder Ausreisser)\n")
            for th, n in plural_test(fach, terms, leer):
                hinweis = (
                    f" — **{n} Treffer ohne Wortgrenze**, also Plural oder "
                    f"Beugung: Suchwort in `terms.txt` erweitern"
                    if n
                    else ""
                )
                fh.write(f"- {th}{hinweis}\n")
    return dest, leer


def plural_test(fach, terms, leer):
    """[(Thema, Treffer ohne Wortgrenze)] — haeufigste Ursache fuer 0 Treffer.

    'artifact' findet 'Artifacts' nicht, 'swimlane' nicht 'Swimlanes'. Die
    Wortgrenze ist Absicht (sonst trifft 'SQL' in 'SQLite'), also melden statt
    aufweichen: wer hier Treffer sieht, ergaenzt die Beugung in terms.txt.
    """
    lose = {th: [_ohne_grenze(p) for p in pats] for th, pats in terms if th in leer}
    if not lose:
        return []
    n = defaultdict(int)
    for _, _, _, txt in pages(fach):
        for th, pats in lose.items():
            if any(p.search(txt) for p in pats):
                n[th] += 1
    return [(th, n[th]) for th in leer]


def init_terms(fach):
    """Starter-terms.txt aus slide_titles.txt — Suchwoerter danach von Hand ergaenzen."""
    src = cache(fach, "slide_titles.txt")
    dest = fest(fach, "planning", "terms.txt")
    if os.path.exists(dest):
        sys.exit(f"{dest} existiert schon — nicht ueberschrieben.")
    seen = []
    with open(src, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"p[\d\-]+(?: \(final p\d+\))?: (.+)", line.strip())
            if m and m.group(1) and m.group(1) not in seen:
                seen.append(m.group(1))
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(
            "# Thema: suchwort, suchwort, ...  (Synonyme/Abkuerzungen ergaenzen,\n"
            "# aehnliche Titel zu EINEM Thema zusammenfassen, Muell loeschen)\n"
        )
        fh.write("".join(f"{t}: {t}\n" for t in seen))
    print(f"{dest} mit {len(seen)} Roh-Titeln. Jetzt verdichten und Suchwoerter setzen.")


def main(fach):
    tp = fest(fach, "planning", "terms.txt")
    if not os.path.exists(tp):
        sys.exit(f'FEHLER: {tp} fehlt. Erst: lernblatt graph "{fach}" --init')
    terms = load_terms(tp)
    treffer, kanten, fund, index, stumm = scan(fach, terms)
    dest, leer = write_report(fach, terms, treffer, kanten, fund, stumm)
    gesamt = titel_themen(fach)
    seiten, platz, quelle = budget(fach, gesamt)
    print(f"{len(terms)} Themen -> {dest}  ({index} Uebersichtsseiten ohne Kanten)")
    print(f"Budget: {seiten} Blattseiten ({quelle}) -> rund {platz} Themen `rein`")
    if stumm:
        print(f"WARN {len(stumm)} Decks ohne jedes Thema: {', '.join(stumm)}")
    if leer:
        print(f"WARN {len(leer)} Themen ohne jeden Treffer: {', '.join(leer[:8])}")


def _selftest():
    assert _pat("SQL").search("das SQL-Modell") and not _pat("SQL").search("SQLite")
    assert _pat("select ?").search("SELECT ?x WHERE")
    assert not _pat("swimlane").search("die Swimlanes")  # Wortgrenze greift
    assert _ohne_grenze(_pat("swimlane")).search("die Swimlanes")
    assert split_pages("x\n<!-- Seite 3 -->\nA\n<!-- Seite 4 -->\nB") == [(3, "\nA\n"), (4, "\nB")]
    import tempfile

    alt = os.environ.get("LERNBLATT_ROOT")
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["LERNBLATT_ROOT"] = tmp
        try:
            assert budget("Testfach", 400)[:2] == (40, 100)
            # Synthetischer Kurs: Regression und Gradient treten gemeinsam auf,
            # Clustering steht allein. Ein Deck trifft kein Thema.
            seiten = {
                "VL_01.md": ["Regression mit Gradient", "Clustering allein", "Regression"],
                "VL_02.md": ["Organisation und Termine"],
                "UE_01.md": ["Aufgabe: Regression per Gradient"],
                "KL_01.md": ["Gradient einer Regression", "Clustering"],
            }
            for name, texte in seiten.items():
                body = "".join(f"<!-- Seite {i} -->\n{t}\n" for i, t in enumerate(texte, 1))
                with open(cache("Testfach", "text", name), "w", encoding="utf-8") as fh:
                    fh.write(body)
            terms = [
                ("Regression", [_pat("regression")]),
                ("Gradient", [_pat("gradient")]),
                ("Clustering", [_pat("clustering")]),
            ]
            tr, kn, fund, _, stumm = scan("Testfach", terms)
            assert dict(tr["Regression"]) == {"VL": 2, "UE": 1, "KL": 1}, tr["Regression"]
            assert kn[("Gradient", "Regression")] == 1 + 2 + 3, kn  # VL + UE + KL
            assert ("Clustering", "Regression") not in kn, kn
            assert stumm == ["02"], stumm
            assert fund["Clustering"] == ["01 p2"], fund
        finally:
            if alt is None:
                os.environ.pop("LERNBLATT_ROOT", None)
            else:
                os.environ["LERNBLATT_ROOT"] = alt
    print(f"selftest ok - Kante Gradient-Regression {kn[('Gradient', 'Regression')]}")


def cli(argv):
    """lernblatt graph <Fach> [--init] | --selftest"""
    fach = [x for x in argv if not x.startswith("--")]
    if "--selftest" in argv:
        _selftest()
    elif not fach:
        sys.exit('Fachname noetig, z.B. lernblatt graph "Mein Fach" --init')
    elif "--init" in argv:
        init_terms(fach[0])
    else:
        main(fach[0])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    cli(sys.argv[1:])
