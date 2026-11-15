---
name: moodle-kurs-material
description: >-
  Lädt Vorlesungsfolien, Übungen und Klausur-Material aus einem Kurs der Goethe-Uni
  herunter und sortiert die Dateien in die Fach-Ordner Vorlesungsfolien, Klausuren
  und Uebungen. Unterstützt Moodle (moodle.studiumdigitale.uni-frankfurt.de, per
  Session-Cookie) und OLAT (olat-ce.server.uni-frankfurt.de, per ZIP-Import). Nutze
  diesen Skill immer, wenn der Nutzer Kursmaterial, Folien, Übungsblätter,
  Notebooks oder Altklausuren aus Moodle oder OLAT sammeln, herunterladen, sichern,
  aktualisieren oder für ein neues Fach anlegen will — auch wenn nur eine Moodle-
  oder OLAT-Kurs-URL oder ein Fachname genannt wird.
---

# Kurs-Material holen (Moodle + OLAT)

Zweck: aus einem Kurs alle Dateien holen und pro Fach in `Vorlesungsfolien`,
`Klausuren` und `Uebungen` unter `W:\Studium\Lernen\Vorlesungen\<Fach>` einsortieren.
Die Dateien dienen später als Kontext, um Lernblätter und Übungsaufgaben zu erzeugen.

## Quelle wählen

Erkenne die Quelle an der URL, dann folge dem passenden Abschnitt:

- **Moodle** (`moodle.studiumdigitale.uni-frankfurt.de/.../course/view.php?id=...`)
  → Abschnitt "Moodle". Headless per Session-Cookie, `fetch_moodle.ps1`.
- **OLAT** (`olat-ce.server.uni-frankfurt.de/olat/...`) → Abschnitt "OLAT".
  Kein Headless-Download möglich, darum ZIP-Import mit `ingest_zip.ps1`.

Ab Schritt "In Kategorien einsortieren" ist der Ablauf für beide Quellen gleich,
weil beide Skripte dasselbe `manifest.json`-Format schreiben.

## Moodle

### Warum nicht Firecrawl

Der Kurs liegt hinter dem HRZ/CAS-Login. Firecrawl und andere Scraper sehen nur
die Login-Seite. Der einzige Weg ist der Session-Cookie des eingeloggten Nutzers.

### Was du vom Nutzer brauchst (Moodle)

1. **Kurs-URL oder Kurs-id** — z.B. `.../course/view.php?id=8844` → id `8844`.
2. **MoodleSession-Cookie** — so holt der Nutzer ihn:
   1. Kursseite in Chrome öffnen (eingeloggt).
   2. `F12` → Reiter **Application** (Anwendung).
   3. Links **Cookies** → die Moodle-Domain wählen.
   4. Zeile **`MoodleSession`** → **Value** kopieren und einfügen.
3. **Fach-Ordner** — Zielordner unter `W:\Studium\Lernen\Vorlesungen\<Fach>` (z.B.
   `Vorlesungen\Eingebettete Systeme`). Der Fachname kommt aus dem Kurstitel, den
   `fetch_moodle.ps1` ausgibt. Frag nur nach, wenn der Titel mehrdeutig ist.

Der Cookie ist ein Sitzungs-Token. Behandle ihn vertraulich, logge ihn nicht.
Erinnere den Nutzer am Ende: einmal in Moodle aus- und wieder einloggen, dann ist
der Cookie ungültig.

### Dateien laden (Moodle, ein Skript, ein Lauf)

Führe `scripts/fetch_moodle.ps1` aus. Es baut die Session, prüft den Login, parst
die Kursseite, löst jede Ressource zur echten Datei auf und lädt sie in einen
Staging-Ordner. Nutze den Scratchpad als Staging.

```powershell
& "<skill>\scripts\fetch_moodle.ps1" -Cookie "<MoodleSession>" -CourseId <id> -OutDir "<scratchpad>\staging"
```

Wichtig: **alles in EINEM PowerShell-Aufruf.** PowerShell-Variablen (die Session
mit dem Cookie) überleben nicht zwischen getrennten Tool-Aufrufen. Teilst du das
auf, leitet Moodle auf die Login-Seite um und du lädst nur HTML. Das Skript ist
genau darum in sich geschlossen.

Ergebnis: Dateien als `<id>_<originalname>` im Staging plus `manifest.json` mit
`files` (id, name, ext, sizeKB, status) und `links` (externe Tool-Links).

Wenn der Login fehlschlägt: Cookie ist abgelaufen. Bitte um einen frischen Wert.

## OLAT

OpenOLAT (`olat-ce.server.uni-frankfurt.de`) lässt sich **nicht headless laden**
wie Moodle, und zwar aus zwei Gründen, die man nicht umgehen kann:

- Die Datei-Liste rendert der OpenOLAT-GUI-Rahmen per Wicket-AJAX, nicht statisch.
  Ein Session-Cookie holt die Rahmen-Seite, aber nicht die Dateien.
- Der saubere Automatik-Weg (WebDAV / REST) verlangt Basic-Auth mit dem
  OLAT-Passwort. Ein Passwort einzugeben ist verboten. Nicht versuchen.

Darum: **ZIP-Import.** Der Nutzer lädt das Material in OLAT selbst als ZIP und du
entpackst und sortierst es.

### Was du vom Nutzer brauchst (OLAT)

1. **ZIP-Datei(en)** — In OLAT den Material-/Ordner-Baustein öffnen, oben
   "Herunterladen" bzw. "Als ZIP herunterladen" wählen. Bei mehreren Ordnern
   (z.B. Folien, Übungen getrennt) mehrere ZIPs. Ablegen z.B. in Downloads.
2. **Pfad zu den ZIP(s)** — eine Datei, mehrere Dateien, oder ein Ordner, der die
   ZIPs enthält.
3. **Fachname** — aus dem Kurstitel (z.B. `Prozessorientierte Informationssysteme`).
   Ziel bleibt `W:\Studium\Lernen\Vorlesungen\<Fach>`.

### Dateien einlesen (OLAT)

```powershell
& "<skill>\scripts\ingest_zip.ps1" -ZipPath "<pfad-zur-zip-oder-ordner>" -OutDir "<scratchpad>\staging"
```

Das Skript entpackt die ZIP(s), legt jede Datei flach als `<NNNN>_<name>` ins
Staging und schreibt dasselbe `manifest.json` wie das Moodle-Skript — zusätzlich
mit `relpath` (Original-Pfad in der ZIP). Ab hier ist der Ablauf identisch.

## In Kategorien einsortieren (beide Quellen)

Lies `manifest.json` und ordne jede Datei genau einer der drei Kategorien zu.
Heuristik (nach Name, Endung und bei OLAT auch `relpath`), im Zweifel den Nutzer
fragen. Ordnernamen in der ZIP (`relpath`) sind oft schon ein Kategorie-Hinweis:

- **Vorlesungsfolien** — Folien und Vortrags-PDFs: Namen mit "Folien", "Intro",
  "Overview", Themen-Slides, Gastvorträge. Meist `.pdf`.
- **Klausuren** — Prüfungs-Material: Namen mit "Klausur", "Klausuraufgabe",
  "Deckblatt", "Zusammenfassung ... Aufgaben", "Altklausur", plus die dazu
  gehörenden Datendateien (z.B. eine `.ttl` zu einer Klausuraufgabe).
- **Uebungen** — Übungsmaterial und Code: `.ipynb`-Notebooks, `.py`-Programme,
  Übungsblätter, sowie Datensätze (`.csv`, `.ttl`, `.zip`), die eine Übung
  füttern.

Regeln:
- **Nur diese drei Ordner.** Kein `Datensaetze`, kein `Tools-Links`. Datensätze
  gehören zur Übung oder Klausur, zu der sie passen.
- **Externe Tool-Links** (`links` im Manifest, z.B. RDFGrapher, Fuseki) sind
  keine Dateien. Nicht herunterladen, nur in der Chat-Zusammenfassung nennen.
- Vergib **saubere, sprechende Dateinamen**. Folien chronologisch nummerieren
  (`01_...`, `02_...`) in Kursreihenfolge (die Manifest-Reihenfolge entspricht
  der Kursseite).
- Wenn eine Datei in keine Kategorie klar passt, frag den Nutzer statt zu raten.

Schreibe eine Map-JSON (id → `Kategorie\SauberterName.ext`) in den Scratchpad,
z.B.:

```json
{
  "363777": "Vorlesungsfolien\\01_Orga_Intro.pdf",
  "363805": "Klausuren\\Deckblatt_Klausur.pdf",
  "363783": "Uebungen\\SPARQL_Notebook.ipynb"
}
```

## Verschieben und prüfen (beide Quellen)

```powershell
& "<skill>\scripts\organize.ps1" -MapJson "<scratchpad>\map.json" -StagingDir "<scratchpad>\staging" -TargetRoot "W:\Studium\Lernen\Vorlesungen\<Fach>"
```

Das Skript legt die Ordner an, verschiebt jede Datei per `Move-Item` auf ihren
vollen Ziel-Dateipfad und gibt die fertige Struktur aus. `Move-Item` (nicht
`Copy-Item`) mit vollem Dateipfad ist bewusst gewählt: `Copy-Item` hat in einem
früheren Lauf das Ziel als Ordner behandelt und alles im Wurzelordner abgelegt.

Prüfe die ausgegebene Struktur. `FEHLT`-Einträge heißt: für den Schlüssel gab es
keine Staging-Datei (siehe Status im Manifest).

## Abschluss

- Kurze Zusammenfassung: Anzahl Dateien je Kategorie, externe Links als Liste.
- Wenn ein Fach schon einen Teil-Ordner hat, ersetze veraltete Duplikate durch
  den vollständigen aktuellen Satz (frag kurz nach, bevor du löschst).
- Nur bei Moodle: erinnere den Nutzer, sich aus- und wieder einzuloggen (Cookie
  ungültig machen). Bei OLAT entfällt das.

## Grenzen

- Moodle: `mod/folder` (mehrere Dateien in einem Ordner-Modul) und
  `mod/assign`-Anhänge parst `fetch_moodle.ps1` noch nicht — falls im Kurs
  vorhanden, dem Nutzer melden.
- Moodle: nur die studiumdigitale-Instanz ist als Basis-URL voreingestellt; für
  eine andere Instanz `-Base` setzen.
- OLAT: kein Headless-Download (siehe Abschnitt OLAT). Immer über ZIP-Import.
  `ingest_zip.ps1` entpackt nur `.zip` (keine verschachtelten ZIPs).
