---
name: lernblatt-generator
description: >-
  Erzeugt aus einer freigegebenen Themenliste die Lernblätter eines Studienfachs als
  .html (eine scrollbare Datei pro Fach mit verlinkten Bildern daneben, druckbar auf
  A4), screenshot-lastig im Stil der eigenen Beispiel-Lernblätter. Rendert echte
  Folien-Screenshots, croppt Folien-Chrome (Titel/Logo/Seitenzahl), annotiert
  Klausur-Rechenbeispiele und baut die Seite mit dem wiederverwendbaren HTML-Helfer.
  Wertet die eigenen Markierungen im PDF aus: ein Kasten
  bestimmt, was reinkommt, ein Textmarker verlangt eine Begriffserklärung, eine
  handschriftliche Notiz ist eine Anweisung. Schreibt ein bestehendes Lernblatt fort,
  wenn während des Semesters neue Foliensätze dazukommen, statt es neu zu bauen.
  Nutze diesen Skill immer,
  wenn der Nutzer aus Folien/Themen ein Lernblatt, eine Zusammenfassung, ein
  Klausur-Lernblatt oder Übungsmaterial generieren will, oder wenn er ein
  vorhandenes Lernblatt um neue Vorlesungen erweitern, aktualisieren oder ergänzen
  will — auch wenn nur ein Fachname
  oder eine freigegebene Themenliste genannt wird. Dies ist Stufe 3 nach
  `themen-analyse` und `lernblatt-erweiterung`.
---

# Lernblatt-Generator (Stufe 3)

Zweck: aus der **freigegebenen** Themenliste (`_derived/<Fach>/planung/themenliste.md`,
Output von `themen-analyse`) und den markierten Erweiterungen aus
`lernblatt-erweiterung` die Lernblätter als **eine `.html` pro Fach** bauen.
Läuft immer erst, nachdem Themenliste und Erweiterungen freigegeben sind.

Layout-Spez: `docs/html-style-guide.md`. Inhaltliche Stil-Spez: `docs/style-guide.md`.
**Bildausschnitte: `docs/bild-zuschnitt.md` — lies das, bevor du den ersten Crop
renderst.**
Kalibrierung aus dem Selbstvergleich: `docs/vergleich-datascience.md`. Ground Truth
= Vorlesungsfolien; die alten Lernblätter sind nur Stil-Referenz.

## Stil in einem Satz
Eine zentrierte, durchgehend scrollbare HTML-Seite: BLAUE fette Themen-Überschrift
+ fett-schwarze Kernaussage/Unter-Labels, Glossar-Bullets und **echte Folien-
Screenshots** (ohne Folien-Chrome, volle Spaltenbreite), A4-Marker links zur
Orientierung. ~1/8 der bereinigten Folien. Klausur-Rechenbeispiele als
**annotierte** Screenshots.

**Ausnahme: markierte Decks.** Hat der Nutzer im PDF Kästen gezogen, dreht sich das
Verhältnis um — dann trägt der Text, und Screenshots kommen nur dort, wo die Aussage
wirklich im Bild steckt. Warum, steht in Schritt 1b.

## Ablauf pro Fach

### 1. Freigegebene Themenliste laden und Modus wählen
Lies `_derived/<Fach>/planung/themenliste.md` und die vorbereiteten Erweiterungen aus
`lernblatt-erweiterung`. Arbeite **kapitelweise** (eine Vorlesung je Schritt im
Context) — das hält den Token-Verbrauch niedrig und die Struktur folgt
der Vorlesung.

Bau nur Themen mit Empfehlung **`rein`**. Zusätzlich müssen alle Übungs- und
Klausurthemen aus der Aufgabenliste abgedeckt werden. Ordne jedes davon einem
Foliensatz und einem Lernblatt-Thema zu. Fehlt ein passendes Folienthema, baue einen
klar beschrifteten Prüfungs- und Übungsergänzungsblock. Der Abschnitt `## Optional`
und der Abschnitt `wartet auf Nutzerfreigabe` bleiben für reine Folienthemen draußen,
bis der Nutzer eine Zeile hochstuft. Themen mit `★` (eigene Markierung im PDF,
Signal 0) kommen immer rein, und zwar mit dem markierten Ausschnitt als Screenshot:
steht in der Folien-Spalte ein Rechteck (`03 p12 (Kasten 72,200–300,320)`), rendere
genau das statt der ganzen Folie. Übungs- und Klausurmaterial wird als Text,
Beispiel oder annotierte Aufgabe ergänzt, nicht durch eine unmarkierte Folie.

**Prüf, ob `_derived/<Fach>/build/build_lernblatt.py` schon existiert.**

| Fall | Modus |
|---|---|
| kein Build-Skript | **Neu** — Ablauf unten, Skript am Ende dort ablegen |
| Build-Skript da | **Erweitern** — siehe unten |

#### Erweitern (wöchentlich mitwachsen)

Während des Semesters kommt jede Woche Stoff dazu. Dann wird das Lernblatt nicht
neu gebaut, sondern fortgeschrieben.

**Der Quelltext ist das Build-Skript, nicht die `.html`.** Die HTML ist ein
Artefakt — sie zu parsen und Blöcke hineinzuflicken wäre fehleranfällig und würde
bei jedem Lauf anders aussehen. Das Build-Skript dagegen ist linear lesbar, der
Nutzer kann es selbst korrigieren, und ein neuer Lauf erzeugt deterministisch
dieselbe Seite plus die neuen Kapitel.

1. Lies `_derived/<Fach>/build/build_lernblatt.py`. Es zeigt dir, welche Themen schon
   drin sind und in welchem Ton sie geschrieben sind — halt dich daran.
2. Nimm aus der Themenliste die Zeilen mit `Δ = neu` und die, deren Rang gestiegen
   ist. Nur für diese Schritt 2 und 3 laufen lassen (rendern, annotieren). Die
   alten PNGs liegen noch in `<Ausgabeordner>/bilder/` und werden nicht neu
   gerendert.
3. Häng die neuen Kapitel-Blöcke **an der richtigen Stelle** ins Build-Skript —
   die Reihenfolge folgt der Vorlesung, ein Deck aus Woche 9 kommt hinter Woche 8,
   nicht ans Ende.
4. Ist ein Rang gestiegen, kann ein Thema mehr Platz brauchen (aus einem Bullet
   wird ein Screenshot mit Rechenbeispiel). Ersetz den alten Block, statt einen
   zweiten daneben zu setzen.
5. Skript laufen lassen. Die `.html` wird komplett neu geschrieben.
6. Sag dem Nutzer, was dazugekommen ist: welche Kapitel, wie viele Screenshots,
   wie lang die Seite jetzt ist.

### 1b. Ist das Deck markiert? Dann führt die Markierung, nicht der Screenshot

Prüf `_derived/<Fach>/cache/markierungen.md` (erzeugt in Stufe 1 von `annots.py`). Hat das
Deck Markierungen, **lies `docs/markierungen.md`** — dort steht der vollständige
Vertrag. Kurzfassung mit dem, was du beim Bauen tust:

| Markierung | Was du baust |
|---|---|
| **Kasten**, `Grafik: 0` | Text abschreiben. `kern`/`para`/`bullet`. **Kein Screenshot.** |
| **Kasten**, kein Text | `pic()` vom `Crop`-Rechteck, nicht von der Folie. |
| **Kasten**, Text steht für sich | Text abschreiben, Grafik separat als `pic()`. |
| **Kasten**, Text beschriftet die Grafik | `pic()` vom Rechteck **`mit Beschriftung`**, Text nicht doppeln. |
| **Textmarker** | `glossar(begriff, "…")` — ein bis zwei Sätze, was es ist. |
| **Notiz** | Anweisung. In Einzelaufträge zerlegen, jeden einzeln abarbeiten. |
| **unmarkierte Seite** | Weglassen. Auch wenn sie gut aussieht. |

**Warum das die Screenshot-Regel schlägt:** ein Folien-Screenshot kostet vier- bis
fünfmal so viel Platz wie derselbe Inhalt als Text und schleppt Titelband, Logo und
Leerraum mit. Der Kasten sagt dir, wo die Substanz sitzt — genau dafür hat der
Nutzer ihn gezogen. Ein Bild ist nur dann die richtige Form, wenn die Aussage **im
Bild** steckt: Diagramm, Baum, Verlauf, strukturierte Tabelle. Eine Aufzählung ist
als Text besser: schärfer im Druck, durchsuchbar, halb so hoch.

Beim Abschreiben gilt der Wortlaut der Folie vollständig und 1:1. Kürze, paraphrasiere
oder glätte ihn nicht still. Erweitere nur mit einer Definition, einer Erklärung oder
einem konkreten Beispiel. Markiere Ergänzungen knapp mit einer eigenen Zeile oder
einem eigenen Label.

Direkt nach jedem `h_topic` steht zuerst genau eine kurze `kern`-Zusammenfassung.
Sie ersetzt keinen Folientext. Begriffe vor einem Doppelpunkt werden fett gesetzt,
und wichtige Schlüsselwörter sowie Kernaussagen werden im Satz zur Leseführung fett
markiert. Eine Unterstreichung bleibt seltenen, besonders merkbaren Ankern
vorbehalten. Markiere nicht ganze Sätze und nicht jedes Fachwort. Auch in Tabellen
sind wichtige Begriffe fett. Korrekte deutsche Umlaute und Grammatik sind Pflicht;
fachübliche englische Begriffe bleiben erhalten.

Verlangt eine Notiz eine Grafik, die es nicht gibt: frage zuerst den Nutzer, wenn die
Notiz nach einem Beispiel oder einer Grafik fragt. Sagt sie ausdrücklich „finde“,
recherchiere eine externe Quelle mit nennbarer Herkunft. Erstelle keine eigene SVG,
Skizze oder Tabelle ohne ausdrückliche Nutzerfreigabe.

### 2. Zielfolien wählen + rendern
Pro Thema 1-2 Folien, die es am besten zeigen (Diagramm, Tabelle, Ablauf,
Rechenbeispiel). Bei einem markierten Deck ist die Auswahl schon getroffen: rendere
die Rechtecke aus `markierungen.md`, sonst nichts. **Steht dort `mit Beschriftung`,
nimm das** — es enthält die Grafik plus den Text auf ihrer Höhe. Nur wenn die
Angabe fehlt, ist `Crop` richtig. Immer die **finale**
Animations-Bau-Stufe (`final pN` in
`slide_titles.txt`, dort auch `*` = Folie mit Grafik). Rendern + croppen in einem
Aufruf:
```bash
python .claude/skills/lernblatt-generator/scripts/render_crop.py \
  --pdf "Examples/<Fach>/Vorlesungsfolien/<Deck>.pdf" \
  --pages 11,19,20 --out "<Ausgabeordner>/bilder" --prefix VLxx
```
Der Crop kommt aus der PDF-Geometrie, nicht aus festen Prozentwerten: Titelband,
Seitenzahl, Vollflächen-Hintergrund und Layout-Weiß fallen automatisch weg. Das
ist der wichtigste Qualitäts-Hebel — sonst steht der Folien-Titel doppelt zur
eigenen Überschrift. Rendere ohne PDF-Annotationsebene, damit rote Arbeitskästen
und Textmarker nicht als Lerninhalt erscheinen.

**Text, der im verwendeten Grafik-Crop steht, bleibt im Bild und wird nicht zusätzlich
als HTML abgeschrieben.** Beschriftungen, Legenden, Aufgabenzeilen und Formeln im
Crop gehören zur Darstellung. Setze davor nur die kurze `kern`-Zusammenfassung.
Text außerhalb des Crops wird vollständig als HTML übernommen. Nimm im Zweifel den
ganzen markierten Kasten statt einer engen Grafik-Hülle. Nur Folien-Chrome fällt weg.

**Jeder Ausschnitt muss allein verständlich sein.** Frag dich: versteht das jemand,
der die Folie nicht daneben liegen hat? Keine Formel ohne ihren Satz, kein
angefangener Satz, keine halbe Legende, kein reiner Text als Bild. Die fünf belegten
Fehlschnitte samt Gegenmaßnahmen stehen in `docs/bild-zuschnitt.md`.

**Zwei Prüfungen, beide Pflicht:**
- `render_crop.py` meldet beim Rendern `WARN Textblock nur zu 26% drin: '…'`, wenn
  das Rechteck einen Textblock durchtrennt. Das ist Geometrie aus dem PDF, keine
  Schätzung — kommt so eine Zeile, ist der Ausschnitt falsch. Rechteck um den
  ganzen Block ziehen und neu rendern.
- Am Ende einmal über den Ordner:
  ```bash
  python .claude/skills/lernblatt-generator/scripts/check_crops.py "<Ausgabeordner>/bilder"
  ```
  Findet leere, winzige und schlitzförmige Bilder in einer Sekunde. Ein Befund
  heißt hinsehen, nicht löschen.

Die Ausgabe nennt je Bild `anteil=0.58` — den Breitenanteil auf der Folie. Gib ihn
an `pic(anteil=…)` weiter, dann ist das Bild im Blatt so breit wie in der Vorlesung.
Der Wert ist exakt `Crop-Breite / Original-Folienbreite`, nicht die Bildgröße im
HTML.
Auf volle Spaltenbreite aufgeblasen wirkt eine Randgrafik wichtiger als sie ist und
frisst eine halbe Seite.

Flags:
- `--rect x0,y0,x1,y1` — **feste Box statt Auto-Crop.** Genau hierhin gehört das
  `Crop`-Rechteck aus `markierungen.md`. Der Auto-Crop würde die Ansage des Nutzers
  überschreiben, deshalb ist `--rect` bei markierten Folien der Normalweg.
- `--figuren` — **je Diagramm/Tabelle/Bild ein eigenes PNG** statt einem Bild je
  Folie. Nimm das, wenn nur das Diagramm ins Lernblatt soll und die Bullets der
  Folie nicht. Dateiname trägt die Art: `VL03-10-1_vektor.png`.
- `--tol` — nur mit `--figuren`: Zusammenfass-Abstand der Vektorpfade
  (Default 25). Zerfällt ein Diagramm in Teile → erhöhen. Verschmelzen zwei
  getrennte Diagramme → senken.
- `--keep-title` — Titelband behalten (z.B. wenn es Teil der Aussage ist).
- `--full` — gar nicht croppen, ganze Folienseite.
- `--top/--bottom/--left/--right` — manuelle Nachkorrektur in Anteilen der
  Auto-Box. **Kalibrierungsknopf** für Sonderfälle (Wasserzeichen, Fußzeile).

Arten bei `--figuren`: `tabelle`, `raster`, `vektor`. Mehr klassifiziert PyMuPDF
nicht. Abdeckung gemessen: CyberSec 52 % der Folien, DS 1 68 %, POIS 62 %.

Steht Inhalt **neben** dem Titel, lässt der sich nicht rechteckig wegschneiden —
das Skript meldet `ACHTUNG Titel bleibt im Bild` und behält ihn ganz.

### 3. Rechenbeispiele annotieren (Klausur-Aufgabentypen)
Für jeden Klausur-Aufgabentyp aus der Themenliste ein Beispiel mit **eingetragener
Lösung** — wie im Beispiel-Lernblatt. Lösungswerte aus der Klausur-Zusammenfassung
nehmen und **selbst mathematisch prüfen** (Ground Truth). Dann in den Screenshot
schreiben:
```bash
python .claude/skills/lernblatt-generator/scripts/annotate.py \
  --img "<Ausgabeordner>/bilder/VLxx-17.png" \
  --out "<Ausgabeordner>/bilder/VLxx-17_annot.png" \
  --ann '[{"type":"text","x":985,"y":625,"val":"2","color":"red"},
          {"type":"box","x0":840,"y0":600,"x1":1140,"y1":660,"color":"red"}]'
```
Koordinaten sind Pixel im (getrimmten) Bild. Erst das Bild ansehen, um Zellen/
Stellen zu finden, dann annotieren und das Ergebnis einmal gegenprüfen.

### 4. HTML bauen mit dem Helfer
Nutze `LernblattHTML` statt HTML von Hand — die Klasse kodiert das Layout (Farben,
Größen, Abstände, A4-Marker, Druck-CSS). Vollständige Spez: `docs/html-style-guide.md`.

Das Build-Skript gehört nach **`_derived/<Fach>/build/build_lernblatt.py`** und bleibt
dort liegen. Es ist der Quelltext des Lernblatts: nächste Woche wird es ergänzt und
neu ausgeführt, statt die HTML anzufassen. Gliedere es mit Kommentar-Zeilen je
Vorlesung (`# --- Deck 07: OpenRefine`), damit die Einfügestelle beim Erweitern
ohne Suchen zu finden ist.

```python
import sys; sys.path.insert(0, ".claude/skills/lernblatt-generator/scripts")
from lernblatt_html import LernblattHTML
lb = LernblattHTML("Lernblatt <Fach>", img_dir="<Ausgabeordner>/bilder")
lb.h_deck("03 LOD2 SPARQL")                 # Foliensatz-Trenner
lb.h_topic("RDF als Grundlage")             # Folientitel 1:1
lb.kern("RDF beschreibt Daten als Tripel Subjekt – Prädikat – Objekt.")
lb.formel("<mrow><mi>x</mi><mo>=</mo><mn>1</mn></mrow>", "x gleich 1")
lb.sublabel("RDF-Datenmodell:")
lb.glossar("resource", "alles Benennbare, per URI identifiziert.")
lb.bullet("offenes Format (CSV statt Excel).", color="red")
lb.pic("VL03-11.png", anteil=0.62)          # so breit wie auf der Folie
lb.tabelle(["Verfahren", "Paradigma"], [["Klassifikation", "überwacht"]])
lb.akzent("Klausur-Aufgabe: ...")
lb.save("Examples/<Fach>/Lernblaetter/Lernblatt_<Fach>.html")
```
Bau das Skript mit **relativen Pfaden ab Projektwurzel** wie oben, sonst bricht der
Lauf nächste Woche an einem anderen Arbeitsverzeichnis.

Methoden: `h_deck`, `h_topic`, `kern`, `sublabel`, `para`, `formel(mathml,aria)`,
`glossar(term,def)`, `bullet(text,color="red")`, `akzent`, `tabelle(kopf,zeilen)`, `img_tag` (Bild in
einer Tabellenzelle), `raw` (inline-SVG), `pic(fname,anteil=,width=,hinweis=)`,
`save`. Aufeinanderfolgende `glossar`/`bullet` werden zu einem `<ul>`.

**Drei Regeln, die das Blatt kurz halten:**
- **Überschrift = Folientitel 1:1.** Der Nutzer sucht damit die Folie wieder.
- **Keine Quellenangaben.** Zitat, Auflage, Seitenzahl aus den Folien fallen weg.
  Nur eine Grafik, die nicht von den Folien stammt, bekommt via `hinweis=` einen
  Halbsatz zur Herkunft — einen Halbsatz, keine Erklärung.
- **Formeln als MathML mit eingesetztem Beispiel.** Nutze für HTML-Formeln
  `formel()` statt Plaintext oder sichtbarem LaTeX-Quelltext. Direkt darunter steht
  die Formel mit echten Zahlen aus der Vorlesung. Abstrakte Notation prüft niemand nach.
- **Gesamtstil:** kleine Zeilen- und Absatzabstände, fett gesetzte Lernanker und
  Schlüsselwörter als Leseführung, seltene Unterstreichungen sowie korrekte
  Umlaute. Jedes Klausur- und Übungsthema erscheint im Lernblatt. Ergänze es im
  passenden Foliensatz mit Definition, Aufgabenform, Beispiel und geprüfter Lösung.
  Fehlt ein passendes Folienthema, nutze einen klar markierten Prüfungs- und
  Übungsergänzungsblock. Hole dafür keine unmarkierte Folienseite zurück.

**Du darfst eigene Struktur-Elemente bauen** — eine Vergleichstabelle, eine
Gegenüberstellung, eine Zuordnung —, wenn die Folien eine Struktur tragen, die sie
selbst nicht zeigen. Drei Verfahren, die über vier Folien verstreut zu Paradigmen
gehören, gehören in eine Tabelle: dann sieht man die Zuordnung in zwei Sekunden.
Bedingung: kein neuer Inhalt, es muss Platz oder Zeit sparen, und Ergänztes wird in
einem Halbsatz markiert. Details in `docs/style-guide.md`.

### 5. Abdeckungs- und Sichtprüfung
Vor dem Bildcheck muss jedes Klausur- und Übungsthema einen Einbauort im
Build-Skript haben. Prüfe dafür die Abdeckungsliste mit Quelle, Thema, Foliensatz
oder Ergänzungsblock, Aufgabentyp und Beispiel oder Lösung. Erst danach
`check_crops.py` über den Bilder-Ordner laufen lassen und das HTML im Browser öffnen
oder als headless-Screenshot prüfen. Prüfen:
- beginnt jeder Topic-Block mit einer Zusammenfassung?
- ist der Folientext vollständig, sind Labels und Tabellenbegriffe fett und sind
  die zentralen Schlüsselwörter beim Überfliegen sichtbar hervorgehoben?
- wiederholt kein HTML-Text den Inhalt eines Bildes?
- sind Formeln MathML und sind Zeilenabstände kompakt?
- ist jedes Klausur- und Übungsthema im Lernblatt sichtbar vertreten?
- sitzen die Crops, ist ein Bild zu groß geraten, schneidet ein Crop Beschriftung ab?

Eine `.html` pro Fach, Reihenfolge folgt der Vorlesung, alles in dasselbe
`LernblattHTML`-Objekt → ein durchgehender Scroll. Oben rechts öffnet **A4** den
Druckdialog. Dort ist „Als PDF speichern" das Ziel. Eine zusammenhängende Endlosseite
wird nicht angeboten.

## Token-Hygiene
- **Lies die erzeugte `.html` nie.** Sie ist ein Artefakt. Zum Prüfen screenshotten
  oder das Build-Skript lesen — das ist der Quelltext und ein Zehntel so groß.
- **Bilder werden verlinkt, nicht eingebettet.** `save()` schreibt relative Pfade
  nach `bilder/`; die Datei bleibt bei ~13 KB statt 631 KB. `save(bundle=True)`
  erzeugt die Ein-Datei-Fassung zum Verschicken — die dann auch niemand mehr öffnet
  außer einem Browser.
- **Rendere nach `<Ausgabeordner>/bilder/`**, nicht nach `_derived`. Die Bilder
  gehören zum Artefakt und ziehen mit ihm um.
- Für die Sichtprüfung reicht ein Screenshot bei reduzierter Größe. Ein
  Vollseiten-PNG eines fünfseitigen Blatts ist ein spürbarer Posten pro Lauf.

## Toolchain & Gotchas
- **PyMuPDF** für Text, Geometrie und Rendern — `slides.py` kapselt das. `pillow`
  für `annotate.py` und `check_crops.py`. Selbsttests: `slides.py --selftest`,
  `check_crops.py --selftest`, `lernblatt_html.py`.
- **PowerShell-Variablen überleben nicht** zwischen Aufrufen → je Skript alles in
  einem Lauf.
- **Formeln:** Als HTML-Text mit `formel()` in nativem MathML setzen. Gehört die
  Formel untrennbar zu einer markierten Grafik, bleibt sie im Folien-Crop. Kein
  sichtbarer LaTeX-Quelltext und keine MathJax- oder KaTeX-Abhängigkeit.
- **Token-Bewusstsein:** je Vorlesung einzeln arbeiten, Bilder lokal halten. Beim
  Erweitern nur die neuen Decks rendern.
- **`build_lernblatt.py` nie wegwerfen.** Es ist der Quelltext des Lernblatts; die
  `.html` lässt sich daraus jederzeit neu erzeugen, umgekehrt nicht. Schreib die
  benutzten `--rect`-Werte als Kommentar hinein, sonst weiß nächste Woche niemand
  mehr, welcher Ausschnitt gerendert wurde.
- Referenz-Output mit Markierungen: `Vorlesungen/GenAi/Lernblaetter/
  Lernblatt_GenAi.html` + `_derived/GenAi/build/build_lernblatt.py`.
