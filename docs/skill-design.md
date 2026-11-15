# Skill-Design (festgelegte Entscheidungen)

Ergänzt [style-guide.md](style-guide.md) und
[vergleich-beispiel2.md](vergleich-beispiel2.md). Die Lernblattpipeline nutzt 3
getrennte Skills. Vorlesungsquiz und Probeklausurgenerator laufen unabhängig davon.

## Warum getrennte Skills
Themenanalyse, Lernblatterweiterung und Lernblatt-Erstellung sind getrennte
Schritte mit einer Freigabe dazwischen. Die Trennung hält jeden Skill fokussiert
und token-sparsam. Sie erlaubt, Themenliste und Erweiterungen unabhängig zu prüfen.

---

## Skill 1 — `themen-analyse` (Stufe 1)
Zweck: über den **ganzen Kurs** eine Themen-Relevanz-Liste zur Freigabe erstellen.
Erstellt KEINE Lernblätter.

Ablauf:
1. Pro Vorlesung Markdown + Folien-Titel extrahieren (`pdf-inspector`). Titel =
   **größte Schrift oben**, nicht erste Textzeile (siehe `research-notes.md`).
2. Animations-Bau-Stufen zusammenfassen (aufeinanderfolgende gleiche Titel = 1
   Thema, finale Stufe merken) — macht das Skript automatisch.
3. Abgleich mit Übungen + Klausuren: jedes Aufgaben- und Wissensthema einzeln
   erfassen, einer Vorlesung oder einem neuen Ergänzungsblock zuordnen und mit
   Quelle sowie Aufgabentyp dokumentieren.
4. Relevanz-Rang: `Übung/Klausur` > `nur Folien`. Prüfungs- und Übungsthemen sind
   trotzdem Pflichtinhalt, nicht nur ein Rangsignal.
5. Ausgabe: **Tabelle** (Thema | Vorlesung oder Ergänzungsblock | in Übung? |
   in Klausur? | Rang | Aufgabentyp | Einbauort | Empfehlung), z.B. als
   Markdown/CSV. Der Nutzer checkt, streicht, ergänzt.
6. Abdeckungsprüfung: Vor der Übergabe an Stufe 2 muss jedes Übungs- und
   Klausurthema einen Einbauort besitzen. Fehlende Zuordnungen sind ein Fehler,
   keine optionale Warteliste.

Wichtig: Themen kommen aus den **Folien + Übungen/Klausuren**, NICHT aus den alten
Lernblättern. Die freigegebene Liste ist der Input für Skill 2.

## Skill 2 — `lernblatt-erweiterung` (Stufe 2)
Zweck: besonders wichtige Prüfungs- und Übungsthemen aus den benötigten Grundlagen
ableiten und als markierte Erweiterungen vorbereiten. Übungen und Klausuren werden
nicht 1:1 übernommen. Der Skill schreibt eigene Erklärungen, Definitionen,
Beispiele und geprüfte Transferlösungen. Die Erweiterung steht am Ende des
zugehörigen Foliensatzes vor dem nächsten Foliensatz. Web-Recherche und externe,
belegte Grafiken sind erlaubt.

## Skill 3 — `lernblatt-generator` (Stufe 3)
Zweck: aus der **freigegebenen Themenliste und den freigegebenen Erweiterungen** die
Lernblätter erzeugen.

Ablauf:
1. Folien der freigegebenen Themen mit `render_crop.py` rendern (finale Bau-Stufe)
   — Crop auf die echte Inhalts-Box, Titelband und Seitenzahl fallen weg.
2. Pro Thema: zuerst eine kurze Zusammenfassung, danach vollständiger Folientext
   im Stil ([style-guide.md](style-guide.md)) + 1–2 Screenshots. Text aus einem
   verwendeten Crop nicht nochmals schreiben. Füge die markierten Erweiterungen am
   Ende des passenden Foliensatzes ein. Labels, zentrale Schlüsselwörter und
   Kernaussagen zur Leseführung fett setzen, seltene Merksignale unterstreichen,
   wichtige Tabellenbegriffe fett setzen und Formeln als MathML setzen, wenn sie
   als HTML erscheinen.
3. Kapitelweise in **eine `.html` pro Fach** bauen (`lernblatt_html.py`),
   durchgehend scrollbar. Token-sicher: nur eine Vorlesung je Schritt im Context.

## Skill 4: `genai-quiz`

Zweck: Vorlesungsdefinitionen und Verständnis mit genau 1 Frage je Runde prüfen.
Der Skill sucht die Wissensgrenze adaptiv. Eine richtige Antwort erhöht die
Schwierigkeit deutlich. Eine falsche Antwort löst eine nahe Diagnosefrage aus.

Die Vorlesungsfolien bleiben Ground Truth. Übungen und Klausuren bestimmen nur die
Priorität. Das vorhandene `questionnaire`-Tool zeigt die Auswahl. Der Agent
`genai-quiz-autor` liefert bei unklaren Quellen genau 1 geprüften
Frageentwurf, aber führt keinen Nutzerdialog.

## Skill 5: `genai-probeklausur`

Zweck: aus den Befunden in `analysen/aufgaben.md` eine dynamische Probeklausur und
eine getrennte Lösungsdatei als HTML erzeugen. Der Standard nutzt 60 Minuten,
100 Punkte und 10 Aufgaben. 7 belegte Muster tragen 70 Punkte, und 3
Erweiterungen tragen 30 Punkte.

Der Agent `genai-probeklausur-autor` arbeitet mit `gpt-5.6-sol` und `xhigh`. Ein kleiner
Python-Renderer mischt Aufgaben und Multiple-Choice-Positionen reproduzierbar.
Optionale Web-Erweiterungen nutzen zuerst die lokale SearXNG-Suche und danach die
lokale Firecrawl-Instanz. Sie bleiben auf Themen aus Folien und Übungen begrenzt.

## Gemeinsame Festlegungen der Lernblattpipeline
- **Balance:** screenshot-lastig (POIS-Stil).
- **Format:** `.html` (eine scrollbare Datei pro Fach, Bilder relativ verlinkt aus
  `bilder/` daneben, druckbar auf A4); 3-Farben-Überschriften, fette Kernaussagen,
  Bullets/farbige Sub-Bullets. Layout: `docs/html-style-guide.md`.
- **Granularität:** eine `.html` pro Fach.
- **Länge:** ~1/8 der bereinigten Folien. Prüfungs- und Übungsthemen werden
  zusätzlich vollständig abgedeckt; das Budget darf dafür überschritten werden.
- **Texttreue:** ausgewählter Folientext bleibt vollständig und 1:1. Erweiterungen
  sind nur Definitionen, Erklärungen und konkrete Beispiele.
- **Lernanker:** jeder Topic beginnt mit `kern`; Begriffe vor `:`, zentrale
  Schlüsselwörter und Kernaussagen erscheinen zur Leseführung fett. Seltene,
  besonders merkbare Anker dürfen unterstrichen werden. Wichtige Tabellenbegriffe
  erscheinen fett; Formeln erscheinen als MathML.
- **Lesbarkeit:** kompakte Zeilen- und Absatzabstände, korrekte Umlaute und
  fachübliche Anglizismen.
- **Prüfungsbezug:** Jedes Thema aus Übungen und Klausuren muss im Lernblatt
  erscheinen, aber nicht als wörtliche Übungsübernahme. Leite die nötigen
  Voraussetzungen ab und erkläre sie in eigener Prosa. Besonders wichtige Themen
  erhalten einen markierten Erweiterungsabschnitt am Ende des Foliensatzes. Eine
  unmarkierte Folienseite eines markierten Decks wird dadurch nicht als Screenshot
  zurückgeholt.
- **Rolle der Beispiel-Lernblätter:** reine Stil-Referenz, inhaltlich NICHT
  maßgeblich (können Fehler enthalten). Ground Truth = Vorlesungsfolien.

## Kalibrierungen (aus vergleich-beispiel2.md)
- Screenshots auf relevanten Ausschnitt **zuschneiden**, nicht ganze Folienseite.
- Prüfungsnahe **Aufzählungen vollständig** ausschreiben (OWASP-10, Malware-Arten).
- Screenshot-Anteil erhöhen Richtung **1/8-Dichte**.
- **Farbige Betonungs-Bullets** und **Screenshot-Annotationen** (Markieren,
  „fehlt"-Notiz) unterstützen.
- Crop kommt aus der PDF-Geometrie, nicht aus festen Prozentwerten. Die
  `--top/--right`-Knöpfe bleiben als Nachkorrektur für Sonderfälle.

## Toolchain
- `pdf-inspector`: schneller Text-Erstpass und Folien-Titel.
- `pymupdf`: PDF-Markierungen, Vektorgeometrie, Crops und Rendering.
- `pymupdf4llm` (Version in `pyproject.toml`): selektiver OCR-Fallback für unlesbare oder visuelle Seiten.
- Tesseract mit `deu+eng`: erster OCR-Motor; RapidOCR ist der lokale Ersatz.
- Das aktive OpenAI-Modell: Inhaltsauswahl, Crop-Entscheidung und Review.

OCR ersetzt keinen guten Erstpass. `extract_and_map.py` ruft sie nur für von
`pdf-inspector` gemeldete Problemseiten oder für Seiten mit weniger als 30 Wörtern
und großer Raster- oder Vektorgrafik auf. Das aktive Modell entscheidet danach wie
bisher über Inhalt, Grafik und Crop.

## Offen / später
- Übungs-Screenshots (Aufgabenstellung) zusätzlich einbetten?
- Genaue Farbwerte/Heading-Styles an die Google-Docs-Vorlage angleichen.
- Auto-Cropping-Heuristik (relevanter Folienausschnitt) umsetzen.
