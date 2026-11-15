# Markierungen im PDF — was sie bedeuten

Der Nutzer arbeitet laufende Vorlesungen im PDF durch und hinterlässt dabei
Markierungen. Sie sind **das stärkste Signal im ganzen Projekt**: sie kommen von
einem Menschen, der in der Vorlesung saß, und nicht aus einer Wortzählung.
Klausur, Übung und Kopplungs-Graph stehen dahinter.

Gelesen werden sie mit
`.claude/skills/themen-analyse/scripts/annots.py "<Fach>"` → `_derived/<Fach>/cache/markierungen.md`.
`pdf-inspector` sieht sie **nicht** — sie liegen in der Annotations-Ebene des PDFs,
nicht im Text.

Beide Skills lesen diese Datei: `themen-analyse` macht daraus Themen und Ränge,
`lernblatt-generator` macht daraus Absätze und Screenshots.

## Die vier Regeln

### 1. Kasten (Square, Circle, Polygon, Ink) — der Inhalt kommt rein

Was der Kasten umschließt, gehört ins Lernblatt. **Wie** es reinkommt, hängt davon
ab, was drin ist. `annots.py` sagt es dir mit `Grafik: N`:

| Im Kasten | Was du tust |
|---|---|
| nur Text (`Grafik: 0`) | Text **abschreiben**. Kein Screenshot. |
| nur Grafik (kein Text) | Screenshot vom `Crop`-Rechteck. |
| beides, Text steht für sich | Text abschreiben, Grafik separat als Screenshot. |
| beides, Text **beschriftet** die Grafik | Screenshot vom Rechteck `mit Beschriftung`, Text nicht doppeln. |
| leer (kein Text, `Grafik: 0`) | Eigene Handzeichnung. Gehört zur Notiz daneben, kein Folieninhalt. |

**Die vierte Zeile ist die, die man übersieht — deshalb rechnet das Skript sie
aus.** `Crop` ist die enge Hülle um die gezeichneten Elemente: richtig, wenn die
Grafik für sich steht, falsch, wenn Text Teil der Darstellung ist. Für den zweiten
Fall gibt `annots.py` ein drittes Rechteck aus:

```
Kasten (rot) · Rechteck (19, 47, 586, 492) · Grafik: 2,
  Crop (19, 111, 139, 485), **mit Beschriftung (22, 111, 581, 485)**
```

**Steht `mit Beschriftung` da, ist das der Ausschnitt.** Es enthält die Grafik plus
jeden Textblock, der im Kasten liegt und sich mit der Grafik **auf derselben Höhe**
befindet — also genau die Beschriftungen. Ein Absatz über oder unter der Grafik
überlappt nicht, bleibt draußen und wird abgeschrieben; der Folientitel ebenso.

Beleg GenAi Deck 02, S. 14 (k-means): Bildspalte y 111–485, die vier Schritt-Texte
y 136–464 → überlappen, kommen mit. Titel y 42–75 → bleibt draußen. Ohne diese
Regel entstand ein 251 × 780 px schmales Bild mit vier bunten Kästchen ohne
Aussage.

Die vollständigen Zuschnitt-Regeln samt der sechs belegten Fehlschnitte stehen in
`docs/bild-zuschnitt.md` — **lies sie, bevor du den ersten Ausschnitt renderst.**

**Warum nicht einfach die Folie screenshotten?** Weil ein Screenshot der ganzen
Folie das Vier- bis Fünffache an Platz kostet und dabei Titelband, Logo, Fußzeile
und Leerraum mitschleppt. Der Kasten ist die Ansage des Nutzers, wo die Substanz
sitzt. Text als Text ist kompakter, druckt schärfer und lässt sich durchsuchen —
ein Screenshot ist nur dann die richtige Form, wenn die Aussage **im Bild** steckt
(Diagramm, Baum, Verlauf, Tabelle mit Struktur).

**Der vollständige Folienwortlaut bleibt erhalten.** Kürze oder paraphrasiere nicht.
Steht Text bereits im verwendeten Crop, schreibe ihn nicht zusätzlich als HTML ab.
Die kurze Zusammenfassung vor dem Crop bleibt erlaubt.

**Text darf leicht erweitert werden, aber nur aus zwei Gründen:**
- Der Folientext nennt einen Begriff, der **noch nicht definiert** wurde und aus
  sich heraus nicht schlüssig ist. Dann ein knapper Halbsatz dazu.
- Eine **einfachere Erklärung** trifft dieselbe Aussage besser als der Folien-Satz.
  Dann umformulieren statt anhängen.

Sonst gilt der Wortlaut der Folie. Der Nutzer hat sie markiert, weil **diese**
Formulierung in der Klausur zählt — eigene Prosa daneben verwässert das nur.
Erweiterst du, mach es sichtbar (eigene Zeile, eigenes Label), damit der Nutzer
Folienstoff von Ergänzung unterscheiden kann.

### 2. Textmarker (Highlight, Underline) — diesen Begriff erklären

Ein Textmarker über einem Begriff heißt nicht „übernimm den Satz", sondern
**„erklär mir, was das ist"**. Der Nutzer ist über das Wort gestolpert.

Antwort: **kurz und präzise**, ein bis zwei Sätze. Was es ist, wozu es dient, und
wenn es hilft ein Beispiel in drei Wörtern. Kein Absatz, keine Herleitung — der
Begriff ist ein Baustein, nicht das Thema.

Steht der Begriff auch in einem Kasten, kommt beides: der Kastentext als Inhalt,
die Erklärung als Glossar-Zeile darunter.

### 3. Notiz (FreeText, Haftnotiz, oft rot umrandet) — Anweisung, befolgen

Eigener Text im PDF ist keine Beschreibung, sondern ein **Auftrag an dich**. Lies
ihn wörtlich und arbeite ihn ab, Punkt für Punkt.

Beispiel aus `GenAi/02GrundbegriffeML.pdf`, S. 4 neben den Lernparadigmen:

> „Klassifikation, Regression, Clustering, Zuordnung zu lernparadigmen und
> beispiele und Graphiken"

Das sind vier Aufträge in einem Satz: die drei Verfahren nennen, jedes einem
Lernparadigma zuordnen, je ein Beispiel geben, je eine Grafik dazu. Zerleg eine
Notiz genauso und hak sie einzeln ab, sonst fällt die Hälfte unter den Tisch.

**Verlangt eine Notiz eine Grafik, die es auf den Folien nicht gibt, recherchier
eine.** Das ist ausdrücklich erlaubt und erwartet. Vorgehen:
1. Erst die restlichen Folien des Fachs durchsuchen — oft steht die Grafik zwei
   Vorlesungen später.
2. Sonst extern suchen. Nimm eine Quelle, die man nennen kann (Lehrbuch,
   Uni-Skript, Standard-Referenz), keine beliebige Bildersuche.
3. Kann keine Grafik gefunden werden, **frage den Nutzer**, bevor du eine eigene
   Grafik erstellst. Eine selbst gezeichnete Tabelle, ein Schema oder SVG ist nur
   nach ausdrücklicher Freigabe erlaubt.
4. Kennzeichne jede externe Grafik mit der nennbaren Quelle — **in einem Halbsatz**.
   „Regression: in Deck 02 nicht behandelt, externe Ergänzung." Wer hier drei Zeilen
   begründet, schreibt eine Fußnote, die niemand lernt. Die ausführliche Begründung
   gehört in den Chat.

Verlangt eine Notiz etwas, das in den vorhandenen Folien keine Grundlage hat
(bei GenAi: `Regression` kommt in Deck 02 nicht vor), **sag es dem Nutzer** statt
es zu erfinden oder zu übergehen. Er entscheidet, ob es aus einem späteren Deck
nachkommt oder von außen.

### 4. Nicht markierte Folienseite — bleibt als Folienseite draußen

Hat ein Foliensatz Markierungen, ist das Fehlen einer Markierung weiterhin eine
Aussage: **Diese Folienseite wird nicht als Screenshot und nicht als vollständiger
Folienblock übernommen.**

### 5. Übungs- und Klausurthemen — dauerhaft freigegebene Ergänzung

Übungs- und Klausurthemen sind eine ausdrückliche, dauerhafte Nutzerfreigabe. Jedes
Thema muss in das Lernblatt, auch wenn es auf keiner markierten Folie steht. Übernimm
die Übung oder Klausur aber **nicht 1:1**. Leite daraus die benötigten Grundlagen,
Voraussetzungen, Begriffe und Aufgabenformen ab und erkläre sie in eigener, klarer
Prosa. Ergänze Definitionen, Beispiele und bei Transfer eine geprüfte Lösung.
Schreibe diese Ergänzung als Text oder als annotiertes Aufgabenbild, nicht als
unmarkierten Folien-Screenshot.

Gibt es kein passendes Folienthema, lege einen Abschnitt
`Prüfungs- und Übungsergänzungen` an. Kennzeichne dort die Quelle und den
Aufgabentyp. Bei besonders wichtigen Themen steht die Erweiterung als klar
markierter Abschnitt **am Ende des zugehörigen Foliensatzes**, direkt vor dem
Übergang zur nächsten Vorlesung. Sie darf die wichtigsten Folienthemen nochmals
zusammenfassen, erweitern, Begriffe definieren und mit Beispielen erklären. Web-
Recherche und passende externe Grafiken sind erlaubt, wenn die Aussagen dadurch
verlässlich gestützt werden. Dieses Verfahren holt keine unmarkierte Vorlesungsseite
zurück, darf aber fehlende prüfungsrelevante Inhalte aus Übungen und Klausuren
aufnehmen.

`annots.py` listet die unmarkierten Seiten mit Wortzahl und Grafikzahl am Ende
jedes Deck-Abschnitts, damit du siehst, was du als Folieninhalt weglässt.

**Ein Deck ganz ohne Markierungen ist etwas anderes.** Dort ist der Nutzer noch
nicht durch. Es fällt zurück auf die normale Bewertung über Klausur, Übung und
Graph — nicht auf „alles weglassen".

### 6. Vollständigkeitsprüfung
Vor dem Build muss jede Übungs- und Klausuraufgabe in einer Abdeckungsliste stehen:
Quelle, Thema, passender Foliensatz oder Ergänzungsblock, Einbauort, Aufgabentyp
und Beispiel oder Lösung. Ein Thema in `analysis_pruefung.md` ohne Einbauort ist
ein Build-Fehler.

## Was `annots.py` liefert

Je Markierung: Seite, Rolle (Kasten/Textmarker/Notiz), Farbe, Rechteck, der Text im
Wortlaut, die Zahl der Grafik-Elemente und das `Crop`-Rechteck um genau diese
Grafik.

Zwei Dinge, die das Skript für dich löst und die du nicht nachprüfen musst:
- **Master-Elemente sind rausgerechnet.** Fußzeile, Logo und Titelstrich sind auf
  jeder Folie dieselben Vektorpfade (bei GenAi rund 72 pro Seite). Ohne diesen
  Filter hätte jeder Kasten „Grafik" gemeldet.
- **Der Kastenrahmen zählt sich nicht selbst.** Er ist auch nur ein Vektorpfad.

Drei Rechtecke je Kasten, und die Reihenfolge ist die Rangfolge:
1. **`mit Beschriftung`** — Grafik plus Text auf ihrer Höhe, 3 pt innerhalb des
   Rahmens. Nimm dieses, wenn es da steht.
2. **`Crop`** — nur die Grafik. Nimm dieses, wenn kein `mit Beschriftung` da ist.
3. **`Rechteck`** — der ganze Kasten. Nur, wenn du beides begründet verwirfst.
