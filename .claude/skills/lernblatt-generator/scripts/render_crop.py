#!/usr/bin/env python3
"""Rendert Folienseiten -> PNG und croppt auf den echten Inhalt.

Der Crop ist der wichtigste Qualitaets-Hebel: sonst steht der Folien-Titel
doppelt zur eigenen Ueberschrift und ringsum bleibt Layout-Weiss. Er kommt jetzt
aus der PDF-Geometrie (slides.py), nicht aus festen Prozentwerten — kein
Titel-Sliver mehr, kein internes Weiss.

  python render_crop.py --pdf DECK.pdf --pages 11,19,20 --out DIR --prefix VL03
      [--keep-title] [--full] [--top 0.05] [--bottom 0] [--left 0] [--right 0]
      [--dpi 150] [--pad 6]

--keep-title  Titelband behalten (Default: exakt an seiner Unterkante abschneiden)
--full        gar nicht croppen, ganze Folienseite
--top/...     manuelle Nachkorrektur in Anteilen der Auto-Box (Kalibrierungsknopf)

PDF-Annotationen werden standardmäßig nicht gerendert: Markierungsrahmen sind
Arbeitsanweisungen, kein Folieninhalt.
"""

import argparse
import io
import os
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slides import content_rect, figures, page_title, render, title_cut


def zerschnitten(page, r, mindest=0.02):
    """[Meldung] fuer Textbloecke und Bilder, die das Rechteck durchtrennt.

    Das ist die exakte Antwort auf die Frage, die man dem fertigen PNG nicht mehr
    ansieht: geht der Satz ausserhalb weiter? Ein Block, der nur zum Teil im Crop
    liegt, wird im Lernblatt zu einem angefangenen Satz oder einer Formel ohne
    ihren Bezug — der haeufigste Grund fuer unbrauchbare Ausschnitte.
    """
    # 0.98 statt `bb in r`: bei einem Crop, der genau auf der Blockkante sitzt,
    # liefert die Rechteck-Enthaltensein-Pruefung wegen Rundung False, obwohl der
    # Block vollstaendig drin ist. Der Flaechenanteil ist robuster.
    out = []
    for b in page.get_text("blocks"):
        bb, txt = pymupdf.Rect(b[:4]), " ".join(b[4].split())
        if not txt or not bb.intersects(r) or not bb.get_area():
            continue
        drin = (bb & r).get_area() / bb.get_area()
        if mindest < drin < 0.98:
            out.append(f"Textblock nur zu {drin * 100:.0f}% drin: {txt[:60]!r}")
    for i in page.get_image_info():
        bb = pymupdf.Rect(i["bbox"])
        if not bb.intersects(r) or not bb.get_area():
            continue
        drin = (bb & r).get_area() / bb.get_area()
        if mindest < drin < 0.98:
            out.append(f"Bild nur zu {drin * 100:.0f}% drin")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--pages", required=True, help="Komma-Liste, z.B. 11,19,20")
    ap.add_argument("--out", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--keep-title", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument(
        "--figuren",
        action="store_true",
        help="je Diagramm/Tabelle/Bild ein eigenes PNG statt einem Bild je Folie",
    )
    ap.add_argument(
        "--tol",
        type=float,
        default=25.0,
        help="Zusammenfass-Abstand der Vektorpfade (nur --figuren)",
    )
    for side in ("top", "bottom", "left", "right"):
        ap.add_argument(f"--{side}", type=float, default=0.0)
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument(
        "--pad",
        type=int,
        default=None,
        help="Polster in pt; Default 6, mit --rect 0 — sonst faengt der Crop den Rahmen der Markierung mit ein",
    )
    ap.add_argument(
        "--rect",
        help="feste Box 'x0,y0,x1,y1' in PDF-Punkten statt "
        "Auto-Crop — das Crop-Rechteck aus "
        "markierungen.md kommt hier rein",
    )
    a = ap.parse_args()
    if a.pad is None:
        a.pad = 0 if a.rect else 6
    os.makedirs(a.out, exist_ok=True)

    doc = pymupdf.open(a.pdf)
    for s in [x.strip() for x in a.pages.split(",") if x.strip()]:
        p = int(s)
        if not 1 <= p <= doc.page_count:
            print(f"WARN Seite {p}: Deck hat {doc.page_count} Seiten")
            continue
        page = doc[p - 1]
        if a.figuren:
            figs = figures(page, tol=a.tol)
            if not figs:
                print(
                    f"WARN Seite {p}: keine Figur gefunden — ohne --figuren "
                    f"rendern oder --tol senken"
                )
            for i, (art, r) in enumerate(figs, 1):
                target = os.path.join(a.out, f"{a.prefix}-{p}-{i}_{art}.png")
                render(page, target, dpi=a.dpi, clip=r)
                print(
                    f"OK {os.path.basename(target)} "
                    f"{round(r.width * a.dpi / 72)}x{round(r.height * a.dpi / 72)}px "
                    f"({100 * r.get_area() / page.rect.get_area():.0f}% der Folie)"
                )
            continue
        if a.rect:
            # Feste Box: der Nutzer hat im PDF markiert, wo die Grafik sitzt.
            # Auto-Crop wuerde diese Ansage ueberschreiben.
            x0, y0, x1, y1 = (float(v) for v in a.rect.split(","))
            r = pymupdf.Rect(x0 - a.pad, y0 - a.pad, x1 + a.pad, y1 + a.pad) & page.rect
        elif a.full:
            r = page.rect
        else:
            r = content_rect(page, cut_title=not a.keep_title, pad=a.pad)
        if any((a.top, a.bottom, a.left, a.right)):  # manuelle Nachkorrektur
            w, h = r.width, r.height
            r = pymupdf.Rect(
                r.x0 + w * a.left, r.y0 + h * a.top, r.x1 - w * a.right, r.y1 - h * a.bottom
            )
        target = os.path.join(a.out, f"{a.prefix}-{p}.png")
        render(page, target, dpi=a.dpi, clip=r)
        px = (round(r.width * a.dpi / 72), round(r.height * a.dpi / 72))
        # Breitenanteil, nicht Flaechenanteil: er geht direkt als anteil= in pic().
        # So ist das Bild im Lernblatt so breit wie auf der Folie.
        anteil = r.width / page.rect.width
        drin = (
            ""
            if (a.full or a.rect or a.keep_title or title_cut(page))
            else "  ACHTUNG Titel bleibt im Bild (Inhalt steht daneben)"
        )
        print(
            f"OK {os.path.basename(target)} {px[0]}x{px[1]}px "
            f"| anteil={anteil:.2f} (so breit wie auf der Folie) "
            f"| Titel: {page_title(page, 60)!r}{drin}"
        )
        for m in zerschnitten(page, r):
            print(f"   WARN {m}")
    doc.close()


if __name__ == "__main__":
    # Folientext enthaelt Umlaute und Mathe-Zeichen; ohne das bricht die Ausgabe
    # unter Windows an der Konsolen-Codepage ab.
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
