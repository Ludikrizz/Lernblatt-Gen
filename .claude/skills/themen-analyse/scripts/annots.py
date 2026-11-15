#!/usr/bin/env python3
"""Liest die eigenen Markierungen aus den PDFs eines Fachs und sagt, was drinsteht.

    python annots.py "<Fach>"                    # cache/markierungen.md
    python annots.py --pdf <datei.pdf> [--out X] # einzelnes PDF
    python annots.py --selftest

Wer eine laufende Vorlesung mitschreibt, markiert im PDF, was drankommt. Das ist
das staerkste Signal im ganzen Skill — es kommt vom Menschen, nicht aus einer
Zaehlung. Drei Arten, drei Bedeutungen:

  Kasten (Square/Circle/Polygon/Ink)  -> Inhalt gehoert ins Lernblatt
  Textmarker (Highlight/Underline)    -> diesen Begriff erklaeren
  Notiz (FreeText/Text)               -> Anweisung an den Autor

Fuer jeden Kasten sagt das Skript zusaetzlich, **was** er umschliesst: den Text im
Wortlaut, und ob Grafik drin ist. Das entscheidet in Stufe 2, ob abgeschrieben oder
gescreenshottet wird — ein Kasten um reinen Text braucht kein Bild.

Grafik-Erkennung: Rasterbilder zaehlen direkt. Vektorpfade nicht, denn jede Folie
traegt die Master-Vorlage (Fusszeile, Logo, Titelstrich) als Pfade — hier rund 72
pro Seite. Pfade, die auf fast jeder Seite an derselben Stelle liegen, sind Chrome
und fallen raus. Was uebrig bleibt, ist gezeichneter Inhalt: Diagramme, Baeume,
Tabellenlinien.
"""
import io
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pfade import cache, pdfs
# Rolle je Annotationstyp. Der Nutzer denkt in diesen drei Kategorien, nicht in
# PDF-Typnamen — die Uebersetzung gehoert hierher, nicht in den Skill-Text.
ROLLE = {
    "Square": "Kasten", "Circle": "Kasten", "Polygon": "Kasten",
    "PolyLine": "Kasten", "Ink": "Kasten",
    "Highlight": "Textmarker", "Underline": "Textmarker",
    "StrikeOut": "Textmarker", "Squiggly": "Textmarker",
    "FreeText": "Notiz", "Text": "Notiz",
}
TEMPLATE_ANTEIL = 0.8   # Pfad auf >= 80 % der Seiten an gleicher Stelle = Master
MIN_PFAD = 200.0        # pt^2; kleiner ist ein Strich, keine Grafik
MAX_TEXT = 1500         # Zeichen je Kasten im Report, danach gekuerzt
RAND = 3                # pt Abstand zur Kastenkante, sonst laeuft der
                        # rote Markierungsstrich mit ins Bild
FARBEN = {(1, 1, 0): "gelb", (1, 0, 0): "rot", (0, 1, 0): "gruen",
          (0, 0, 1): "blau", (0, 1, 1): "cyan", (1, 0, 1): "magenta",
          (0, 0, 0): "schwarz", (1, 1, 1): "weiss"}


def _rkey(r):
    return (round(r.x0), round(r.y0), round(r.x1), round(r.y1))


def _nah(a, b, tol=3):
    return all(abs(x - y) <= tol for x, y in zip(_rkey(a), _rkey(b)))


def farbe(an):
    """'gelb' / 'rot' / ... aus der Annotations-Farbe, sonst ''.

    Der Nutzer unterscheidet Farben (gelber Marker, rote Umrandung). Auf die
    naechste Grundfarbe runden reicht — PDF-Viewer speichern nie exakt 1.0/0.0.
    """
    c = an.colors or {}
    rgb = c.get("stroke") or c.get("fill")
    if not rgb or len(rgb) != 3:
        return ""
    return FARBEN.get(tuple(round(v) for v in rgb), "")


def template_pfade(doc):
    """Vektorpfade, die auf fast jeder Seite gleich liegen — Master, kein Inhalt."""
    zaehler = Counter()
    for page in doc.pages():
        for d in page.get_drawings():
            zaehler[_rkey(d["rect"])] += 1
    grenze = max(2, TEMPLATE_ANTEIL * doc.page_count)
    return {k for k, n in zaehler.items() if n >= grenze}


def _eigen(page):
    """Rechtecke der Annotationen selbst. Ihr Rahmen ist ein Vektorpfad wie jeder
    andere — ohne diesen Filter zaehlt sich jeder Kasten als eigene Grafik."""
    return [an.rect for an in (page.annots() or [])]


def grafik_teile(page, template, clip=None):
    """[Rechteck] der gezeichneten/eingebetteten Grafik, optional auf clip begrenzt."""
    import pymupdf as fitz
    eigen = _eigen(page)
    out = [fitz.Rect(i["bbox"]) for i in page.get_image_info()]
    out += [d["rect"] for d in page.get_drawings()
            if _rkey(d["rect"]) not in template
            and abs(d["rect"].get_area()) >= MIN_PFAD
            and not any(_nah(d["rect"], e) for e in eigen)]
    if clip is not None:
        out = [r for r in out if r.intersects(clip)]
    return out


def mit_beschriftung(page, kasten, huelle):
    """Huelle erweitert um y-ueberlappende Beschriftungen — oder None.

    Nur Textbloecke, die vollstaendig im Kasten liegen und auf derselben Hoehe
    wie die Grafik stehen, sind Beschriftungen. Danach werden angeschnittene
    Nachbarbloecke voll aufgenommen: PDF-Textbloecke gruppieren Zeilen und
    Formeln gelegentlich unguenstig, ein Crop darf aber niemals eine Zeile
    zerschneiden.
    """
    import pymupdf as fitz
    if huelle is None:
        return None
    innen = kasten + (RAND, RAND, -RAND, -RAND)
    out = fitz.Rect(huelle) & innen
    blocks = []
    for b in page.get_text("blocks"):
        if not b[4].strip():
            continue
        bb = fitz.Rect(b[:4])
        if not innen.contains(bb):
            continue
        if min(bb.y1, huelle.y1) - max(bb.y0, huelle.y0) <= 0:
            continue                         # Absatz ueber/unter der Grafik
        blocks.append(bb)
        out |= bb

    # Ganze Textbloecke aufnehmen, sobald der erste Zuschnitt sie beruehrt.
    # So wird z.B. keine zweite Zeile oder Formel an der Cropkante gekappt.
    while True:
        neu = [bb for b in page.get_text("blocks") if b[4].strip()
               for bb in [fitz.Rect(b[:4])]
               if innen.contains(bb) and bb.intersects(out) and bb not in blocks]
        if not neu:
            break
        blocks.extend(neu)
        for bb in neu:
            out |= bb
    return out if blocks else None


def inhalt(page, rect, template):
    """Was steckt im Kasten: (Text, Grafik-Rechtecke, Huelle, Huelle+Beschriftung)."""
    import pymupdf as fitz
    txt = re.sub(r"[ \t]+\n", "\n", page.get_text("text", clip=rect)).strip()
    teile = grafik_teile(page, template, rect)
    huelle = None
    if teile:
        huelle = fitz.Rect(teile[0])
        for r in teile[1:]:
            huelle |= r
        huelle &= rect                       # nie ueber den Kasten hinaus croppen
    # Bei einer reinen Grafik gibt es keine separate Beschriftung. Text, der
    # innerhalb der Grafik gezeichnet ist, bleibt Teil des normalen Grafik-Crops.
    beschr = mit_beschriftung(page, rect, huelle) if txt else None
    return txt, teile, huelle, beschr


def lies(pfad):
    """[dict] je Markierung + je Seite, was sonst noch drauf ist.

    Rueckgabe: (markierungen, seiten). `seiten` listet auch die unmarkierten —
    Regel 4 des Nutzers: was er nicht markiert hat, laesst das Lernblatt weg,
    aber der Autor soll sehen, was er damit weglaesst.
    """
    import pymupdf as fitz
    marks, seiten = [], []
    with fitz.open(pfad) as doc:
        template = template_pfade(doc)
        for nr, page in enumerate(doc.pages(), 1):
            an_seite = []
            for an in page.annots() or []:
                typ = an.type[1]
                rolle = ROLLE.get(typ, typ)
                notiz = (an.info.get("content") or "").strip()
                txt, teile, huelle, beschr = inhalt(page, an.rect, template)
                if rolle == "Notiz":
                    # Der Wortlaut der Anweisung steht im content, nicht im Folientext.
                    txt = notiz or txt
                elif notiz:
                    txt = f"{txt}\n[Randnotiz: {notiz}]" if txt else notiz
                an_seite.append({
                    "seite": nr, "typ": typ, "rolle": rolle, "farbe": farbe(an),
                    "rect": _rkey(an.rect), "text": re.sub(r"\n{3,}", "\n\n", txt),
                    "grafik": len(teile), "crop": _rkey(huelle) if huelle else None,
                    "crop_text": _rkey(beschr) if beschr else None,
                })
            marks += an_seite
            wort = len(page.get_text("text").split())
            seiten.append({"seite": nr, "marks": len(an_seite), "woerter": wort,
                           "grafik": len(grafik_teile(page, template))})
    return marks, seiten


KOPF = """# Eigene Markierungen — {fach}

Was hier steht, hat der Nutzer selbst im PDF markiert. Staerkstes Signal, geht dem
Graphen und der Klausur vor. Drei Arten:

| Art | Bedeutung fuer das Lernblatt |
|---|---|
| **Kasten** | Inhalt kommt rein. Text abschreiben, Grafik als Screenshot. |
| **Textmarker** | Diesen Begriff kurz und praezise erklaeren. |
| **Notiz** | Anweisung an den Autor. Befolgen. |

`Grafik: N` heisst, im Kasten liegen N gezeichnete oder eingebettete Elemente —
dann gehoert ein Screenshot dazu, sonst reicht der Text. `Crop` ist das Rechteck
um genau diese Grafik, enger als der Kasten. Master-Elemente (Fusszeile, Logo,
Titelstrich) sind rausgerechnet und zaehlen nicht als Grafik.

Seiten ohne Markierung stehen unten. Sie bleiben draussen — das ist die Ansage des
Nutzers, kein Versehen.
"""


def write_report(fach, quellen=None, dest=None):
    dest = dest or cache(fach, "markierungen.md")
    treffer, dateien = 0, 0
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(KOPF.format(fach=fach))
        for src, name, pfad in (quellen or pdfs(fach)):
            try:
                marks, seiten = lies(pfad)
            except Exception as e:                  # kaputtes PDF ueberspringen
                fh.write(f"\n- WARN {name}: nicht lesbar ({e})\n")
                continue
            dateien += 1
            if not marks:
                continue
            treffer += len(marks)
            fh.write(f"\n## {src} · {name} — {len(marks)} Markierungen "
                     f"auf {len({m['seite'] for m in marks})} von {len(seiten)} Seiten\n")
            for s in seiten:
                auf = [m for m in marks if m["seite"] == s["seite"]]
                if not auf:
                    continue
                fh.write(f"\n### p{s['seite']}\n")
                for m in auf:
                    kopf = f"**{m['rolle']}**"
                    if m["farbe"]:
                        kopf += f" ({m['farbe']})"
                    kopf += f" · Rechteck {m['rect']}"
                    if m["rolle"] == "Kasten":
                        kopf += (f" · Grafik: {m['grafik']}"
                                 + (f", Crop {m['crop']}" if m["crop"] else "")
                                 + (f", **mit Beschriftung {m['crop_text']}**"
                                    if m["crop_text"] else ""))
                    fh.write(f"\n{kopf}\n")
                    t = m["text"]
                    if len(t) > MAX_TEXT:
                        t = t[:MAX_TEXT] + f"\n… (gekuerzt, {len(m['text'])} Zeichen)"
                    if t:
                        fh.write("\n```\n" + t + "\n```\n")
                    elif m["rolle"] != "Kasten":
                        pass
                    elif m["grafik"]:
                        fh.write("\n(kein Text — reine Grafik, Screenshot vom Crop)\n")
                    else:
                        # Weder Folientext noch Folien-Grafik: der Kasten umschliesst
                        # leere Flaeche. Fast immer eine eigene Handzeichnung neben
                        # einer Notiz — Deko der Anweisung, kein Folieninhalt.
                        fh.write("\n(leer — weder Text noch Grafik. Vermutlich eigene "
                                 "Handzeichnung; gehoert zur Notiz daneben.)\n")
            ohne = [s for s in seiten if not s["marks"]]
            fh.write(f"\n### Nicht markiert — {len(ohne)} von {len(seiten)} Seiten\n\n")
            if ohne:
                fh.write("| Seite | Woerter | Grafik |\n|---|---|---|\n")
                for s in ohne:
                    fh.write(f"| p{s['seite']} | {s['woerter']} | {s['grafik']} |\n")
                fh.write("\nDiese Seiten bleiben draussen. Nur zurueckholen, wenn ein "
                         "Kasten oder eine Notiz auf sie verweist.\n")
            else:
                fh.write("Keine — jede Seite ist markiert.\n")
        if not treffer:
            fh.write("\nKeine Markierungen gefunden. Das ist der Normalfall, wenn der "
                     "Nutzer die PDFs noch nicht durchgearbeitet hat — Signal 0 "
                     "entfaellt, kein Fehler.\n")
    return dest, treffer, dateien


def _selftest():
    import pymupdf as fitz
    tmp = os.environ.get("TEMP", ".") + "/annots_selftest.pdf"
    doc = fitz.open()
    for _ in range(3):                               # 3 Seiten mit gleicher Fusszeile
        p = doc.new_page()
        p.draw_line((40, 560), (550, 560))           # Master -> darf keine Grafik sein
    p = doc[0]
    p.insert_text((72, 100), "Hamming-Distanz zaehlt Positionen")
    # Beschriftung NEBEN der Grafik (gleiche Hoehe) und ein Absatz DARUNTER.
    p.insert_text((360, 250), "Schritt 1: neben dem Kreis")
    p.insert_text((72, 420), "Absatz weit unter der Grafik")
    p.add_highlight_annot(p.search_for("Hamming-Distanz")[0])
    p.draw_circle((200, 250), 40)                    # echter Inhalt, nur auf Seite 1
    p.add_rect_annot(fitz.Rect(72, 200, 520, 340))
    doc[1].insert_text((72, 100), "Nur Text, kein Bild")
    doc[1].add_rect_annot(fitz.Rect(60, 80, 400, 120))
    doc.save(tmp)
    doc.close()

    marks, seiten = lies(tmp)
    assert [s["marks"] for s in seiten] == [2, 1, 0], seiten
    assert seiten[2]["grafik"] == 0, "Master-Linie als Grafik gezaehlt"

    hl = next(m for m in marks if m["rolle"] == "Textmarker")
    assert hl["text"].startswith("Hamming-Distanz"), hl

    mit = next(m for m in marks if m["seite"] == 1 and m["rolle"] == "Kasten")
    assert mit["grafik"] >= 1 and mit["crop"], f"Kreis nicht erkannt: {mit}"
    assert mit["crop"][1] >= 200 and mit["crop"][3] <= 320, mit["crop"]
    # Der Text auf gleicher Hoehe zieht den Crop nach rechts, der darunter nicht.
    ct = mit["crop_text"]
    assert ct and ct[2] > mit["crop"][2], f"Beschriftung nicht aufgenommen: {ct}"
    assert ct[3] <= 320, f"Absatz unterhalb faelschlich drin: {ct}"

    ohne = next(m for m in marks if m["seite"] == 2)
    assert ohne["grafik"] == 0 and "Nur Text" in ohne["text"], ohne

    os.remove(tmp)
    print(f"selftest ok - {len(marks)} Markierungen, crop={mit['crop']}, "
          f"mit Beschriftung={ct}, Text-Kasten grafik={ohne['grafik']}")


def main(fach=None, pdf=None, out=None):
    quellen = None
    if pdf:
        name = os.path.basename(pdf)
        quellen = [("VL", name, pdf)]
        fach = fach or os.path.splitext(name)[0]
    dest, treffer, dateien = write_report(fach, quellen, out)
    print(f"{treffer} Markierungen in {dateien} PDFs -> {dest}")
    if not treffer:
        print("Keine Markierungen — Signal 0 entfaellt fuer dieses Fach.")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    if "--selftest" in a:
        _selftest()
    elif "--pdf" in a:
        i = a.index("--pdf")
        main(pdf=a[i + 1], out=(a[a.index("--out") + 1] if "--out" in a else None))
    elif not a:
        sys.exit('Fachname noetig, z.B. annots.py "Datascience 1"')
    else:
        main(a[0])
