"""Prueft gerenderte Ausschnitte auf die vier haeufigsten Zuschnitt-Fehler.

    lernblatt check <bilder-ordner> [--streng]
    lernblatt check --selftest

Warum ueberhaupt: ein schlechter Crop faellt beim Bauen nicht auf, weil man das
Bild nicht ansieht — es landet einfach im Blatt. Erst beim Lernen merkt man, dass
eine Formel ohne ihren Satz dasteht oder eine Legende rechts abgeschnitten ist.
Dieses Skript findet das in einer Sekunde, ohne dass ein Modell die Bilder ansehen
(und dafuer Token bezahlen) muss.

Die Befunde, alle an echten Faellen aus einem Testkurs kalibriert:

  LEER      die Tinte liegt in wenigen Zeilen oder Spalten — eine Linie, kein
            Inhalt. Der Crop hat nur den Rahmen der Markierung erwischt.
            Beleg: VL05-05_autoregressive.png, 485x24 px, ein roter Strich.
  KANTE     (nur mit --streng) Tinte laeuft in eine Bildkante. Mit --pad 0 ist das
            der Normalfall, deshalb standardmaessig still. Ob wirklich ein Satz
            zerschnitten wurde, prueft lernblatt crop exakt am PDF.
  WINZIG    kleiner als MIN_KANTE. Meist eine Formel ohne ihren Satz.
            Beleg: VL05-10_softmax-formula.png, 147x31 px, zeigt "(u1,...,uk)".
  SCHLITZ   extremes Seitenverhaeltnis. Ein Streifen ist fast nie eine
            abgeschlossene Aussage.

Ein Befund ist kein Beweis. Ein Diagramm mit Rahmen loest ANGESCHN aus, ein
bewusst schmaler Bildstreifen SCHLITZ. Das Skript zeigt, wo man hinsehen muss.
"""

import io
import os
import sys

from PIL import Image

MIN_KANTE = 120  # px; darunter ist es ein Fragment, keine Aussage
MIN_STRICH = 6  # px; duenner ist die Tinte eine Linie, kein Inhalt
MAX_RATIO = 8.0  # Breite/Hoehe oder umgekehrt
KANTE_PX = 2  # Streifenbreite, in der auf Anschnitt geprueft wird
KANTE_ANTEIL = 0.06  # so viel Tinte in der Kante = angeschnitten
HELL = 235  # ab hier gilt ein Pixel als Hintergrund


def _tinte(bild, box=None):
    """Anteil nicht-weisser Pixel in `box`. Ueber das Histogramm, nicht ueber eine
    Python-Schleife — sonst dauert ein 1500-px-Bild Sekunden."""
    teil = bild.crop(box) if box else bild
    h = teil.histogram()
    n = teil.size[0] * teil.size[1]
    return (sum(h[:HELL]) / n) if n else 0.0


def befunde(pfad, streng=False):
    """[(Kuerzel, Erklaerung)] fuer ein Bild. Leere Liste = unauffaellig."""
    im = Image.open(pfad).convert("L")
    w, h = im.size
    # Tinte-Maske: alles Dunkle wird weiss, der Rest schwarz. getbbox() liefert
    # dann die Ausdehnung des Inhalts — daran haengen die ersten beiden Tests.
    maske = im.point(lambda v: 255 if v < HELL else 0)
    kasten = maske.getbbox()
    out = []

    if kasten is None:
        return [("LEER", "kein einziges dunkles Pixel")]
    iw, ih = kasten[2] - kasten[0], kasten[3] - kasten[1]
    if min(iw, ih) < MIN_STRICH:
        # Genau der Fall VL05-05: die Tinte liegt in 3 von 24 Zeilen, ueber die
        # volle Breite. Das ist eine Linie — der Rahmen der Markierung, kein Inhalt.
        out.append(
            (
                "LEER",
                f"Inhalt nur {iw}x{ih} px hoch/breit — eine Linie, "
                f"vermutlich nur der Rahmen der Markierung",
            )
        )
        return out  # alles andere ist dann bedeutungslos

    if min(w, h) < MIN_KANTE:
        out.append(
            (
                "WINZIG",
                f"{w}x{h} px — als eigenes Bild zu klein, gehoert "
                f"vermutlich in seinen Satz zurueck",
            )
        )
    r = max(w / h, h / w)
    if r > MAX_RATIO:
        out.append(
            (
                "SCHLITZ",
                f"Seitenverhaeltnis {r:.0f}:1 — ein Streifen ist "
                f"selten eine abgeschlossene Aussage",
            )
        )

    k = min(KANTE_PX, w, h)
    seiten = {
        "links": (0, 0, k, h),
        "rechts": (w - k, 0, w, h),
        "oben": (0, 0, w, k),
        "unten": (0, h - k, w, h),
    }
    warm = [s for s, box in seiten.items() if _tinte(im, box) > KANTE_ANTEIL]
    if streng and warm and len(warm) < 4:
        # Nur mit --streng: mit --pad 0 beruehrt Inhalt die Kante voellig normal,
        # weil der Crop genau am Markierungsrechteck sitzt. Ob wirklich ein Satz
        # zerschnitten wurde, weiss nur das PDF — lernblatt crop prueft das exakt.
        out.append(
            (
                "KANTE",
                f"Tinte in der Kante {', '.join(warm)} — falls dort "
                f"Text steht, geht er ausserhalb weiter",
            )
        )
    return out


def main(ordner, streng=False):
    bilder = sorted(n for n in os.listdir(ordner) if n.lower().endswith(".png"))
    if not bilder:
        sys.exit(f"keine PNG in {ordner}")
    treffer = 0
    for n in bilder:
        b = befunde(os.path.join(ordner, n), streng)
        if not b:
            continue
        treffer += 1
        w, h = Image.open(os.path.join(ordner, n)).size
        print(f"\n{n}  ({w}x{h})")
        for kuerzel, text in b:
            print(f"  {kuerzel:9} {text}")
    print(f"\n{treffer} von {len(bilder)} Bildern auffaellig.")
    if treffer:
        print(
            "Ansehen, nicht blind loeschen — ein Rahmen oder ein bewusst "
            "schmaler Bildstreifen loest die Pruefung auch aus."
        )


def _selftest():
    from PIL import ImageDraw

    tmp = os.path.join(os.environ.get("TEMP", "."), "crop_selftest")
    os.makedirs(tmp, exist_ok=True)

    leer = Image.new("L", (400, 30), 255)
    ImageDraw.Draw(leer).line((0, 29, 400, 29), fill=0)  # nur ein Strich
    leer.save(f"{tmp}/leer.png")

    winzig = Image.new("L", (140, 40), 255)
    ImageDraw.Draw(winzig).rectangle((10, 10, 120, 30), fill=90)
    winzig.save(f"{tmp}/winzig.png")

    ok = Image.new("L", (600, 400), 255)
    ImageDraw.Draw(ok).ellipse((80, 60, 520, 340), fill=120)  # Abstand zum Rand
    ok.save(f"{tmp}/ok.png")

    schnitt = Image.new("L", (600, 400), 255)
    ImageDraw.Draw(schnitt).rectangle((0, 60, 520, 340), fill=120)  # klebt links
    schnitt.save(f"{tmp}/schnitt.png")

    k = lambda n: [x[0] for x in befunde(f"{tmp}/{n}.png")]
    assert k("leer") == ["LEER"], k("leer")
    assert "WINZIG" in k("winzig"), k("winzig")
    assert k("ok") == [], k("ok")
    assert k("schnitt") == [], "KANTE darf ohne --streng nicht feuern"
    assert "KANTE" in [x[0] for x in befunde(f"{tmp}/schnitt.png", streng=True)]

    import shutil

    shutil.rmtree(tmp, ignore_errors=True)
    print("selftest ok - LEER, WINZIG erkannt, KANTE nur mit --streng, sauberes Bild still")


def cli(argv):
    """lernblatt check <bilder-ordner> [--streng] | --selftest"""
    a = [x for x in argv if not x.startswith("--")]
    if "--selftest" in argv:
        _selftest()
    elif not a:
        sys.exit('Ordner noetig, z.B. lernblatt check "data/Mein Fach/output/bilder"')
    else:
        main(a[0], "--streng" in argv)


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    cli(sys.argv[1:])
