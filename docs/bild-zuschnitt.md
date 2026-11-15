# Bild-Zuschnitt — welcher Ausschnitt ins Lernblatt kommt

Gilt für jeden Screenshot aus einer Folie, ob der Ausschnitt aus einer eigenen
Markierung kommt (`markierungen.md`) oder du ihn selbst wählst.

Der Zuschnitt entscheidet, ob ein Bild beim Lernen etwas nützt. Ein zu enger
Ausschnitt ist schlimmer als gar keiner: er sieht aus, als wäre er vollständig,
und man merkt erst vor der Klausur, dass die Aussage fehlt.

## Die Grundregel: der Ausschnitt ist eine abgeschlossene Aussage

Frag dich vor jedem Crop: **versteht jemand dieses Bild, der die Folie nicht
daneben liegen hat?** Wenn nein, ist der Ausschnitt zu eng.

Eine Formel ohne ihren Satz ist keine abgeschlossene Aussage. Eine Legende ohne
das Diagramm, zu dem sie gehört, auch nicht. Ein Diagramm ohne seine
Achsenbeschriftung auch nicht.

## Text, der zur Grafik gehört, kommt mit ins Bild

Das ist der wichtigste Punkt und die häufigste Fehlerquelle.

Wenn eine Bounding Box **Text und Grafik** enthält, die **nah beieinander** stehen,
dann gehört der Text zur Grafik. Er wird **mitfotografiert, nicht abgeschrieben**.

Warum nicht abschreiben: der Text steht auf der Folie an einer bestimmten Stelle —
neben der dritten Bildstufe, über dem linken Ast, unter der Kurve. Diese Zuordnung
ist die halbe Information. Reißt man den Text heraus und setzt ihn als Fließtext
daneben, bleibt eine Bildergalerie ohne Beschriftung und ein Absatz ohne Bezug
übrig. Beides ist unbrauchbar, und zusammen brauchen sie mehr Platz als das Bild
allein.

### Die Bedingung ist gerechnet, nicht geschätzt

Du musst nicht abwägen, ob ein Text „dazugehört". `lernblatt annots` entscheidet es an der
Geometrie und gibt das fertige Rechteck aus:

> **Ein Textblock gehört zur Grafik, wenn er im Kasten liegt und sich mit der
> Grafik auf derselben Höhe befindet** (die y-Bereiche überlappen).

Genau das trifft Beschriftungen: die Schrittbeschreibung neben der dritten
Bildstufe, die Achsenbeschriftung neben der Kurve, die Legende neben dem Diagramm.
Ein Absatz **über oder unter** der Grafik überlappt nicht, bleibt draußen und wird
abgeschrieben. Der Folientitel fällt aus demselben Grund heraus.

**Beleg aus einem Testkurs (k-means-Folie):**

| Element | y-Bereich | Überlappt die Bildspalte? |
|---|---|---|
| Bildspalte, vier Stufen | 111–485 | — |
| die vier Schritt-Texte | 136–464 | **ja** → kommen mit |
| Folientitel | 42–75 | nein → bleibt draußen |
| Fußzeile | 522–537 | liegt außerhalb des Kastens |

`lernblatt annots` meldet daraus:

```
Kasten (rot) · Rechteck (19, 47, 586, 492) · Grafik: 2,
  Crop (19, 111, 139, 485), **mit Beschriftung (22, 111, 581, 485)**
```

`Crop` ist die nackte Bildspalte — vier bunte Kästchen ohne Aussage.
**`mit Beschriftung` ist der richtige Ausschnitt.** Steht diese Angabe da, nimm
sie; sonst den `Crop`.

Dasselbe auf S. 9 (Entscheidungsbaum): die zwei Anfragen Branic und Schröder
überlappen den Baum auf gleicher Höhe und kommen mit ins Bild — sie sind die
Aufgabe zum Bild, nicht Beiwerk.

### Warum nicht einfach immer den ganzen Kasten?

Weil der Kasten oft mehr umschließt, als ins Bild soll: den Folientitel (steht
schon als Überschrift darüber), einen einleitenden Absatz (gehört als Text ins
Blatt), den Rahmenstrich selbst. `mit Beschriftung` nimmt genau die Beschriftung
mit und hält 3 pt Abstand zum Rahmen — sonst läuft der rote Markierungsstrich ins
Bild, wie in der ersten Fassung von `VL02-14.png` und `VL02-13.png` geschehen.

## Sechs Zuschnitte, die nicht gehen

Alle sechs sind echte Fälle aus dem Bilderordner eines Testkurses.

### 1. Nur der Rahmen der Markierung
`VL05-05_encoder-decoder.png`, 485 × 24 px: ein roter Strich auf Weiß. Der Crop lag
auf der Kante der Bounding Box statt auf ihrem Inhalt.
→ `lernblatt check` meldet das als `LEER`. `lernblatt annots` hält seit dem Fund 3 pt
Abstand zur Kastenkante, damit der Rahmenstrich gar nicht erst mitkommt.

### 2. Grafik ohne ihre Beschriftung
`VL02-14.png` in der ersten Fassung: 251 × 780 px, nur die vier k-means-Bildstufen.
Die Schritt-Texte daneben fehlten, übrig blieben vier bunte Kästchen ohne Aussage.
→ `mit Beschriftung` statt `Crop` nehmen. Richtig sind (22, 111, 581, 485).

### 3. Formel ohne ihren Satz
`VL05-10_softmax-formula.png` (147 × 31 px) zeigt `(u₁, …, u_k)`. Was das ist,
stand im Satz daneben — der fehlt.
Ebenso `VL05-09_rnn-formula.png`, `VL04-9.png`, `VL12-7.png`.
→ Formel **plus** einleitenden Satz croppen, oder die Formel abschreiben und im
Text erklären. Nie die Formel allein als Bild.

### 4. Angefangener Satz
`VL03-5.png` beginnt mit `(x₁, x₂, …, xₙ)` — der Satzanfang liegt außerhalb.
`VL03-9.png` genauso.
→ Ein Ausschnitt beginnt am Anfang einer Zeile und endet am Ende eines Satzes.

### 5. Abgeschnittene Legende
`VL07-9-label.png` endet mitten in `Gelb:` — die vierte Farberklärung fehlt.
→ Eine Legende ist eine Liste. Entweder ganz oder gar nicht.

### 6. Reiner Text als Bild
`VL08-13.png` ist ein gelb markierter Absatz, 1345 × 119 px, ohne jede Grafik.
→ Text mit `Grafik: 0` wird **abgeschrieben**. Als Bild ist er unschärfer, nicht
durchsuchbar und braucht mehr Platz. Siehe `markierungen.md`, Regel 1.

## Wie du es richtig machst

1. **Nimm `mit Beschriftung`, wenn `lernblatt annots` es ausgibt** — das ist die
   Grafik plus den Text auf ihrer Höhe, 3 pt innerhalb des Rahmens. Fehlt die
   Angabe, steht die Grafik für sich: dann `Crop`.
2. **Rande auf Blockgrenzen aus.** `page.get_text("blocks")` liefert die
   Textblöcke einer Folie mit ihren Rechtecken. Ein Crop soll Blöcke ganz
   enthalten oder ganz auslassen.
3. **Rendern und die Warnung lesen:**
   ```bash
   uv run lernblatt crop \
     --pdf "<Deck>.pdf" --pages 10 --rect 30,100,700,280 \
     --out "<Ausgabeordner>/bilder" --prefix VL05
   ```
   Das Skript prüft am PDF, ob das Rechteck einen Textblock oder ein Bild
   durchtrennt, und meldet es:
   ```
   WARN Textblock nur zu 26% drin: 'Softmax-Funktion (normalisierte Exponential…'
   WARN Textblock nur zu 22% drin: 'zur Überführung eines k-dimensionalen Vekt…'
   ```
   Das ist keine Heuristik, sondern Geometrie. Kommt eine solche Zeile, ist der
   Ausschnitt falsch — zieh das Rechteck bis um den Block herum und rendere neu.
4. **Am Ende den Ordner prüfen:**
   ```bash
   uv run lernblatt check "<Ausgabeordner>/bilder"
   ```
   Findet `LEER`, `WINZIG` und `SCHLITZ` in einer Sekunde, ohne dass ein Modell
   die Bilder ansehen muss. Auf den 84 Bildern eines Testkurs-Blatts meldet es 9 — und
   das sind genau die Fehlerarten oben.

## Grenzwerte und warum sie so stehen

| Schwelle | Wert | Begründung |
|---|---|---|
| kleinste Kante | 120 px | darunter ist es ein Fragment. Alle gefundenen Formel-Schnipsel lagen unter 90 px hoch. |
| Seitenverhältnis | 8:1 | ein Streifen ist selten eine abgeschlossene Aussage. `VL07-9-label.png` hat 26:1. |
| Tinte-Ausdehnung | 6 px | dünner ist die Tinte eine Linie, kein Inhalt — der Rahmen-Fall. |
| Block-Überlappung | 2 %–98 % | dazwischen ist ein Block angeschnitten. Außerhalb ist er ganz drin oder ganz draußen. |

Die Werte sind Knöpfe, keine Wahrheiten. Die falsche k-means-Spalte (251 × 780 px)
löste `SCHLITZ` **nicht** aus, weil 3:1 unter der Schwelle liegt — kein Prüfskript
ersetzt die Frage „versteht das jemand ohne die Folie?". **Ein Befund heißt
hinsehen, nicht löschen; kein Befund heißt nicht, dass der Ausschnitt gut ist.**

## Kanten-Prüfung im Bild: nur mit `--streng`

`lernblatt check --streng` meldet zusätzlich Tinte, die in eine Bildkante läuft. Das
ist standardmäßig aus, weil es im Normalbetrieb ständig feuert: mit `--pad 0` sitzt
der Crop exakt am markierten Rechteck, und Inhalt berührt die Kante dann
selbstverständlich. Auf den 84 Bildern eines Testkurses meldete die Prüfung 53 Treffer und war
damit wertlos. Ob wirklich ein Satz zerschnitten wurde, weiß nur das PDF — dafür
gibt es die Warnung in `lernblatt crop`.
