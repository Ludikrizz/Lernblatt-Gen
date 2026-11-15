"""Extrahiert Text lokal + baut die Folien-Titel-Map. Token-sparsam: laedt nichts
in den Context, schreibt nur nach data/<Fach>/work/cache/.

    lernblatt extract "<Fach>"

Parser ist **pdf-inspector** (Rust, MIT, lokal, kein Modell, keine Kosten):
- `extract_pages_markdown` liefert Markdown je Seite (Ueberschriften, Listen,
  Tabellen) statt roher Textzeilen.
- `extract_text_with_positions` liefert Schriftgroesse und Position je Textstueck.
  Daraus kommt der Folien-Titel = groesste Schrift ganz oben. Die alte Heuristik
  "erste Textzeile" lieferte in einem Testkurs auf 669/671 Seiten nur die Seitenzahl.

Folgeseiten mit gleichem Titel werden zu einem Thema zusammengefasst; die letzte
Seite ist die finale Animations-Bau-Stufe.
"""

import io
import os
import re
import sys

import pdf_inspector as pi

from lernblatt.paths import cache, kursordner, prefix_fuer_datei, quellen

SIZE_TOL = 0.6  # pt Toleranz, damit mehrzeilige Titel zusammenbleiben
GAP = 2.2  # Zeilenabstand > GAP * Schriftgroesse => nicht mehr Titel
OCR_VISUAL_WORDS = 30  # wenig Text + grosse Grafik => OCR-Fallback pruefen
# PyMuPDF4LLM markiert OCR aus Fotos, Karten und Screenshots als Bildtext. Der
# ist meist Rauschen ("SI Bi 5 Yt Jh") und darf den Seitenvergleich nicht gewinnen.
BILDTEXT = re.compile(r"<!-- Start of picture text -->.*?<!-- End of picture text -->", re.S)


def _fliesstext_woerter(md):
    """Wortzahl ohne OCR-Bildtext. Massstab fuer Erstpass gegen OCR-Fallback."""
    return len(BILDTEXT.sub(" ", md or "").split())


def page_titles(pdf):
    """{Seite (1-basiert): Titel}. Titel = groesste Schrift, oberste Zeile;
    y ist bottom-up, grosses y = weit oben. Bild-Platzhalter (item_type 'image',
    font_size 0) sind kein Text und fallen raus."""
    by_page = {}
    for it in pi.extract_text_with_positions(pdf):
        by_page.setdefault(it.page, []).append(it)
    out = {}
    for p, its in by_page.items():
        cand = [i for i in its if i.item_type == "text" and len(i.text.strip()) > 1]
        if not cand:
            out[p] = ""
            continue
        mx = max(i.font_size for i in cand)
        same = sorted((i for i in cand if i.font_size >= mx - SIZE_TOL), key=lambda i: (-i.y, i.x))
        parts, last = [], None
        for c in same:  # mehrzeilige Titel ja, Seitenmitte nein
            if last is not None and last - c.y > mx * GAP:
                break
            parts.append(c.text.strip())
            last = c.y
        out[p] = " ".join(parts)[:90]
    return out


def _key(t):
    return t.lower().rstrip(" .:0123456789")


def topic_blocks(titles, n):
    """[(Titel, [Seiten], finale Seite)] — Folgeseiten mit gleichem Titel = 1 Thema,
    die letzte ist die finale Animations-Bau-Stufe."""
    out = []
    for p in range(1, n + 1):
        t = titles.get(p, "")
        if out and t and _key(t) == _key(out[-1][0]):
            out[-1][1].append(p)
        else:
            out.append([t, [p]])
    return [(t, ps, ps[-1]) for t, ps in out]


def _visual_pages(pdf, pages):
    """0-basierte Seiten mit wenig Text und grossem Raster-/Vektorinhalt."""
    import pymupdf

    out = set()
    with pymupdf.open(pdf) as doc:
        for extracted in pages:
            if len((extracted.markdown or "").split()) >= OCR_VISUAL_WORDS:
                continue
            page = doc[extracted.page]
            area = page.rect.get_area()
            has_image = bool(page.get_image_info())
            has_graphic = any(d["rect"].get_area() > area * 0.03 for d in page.get_drawings())
            if has_image or has_graphic:
                out.add(extracted.page)
    return out


def _tessdata():
    """Findet deutsche/englische Tesseract-Daten ohne globale PATH-Annahme."""
    candidates = [
        os.environ.get("TESSDATA_PREFIX"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Tesseract-OCR", "tessdata"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Tesseract-OCR", "tessdata"),
    ]
    for candidate in candidates:
        if candidate and os.path.exists(os.path.join(candidate, "eng.traineddata")):
            os.environ["TESSDATA_PREFIX"] = candidate
            return candidate
    return None


def _ocr_markdown(pdf, page_numbers):
    """{Seite: Markdown}; Tesseract zuerst, RapidOCR als Ersatz."""
    if not page_numbers:
        return {}, []
    errors, recovered = [], {}

    def run(callback, wanted, language):
        import pymupdf
        import pymupdf4llm
        from pymupdf4llm.ocr import OCRMode

        doc = pymupdf.open(pdf)
        try:
            chunks = pymupdf4llm.to_markdown(
                doc,
                pages=sorted(wanted),
                page_chunks=True,
                use_ocr=OCRMode.FORCE_KEEP_OLD,
                ocr_language=language,
                ocr_function=callback,
                show_progress=False,
            )
        finally:
            doc.close()
        for chunk in chunks:
            page = chunk["metadata"]["page_number"] - 1
            text = (chunk.get("text") or "").strip()
            if text:
                recovered[page] = text

    tessdata = _tessdata()
    if tessdata:
        try:
            from pymupdf4llm.ocr import tesseract_api

            language = (
                "deu+eng" if os.path.exists(os.path.join(tessdata, "deu.traineddata")) else "eng"
            )
            run(tesseract_api.exec_ocr, page_numbers, language)
        except Exception as exc:
            errors.append(f"Tesseract: {exc}")
    missing = set(page_numbers) - set(recovered)
    if missing:
        try:
            from pymupdf4llm.ocr import rapidocr_api

            run(rapidocr_api.exec_ocr, missing, "eng")
        except Exception as exc:
            errors.append(f"RapidOCR: {exc}")
    return recovered, errors


def write_markdown(pdf, dest):
    """pdf-inspector zuerst; PyMuPDF4LLM-OCR nur fuer Problemseiten."""
    res = pi.extract_pages_markdown(pdf)
    required = {page - 1 for page in res.pages_needing_ocr}
    visual = _visual_pages(pdf, res.pages)
    candidates = required | visual
    ocr, errors = _ocr_markdown(pdf, candidates)
    recovered, parts = set(), []
    for page in res.pages:
        fast = (page.markdown or "").strip()
        fallback = ocr.get(page.page, "")
        if _fliesstext_woerter(fallback) > _fliesstext_woerter(fast):
            fast = fallback
            recovered.add(page.page)
        parts.append(f"<!-- Seite {page.page + 1} -->\n{fast}\n")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    return len(res.pages), recovered, errors


def main(fach):
    if not quellen(fach):
        sys.exit(f"FEHLER: keine PDFs unter {kursordner(fach)}/sources/ gefunden")
    decks, warn = [], []

    for d, pre in quellen(fach):
        unter = os.path.basename(d)
        print(f"=== {unter} ===")
        pdfs = (
            sorted(f for f in os.listdir(d) if f.lower().endswith(".pdf"))
            if os.path.isdir(d)
            else []
        )
        if not pdfs:
            print(f"  ({unter} fehlt oder leer)")
            continue
        for name in pdfs:
            path, base = f"{d}/{name}", os.path.splitext(name)[0]
            file_pre = prefix_fuer_datei(name, pre)
            cls = pi.classify_pdf(path)
            dest = cache(fach, "text", f"{file_pre}_{base}.md")
            n, recovered, ocr_errors = write_markdown(path, dest)
            flag = ""
            if cls.pdf_type != "text_based":
                flag = f"  TYP={cls.pdf_type}"
                warn.append(f"{pre}_{base}: {cls.pdf_type} (conf {cls.confidence:.2f})")
            if recovered:
                flag += f"  OCR={len(recovered)}"
            for error in ocr_errors:
                warn.append(f"{pre}_{base}: OCR-Fallback {error}")
            words = len(open(dest, encoding="utf-8").read().split())
            print(f"  {file_pre}_{base}.md  pages={n} words={words}{flag}")
            if file_pre == "VL":
                decks.append((base, path, n))

    mp = cache(fach, "slide_titles.txt")
    print(f"=== Folien-Titel -> {mp} ===")
    ges = them = 0
    with open(mp, "w", encoding="utf-8") as fh:
        fh.write("# Ein Thema je Zeile. 'final pN' = vollstaendige Animations-Bau-Stufe.\n")
        for base, path, n in decks:
            blocks = topic_blocks(page_titles(path), n)
            ges += n
            them += len(blocks)
            fh.write(f"\n### {base} ({n} Seiten, {len(blocks)} Themen)\n")
            for titel, pages, final in blocks:
                span = (
                    f"p{pages[0]}"
                    if len(pages) == 1
                    else f"p{pages[0]}-{pages[-1]} (final p{final})"
                )
                fh.write(f"{span}: {titel}\n")
    print(f"{ges} Seiten -> {them} Themen.")
    for w in warn:
        print(f"WARN {w}")
    print("Naechste Schritte: Klausur-Zusammenfassung in cache/text/KL_*.md lesen,")
    print(
        f"slide_titles.txt zu Themen verdichten, Tabelle in data/{fach}/work/planning/themenliste.md."
    )


def _testdeck(path):
    """Kleines Foliendeck auf Platte, damit der Selbsttest ohne Kursmaterial
    laeuft: Titel gross oben, Fliesstext, Umlaute, eine Bau-Stufe."""
    import pymupdf

    doc = pymupdf.open()
    seiten = [
        ("Einfuehrung", ["Erster Punkt"]),
        ("Einfuehrung", ["Erster Punkt", "Zweiter Punkt"]),
        ("Regression als Grundlage", ["Gerade durch die Datenpunkte legen"]),
        ("Gradient descent mechanism (steps)", ["Schrittweite und Lernrate"]),
        ("Organisation", ["Vorlesung im Hörsaal 3, Übung montags"]),
    ]
    for nr, (titel, zeilen) in enumerate(seiten, 1):
        p = doc.new_page(width=720, height=540)
        p.insert_text((40, 60), titel, fontsize=28)
        for i, z in enumerate(zeilen):
            p.insert_text((40, 130 + i * 24), z, fontsize=14)
        p.insert_text((680, 525), str(nr), fontsize=10)
    doc.save(path)
    doc.close()


def _selftest():
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmp:
        pdf = f"{tmp}/deck.pdf"
        _testdeck(pdf)
        titles = page_titles(pdf)
        assert titles[3] == "Regression als Grundlage", titles
        assert titles[4] == "Gradient descent mechanism (steps)", titles[4]
        assert not any(t.startswith("[Image") for t in titles.values()), "Bild-Platzhalter im Titel"
        assert topic_blocks(titles, len(titles))[0] == ("Einfuehrung", [1, 2], 2)
        res = pi.extract_pages_markdown(pdf)
        assert res.pages[2].markdown.strip(), "Seite 3 ohne Markdown"
        assert "Hörsaal" in pi.extract_pages_markdown(pdf, [4]).pages[0].markdown, (
            "Umlaut-Encoding kaputt"
        )
    blocks = topic_blocks({1: "A", 2: "A", 3: "B"}, 3)
    assert blocks == [("A", [1, 2], 2), ("B", [3], 3)], blocks

    from PIL import Image, ImageDraw

    with TemporaryDirectory() as tmp:
        scan = f"{tmp}/scan.pdf"
        dest = f"{tmp}/scan.md"
        image = Image.new("RGB", (1000, 400), "white")
        ImageDraw.Draw(image).text((50, 120), "OCR erkennt Text 123", fill="black", font_size=48)
        image.save(scan, "PDF", resolution=150)
        _, recovered, errors = write_markdown(scan, dest)
        output = open(dest, encoding="utf-8").read()
        assert recovered and "OCR erkennt Text 123" in output, (recovered, errors, output)
    print(
        f"selftest ok - {len(topic_blocks(titles, len(titles)))} Themen aus "
        f"{len(titles)} Seiten, Umlaute ok, OCR-Fallback ok"
    )


def cli(argv):
    """lernblatt extract <Fach> | --selftest"""
    if "--selftest" in argv:
        _selftest()
    elif not argv:
        sys.exit('Fachname als Argument noetig, z.B. lernblatt extract "Mein Fach"')
    else:
        main(argv[0])


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    cli(sys.argv[1:])
