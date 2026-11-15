# Style Guide — Lernblätter

Fachunabhängige Spezifikation des **inhaltlichen** Stils. Basis: die drei eigenen
Beispiel-Lernblätter (CyberSec 42 S., Datascience 1 30 S., POIS 35 S.). Der
Generator lädt diese Datei statt der Beispiel-PDFs. Layout: `html-style-guide.md`.
Markierte Folien: `markierungen.md`. Bildausschnitte: `bild-zuschnitt.md`.

## 1. Grundprinzip
Lernblatt = strukturierte, lesbare Aufbereitung der Vorlesungsfolien, Ground Truth
sind die Folien. Folientext bleibt inhaltlich und sprachlich vollständig erhalten,
aber steht als klar gegliederter Text, Liste, Tabelle oder Folien-Crop statt als
ungeordneter Fließtext.

**Zwei Betriebsarten, je nachdem ob der Nutzer das Deck markiert hat:**

| | unmarkiertes Deck | markiertes Deck |
|---|---|---|
| Auswahl | du, nach der Themenliste | die Kästen des Nutzers |
| Form | screenshot-lastig, ~1/8 der Folien | Text trägt, Bild nur wo die Aussage im Bild steckt |

Bei markierten Decks gilt `markierungen.md`, nicht Abschnitt 5 hier.

## 2. Dichte
Gemessen: POIS 1/8, DS 1/14, CyberSec 1/16 der bereinigten Folien. Richtwert 1/8.
Spätere Kapitel dürfen textdichter sein als frühe.

## 3. Überschriften
- **Foliensatz-Trenner:** der Name des Foliensatzes, sonst nichts. Kein Dozent,
  keine Quelle, kein „Ground Truth"-Zusatz.
- **Themen-Überschrift: der Folientitel 1:1.** Nicht umformulieren, nicht kürzen,
  nicht zusammenfassen. Der Nutzer sucht damit die Folie wieder, und eine eigene
  Überschrift zerstört genau das. Erfinde nur dort einen Titel, wo die Folie keinen
  hat.
- Direkt darunter steht als erster Inhalt eine **fett-schwarze Kernaussage**:
  eine kurze Zusammenfassung des Folienthemas. Sie ersetzt keinen Folientext.
- **Rot** ist der Akzent — Klausur-Hinweis, Ergebniszeile, Merksatz. Sparsam.
- Jeder `h_topic`-Block beginnt mit genau dieser Zusammenfassung, bevor weitere
  Textbausteine, Tabellen oder Bilder folgen.

## 4. Text-Bausteine
- **Begriff/Definition:** Bullet mit **fettem Begriff**, die Erklärung umgebrochen
  in die Zeile darunter, noch eine Stufe eingerückt. Das Arbeitspferd des Blatts.
  Der Punkt bleibt am Begriff — so bildet die linke Kante eine Spalte aus Begriffen,
  die man senkrecht abscannen kann, statt sie aus Fließtext herauszusuchen.
- **Listen rücken als Ganzes ein**, Punkt und Text rechts vom Label darüber. Auf
  gleicher Höhe verschwimmt die Gliederung: man sieht nicht mehr, welche Punkte zu
  welcher Überschrift gehören.
- **Bullets:** Hauptpunkte. Aufzählungen aus den Folien bleiben Aufzählungen.
- **Labels:** Der Begriff vor einem Doppelpunkt wird fett gesetzt, etwa
  **Aufgabe:**, **Performanz-Maß:** oder **Training:**.
- **Schlüsselwörter:** Wichtige Begriffe und Kernaussagen werden im Satz mit
  **Fettdruck** oder, sparsam bei besonderer Merkwürdigkeit, mit <u>Unterstreichung</u>
  ausgezeichnet. Die Hervorhebung dient der Leseführung: Beim Überfliegen muss das
  zentrale Keyword eines Absatzes oder Stichpunkts sofort sichtbar sein. Markiere
  nicht ganze Sätze und nicht jedes Fachwort, sondern nur den inhaltlichen Anker.
  Bei Stichpunkten steht das entscheidende Keyword möglichst am Anfang.
- **Tabellen:** Die erste Spalte und alle wichtigen Begriffe werden fett gesetzt.
- **Beispiel:** konkrete Mini-Szenarien (Krankenhaus, Alice/Bob/Eve). Fehlt ein
  Beispiel in der Quelle, darf eine kurze, klar als Ergänzung erkennbare Tabelle
  oder Beispielzeile hinzukommen.
- **Texttreue:** Nicht kürzen, paraphrasieren oder still korrigieren. Erweitere nur
  mit einer Definition, einer Erklärung oder einem Beispiel.
- **Nummerierte Sequenz** für Abläufe und Phasen.
- **Vier-Felder-Schema** für Mechanismen und Angriffe: Erklärung / Ziel / Schwächen
  / Attacke.

### Keine Quellenangaben
Zitate, Auflagen und Seitenzahlen aus den Folien nicht übernehmen. Sie kosten eine
Zeile und helfen in der Klausur nicht. Ausnahme: eine Grafik, die **nicht** von den
Folien stammt — die braucht einen Halbsatz zur Herkunft.

### Folientext und Bildtext
Text, der im verwendeten Folien-Crop lesbar enthalten ist, wird nicht nochmals als
HTML abgeschrieben. Der Crop trägt diesen Inhalt. Ein kurzer `kern`-Satz davor ist
weiterhin Pflicht. Text außerhalb des Crops bleibt vollständig als HTML erhalten.

### Formeln als MathML setzen und konkret erklären
Eine Formel im HTML wird mit `LernblattHTML.formel()` als natives MathML gesetzt.
Schreibe sie nicht als Plaintext oder sichtbaren LaTeX-Quelltext. MathML bleibt
offline, druckt scharf und braucht weder MathJax noch KaTeX. Gehört eine Formel
untrennbar zu einer markierten Grafik, bleibt sie stattdessen im Folien-Crop.

Direkt unter der Formel steht ein ausgerechnetes Beispiel mit echten Zahlen aus der
Vorlesung. Abstrakte Notation prüft niemand nach, ein eingesetztes Beispiel sitzt
sofort.

> D = { (x₁, y₁), …, (xₙ, yₙ) }
> x = (Umsatz 2, Bezahlverzug 2) → y = *hoch*
> x = (Umsatz 5, Bezahlverzug 0) → y = *sehr hoch*

Nimm die Zahlen aus dem Beispiel, das die Vorlesung ohnehin benutzt. Ein zweiter,
eigener Datensatz zwingt den Nutzer, zwei Beispiele im Kopf zu halten.

### Eigene Struktur-Elemente sind erwünscht
Du darfst und sollst etwas hinzufügen, das die Folien nicht haben, wenn es das Blatt
messbar besser macht — eine Vergleichstabelle, eine Gegenüberstellung, eine
Zuordnung, eine nummerierte Kurzfassung.

Der Auslöser ist immer derselbe: **die Folien tragen eine Struktur, die sie selbst
nicht zeigt.** Drei Verfahren, die über vier Folien verstreut zu Paradigmen gehören,
gehören in eine Tabelle mit vier Spalten — dann sieht man die Zuordnung in zwei
Sekunden statt sie sich zusammenzusuchen. Zwei Konzepte, die sich in genau einem
Punkt unterscheiden, gehören nebeneinander.

Drei Bedingungen:
- **Kein neuer Inhalt.** Ordne um, was in den Folien steht. Fehlt eine Zelle, lass
  sie leer oder sag es dem Nutzer — füll sie nicht mit Vermutung.
- **Es muss Platz sparen oder Zeit sparen.** Eine Tabelle, die genauso lang ist wie
  der Fließtext, ist nur anders formatiert.
- **Ergänztes markieren, in einem Halbsatz.** „Regression: in Deck 02 nicht
  behandelt, ergänzt." Mehr nicht — eine Begründung, die drei Zeilen braucht,
  gehört in den Chat, nicht aufs Blatt.

## 5. Screenshots (unmarkierte Decks)
- Pro Thema die Folie(n), die es am besten zeigen: Diagramme, Tabellen, Abläufe,
  Rechenbeispiele. Ein bis zwei je Thema.
- **Finale Bau-Stufe** einer Animations-Folge.
- **Größe wie auf der Folie.** Ein Bild, das ein Drittel der Folienbreite einnahm,
  bekommt auch im Blatt ein Drittel. Auf volle Spaltenbreite aufgeblasen wirkt eine
  Randgrafik wichtiger als sie ist und frisst eine halbe Seite. `render_crop.py`
  gibt den Breitenanteil aus, `pic(anteil=…)` nimmt ihn.
- **Text, der zur Grafik gehört, bleibt drin** und wird nicht zusätzlich
  abgeschrieben. Beschriftungen neben den Bildstufen, die Anfragezeile über einem
  Baum, die Legende unter einem Diagramm — das ist Teil der Darstellung.
  Wegschneiden macht das Bild unverständlich, Abschreiben zerreißt die Zuordnung
  zwischen Text und Bildstelle. Nur Folien-Chrome fällt weg.
- **Jeder Ausschnitt ist eine abgeschlossene Aussage.** Keine Formel ohne ihren
  Satz, kein angefangener Satz, keine halbe Legende, kein reiner Text als Bild.
  Regeln, Belege und die zwei Prüfskripte: `bild-zuschnitt.md`.
- **Annotieren:** Rechenbeispiele mit eingetragener Lösung, wichtige Stellen mit
  Kasten oder Unterstreichung.

## 6. Ton
Deutsch, präzise, verdichtet. Englische Fachbegriffe bleiben englisch. Knappe volle
Sätze. Kein Füllwort, keine Meta-Kommentare.

## 7. Dichte und Sprache
Zeilen- und Absatzabstände bleiben eng, damit das Blatt scanbar bleibt. Schreibe
korrektes Deutsch mit Umlauten. Nutze englische Fachbegriffe, wenn sie auf der
Folie stehen oder fachlich üblich sind.

Übungs- und Klausurthemen sind Pflichtquellen, aber keine Textvorlage. Übernimm
Übungen und Klausuren nicht 1:1. Leite daraus die benötigten Grundlagen,
Voraussetzungen, Begriffe und Aufgabenformen ab und erkläre sie in eigener Prosa.
Ordne jedes Thema dem passenden Foliensatz und Lernblatt-Thema zu und ergänze dort
Definitionen, Beispiele und bei Transfer eine geprüfte Lösung. Fehlt ein passendes
Folienthema, erstelle einen klar markierten Prüfungs- und Übungsergänzungsblock.
Eine unmarkierte Folienseite eines markierten Decks wird dadurch nicht als
Screenshot zurückgeholt.

## 8. Erweiterungen für besonders wichtige Themen
Markiert die Themenanalyse ein Thema als besonders wichtig, folgt am Ende des
zugehörigen Foliensatzes ein sichtbarer Abschnitt **„Erweiterung: …“**, direkt vor
dem nächsten Foliensatz. Dieser Abschnitt ist kein neuer Folieninhalt. Er darf die
wichtigsten Folienthemen nochmals zusammenfassen, Voraussetzungen erklären,
Definitionen ergänzen und mit Beispielen oder Transferaufgaben vertiefen.
Kennzeichne den Abschnitt und jede eigene Ergänzung deutlich. Nutze bei Bedarf
Web-Recherche zur fachlichen Prüfung und nenne die Quelle bei externen Grafiken.

## 9. Abdeckungsprüfung
Vor dem Build muss eine Abdeckungsliste vorliegen. Sie enthält für jedes Übungs-
und Klausurthema den Foliensatz, den Einbauort, die abgeleiteten Voraussetzungen,
die Quelle und den Aufgabentyp. Kein Thema darf nur in `analysis_pruefung.md`
stehen und im HTML fehlen. Der Build ist erst abgeschlossen, wenn diese Liste und
alle markierten Erweiterungsabschnitte ohne Lücken vorhanden sind.

## 10. Nicht-Ziele
Keine erfundenen Fakten und keine stille Umdeutung von Folientext. Die
Beispiel-Lernblätter sind **Stil-Referenz, nicht inhaltlich maßgeblich**; sie haben
belegte Lücken.
