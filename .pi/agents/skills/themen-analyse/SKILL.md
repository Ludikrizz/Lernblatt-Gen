---
name: themen-analyse
description: >-
  Erstellt für ein Studienfach eine kursweite Themen-Relevanz-Liste zur Freigabe,
  bevor Lernblätter gebaut werden. Extrahiert lokal (token-sparsam) die Titel aus
  Vorlesungsfolien, gleicht sie mit Übungen und Klausuren ab und rechnet einen
  Kopplungs-Graph, der zeigt, welche Themen den Prüfungsstoff tragen. Ausgabe: die
  Klausur-Aufgabentypen (Transfer und Wissensabfrage) plus eine Tabelle (Thema |
  Folien | KL | UE | Grad | Rolle | Aufgabentyp | Rang | Empfehlung). Liest auch die
  eigenen Markierungen aus den PDFs (Textmarker, Kästen, Notizen) und behandelt sie
  als stärkstes Signal, und schreibt eine vorhandene Themenliste fort, wenn während
  des Semesters neue Foliensätze oder Übungen dazukommen.
  Nutze diesen Skill immer, wenn der Nutzer für
  ein Fach eine Themenliste, Relevanz-Analyse, Klausur-Schwerpunkte oder eine
  Vorbereitung auf die Lernblatt-Erstellung will, oder wenn er eine bestehende
  Themenliste um neues Kursmaterial erweitern, aktualisieren oder neu bewerten will
  — auch wenn nur ein Fachname oder Vorlesungen/<Fach>-Ordner genannt wird. Dies ist
  Stufe 1 vor `lernblatt-generator`.
---

# Themen-Analyse (Stufe 1)

Zweck: über den **ganzen Kurs** eine Themen-Relevanz-Liste erstellen, die der
Nutzer freigibt. Erstellt KEINE Lernblätter — das macht danach `lernblatt-generator`.

Warum getrennt: Der Nutzer soll die Themen prüfen, streichen und ergänzen, bevor
Aufwand in Screenshots und Text fließt. Die freigegebene Liste ist der Input für
Stufe 2. Details der Entscheidung: `docs/skill-design.md`.

## Kern-Prinzip
Bei markierten Decks bleibt unmarkierter Folieninhalt als Folienseite draußen.
Übungs- und Klausurthemen sind jedoch eine dauerhafte Nutzerfreigabe zur Ergänzung.
Jedes solche Thema muss in die freigegebene Themenliste und später in das Lernblatt.
Ordne es einem passenden Foliensatz und Thema zu oder weise ihm einen klar
beschrifteten Prüfungs- und Übungsergänzungsblock zu. Markiere besonders wichtige
Themen mit `Erweiterung: ja` und notiere die dafür benötigten Grundlagen,
Begriffe, Beispiele und möglichen Web- oder Grafikquellen. Themen kommen aus **Folien +
Übungen + Klausuren**, NICHT aus alten Lernblättern (die sind Stil-Referenz, können
inhaltlich falsch sein). Ground Truth des Folieninhalts = Vorlesungsfolien.
Prüfungsnähe entscheidet den Rang, aber nicht mehr, ob ein belegtes Übungs- oder
Klausurthema aufgenommen wird.

**Fünf Signale, in dieser Reihenfolge:**
0. **Eigene Markierungen im PDF** — Textmarker, Kasten, Notiz, Freihand. Schlägt
   alles andere, weil es von einem Menschen kommt, der die Vorlesung gehört hat,
   und nicht aus einer Zählung. Kommt immer `rein`, ohne Budget-Prüfung. Oft die
   einzige Quelle, solange die Vorlesung noch läuft. Siehe Schritt 2b.
1. **Klausur** — Altklausuren, Probeklausuren, Klausur-Zusammenfassung des
   Dozenten, alles in `Klausuren/`. Stärkstes Signal für die **Form** der Aufgaben,
   nicht für die Themenauswahl. Siehe Schritt 3.
2. **Übung** — was in Übungsaufgaben tatsächlich drankam.
3. **Kopplung** — wie hängt ein Folien-Thema an 1 und 2? Ein Thema, das man zum
   Lösen einer Klausuraufgabe braucht, ist wichtig, auch wenn es selbst nie
   abgefragt wird. Viele Kopplungen = wahrscheinlich wichtiger.
4. **Ausreißer** — schwach gekoppelte Themen, die trotzdem eine gute
   **Wissensabfrage** hergeben (Definition, Auflistung, beschriftete Grafik).
   Nicht streichen, nur weil der Graph sie nicht findet.

**Zwei Aufgabenarten**, die eine Klausur mischt:
- **Transfer** — rechnen, schreiben, modellieren, anwenden. Quelle: Klausur- und
  Übungsaufgaben. Braucht in Stufe 2 ein annotiertes Rechenbeispiel.
- **Wissensabfrage** — Definition nennen, Prinzip erklären, Multiple Choice,
  Auflistung („nenne die 5 X"), Begriffe in eine leere Grafik eintragen. Braucht
  in Stufe 2 die vollständige Liste bzw. die beschriftete Folien-Grafik.

## Umfang ist ein Auswahlkriterium, kein Nebeneffekt
Eine Themenliste, die alles aufnimmt, ist keine Auswahl. Ein Lernblatt, das man
vor der Klausur nicht mehr durchkommt, ist verschenkte Arbeit — deshalb hat die
Liste ein **Budget** und `graph.py` rechnet es aus (Schritt 6).

Das eigene Beispiel-Lernblatt liefert dafür die Referenz. Es entscheidet **nicht**
über den Inhalt (es kann Lücken haben, Ground Truth bleiben die Folien), aber es
sagt sehr genau, welche **Länge** der Nutzer noch lernt. Gemessen an den drei
vorhandenen Blättern liegt die Dichte bei **2,4 bis 3,0 Themen je Blattseite**
(CyberSec 125/42 S., DS1 90/30 S., POIS 84/35 S.) — der Richtwert ist 2,5.

Das Budget ist eine **Orientierung, keine Obergrenze**. Es sagt, wie lang das Blatt
wird — nicht, welches Thema falsch ist. Gekappt wird nur, was ohnehin unten in der
Rangfolge steht, und gekappte Themen bleiben mit voller Zeile in einem eigenen
`optional`-Abschnitt stehen. Die Auswahl trifft am Ende der Nutzer, das Budget gibt
ihm nur die Zahl dazu. Regeln dafür in Schritt 8.

## Ablauf

### 1. Fach-Ordner bestätigen und Modus wählen
Arbeite auf `W:\Studium\Lernen\Vorlesungen\<Fach>\` mit Unterordnern
`Vorlesungsfolien/`, `Uebungen/`, `Klausuren/`. Frag den Fachnamen, falls unklar.
`Examples/<Fach>/` ist nur ein Rückfall für alte Bestände.

**Prüf, ob `_derived/<Fach>/planung/themenliste.md` schon existiert.** Davon hängt ab, wie
du arbeitest:

| Fall | Modus |
|---|---|
| keine Liste da | **Neu** — der Ablauf unten, Schritt für Schritt |
| Liste da, Material dazugekommen | **Fortschreiben** — siehe unten |

#### Fortschreiben (laufende Vorlesung)

Der Normalfall während des Semesters: jede Woche kommen ein Foliensatz und ein
Übungsblatt dazu. Dann ist die alte Liste kein Altpapier, sondern die Vorarbeit —
der Nutzer hat sie schon geprüft und freigegeben, und diese Entscheidungen darfst
du nicht stillschweigend überschreiben.

1. Lauf Schritt 2 und 2b neu. Beide sind billig und lesen alles, was da ist.
2. Lies die **alte** `themenliste.md` ein. Sie ist ab jetzt die Basis.
3. Ergänze `terms.txt` um die Themen aus den neuen Decks. Bestehende Zeilen
   **nicht** anfassen — der Nutzer hat daran gearbeitet.
4. Lauf Schritt 6 (`graph.py`). Der Graph rechnet über **alles** neu, auch über
   alte Themen. Das ist der Punkt: ein Thema aus Woche 2 kann durch die Übung aus
   Woche 9 plötzlich zum Kern werden.
5. Übernimm alte Zeilen mit ihrem Rang, **ändere ihn nur mit Begründung**. Ein Rang,
   den der Nutzer selbst gesetzt hat, bleibt stehen, solange kein neuer Beleg
   dagegen spricht.
6. Markier in der Ausgabe, was sich geändert hat — eine Spalte `Δ` reicht:
   `neu` · `↑ Hoch→Sehr hoch (Übung 9)` · leer für unverändert.

Über die Tabelle kommt ein kurzer Änderungs-Block: welche Decks neu sind, wie viele
Themen dazukamen, welche Ränge sich bewegt haben und warum. Der Nutzer soll die
Liste nicht noch einmal ganz lesen müssen, nur weil drei Zeilen dazugekommen sind.

#### Material ist unvollständig — das ist normal

Läuft die Vorlesung noch, fehlen Decks am Ende und meist die Klausur. Halt das in
der Quellenlage fest: welche Decks da sind (`01`–`07` von vermutlich 14), ob
Übungen fehlen, ob Klausur-Material vorliegt. Zwei Konsequenzen für den Ablauf:

- **Die Deck-Abdeckungs-Prüfung in Schritt 8 gilt nur für vorhandene Decks.** Melde
  keine Lücke für einen Foliensatz, der noch nicht hochgeladen ist.
- **Das Budget skaliert mit.** `graph.py` rechnet es aus den vorhandenen Folien-
  Themen. Halbes Semester heißt halbes Budget — was am Ende zusammenkommt, ergibt
  sich beim Fortschreiben von selbst.

### 2. Text lokal extrahieren + Folien-Titel mappen
Installiere die lokalen Parser einmal und starte dann den Lauf:
```bash
uv sync
winget install --id UB-Mannheim.TesseractOCR -e
uv run python .claude/skills/themen-analyse/scripts/extract_and_map.py "<Fach>"
```
**pdf-inspector** bleibt der schnelle Erstpass. Nur gemeldete Problemseiten und
Seiten mit weniger als 30 Wörtern plus großer Grafik gehen an PyMuPDF4LLM.
Tesseract mit `deu+eng` läuft zuerst; RapidOCR übernimmt lokal bei einem Fehler.
Das Skript schreibt
nach `_derived/<Fach>/cache/` — alles dort ist wegwerfbar und in Sekunden neu da
(Layout: `_derived/README.md`):
- `text/VL_*.md`, `text/KL_*.md`, `text/UE_*.md` — **Markdown** je Vorlesung,
  Überschriften/Listen/Tabellen erhalten, Seiten getrennt durch
  `<!-- Seite N -->`.
- `slide_titles.txt` — je Vorlesung eine Zeile pro **Thema**, nicht pro Seite:
  ```
  ### 03_LOD2_SPARQL (39 Seiten, 36 Themen)
  p7: RDF als Grundlage
  p10-12 (final p12): RDF Schema mechanism
  ```
  `p10-12 (final p12)` = Folgeseiten mit gleichem Titel, also eine Animations-
  Bau-Folge; **p12 ist die finale Stufe** und die Folie für Stufe 2.

Der Titel ist die **größte Schrift oben** auf der Folie, nicht die erste Textzeile.

**Achte auf die `WARN`-Zeilen am Ende:**
- `OCR=N` — PyMuPDF4LLM und Tesseract oder RapidOCR haben N Seiten ergänzt.
- `OCR-Fallback ...` — ein OCR-Motor fiel aus. Der zweite Motor übernimmt.
- `mixed` — Deck mischt Text- und Bildseiten. Bei Folien normal, kein Fehler.

Selbsttest: `uv run python .claude/skills/themen-analyse/scripts/extract_and_map.py --selftest`

### 2b. Eigene Markierungen einlesen (Signal 0)
```bash
uv run python .claude/skills/themen-analyse/scripts/annots.py "<Fach>"
```
Schreibt `_derived/<Fach>/cache/markierungen.md`. Läuft in unter einer Sekunde und meldet
`0 Markierungen`, wenn es keine gibt — dann entfällt Signal 0 und du gehst weiter.

Findet das Skript etwas, **lies die Datei ganz und dazu `docs/markierungen.md`**.
Dort steht, was jede Markierungsart bedeutet; hier steht nur, was daraus für die
Themenliste folgt.

| Markierung | Folge für die Themenliste |
|---|---|
| **Kasten** | Der Inhalt wird ein Thema. Trag das Rechteck in die Folien-Spalte, das `annots.py` empfiehlt: **`mit Beschriftung`**, falls angegeben, sonst `Crop`. Dazu `Grafik: N` — daran entscheidet Stufe 2, ob abgeschrieben oder gerendert wird (`docs/bild-zuschnitt.md`). |
| **Textmarker** | Eigenes Thema mit Aufgabentyp `Wissen`. Der Nutzer will den Begriff erklärt bekommen, nicht den Satz drumherum. |
| **Notiz** | Anweisung. Zerleg sie in ihre Einzelaufträge und mach daraus je ein Thema oder eine Zeile in der Empfehlungs-Begründung. |
| **nichts markiert** (im markierten Deck) | Kein Thema. Der Nutzer hat die Seite bewusst ausgelassen. |

Drei Dinge, die dabei leicht untergehen:

- **Eine Notiz kann ein Thema verlangen, das die Folien nicht hergeben.** Bei GenAi
  fordert die Notiz auf S. 4 `Regression`, das Wort kommt in Deck 02 kein einziges
  Mal vor. Nimm es trotzdem auf, markier es sichtbar als `Quelle fehlt`, und frag
  den Nutzer, ob es aus einem späteren Deck nachkommt. Weder erfinden noch
  weglassen.
- **Markierte Themen sind budgetfest** (Schritt 8) und kommen nie auf `optional`.
- Übungs- und Klausurthemen werden immer als `rein` vorgeschlagen und erhalten einen
  Einbauort. Sie werden nicht als unmarkierte Folienrückholung behandelt.
- **Ein Deck ohne Markierungen ist nicht unwichtig** — der Nutzer ist dort nur noch
  nicht durch. Es fällt zurück auf Klausur, Übung und Graph. Schreib in die
  Quellenlage, **welche** Decks markiert sind, damit der Unterschied sichtbar ist.

### 3. Klausur-Material ganz lesen (Signal 1)
Lies **alle** `_derived/<Fach>/cache/text/KL_*.md` (meist klein). Die
Zusammenfassung/Themenliste des Dozenten (oft `Zusammenfassung*`, `Themen*`) ist
das stärkste Einzelsignal, weil sie Themen und Aufgabentypen direkt nennt.

Für **Data Science 1** gilt ein wichtiger Sonderfall:
`W:\Studium\Lernen\Vorlesungen\Data Science 1\Vorlesungsfolien\2026_07_06_Zusammenfassung_Klausuraufgaben_mitL.pdf`
liegt technisch im Folienordner, ist aber als Klausur-Zusammenfassung zu behandeln.
Lies die Datei vollständig. Übernimm jede Themenliste einzeln, jede Beispielaufgabe
mit Aufgabenform und nötigem Vorwissen in die Aufgaben-Liste. `extract_and_map.py`
ordnet diese Datei als `KL_*.md` ein, damit sie im Graphen als Klausurquelle zählt.
Prüfe bei DS1, dass sie unter `cache/text/KL_*.md` auftaucht.

Schreib dabei eine **Aufgaben-Liste** mit, je Aufgabe:
`Art (Transfer/Wissen) | Form | gefragtes Thema | Vorwissen zum Lösen`.
Formen: rechnen, Query schreiben, modellieren, Definition, erklären, Multiple
Choice, Auflistung, Grafik beschriften. Die Spalte *Vorwissen* ist wichtiger als
die Spalte *Thema* — sie liefert die Themen aus Signal 3.

#### Die Begriffsliste des Dozenten ist die beste Einzelquelle

Viele Dozenten legen dem Klausur-Material eine Liste bei („folgende Begriffe sollten
Sie erklären können", „Themen der Klausur"). **Nimm jeden Begriff daraus einzeln
auf**, auch wenn er nur ein Wort ist und der Graph ihn später nicht findet.

Warum das so wichtig ist: eine Begriffsliste ist eine Ansage, keine Stichprobe.
Jeder Begriff kostet im Lernblatt zwei Zeilen und bringt 1–2 sichere Punkte — das
beste Verhältnis von Platz zu Punkten, das es gibt. Beim Abgleich der eigenen
Lernblätter waren **alle zehn echten Lücken in DS1 Begriffe aus dieser Liste**
(Overfitting, ALTAI, Lack of Trust, Master Data Management, Schutzbedürftige
Gruppen …). Sie fallen durch, weil sie unscheinbar sind, nicht weil sie unwichtig
sind.

Praktisch: hak die Liste Begriff für Begriff gegen `terms.txt` ab. Fehlt einer, trag
ihn nach. In der Ausgabe bekommen diese Themen Rang mindestens `Hoch`, Aufgabentyp
`Wissen` und Empfehlung `rein` — sie sind vom Budget in Schritt 8 ausgenommen.

#### Eine Altklausur ist ein Formular, keine Themenliste

**Die kommende Klausur ist nicht 1:1 die alte.** Eine Alt- oder Probeklausur zeigt,
**wie** geprüft wird, nicht **was** drankommt. Dozenten sagen das oft selbst
(DS1: „nur weil etwas hier nicht genannt wird, heißt es nicht, dass es nicht
drankommen kann"; CyberSec: „Probeklausur deckt nicht zwingend alle Themenfelder ab").

**Verwertbar** — übertrage das direkt in die Ausgabe:
- **Aufgabenformen** — rechnen, zeichnen, Query schreiben, Grafik beschriften,
  Szenario zuordnen. Diese Formen wiederholen sich fast immer.
- **Schwierigkeit und Antworttiefe** — wie lang ist eine 2-Punkte-Antwort, wird ein
  Rechenweg verlangt, gibt es Key-Words wie `Name`/`Explain`/`Compute`.
- **Gewichtung als Größenordnung** — welcher Themenblock trägt viele Punkte. Als
  Tendenz nutzen, nicht als Prozentzahl fortschreiben.
- **Rahmen** — Dauer, Hilfsmittel, Sprache, Bestehensgrenze.

**Nicht verwertbar:** die Themenauswahl als abschließende Liste. Ein Thema fehlt in
der Probeklausur → das schließt **nichts** aus. Ein Thema steht drin → das macht
seine *Form* sicher, nicht seine Wiederkehr.

Konsequenz für Schritt 7 und 8:
- Ein Thema **nur** wegen fehlendem Klausur-Treffer niemals auf `Niedrig` setzen
  oder streichen. Streichen nur bei ausdrücklicher Ansage des Dozenten.
- Die Themen**breite** kommt aus Folien + Übungen + Kopplung (Signal 2 und 3), die
  Aufgaben**form** aus der Klausur.
- Schreib in die Ausgabe dazu, **aus wie vielen Klausuren** eine Aussage stammt.
  Eine einzige Altklausur ist eine Stichprobe, keine Verteilung.

#### Wenn kein Klausur-Material da ist

Das ist der Normalfall bei neuen Kursen. Dann:
- Signal 1 entfällt, Signal 2 (Übungen) wird das stärkste. Übungsaufgaben sagen die
  Transferaufgaben am zuverlässigsten vorher.
- Rang aus Kopplung (Signal 3) und Folien-Umfang je Thema ableiten.
- Nach Aufgabenformen im Vorlesungsmaterial suchen: Folien mit „Aufgabe",
  „Beispiel", „Übung", durchgerechnete Beispiele, Klausurhinweis-Folien.
- **Schreib in die Ausgabe, dass Signal 1 fehlt.** Der Nutzer soll wissen, worauf
  die Rangfolge beruht, und kann Material nachliefern.

### 4. Übungsaufgaben auswerten (Signal 2)
Dasselbe für `UE_*.md`: welche Aufgabe fragt welches Thema, was braucht man zum
Lösen. Ist `Uebungen/` leer, notiere das und stütze dich auf Signal 1.
Übungsaufgaben sagen die Transfer-Aufgaben der Klausur oft direkt vorher.

### 5. Folien-Titel zu Themen verdichten + `terms.txt` schreiben
Lies `slide_titles.txt`. Identische Folgetitel sind schon zusammengefasst; fasse
zusätzlich **ähnliche** Titel zu einem Thema zusammen. Notiere je Thema die finale
Seite (`final pN`) — die braucht Stufe 2 zum Rendern. Wirf Orga-, Link- und
Gastvortrags-Titel raus; bei Dozenten-Markern wie „V" (Vertiefung) frag im Zweifel.

Starter erzeugen, dann von Hand verdichten:
```bash
uv run python .claude/skills/themen-analyse/scripts/graph.py "<Fach>" --init
```
Das schreibt `_derived/<Fach>/planung/terms.txt` mit den Roh-Titeln (bei DS1: 326, davon
ist der Großteil Müll). Kürze auf ~20–50 echte Themen und gib je Thema die
**Suchwörter** an — Synonyme, englische Begriffe, Abkürzungen, typische
Code-Schnipsel:
```
SPARQL: sparql, select ?, prefix, where {
Datenqualität-Metriken: metrik, completeness, accuracy, vollständigkeit
```
Ohne Suchwörter findet der Abgleich nur wörtliche Titel-Treffer. Nimm die Begriffe
aus Schritt 3 und 4 mit auf — auch Themen, die nur in der Klausur einen Namen haben.

**Suchwörter matchen ganze Wörter, kein Präfix.** `artifact` findet `Artifacts`
nicht, `swimlane` findet `Swimlanes` nicht. Schreib Plural und Beugung mit aus.
Das ist Absicht: Präfix-Suche würde `RDF` in `RDFS` finden. Die häufigste Ursache
für 0-Treffer-Themen in Schritt 6.

### 6. Kopplungs-Graph rechnen (Signal 3)
```bash
uv run python .claude/skills/themen-analyse/scripts/graph.py "<Fach>"
```
Schreibt `_derived/<Fach>/cache/graph.md`: je Thema die Treffer in KL/UE/VL, den **Grad**
und die stärksten Nachbarn. Zwei Themen auf derselben Seite = eine Kante,
gewichtet nach Quelle (Klausur 3, Übung 2, Folien 1). Hoher Grad = das Thema
taucht überall zusammen mit anderen auf, ist also Träger des Stoffs.

Übersichtsseiten (mehr als `MAX_KLIQUE` Themen auf einer Seite, z.B. die
Themenliste der Klausur) zählen als Treffer, erzeugen aber keine Kanten — sonst
verklebt eine einzige Inhaltsverzeichnis-Seite alle Themen zu einer Clique. Das
Skript meldet, wie viele Seiten es so behandelt hat.

Lies nur `graph.md`, nicht die Extrakte. Der Kopf der Datei nennt drei Dinge, die
in Schritt 8 gebraucht werden:

- **Umfangs-Budget** — Folien-Themen gesamt, Ziel-Seitenzahl und daraus „rund N
  Themen mit `rein`". Die Seitenzahl kommt aus dem eigenen Beispiel-Lernblatt in
  `Vorlesungen/<Fach>/`, sonst aus einer Schätzung (1 Blattseite je 10 Folien-Themen).
- **stumme Decks** — Foliensätze, in denen kein einziges Thema aus `terms.txt`
  trifft. Fast immer fehlen Suchwörter oder ein ganzer Foliensatz wurde beim
  Verdichten übersehen. Reine Orga-Dateien (`00_*_Infos`) dürfen stumm bleiben.
- **Themen ohne Treffer** — meist falsche Suchwörter. Steht dahinter „N Treffer
  ohne Wortgrenze", ist es Plural oder Beugung (`swimlane` findet `Swimlanes`
  nicht): Suchwort erweitern und neu laufen (0,8 s).

### 7. Rolle und Aufgabentyp je Thema festlegen (Signal 4)
Jetzt kombinieren. Trag je Thema ein:
- **Rolle:** `Kern` (direkt abgefragt) / `Voraussetzung` (zum Lösen einer Klausur-
  oder Übungsaufgabe nötig, hoher Grad) / `Erweiterung` (schafft Verständnis, nicht
  direkt abgefragt) / `Ausreißer` (kaum gekoppelt).
- **Aufgabentyp:** `Transfer` / `Wissen` / `beide` / `–`.

Bei **Ausreißern** ausdrücklich prüfen, ob die Folie eine Wissensabfrage hergibt:
eine nummerierte Aufzählung („die 5 X"), eine scharfe Definition, ein
Prinzip/Ablauf, oder eine beschriftete Grafik, deren Begriffe man ausschneiden
könnte. Wenn ja → `rein`, obwohl der Grad niedrig ist. Genau diese Themen fallen
sonst durch, und genau sie sind billige Klausurpunkte.

Baut Stoff aufeinander auf, hebt das **Oberthema**: hat ein Thema mehrere Kanten
zu Kern-Themen, ist es Voraussetzung und kommt rein, auch ohne eigenen
Klausur-Treffer.

**Bonus-Block nur bauen, wenn das Fach ihn belegt hat.** Das ist die Ausnahme, nicht
die Regel — die meisten Klausuren haben keine Zusatzaufgabe, und wo es eine gibt,
fragt sie meist normalen Stoff. Bau den Block **nur**, wenn eine dieser zwei
Bedingungen zutrifft:

- Das Klausur-Material zeigt eine Bonus- oder Zusatzaufgabe, oder
- der Nutzer sagt dir, dass es eine gab. Frag ihn kurz — seine Erinnerung ist hier
  die einzige Quelle, und die Antwort ist in zehn Sekunden da.

Trifft keins von beiden zu, überspring diesen Absatz komplett und schreib in die
Quellenlage, dass kein Bonus-Material vorliegt.

Nur wenn du einen Block baust: manche Bonusaufgaben fragen **fachfremdes
Folien-Randwissen** — Details, die auf den Folien stehen, aber nichts mit dem Fach
zu tun haben. Bei DS1 ist das belegt („Unterschied Herzinfarkt und Herzstillstand"
aus dem Ethik-Use-Case). Solche Themen findet der Graph nie: sie koppeln an nichts
und stehen in keiner Zusammenfassung. Geh die Folien dann gezielt nach dem Muster
durch (konkrete Zahl, Eigenname, medizinisches oder historisches Detail,
fachfremdes Bild oder Beispiel-Datensatz) und gib das Ergebnis als eigenen Block
mit Rang `Bonus` aus — zuletzt lernen, Aufwand klein halten.

### 8. Relevanz-Tabelle ausgeben
Schreibe `_derived/<Fach>/planung/themenliste.md` und lege sie dem Nutzer vor:
```markdown
| # | Thema | Folien | KL | UE | Grad | Rolle | Aufgabentyp | Rang | Empfehlung |
|---|-------|--------|----|----|------|-------|-------------|------|-----------|
```
Zwei Spalten kommen nur dazu, wenn es sie zu füllen gibt — eine leere Spalte kostet
Breite und sagt nichts:
- **`Mark`** wenn Signal 0 etwas gefunden hat: `★` für ein markiertes Thema, dazu
  Seite und Typ in der Folien-Spalte.
- **`Δ`** im Fortschreib-Modus: `neu`, `↑ Hoch→Sehr hoch (Übung 9)`, sonst leer.

- **Folien:** Deck + finale Seite(n), z.B. `03 p12, p18`. Stufe 2 rendert daraus.
  Bei einer Kasten-Markierung das Rechteck dazu: `03 p12 (Kasten 72,200–300,320)`.
- **Rang:** `Sehr hoch` (Klausur-Aufgabentyp oder Voraussetzung dafür) > `Hoch`
  (in Klausur/Übung genannt, in der Begriffsliste des Dozenten, oder hoher Grad) >
  `Mittel` (nur Folien, aber Wissensabfrage-Kandidat) > `Niedrig`.
- **Erweiterung:** `ja`, wenn das Thema besonders wichtig ist, mehrere Aufgaben
  trägt oder zentrale Voraussetzungen bündelt; sonst `nein`. `ja` verlangt den
  markierten Erweiterungsabschnitt am Ende des zugehörigen Foliensatzes.
- Nenne über der Tabelle die **Quellenlage**: wie viele Klausuren, welchen Jahrgangs,
  ob Probeklausur oder echte Altklausur, ob Übungen vorliegen. Eine Gewichtung aus
  einer einzigen Klausur als Tendenz kennzeichnen, nicht als Prozentzahl behaupten.
- **Empfehlung:** `rein` / `optional` / `ausschließen (Grund)`. Übungs- und
  Klausurthemen sind standardmäßig immer `rein`; der Nutzer kann sie nur durch eine
  ausdrückliche Streichung entfernen.
- Über die Tabelle kommt die **Aufgaben-Liste aus Schritt 3 und 4**, getrennt nach
  Transfer und Wissensabfrage. Das ist der wichtigste Teil der Ausgabe — Stufe 2
  baut daraus die annotierten Beispiele und die vollständigen Aufzählungen.

#### Das Budget ist eine Ansage über die Länge, kein Urteil über ein Thema

`graph.md` nennt im Kopf das Budget (Schritt 6), z.B. „30 Blattseiten → rund 75
Themen `rein`". Diese Zahl sagt dir, **wie lang das Blatt wird**. Sie sagt nicht,
welches Thema falsch ist. Der Unterschied ist wichtig: die Zahl kommt aus einer
Seitenzahl-Messung, nicht aus Wissen über den Kurs. Ein Thema wegen einer solchen
Zahl aus dem Blick des Nutzers zu nehmen, wäre ein Fehler mit echten Kosten — ein
verpasstes Klausurthema ist teurer als zwei Seiten mehr zu lesen.

**Auf `optional` kommt nur ein reines Folienthema, das keinen Übungs- oder
Klausurbezug hat:**
- Rang `Niedrig`.
- Rang `Mittel`, bei dem Schritt 7 **kein** Wissensabfrage-Potenzial gefunden hat.
- `Erweiterung` oder `Ausreißer` ohne Wissensabfrage-Potenzial.

**Nie auf `optional`, egal wie die Zahl steht:**
- Rang `Sehr hoch` und `Hoch` — ohne Ausnahme.
- Themen mit Aufgabentyp `Transfer`, die eine belegte Klausur- oder Übungsaufgabe
  tragen. Ohne sie fehlt das gerechnete Beispiel, und das improvisiert man in der
  Klausur nicht.
- Begriffe aus der Begriffsliste des Dozenten (Schritt 3).
- Alles, was der Nutzer selbst im PDF markiert hat (Schritt 2b).
- Übungs- und Klausurthemen dürfen nicht auf `optional` oder in die Warteliste.
- Der `Bonus`-Block, falls es einen gibt, wird ebenfalls als Prüfungsquelle erfasst
  und standardmäßig `rein` gesetzt.

**Wenn das nicht reicht, hör auf zu kappen.** Bist du nach dieser Regel immer noch
über dem Budget, ist das ein Befund, kein Problem, das du lösen musst: der Stoff
gibt nicht weniger her. Schreib es hin — „Budget 75, es bleiben 92 auf `rein`; der
Kurs hat keine 17 entbehrlichen Themen" — und lass die Entscheidung beim Nutzer.
Weiter zu kappen hieße, gute Themen wegzuwerfen, um eine geschätzte Zahl zu treffen.

#### Gekappte Themen bleiben sichtbar

Nichts verschwindet aus der Datei. Themen auf `optional` kommen **vollständig** in
einen eigenen Abschnitt unter der Haupttabelle, mit denselben Spalten plus einer
Spalte `Warum optional`:

```markdown
## Optional — vom Budget gekappt, jederzeit zurückholbar

| # | Thema | Folien | KL | UE | Grad | Rolle | Aufgabentyp | Rang | Warum optional |
```

Der Grund ist ein halber Satz, der nachprüfbar ist („Grad 3, kein Klausur- oder
Übungstreffer, keine Aufzählung auf der Folie") — nicht „weniger wichtig". Nur so
kann der Nutzer eine Zeile in zehn Sekunden zurückholen, ohne die Folie zu öffnen.

Prüf zum Schluss zwei Dinge:
- **Hat jeder Foliensatz mindestens ein Thema mit `rein`?** Fehlt einer ganz, fällt
  beim Lernen ein kompletter Kursteil weg. Genau das ist im CyberSec-Lernblatt
  passiert: Deck 11 (AI Security) fehlt vollständig und kostet 10 Klausurpunkte.
  Ausnahmen sind Orga- und Gastvortrags-Decks — die schreib dazu.
- **Ist jede Transfer- und Wissensabfrage aus Schritt 3 und 4 durch ein Thema mit
  `rein` und einem Einbauort abgedeckt?** Sonst ist die Liste fehlerhaft.
- **Steht jedes Übungs- und Klausurthema im Build-Plan?** Eine Lücke stoppt die
  Übergabe an `lernblatt-generator`.

Schreib die Rechnung über die Tabelle: „Budget 75 · 82 Folienthemen plus 17
Prüfungs- und Übungsergänzungen · 7 reine Folienthemen optional." Das Budget darf
für die vollständige Prüfungsabdeckung überschritten werden.

Bitte den Nutzer explizit um Freigabe: streichen, ergänzen, Rang ändern, `optional`
hochstufen. Die freigegebene Datei ist der Input für `lernblatt-generator`.

## Gotchas
- **Quellenpfad:** Kursmaterial liegt primär in `Vorlesungen/<Fach>/`.
  `Examples/<Fach>/` bleibt nur ein Rückfall für alte Bestände.
- **PowerShell-Variablen überleben nicht** zwischen Tool-Aufrufen → jedes Skript
  macht alles in einem Lauf.
- Der pdf-inspector-Erstpass bleibt schnell. OCR kostet nur auf Problemseiten Zeit;
  `graph.py` bleibt bei etwa 1 s.
- **Der Graph ist ein Hinweis, kein Urteil.** Er zählt nur Ko-Vorkommen auf einer
  Seite. Ein hoher Grad kann auch heißen, dass ein Wort einfach überall steht
  (Fußzeilen, Links). Prüf die Top-Themen kurz gegen `slide_titles.txt`.
- **Token-Bewusstsein:** Extraktion bleibt lokal. In den Context kommen nur
  `KL_*`/`UE_*`, `slide_titles.txt` und `graph.md` — nie die Folien-PDFs und nie
  die `VL_*.md` am Stück.
- Parser liefern Kandidaten. Das aktuelle OpenAI-Modell entscheidet weiterhin,
  was relevant ist, welcher Ausschnitt passt und ob der fertige Crop verständlich ist.
- **`_derived/<Fach>/cache/` ist wegwerfbar.** `planung/`, `analysen/` und `build/`
  bleiben erhalten. Das vollständige Layout steht in `_derived/README.md`.
  `--init` überschreibt `terms.txt` nicht.
- **Nie ganze `cache/text/VL_*.md` in den Context laden** — CyberSec sind 505 KB.
  Dafür gibt es `slide_titles.txt` und `graph.md`. `KL_*`/`UE_*` sind klein genug.
- **`planung/themenliste.md` ist keine Wegwerf-Datei.** Existiert sie schon, arbeite im
  Fortschreib-Modus (Schritt 1). Ein Rang, den der Nutzer gesetzt hat, überlebt
  jeden neuen Lauf, solange kein neuer Beleg dagegen spricht.
- Markierungen liest nur `annots.py`. `pdf-inspector` sieht sie nicht — sie stehen
  in der Annotations-Ebene des PDFs, nicht im Text.
- Selbsttests: `extract_and_map.py --selftest`, `graph.py --selftest`,
  `annots.py --selftest`.
