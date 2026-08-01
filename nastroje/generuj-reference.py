#!/usr/bin/env python3
# coding: utf-8
"""
Generator detailnich stranek referenci + sitemap.xml.

Proc skript a ne rucne psane stranky:
  - hlavicka a paticka jsou na statickem hostingu duplikovane v kazdem souboru;
    u dvaceti dalsich stranek uz to rucne udrzovat nejde. Skript si hlavicku
    i paticku vytahne z kontakt.html a prepise v ni relativni cesty o dve urovne
    vys, takze po zmene menu staci spustit tenhle soubor znovu.

Co dela:
  1. z foto/insta/posts.json vygeneruje reference/<slug>/index.html pro kazdou
     realizaci, ktera ma v tabulce SLUGY svuj slug (tj. zna se lokalita),
  2. v galeriich na vsech strankach prepise odkazy karet z Instagramu na detail
     realizace (karty bez detailu zustavaji na Instagram),
  3. vygeneruje sitemap.xml pro cely web.

Spousti se z korene repozitare:  python3 nastroje/generuj-reference.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.bftechnology.cz"

# Slug = URL detailu. Klic je "code" z posts.json.
# Zaznamy, ktere tu nejsou, detailni stranku nedostanou — typicky proto, ze
# u nich neznáme lokalitu ("Bytový dům" bez mesta), takze by z toho vznikla
# prazdna stranka bez informacni hodnoty.
SLUGY = {
    "vysonin-999kwp":  "fve-vysonin-999-kwp",
    "DZjcImrIds9":     "fve-novy-bor-11-kwp",
    "DZH5j6RIC-B":     "fve-varnsdorf-prumyslovy-objekt-50-kwp",
    "DY7BKuXIYuj":     "fve-krasna-lipa-12-kwp",
    "DWPNIuaiGWk":     "fve-tachov-223-kwp",
    "DNkObx4M7ZB":     "bytovy-dum-decin-krizove-bydleni-12-kwp",
    "DMtEi22uOE1":     "fve-rumburk-10-kwp",
    "DMP3SU-t2fi":     "fve-stare-krecany-22-kwp",
    "DLaDVkdNRE5":     "bytovy-dum-rumburk-13-kwp",
    "krasna-lipa-19-3kwp": "fve-krasna-lipa-19-kwp",
    "DKMSx5tNauK":     "fve-krasna-lipa-10-kwp",
    "DJ6usuEMCbJ":     "smartflower-praha-dvorakovo-nabrezi",
    "DJvqYbTMoux":     "fve-rumburk-heckl-25-kwp",
    "DEVlmJxO2zQ":     "fve-zakladni-skola-varnsdorf-11-kwp",
    "DDP99mJu1Em":     "fve-jilove-10-kwp",
    "DDEwia7u-H8":     "fve-rozany-stary-mlyn-12-kwp",
    "DB81wiANldf":     "bytovy-dum-varnsdorf-36-kwp",
    "DAjjt43OpSU":     "fve-kemp-decin-48-kwp",
    "C8u8Ap8O0C5":     "fve-vlci-hora-21-kwp",
    "C75tEOGN5q2":     "bytovy-dum-dolni-podluzi-42-kwp",
    "C7ErmKxNVE0":     "fve-nova-oleska-10-kwp",
    "C6CQkqpN_iO":     "ohrev-vody-2-6-kwp",
    "C5jSy7LtMoC":     "ohrev-vody-rumburk-rodinny-dum",
    "C5fNscQNfg7":     "ohrev-vody-rumburk-bojler",
    "CzrrrDXNkYI":     "fve-rumburk-prumyslova-strecha-39-kwp",
}

SEGMENTY = {
    "rodinne-domy": ("Rodinné domy",       "fotovoltaika-rodinne-domy.html"),
    "bytove-domy":  ("Bytové domy",        "bytove-domy.html"),
    "firmy":        ("Firmy a průmysl",    "fotovoltaika-firmy.html"),
    "ohrev-vody":   ("Ohřev vody",         "ohrev-vody.html"),
}

MESICE = ["", "ledna", "února", "března", "dubna", "května", "června",
          "července", "srpna", "září", "října", "listopadu", "prosince"]

# Stranky, ve kterych se prepisuji odkazy galerii a ktere jdou do sitemapy.
STRANKY = [
    "index.html", "fotovoltaika-rodinne-domy.html", "bytove-domy.html",
    "fotovoltaika-firmy.html", "bateriova-uloziste.html", "ohrev-vody.html",
    "simulacni-zkousky-rfg.html", "inzenyrske-sluzby.html", "reference.html",
    "kontakt.html", "zasady-zpracovani-osobnich-udaju.html",
]


def nacti_posts():
    return json.loads((ROOT / "foto/insta/posts.json").read_text())


def sablona_ram():
    """Hlavicka + paticka z kontakt.html s cestami prepsanymi o dve urovne vys."""
    # reference.html a ne kontakt.html: kontakt ma pod patickou jeste
    # <script src="assets/form.js">, ktery na detailu realizace nema co delat.
    src = (ROOT / "reference.html").read_text()

    hlavicka = src[src.index("<!-- HEADER -->"):src.index("<section class=\"block\">")]
    paticka = src[src.index("<!-- FOOTER -->"):src.index("<!-- Rozbalovací menu -->")]

    def nahoru(html):
        html = re.sub(r'(href|src)="([a-z0-9][a-z0-9._-]*\.(?:html|png|jpg|css|js))', r'\1="../../\2', html)
        html = re.sub(r'(href|src)="(assets/|foto/)', r'\1="../../\2', html)
        return html

    hlavicka = nahoru(hlavicka)
    # Aktivni polozka menu z kontakt.html na detailu referenci nedava smysl.
    hlavicka = hlavicka.replace(' class="active"', '').replace(' class="m-sub active"', ' class="m-sub"')
    hlavicka = hlavicka.replace(' aria-current="page"', '')
    return hlavicka, nahoru(paticka)


def cesky_datum(iso):
    r, m, d = iso.split("-")
    return f"{int(d)}. {MESICE[int(m)]} {r}"


def uloziste(detail):
    """Kapacita baterie z popisu, jen kdyz je tam explicitne uvedena."""
    m = re.search(r"(?:baterie|úložiště|bateriové úložiště)\s+(?:Dyness\s+)?([\d,\.]+)\s*kWh", detail, re.I)
    return f"{m.group(1)} kWh" if m else None


def stranka(p, slug, hlavicka, paticka):
    seg_nazev, seg_soubor = SEGMENTY[p["kategorie"]]
    kwp = p["kwp"]
    bat = uloziste(p["detail"])
    rok = p["date"][:4]
    url = f"{BASE}/reference/{slug}/"
    popis_meta = f"{p['title']}" + (f" — {kwp}" if kwp else "") + f". {p['detail'][0].upper()}{p['detail'][1:]}. Realizace BF technology s.r.o., {rok}."

    dlazdice = []
    if kwp:
        dlazdice.append((kwp, "Výkon elektrárny"))
    if bat:
        dlazdice.append((bat, "Bateriové úložiště"))
    dlazdice.append((rok, "Rok realizace"))

    radky = [
        ("Segment", seg_nazev),
        ("Výkon fotovoltaické elektrárny", kwp or "—"),
        ("Bateriové úložiště", bat or "bez úložiště"),
        ("Co jsme instalovali", p["detail"]),
        ("Dokončeno", cesky_datum(p["date"])),
    ]

    # Pole "url" v posts.json ma tri stavy:
    #   chybi        -> prispevek existuje, odkaz se sklada z kodu
    #   ""           -> realizace nema prispevek na Instagramu
    #   "https://.." -> prispevek existuje pod jinym kodem, nez je nazev fotky
    #                   (typicky u fotek, ktere jsme dostali drive nez vysly na IG)
    ig = ""
    odkaz = p.get("url", None)
    if odkaz != "":
        if not odkaz:
            odkaz = f'https://www.instagram.com/p/{p["code"]}/'
        ig = (f'\n      <p class="ref-ig"><a href="{odkaz}" '
              f'target="_blank" rel="noopener">Zobrazit příspěvek na Instagramu →</a></p>')

    return f"""<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no, viewport-fit=cover">
<title>{p['title']}{' — ' + kwp if kwp else ''} | Reference BF technology</title>
<meta name="description" content="{popis_meta}">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" href="../../assets/favicon.png">

<!-- Open Graph -->
<meta property="og:type" content="article">
<meta property="og:site_name" content="BF technology">
<meta property="og:title" content="{p['title']}{' — ' + kwp if kwp else ''}">
<meta property="og:description" content="{popis_meta}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/foto/insta/{p['code']}.jpg">
<meta property="og:locale" content="cs_CZ">
<meta name="theme-color" content="#3C3C3C">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" rel="stylesheet">

<link rel="stylesheet" href="../../assets/style.css">
</head>

<body>

<!--
  GENEROVANY SOUBOR — needituj rucne.
  Vznikl z foto/insta/posts.json skriptem nastroje/generuj-reference.py.
  Zmeny delej tam a skript pust znovu.
-->

{hlavicka}
<!-- UVOD STRANKY -->
<section class="block">
  <div class="container">
    <nav class="breadcrumb" aria-label="Drobečková navigace">
      <a href="../../index.html">Úvod</a> <span>›</span>
      <a href="../../reference.html">Reference</a> <span>›</span>
      <span aria-current="page">{p['title']}</span>
    </nav>
    <div class="section-head">
      <p class="eyebrow">{seg_nazev}</p>
      <h1>{p['title']}</h1>
      <p>{p['detail'][0].upper()}{p['detail'][1:]}. Realizaci jsme dokončili {cesky_datum(p['date'])} vlastními montážními týmy.</p>
    </div>
  </div>
</section>

<!-- STATS PRUH -->
<div class="stats-band">
  <div class="container grid{' cols-2' if len(dlazdice) == 2 else ''}">
{chr(10).join(f'    <div><div class="num">{h}</div><div class="label">{l}</div></div>' for h, l in dlazdice)}
  </div>
</div>

<!-- DETAIL -->
<section class="block">
  <div class="container">
    <div class="ref-detail">
      <figure class="ref-foto">
        <img src="../../foto/insta/{p['code']}.jpg" alt="{p['title']} — realizace BF technology" width="700" height="525">
      </figure>
      <div class="ref-params">
        <h2>Parametry realizace</h2>
        <dl>
{chr(10).join(f'          <dt>{k}</dt><dd>{v}</dd>' for k, v in radky)}
        </dl>{ig}
      </div>
    </div>

    <div class="seg-note">
      <p>Plánujete něco podobného? Přijedeme se podívat, spočítáme návratnost na vaší reálné spotřebě a dáme vám pevnou cenu.</p>
      <a class="btn btn-primary" href="../../kontakt.html">Chci nezávaznou nabídku</a>
    </div>

    <p class="ref-zpet"><a href="../../reference.html">← Všechny realizace</a> · <a href="../../{seg_soubor}">{seg_nazev}</a></p>
  </div>
</section>

{paticka}
<!-- Rozbalovací menu -->
<script src="../../assets/nav.js"></script>

</body>
</html>
"""


def prepis_odkazy_galerii(mapa):
    """V galeriich prepise href karet z Instagramu na detail realizace."""
    zmeneno = {}
    for f in STRANKY:
        p = ROOT / f
        t = p.read_text()
        orig = t
        hloubka = ""  # vsechny tyhle stranky jsou v koreni
        for code, slug in mapa.items():
            t = t.replace(f'href="https://www.instagram.com/p/{code}/" target="_blank" rel="noopener" title="Otevřít příspěvek na Instagramu"',
                          f'href="{hloubka}reference/{slug}/" title="Detail realizace"')

        # Uz prepsane karty: kdyz se v SLUGY zmeni slug, puvodni odkaz na
        # Instagram uz v souboru neni, na co navazat. Slug proto dopocitavame
        # znovu z kodu fotky uvnitr karty.
        def oprav(m):
            return m.group(1) + f'{hloubka}reference/{mapa[m.group(3)]}/' + m.group(2) if m.group(3) in mapa else m.group(0)

        t = re.sub(r'(<a class="ig-card" href=")[^"]*(" title="Detail realizace">\s*<div class="ph">\s*<img src="[^"]*foto/insta/([^."]+)\.jpg")',
                   oprav, t)

        # Karty realizaci bez prispevku na Instagramu byly staticke <div>.
        # Ted uz maji kam vest, takze z nich delame odkazy na detail.
        def zeStatickeKarty(m):
            telo = m.group(1)
            kod = re.search(r'foto/insta/([^."]+)\.jpg', telo)
            if not kod or kod.group(1) not in mapa:
                return m.group(0)
            return (f'<a class="ig-card" href="{hloubka}reference/{mapa[kod.group(1)]}/" '
                    f'title="Detail realizace">{telo}\n      </a>')

        t = re.sub(r'<div class="ig-card is-static">(.*?)\n      </div>', zeStatickeKarty, t, flags=re.S)

        # Ikona Instagramu na karte, ktera vede na detail realizace, by lhala —
        # odkaz na prispevek je az na detailu.
        t = re.sub(r'(<a class="ig-card" href="[^"]*" title="Detail realizace">.*?)\n\s*<span class="ig-ico">.*?</span>',
                   r'\1', t, flags=re.S)
        if t != orig:
            p.write_text(t)
            zmeneno[f] = orig.count('title="Otevřít příspěvek na Instagramu"') - t.count('title="Otevřít příspěvek na Instagramu"')
    return zmeneno


def sitemap(slugy):
    polozky = [(f"{BASE}/", "1.0")]
    for f in STRANKY:
        if f == "index.html":
            continue
        priorita = "0.4" if f == "zasady-zpracovani-osobnich-udaju.html" else "0.8"
        polozky.append((f"{BASE}/{f}", priorita))
    for slug in sorted(slugy):
        polozky.append((f"{BASE}/reference/{slug}/", "0.6"))

    radky = "\n".join(
        f"  <url><loc>{u}</loc><priority>{pr}</priority></url>" for u, pr in polozky)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f'{radky}\n'
            '</urlset>\n')


def main():
    posts = {p["code"]: p for p in nacti_posts()}
    hlavicka, paticka = sablona_ram()

    mapa = {}
    for code, slug in SLUGY.items():
        if code not in posts:
            print(f"  !! kod {code} neni v posts.json — preskakuji")
            continue
        d = ROOT / "reference" / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(stranka(posts[code], slug, hlavicka, paticka))
        mapa[code] = slug
    print(f"vygenerovano {len(mapa)} detailnich stranek")

    zmeny = prepis_odkazy_galerii(mapa)
    for f, n in zmeny.items():
        print(f"  odkazy v galerii: {f} — prepsano {n}")

    (ROOT / "sitemap.xml").write_text(sitemap(mapa.values()))
    print(f"sitemap.xml — {len(mapa) + len(STRANKY)} URL")

    bez = [p["title"] for c, p in posts.items() if c not in SLUGY and p["kategorie"] != "tym"]
    if bez:
        print("\nbez detailni stranky (chybi lokalita):")
        for b in bez:
            print("  -", b)


if __name__ == "__main__":
    main()
