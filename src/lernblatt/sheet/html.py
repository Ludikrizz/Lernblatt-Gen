"""HTML-Builder fuer Lernblaetter: 1 scrollbarer Foliensatz, zentriert, mit
A4-Marker links. Bilder werden relativ verlinkt, save(bundle=True) bettet sie
als base64 ein (eine Datei zum Verschicken).

Stil-Spez: docs/html-style-guide.md.
"""

import base64
import html
import os
import re

from PIL import Image

# Platzhalter im Body; save() ersetzt ihn durch relativen Pfad oder data:-URI.
IMG_MARKE = "\x00IMG\x00"


def b64_of(path):
    return base64.b64encode(open(path, "rb").read()).decode()


CSS = """
:root{ --blau:#1F549B; --rot:#C0000C; --text:#111; --grau:#555;
       --a4:1122px; --rail:3.2rem; --col:1040px;
       }
*{ box-sizing:border-box; }
html,body{ margin:0; }
body{ background:#f4f4f6; color:var(--text);
      font-family:"Segoe UI",Calibri,-apple-system,system-ui,Arial,sans-serif;
      font-size:19px; line-height:1.28; }
.page{ position:relative; max-width:var(--col); margin:0 auto; background:#fff;
       padding:1.6rem var(--rail) 3rem;
       box-shadow:0 0 0 1px #e3e3e8, 0 6px 24px rgba(0,0,0,.06); }
/* Vertikale Abstaende an Text: hoechstens 3pt = 4px. Ein Lernblatt wird gescannt,
   nicht gelesen — Luft zwischen den Zeilen kostet Seiten, ohne etwas zu klaeren.
   Getrennt wird durch Fettung und Farbe, nicht durch Abstand. */
h1{ color:var(--blau); font-size:2.1rem; font-weight:700; text-align:center;
    margin:.2rem 0 1rem; }
h2.deck{ color:var(--blau); font-size:1.75rem; font-weight:700; text-align:center;
         margin:2.2rem 0 .6rem; padding-top:1rem;
         border-top:3px solid var(--blau); }
h2.deck:first-of-type{ margin-top:.4rem; }
h3{ color:var(--blau); font-size:1.45rem; font-weight:700; margin:10px 0 2px; }
.kern{ font-weight:700; margin:2px 0 3px; }
/* Inline emphasis is a scan aid: bold the keyword, underline only rare anchors. */
b,strong{ font-weight:700; }
u{ text-decoration-thickness:1.5px; text-underline-offset:2px; }
.sublabel{ font-weight:700; margin:4px 0 2px; }
.text{ margin:2px 0 3px; }
.formel{ margin:4px 0 6px; overflow-x:auto; text-align:center; }
.formel math{ font-size:1.3em; }
/* Die Liste rueckt als Ganzes ein — Punkt UND Text stehen rechts vom Label
   darueber. Auf gleicher Hoehe verschwimmt die Gliederung: man sieht nicht mehr,
   welche Punkte zu welcher Ueberschrift gehoeren. */
ul.text{ padding-left:2.4rem; margin:2px 0 3px; }
ul.text li{ margin:1px 0; }
table.lb td:first-child{ font-weight:700; }
/* Definition umgebrochen unter ihren Begriff, noch eine Stufe eingerueckt. */
.def{ display:block; padding-left:1rem; }
li.red{ color:var(--rot); font-weight:700; }
.akzent{ color:var(--rot); font-weight:700; font-size:1.15rem; margin:10px 0 3px; }
.knopf{ position:fixed; top:12px; right:12px; z-index:9; display:flex; gap:6px; }
.knopf button{ background:var(--blau); color:#fff; border:0; border-radius:6px;
         padding:.5rem .9rem; font:inherit; font-size:.9rem; font-weight:700;
         cursor:pointer; box-shadow:0 2px 8px rgba(0,0,0,.2); }
figure{ margin:5px auto 8px; text-align:center; }
img.shot{ display:block; margin:0 auto; width:100%; height:auto; }
figcaption{ color:var(--grau); font-size:.82rem; font-style:italic;
            margin-top:2px; }
table.lb{ border-collapse:collapse; width:100%; margin:4px 0 8px;
          font-size:.92rem; }
table.lb th{ background:var(--blau); color:#fff; font-weight:700;
             text-align:left; padding:.35rem .6rem; }
table.lb td{ border:1px solid #d5d8de; padding:.35rem .6rem; vertical-align:top; }
table.lb tr:nth-child(even) td{ background:#f7f8fa; }
table.lb img{ display:block; max-width:100%; height:auto; }
#rail{ position:absolute; top:0; left:0; width:var(--rail); height:100%;
       pointer-events:none; }
.a4mark{ position:absolute; left:0; width:var(--rail);
         display:flex; flex-direction:column; align-items:center; }
.a4mark .tick{ width:0; height:22px; border-left:3px solid var(--blau); }
.a4mark .num{ font-size:.95rem; font-weight:700; color:var(--blau);
              background:#fff; padding:1px 4px; border-radius:4px;
              font-variant-numeric:tabular-nums; }
@media print{
  @page{ size:A4; margin:12mm; }
  body{ background:#fff; }
  .page{ max-width:none; padding:0; box-shadow:none; }
  #rail,.knopf{ display:none; }
  figure,img.shot,table.lb tr{ break-inside:avoid; }
  h2,h3,.akzent{ break-after:avoid; }
  h2.deck{ break-before:page; }
  h2.deck:first-of-type{ break-before:auto; }
}
"""

# Durchgehendes PDF: eine Seite so hoch wie das ganze Dokument. Chrome nimmt die
# @page-Groesse, die beim Oeffnen des Druckdialogs gilt — also erst messen, Regel
# setzen, dann drucken. Grenze ist 200 Zoll (5080 mm); darueber faellt der Druck
# auf A4 zurueck, sonst schneidet der Browser stillschweigend ab.
DRUCK_JS = """
function lbDruck(){ window.print(); }
"""

# A4-Marker alle ~1122px am linken Rand (Resume-Hilfe, "ungefaehr").
RAIL_JS = """
(function(){
  var A4=1122, rail=document.getElementById('rail'),
      page=document.querySelector('.page');
  function draw(){
    rail.innerHTML='';
    var n=Math.ceil(page.scrollHeight/A4);
    for(var i=0;i<n;i++){
      var m=document.createElement('div'); m.className='a4mark';
      m.style.top=(i*A4)+'px';
      m.innerHTML='<span class="num">'+(i+1)+'</span><span class="tick"></span>';
      rail.appendChild(m);
    }
  }
  window.addEventListener('load',draw);
  window.addEventListener('resize',draw);
})();
"""


class LernblattHTML:
    def __init__(self, titel, img_dir="."):
        """`titel` ist der Fachname, sonst nichts. Dozent, Quelle und
        Ground-Truth-Hinweis gehoeren nicht aufs Blatt — sie kosten die erste
        Zeile und helfen beim Lernen nicht. Woher ein Abschnitt stammt, sagt der
        Foliensatz-Trenner `h_deck`."""
        self.titel = titel
        self.img_dir = img_dir
        self.body = []
        self.bilder = set()  # benutzte Bildpfade, fuer den Bericht in save()
        self._li = []  # offene Bullet-Liste puffern

    def _flush(self):
        if self._li:
            self.body.append('<ul class="text">' + "".join(self._li) + "</ul>")
            self._li = []

    def h_deck(self, t):
        """Trenner je Vorlesung. Ohne ihn verschwimmen mehrere Foliensaetze in
        einem Blatt zu einem Strom — beim Lernen will man wissen, aus welcher
        Vorlesung ein Abschnitt kommt. Nur der Foliensatz-Name, kein Zusatz."""
        self._flush()
        self.body.append(f'<h2 class="deck">{t}</h2>')

    def h_topic(self, t):
        self._flush()
        self.body.append(f"<h3>{t}</h3>")

    def kern(self, t):
        self._flush()
        self.body.append(f'<p class="kern">{t}</p>')

    def sublabel(self, t):
        self._flush()
        self.body.append(f'<p class="sublabel">{t}</p>')

    def para(self, t):
        self._flush()
        self.body.append(f'<p class="text">{t}</p>')

    def akzent(self, t):
        self._flush()
        self.body.append(f'<p class="akzent">{t}</p>')

    def formel(self, mathml, aria="Formel"):
        """MathML als gesetzte Formel. Browser rendern es offline ohne JS-Bibliothek."""
        self._flush()
        self.body.append(
            '<div class="formel"><math xmlns="http://www.w3.org/1998/Math/MathML" '
            f'display="block" aria-label="{html.escape(aria)}">{mathml}</math></div>'
        )

    def glossar(self, term, definition):
        """Bullet mit fettem Begriff, Definition umgebrochen in die Zeile darunter.

        Der Punkt bleibt am Begriff, die Erklaerung rueckt darunter ein. So bildet
        die linke Kante eine Spalte aus Begriffen, die man senkrecht abscannen kann,
        statt sie aus Fliesstext herauszusuchen.
        """
        self._li.append(f'<li><b>{term}</b><span class="def">{definition}</span></li>')

    def bullet(self, text, color=None):
        # Labels before a colon are always study anchors, not disposable prose.
        m = re.match(r"^(?!<)([^:<>]{1,80}:)(.*)$", text, re.S)
        if m:
            text = f"<b>{m.group(1)}</b>{m.group(2)}"
        cls = ' class="red"' if color == "red" else ""
        self._li.append(f"<li{cls}>{text}</li>")

    def img_tag(self, fname, width=None, alt="", anteil=None):
        """<img> mit Platzhalter statt Bilddaten — auch fuer eine Tabellenzelle.

        Der echte `src` kommt erst in `save()` rein: normal ein relativer Pfad,
        mit `bundle=True` ein data:-URI. Warum nicht direkt base64: eine Seite mit
        fuenf Screenshots wird so 631 KB gross. Das ist auf der Platte egal, aber
        die Datei ist dann nicht mehr lesbar — wer sie oeffnet, zieht sich rund
        160.000 Token Bildmuell in den Context. Mit externen Bildern sind es 12 KB.

        `anteil` ist der Breitenanteil, den die Grafik auf der Folie hatte
        (lernblatt crop gibt ihn aus). Nimmt ein Bild auf der Folie ein Drittel
        der Breite ein, soll es das im Lernblatt auch — auf volle Spaltenbreite
        aufgeblasen wirkt eine Randgrafik wichtiger als sie ist und frisst eine
        halbe Seite. Nie ueber die native Pixelbreite hinaus, sonst wird es
        unscharf.
        """
        p = fname if os.path.isabs(fname) else os.path.join(self.img_dir, fname)
        w, _ = Image.open(p).size  # nur die Breite, lokal, gratis
        cap = min(width, w) if width else w
        pct = f",{round(anteil * 100)}%" if anteil else ""
        mw = f"min({cap}px{pct})" if pct else f"{cap}px"
        self.bilder.add(p)
        return (
            f'<img class="shot" alt="{html.escape(alt)}" '
            f'style="max-width:{mw}" src="{IMG_MARKE}{p}{IMG_MARKE}">'
        )

    def pic(self, fname, width=None, alt="", anteil=None, hinweis=None):
        """Bild als eigene Abbildung. `anteil` siehe img_tag.

        `hinweis` nur setzen, wenn das Bild NICHT von den Folien stammt (selbst
        gezeichnet oder recherchiert) — Folien-Screenshots bleiben ohne Caption,
        so bleibt sichtbar, was Vorlesungsstoff ist und was Zutat. Halt ihn auf
        einen Halbsatz: er erklaert die Herkunft, nicht den Inhalt.
        """
        self._flush()
        cap = f"<figcaption>{html.escape(hinweis)}</figcaption>" if hinweis else ""
        self.body.append(f"<figure>{self.img_tag(fname, width, alt, anteil)}{cap}</figure>")

    def tabelle(self, kopf, zeilen):
        """Tabelle aus Kopfzeile und Zeilen. Zellen duerfen HTML enthalten —
        `img_tag()` setzt ein Bild hinein. Eine Zuordnung (Verfahren -> Paradigma
        -> Beispiel -> Grafik) liest sich als Tabelle deutlich schneller als als
        Fliesstext, und genau danach fragen die Notizen im PDF meistens.
        """
        self._flush()
        k = "".join(f"<th>{c}</th>" for c in kopf)
        z = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in zeilen)
        self.body.append(f'<table class="lb"><thead><tr>{k}</tr></thead><tbody>{z}</tbody></table>')

    def raw(self, markup):
        """Roh-HTML, z.B. ein inline-SVG. Sparsam nutzen — alles, wofuer es oben
        eine Methode gibt, gehoert dorthin, sonst driftet der Stil auseinander."""
        self._flush()
        self.body.append(markup)

    def html(self, basis=None, bundle=False):
        """Fertiges HTML. `basis` = Ordner, relativ zu dem die Bilder verlinkt
        werden. `bundle=True` bettet sie stattdessen als data:-URI ein."""
        self._flush()
        knopf = (
            '<div class="knopf">'
            '<button onclick="lbDruck()" title="Druckdialog für A4 öffnen">A4</button></div>'
        )
        doc = (
            f'<!doctype html>\n<html lang="de"><head><meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{html.escape(self.titel)}</title>\n<style>{CSS}</style>\n"
            f"</head>\n"
            f'<body>\n{knopf}\n<div class="page">\n<div id="rail"></div>\n'
            f"<h1>{self.titel}</h1>\n"
            + "\n".join(self.body)
            + f"\n</div>\n<script>{DRUCK_JS}{RAIL_JS}</script>\n</body></html>"
        )

        def src(m):
            p = m.group(1)
            if bundle:
                return f"data:image/png;base64,{b64_of(p)}"
            try:
                ziel = os.path.relpath(p, basis or ".").replace(os.sep, "/")
            except ValueError:
                # Bild und .html auf verschiedenen Laufwerken — dann gibt es keinen
                # relativen Pfad. Absolut verlinken ist haesslich, aber die Seite
                # zeigt Bilder statt kaputter Icons.
                ziel = "file:///" + os.path.abspath(p).replace(os.sep, "/")
            return html.escape(ziel)

        return re.sub(f"{IMG_MARKE}(.*?){IMG_MARKE}", src, doc, flags=re.S)

    def save(self, out_path, bundle=False):
        """Schreibt die Datei und meldet ihre Groesse.

        Ohne `bundle` liegen die Bilder daneben und werden relativ verlinkt — die
        .html bleibt bei rund 12 KB und damit lesbar. `bundle=True` erzeugt die
        Ein-Datei-Fassung zum Verschicken; die ist um ein Vielfaches groesser und
        soll niemand mehr oeffnen ausser einem Browser.
        """
        out_path = os.path.abspath(out_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        doc = self.html(os.path.dirname(out_path), bundle)
        open(out_path, "w", encoding="utf-8").write(doc)
        kb = len(doc.encode()) / 1024
        art = "eingebettet" if bundle else f"{len(self.bilder)} Bilder verlinkt"
        print(f"{out_path}  {kb:.0f} KB  ({art})")
        return out_path


def _selftest():
    import shutil

    tmp = os.path.join(os.environ.get("TEMP", "."), "lb_selftest")
    bild = os.path.join(tmp, "bilder")
    os.makedirs(bild, exist_ok=True)
    Image.new("RGB", (400, 200), "white").save(os.path.join(bild, "x.png"))

    lb = LernblattHTML("T", img_dir=bild)
    lb.h_deck("Deck 01")
    lb.h_topic("Thema")
    lb.glossar("a", "b")  # Bullet, Definition umgebrochen
    lb.bullet("c")  # glossar + bullet -> ein <ul>
    lb.formel("<mrow><mi>x</mi><mo>=</mo><mn>1</mn></mrow>", "x gleich 1")
    lb.pic("x.png", anteil=0.5)
    lb.tabelle(["K"], [[lb.img_tag("x.png", 100)]])

    a = open(lb.save(os.path.join(tmp, "a.html")), encoding="utf-8").read()
    b = open(lb.save(os.path.join(tmp, "b.html"), bundle=True), encoding="utf-8").read()
    assert 'src="bilder/x.png"' in a, a[a.find("<img") :][:120]
    assert "base64," not in a, "verlinkte Fassung enthaelt doch Bilddaten"
    assert "data:image/png;base64," in b
    assert a.count("<ul") == 1 and a.count("<li") == 2, "nicht eine gemeinsame Liste"
    assert '<li><b>a</b><span class="def">b</span></li>' in a, "Glossar-Form falsch"
    assert "max-width:min(400px,50%)" in a, "anteil nicht gesetzt"
    assert '<h2 class="deck">' in a and "<h3>" in a
    assert '<div class="formel"><math' in a and "<mi>x</mi>" in a, "MathML fehlt"
    assert "lbDruck()" in a, "Druckknopf fehlt"
    assert "durchgehend" not in a, "Einseiten-Druck ist noch enthalten"
    faktor = len(b) / len(a)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"selftest ok - verlinkt {len(a) / 1024:.1f} KB, gebuendelt {faktor:.0f}x so gross")


if __name__ == "__main__":
    _selftest()
