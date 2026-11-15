#!/usr/bin/env python3
"""Folien-Geometrie: Titel, Inhalts-Box, Themenbloecke, Rendern. Basis PyMuPDF.

Warum PyMuPDF und nicht pdftotext/pdftocairo: nur hier gibt es Schriftgroesse und
Bounding-Box je Zeile. Daraus folgen die zwei Qualitaets-Hebel:

1. Titel = groesste Schrift im oberen Drittel, nicht "erste Textzeile". Gemessen:
   die alte Heuristik lieferte bei CyberSec auf 669/671 Seiten nur die Seitenzahl.
2. Crop = echte Inhalts-Box (Text + Bilder + Vektoren, ohne Vollflaechen-
   Hintergrund), Titelband exakt an seiner Unterkante abgeschnitten. Der fixe
   %-Crop liess sonst einen Titel-Sliver stehen und internes Layout-Weiss drin.

Selbsttest:  python slides.py --selftest
"""
import pymupdf

# find_tables() empfiehlt sonst in jedem Lauf das Zusatzpaket pymupdf_layout.
# Auf Folien nuetzt das nichts, siehe docs/research-visuelle-elemente.md.
pymupdf.no_recommend_layout()

TOP = 0.35        # Titel steht im oberen Drittel der Folie
SIZE_TOL = 0.6    # pt Toleranz, damit mehrzeilige Titel zusammenbleiben
GAP = 2.2         # Zeilenabstand > GAP * Schriftgroesse => nicht mehr Titel


def _lines(page):
    """(Schriftgroesse, bbox, Text) je Textzeile. Zeile, nicht Span, ist die Einheit."""
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for ln in b["lines"]:
            t = "".join(s["text"] for s in ln["spans"]).strip()
            if t:
                out.append((max(s["size"] for s in ln["spans"]), ln["bbox"], t))
    return out


def title_band(page):
    """(Zeilen des Titelbands, Titeltext). Leer, wenn die Seite keinen Text hat."""
    ls = _lines(page)
    if not ls:
        return [], ""
    pool = [l for l in ls if l[1][1] < page.rect.height * TOP and len(l[2]) > 1] or ls
    mx = max(l[0] for l in pool)
    cand = sorted([l for l in pool if l[0] >= mx - SIZE_TOL], key=lambda l: (l[1][1], l[1][0]))
    band, last = [], None
    for c in cand:                      # mehrzeilige Titel ja, Seitenmitte nein
        if last is not None and c[1][1] - last > mx * GAP:
            break
        band.append(c)
        last = c[1][1]
    return band, " ".join(l[2] for l in band)


def page_title(page, maxlen=90):
    return title_band(page)[1][:maxlen]


def _is_pagenum(block, pr):
    """Seitenzahl: kurzer Zahl-Text am oberen oder unteren Rand."""
    if block["type"] != 0 or block["bbox"][1] < pr.height * 0.88:
        return False
    t = "".join(s["text"] for ln in block["lines"] for s in ln["spans"]).strip()
    return 0 < len(t) <= 4 and t.strip("0123456789 .|/-") == ""


def content_rect(page, cut_title=True, pad=6):
    """Bbox des echten Inhalts. Raus fallen: Vollflaechen-Hintergruende, weisse
    Fuellungen, Seitenzahlen und (bei cut_title) das Titelband selbst.

    Der Clip ist ein Rechteck. Steht neben dem Titel noch Inhalt (Bild oben
    rechts), laesst sich das Titelband nicht wegschneiden, ohne den Inhalt zu
    treffen — dann bleibt der Titel drin. `title_cut(page)` sagt vorher, was
    passiert."""
    pr, full = page.rect, page.rect.get_area() * 0.85
    band, _ = title_band(page)
    br = pymupdf.Rect()
    if cut_title:
        for l in band:
            br |= pymupdf.Rect(l[1])
    r = pymupdf.Rect()
    for b in page.get_text("dict")["blocks"]:              # Text UND Bilder
        bb = pymupdf.Rect(b["bbox"])
        if bb.get_area() >= full or _is_pagenum(b, pr):    # Hintergrundbild, Seitenzahl
            continue
        if not br.is_empty and bb in br + (-1, -1, 1, 1):   # Titelzeile
            continue
        r |= bb
    for d in page.get_drawings():
        bb = d["rect"]
        if bb.get_area() >= full:
            continue
        if d.get("fill") == (1.0, 1.0, 1.0) and d.get("color") is None:
            continue
        r |= bb
    if r.is_empty:                                         # z.B. reine Titelfolie
        return pr if not cut_title else content_rect(page, False, pad)
    if not br.is_empty and r.intersects(br):
        r |= br              # Titel ganz drin statt halb angeschnitten
    return pymupdf.Rect(max(pr.x0, r.x0 - pad), max(pr.y0, r.y0 - pad),
                        min(pr.x1, r.x1 + pad), min(pr.y1, r.y1 + pad))


def _is_chrome(r, pr):
    """Folien-Chrome: Titelband/Fusszeile ueber die volle Breite, oder ein
    kleines Objekt in einer oberen Ecke (Uni-Logo)."""
    if r.width > pr.width * 0.9 and (r.y0 < pr.height * 0.02
                                     or r.y1 > pr.height * 0.98):
        return True
    return (r.get_area() < pr.get_area() * 0.03 and r.y1 < pr.height * 0.2
            and (r.x0 > pr.width * 0.8 or r.x1 < pr.width * 0.2))


def figures(page, tol=25, snap=8, min_area=0.03, max_label=0.04):
    """[(Art, Rect)] der einzelnen visuellen Elemente einer Folie.
    Art ist 'tabelle', 'raster' oder 'vektor'.

    PyMuPDF klassifiziert NICHT semantisch — mehr als diese drei Arten gibt die
    Bibliothek nicht her (kein flow_chart/photograph/logo). Messwerte und
    verworfene Alternativen: docs/research-visuelle-elemente.md.

    tol  Zusammenfass-Abstand der Vektorpfade. Default 3 von PyMuPDF zerlegt
         ein Diagramm in Fragmente, 25 haelt es zusammen — Kalibrierungsknopf.
    snap Wie weit ein Textlabel vom Cluster weg stehen darf (Petri-Netz-
         Beschriftungen sitzen ausserhalb der Vektor-Huelle).
    """
    pr = page.rect
    voll, klein = pr.get_area() * 0.85, pr.get_area() * min_area
    out = []

    for t in page.find_tables().tables:                  # Tabellen zuerst
        r = pymupdf.Rect(t.bbox)
        if t.row_count > 1 and t.col_count > 1 and voll > r.get_area() > klein:
            out.append(("tabelle", r))

    # Vollflaechen-Hintergrund VOR dem Clustern raus, sonst klebt die ganze
    # Seite zu einem Cluster zusammen (gemessen an den POIS-Folien).
    dr = [d for d in page.get_drawings() if d["rect"].get_area() < voll]
    labels = [pymupdf.Rect(b["bbox"]) for b in page.get_text("dict")["blocks"]
              if b["type"] == 0
              and pymupdf.Rect(b["bbox"]).get_area() < pr.get_area() * max_label]
    for r in page.cluster_drawings(drawings=dr, x_tolerance=tol, y_tolerance=tol):
        if not (voll > r.get_area() > klein) or _is_chrome(r, pr):
            continue
        if any(r.intersects(t) and t.get_area() > r.get_area() * 0.7
               for _, t in out):
            continue                                     # schon als Tabelle drin
        g = pymupdf.Rect(r)
        for lb in labels:                                # Beschriftung mitnehmen
            if lb.intersects(r + (-snap, -snap, snap, snap)):
                g |= lb
        out.append(("vektor", g))

    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            if voll > r.get_area() > klein and not _is_chrome(r, pr):
                out.append(("raster", r))

    return [(art, r & pr) for art, r in out]     # nie ueber die Seite hinaus


def title_cut(page):
    """True, wenn der Titel beim Crop wirklich verschwindet (nichts steht neben
    ihm). Sonst muss die eigene Ueberschrift den doppelten Titel vermeiden."""
    band, _ = title_band(page)
    if not band:
        return True
    return content_rect(page, cut_title=True).y0 >= max(l[1][3] for l in band) - 1


def render(page, out_path, dpi=150, clip=None, annots=False):
    """Render content without the PDF annotation layer by default.

    Marking boxes are author instructions, not learning content. Keeping them in
    screenshots makes the user's red boxes look like part of the diagram.
    """
    m = pymupdf.Matrix(dpi / 72, dpi / 72)
    page.get_pixmap(matrix=m, clip=clip, annots=annots).save(out_path)
    return out_path


def _key(t):
    return t.lower().rstrip(" .:0123456789")


def topic_blocks(doc):
    """Folgeseiten mit gleichem Titel = ein Thema. Liefert
    (Titel, [Seitenzahlen 1-basiert], finale Seite) — die finale Seite ist die
    vollstaendige Animations-Bau-Stufe."""
    out = []
    for i in range(doc.page_count):
        t = page_title(doc[i])
        if out and _key(t) == _key(out[-1][0]) and t:
            out[-1][1].append(i + 1)
        else:
            out.append([t, [i + 1]])
    return [(t, ps, ps[-1]) for t, ps in out]


def _testdeck():
    """Kleines Foliendeck im Speicher, damit der Selbsttest ohne Kursmaterial
    laeuft. Aufbau wie echte Folien: grosser Titel oben, Fliesstext,
    Seitenzahl unten, eine Animations-Bau-Stufe, ein Vektor- und ein Rasterbild.

      S.1-2  "Einfuehrung"         gleiche Titel = 1 Thema, finale Stufe S.2
      S.3    "RDF als Grundlage"   nur Text, Titelband abschneidbar
      S.4    "Graph-Modell"        Vektordiagramm mit Beschriftung + Text
      S.5    "Architektur"         Rasterbild + Text
    """
    doc = pymupdf.open()
    W, H = 720, 540

    def folie(titel, zeilen, nr):
        p = doc.new_page(width=W, height=H)
        p.insert_text((40, 60), titel, fontsize=28)
        for i, z in enumerate(zeilen):
            p.insert_text((40, 130 + i * 24), z, fontsize=14)
        p.insert_text((W - 40, H - 15), str(nr), fontsize=10)
        return p

    folie("Einfuehrung", ["Erster Punkt"], 1)
    folie("Einfuehrung", ["Erster Punkt", "Zweiter Punkt"], 2)
    folie("RDF als Grundlage", ["Tripel aus Subjekt, Praedikat, Objekt",
                                "Ressourcen werden per URI benannt"], 3)

    p = folie("Graph-Modell", ["Knoten und Kanten"], 4)
    for c in [(260, 300), (460, 300), (360, 420)]:
        p.draw_circle(c, 30, color=(0, 0, 0), fill=(0.8, 0.9, 1.0))
    p.draw_line((290, 300), (430, 300), color=(0, 0, 0), width=2)
    p.draw_line((275, 325), (345, 395), color=(0, 0, 0), width=2)
    p.insert_text((245, 305), "ex:A", fontsize=11)
    p.insert_text((445, 305), "ex:B", fontsize=11)

    p = folie("Architektur", ["Schichtenmodell"], 5)
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 64, 48), False)
    pix.set_rect(pix.irect, (200, 120, 60))
    p.insert_image(pymupdf.Rect(200, 200, 520, 440), pixmap=pix)
    return doc


def _selftest():
    doc = _testdeck()
    p = doc[2]
    assert page_title(p) == "RDF als Grundlage", page_title(p)
    r = content_rect(p, cut_title=True)
    assert r.y0 > 80, f"Titelband nicht abgeschnitten: {r}"
    assert r.get_area() < p.rect.get_area() * 0.7, f"kein echter Crop: {r}"
    assert content_rect(p, cut_title=False).y0 < r.y0, "cut_title wirkungslos"
    assert title_cut(p), "Titel muss beim Crop verschwinden"
    assert r.y1 < p.rect.height - 20, f"Seitenzahl im Crop: {r}"

    blocks = topic_blocks(doc)
    assert blocks[0] == ("Einfuehrung", [1, 2], 2), blocks[0]
    assert len(blocks) == 4, blocks
    assert blocks[-1][2] == blocks[-1][1][-1], "finale Stufe ist die letzte Seite"

    fig = figures(doc[3])                       # Vektordiagramm
    assert [a for a, _ in fig] == ["vektor"], fig
    assert fig[0][1].get_area() < content_rect(doc[3]).get_area(), \
        "Figur muss enger sein als die ganze Inhalts-Box"
    assert figures(doc[4]) and figures(doc[4])[0][0] == "raster", figures(doc[4])
    assert not figures(doc[2]), f"Textfolie ohne Figur: {figures(doc[2])}"
    assert all(r in p.rect for p in doc for _, r in figures(p)), \
        "Figur ragt ueber die Seite hinaus"
    n = doc.page_count
    doc.close()
    print(f"selftest ok - {len(blocks)} Themen aus {n} Seiten")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    else:
        print(__doc__)
