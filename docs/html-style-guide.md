# HTML-Style-Guide — Lernblätter

Ein Lernblatt = **eine scrollbare `.html` pro Fach** plus einen Ordner `bilder/`
daneben. Offline öffenbar, druckbar auf A4.

**Bilder werden verlinkt, nicht als base64 eingebettet.** Eingebettet wäre die Datei
631 statt 13 KB — auf der Platte egal, aber dann ist sie nicht mehr lesbar: wer sie
öffnet, zieht sich rund 160.000 Token Bildmüll in den Context. `save(bundle=True)`
erzeugt bei Bedarf die Ein-Datei-Fassung zum Verschicken.

Implementierung: `.claude/skills/lernblatt-generator/scripts/lernblatt_html.py`
(Klasse `LernblattHTML`). Inhaltlicher Stil: `style-guide.md`.

## Design-Entscheidungen
1. **Zentriertes weißes Blatt** (`--col:1040px`) auf hellgrauem Grund.
2. **Ein durchgehender Scroll**, kein Seiten-Paging am Bildschirm.
3. **Text groß und kräftig** (19px, `#111`) — der eingebrannte Folientext ist groß,
   kleinerer HTML-Text wirkt daneben unpassend.
4. **Enge vertikale Abstände:** Text und Absätze stehen dicht zusammen. Ein Lernblatt
   wird gescannt, nicht gelesen. Luft zwischen den Zeilen kostet Seiten, ohne etwas
   zu klären — getrennt wird durch visuelle Schlüsselwort-Hervorhebung und Farbe,
   nicht durch Abstand. Überschriften dürfen mehr, Text nicht.
5. **Schlüsselwörter als Leseführung:** Wichtige Begriffe und Kernaussagen im Satz
   stehen fett. Eine <u>Unterstreichung</u> bleibt seltenen, besonders merkbaren
   Ankern vorbehalten. Hebe nur das Keyword hervor, nicht den ganzen Satz.
   Besonders in Stichpunkten muss das entscheidende Keyword beim Überfliegen sofort
   erkennbar sein.
5. **Bilder so breit wie auf der Folie**, nie über die native Pixelbreite skaliert.
   `pic(anteil=0.58)` setzt 58 % der Spalte; den Wert gibt `render_crop.py` aus.
6. **Titel ist der Fachname, sonst nichts.** Kein Dozent, keine Quelle, kein
   Ground-Truth-Zusatz. Woher ein Abschnitt kommt, sagt der Foliensatz-Trenner.
7. **A4-Marker links** alle ~1122px: blaue Zahl im weißen Kästchen. Nur Orientierung
   beim Scrollen („wo mach ich weiter"), bewusst ungefähr.
8. **Hell**, kein Dark Mode — die Screenshots haben weißen Grund.
9. Farben: Blau `#1F549B` (Überschriften), Rot `#C0000C` (Akzent, Klausur).

## Drei Überschriften-Ebenen
| Methode | Rendert | Wofür |
|---|---|---|
| `h1` (aus dem Konstruktor) | zentriert, 2.1rem | Fachname, einmal ganz oben |
| `h_deck` | zentriert, 1.75rem, blaue Linie darüber | ein Foliensatz |
| `h_topic` | linksbündig, 1.45rem | ein Thema, **Folientitel 1:1** |

`h_deck` ist wichtig, sobald mehr als eine Vorlesung im Blatt steht: ohne ihn
verschwimmen die Foliensätze zu einem Strom. Im Druck beginnt jeder Foliensatz
(außer dem ersten) auf einer neuen Seite.

## PDF-Druck auf A4

Der einzelne **A4**-Knopf ruft `window.print()` auf. Im Druckdialog kann das
Lernblatt als PDF gespeichert werden. Eine eigene PDF-Erzeugung und eine
zusammenhängende Endlosseite gehören nicht zur Toolchain. Der Knopf druckt sich
nicht mit.

`@media print` sonst: weißer Grund, Rahmen und Marker weg,
`break-inside:avoid` auf Bildern und Tabellenzeilen.

## Bau-Muster
```python
import sys; sys.path.insert(0, ".claude/skills/lernblatt-generator/scripts")
from lernblatt_html import LernblattHTML
lb = LernblattHTML("Lernblatt <Fach>", img_dir="<Ausgabeordner>/bilder")

lb.h_deck("03 LOD2 SPARQL")                   # Foliensatz-Trenner
lb.h_topic("RDF als Grundlage")               # Folientitel 1:1
lb.kern("RDF beschreibt Daten als Tripel Subjekt – Prädikat – Objekt.")
lb.formel("<mrow><mi>x</mi><mo>=</mo><mn>1</mn></mrow>", "x gleich 1")
lb.sublabel("RDF-Datenmodell:")
lb.glossar("resource", "alles Benennbare, per URI identifiziert.")
lb.bullet("offenes Format (CSV statt Excel).", color="red")
lb.pic("VL03-11.png", anteil=0.62)            # so breit wie auf der Folie
lb.tabelle(["Verfahren", "Paradigma"],        # Zellen duerfen HTML enthalten
           [["Klassifikation", "überwacht"]]) #   lb.img_tag(...) setzt ein Bild rein
lb.akzent("Klausur-Aufgabe: …")
lb.pic("VL03-17_annot.png", anteil=0.8)
lb.save("Examples/<Fach>/Lernblaetter/Lernblatt_<Fach>.html")
```
`formel(mathml, aria)` setzt einen MathML-Inhalt als zentrierte Blockformel. `aria`
beschreibt sie für Screenreader. Jeder HTML-Formeltext nutzt diese Methode. Formeln,
die bereits im Folien-Crop stehen, werden nicht nochmals als HTML gesetzt. Nutze MathML statt Plaintext oder sichtbarem
LaTeX-Quelltext; eine zusätzliche JavaScript-Bibliothek ist nicht nötig.

`h_topic` muss direkt mit `kern()` beginnen. `bullet()` setzt ein führendes Label
vor einem Doppelpunkt automatisch fett. Weitere Schlüsselwörter werden im Quelltext
mit `<b>...</b>` oder sparsam mit `<u>...</u>` ausgezeichnet. So bleibt die
Hervorhebung eine Leseführung und wird nicht zur Vollfettung. Die erste
Tabellenspalte wird automatisch fett gesetzt.

`glossar(t, d)` setzt den Bullet-Punkt an den fetten Begriff und bricht die
Definition eingerückt in die Zeile darunter um. Aufeinanderfolgende `glossar`/`bullet` werden zu **einem** `<ul>`; jeder andere
Aufruf schließt die Liste. Listen sind um 2,4 rem eingerückt, damit Punkt und Text
rechts vom Label darüber stehen. `raw(markup)` ist die Notluke für inline-SVG — sparsam,
sonst driftet der Stil auseinander. `pic(hinweis="…")` setzt eine Caption und ist
nur für Grafiken gedacht, die **nicht** von den Folien stammen.

## Sichtprüfung
HTML im Browser öffnen oder headless-Screenshot (Chrome DevTools MCP).

## Bekannte Grenze
Der Auto-Crop ist ein Rechteck. Sitzt neben dem Titel ein Bild, bleibt der Titel im
Screenshot — `render_crop.py` meldet das. Bei markierten Folien umgeht `--rect` den
Auto-Crop ganz.
