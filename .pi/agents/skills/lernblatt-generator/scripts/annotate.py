#!/usr/bin/env python3
"""Schreibt Text/Kaesten in einen Folien-Screenshot (Klausur-Loesungen etc.).

Wie im Beispiel-Lernblatt: Rechenbeispiele mit eingetragener Loesung. Erst das
Bild ansehen, um Koordinaten (Pixel im getrimmten Bild) zu finden, dann annotieren
und das Ergebnis einmal gegenpruefen.

Aufruf:
  python annotate.py --img IN.png --out OUT.png --ann '<json-liste>'

Ann-Ops:
  {"type":"text","x":985,"y":625,"val":"2","color":"red","size":40}
  {"type":"box","x0":840,"y0":600,"x1":1140,"y1":660,"color":"red","width":4}
Text wird um (x,y) zentriert. Farben: red, blue, green, yellow, black.
"""
import argparse, json
from PIL import Image, ImageDraw, ImageFont

COLORS = {"red": (200, 0, 0), "blue": (31, 84, 155), "green": (0, 150, 0),
          "yellow": (240, 200, 0), "black": (0, 0, 0)}


def font(size):
    for path in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ann", required=True, help="JSON-Liste von Ops")
    a = ap.parse_args()
    im = Image.open(a.img).convert("RGB")
    dr = ImageDraw.Draw(im)
    for op in json.loads(a.ann):
        col = COLORS.get(op.get("color", "red"), (200, 0, 0))
        if op["type"] == "text":
            f = font(op.get("size", 40))
            txt = str(op["val"])
            w = dr.textlength(txt, font=f)
            dr.text((op["x"] - w / 2, op["y"] - op.get("size", 40) / 2),
                    txt, fill=col, font=f)
        elif op["type"] == "box":
            dr.rectangle((op["x0"], op["y0"], op["x1"], op["y1"]),
                         outline=col, width=op.get("width", 4))
    im.save(a.out)
    print(f"OK annotiert -> {a.out} {im.size}")


if __name__ == "__main__":
    main()
