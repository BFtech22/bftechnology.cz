#!/usr/bin/env python3
# coding: utf-8
"""
Prepise <img> na <picture> se srcset tam, kde k obrazku existuji varianty
vygenerovane skriptem nastroje/generuj-obrazky.py.

Skript je idempotentni — obrazky, ktere uz jsou v <picture>, preskakuje,
takze se da pustit znovu po pridani nove fotky.

Poradi (generuj-reference musi bezet DRIV, protoze prepisuje cele detailni
stranky ze sablony a <picture> by z nich smazal):
    1. python3 nastroje/generuj-obrazky.py
    2. python3 nastroje/generuj-reference.py
    3. python3 nastroje/generuj-picture.py

Spousti se z korene repozitare.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Atribut sizes podle toho, jak siroky je obrazek ve skutecnem layoutu.
# Bez nej by prohlizec pocital se 100vw a stahoval zbytecne velkou variantu.
SIZES = [
    (r'class="ph"',        "(max-width: 980px) 100vw, 33vw"),   # karty v galeriich
    (r'class="ref-foto"',  "(max-width: 980px) 100vw, 50vw"),   # fotka na detailu realizace
    (r'class="tier-photo"', "(max-width: 980px) 100vw, 33vw"),  # renders u ceniku
    (r'class="photo"',     "100vw"),                            # hero
    (r'class="brand"',     "180px"),                            # logo v hlavicce
    (r'class="logo-cell"', "200px"),                            # logo v paticce
]
VYCHOZI_SIZES = "(max-width: 980px) 100vw, 33vw"


def varianty(cesta_v_repu):
    """Vraci {sirka: {'webp': cesta, 'orig': cesta}} pro dany zdrojovy obrazek."""
    zdroj = ROOT / cesta_v_repu
    if not zdroj.exists():
        return {}
    from PIL import Image
    with Image.open(zdroj) as im:
        puvodni = im.width

    out = {}
    for soubor in sorted(zdroj.parent.glob(zdroj.stem + "*")):
        if soubor.stem == zdroj.stem:
            # stejny nazev, jina pripona = varianta v puvodni sirce (.webp)
            m_sirka = puvodni
        else:
            m = re.fullmatch(re.escape(zdroj.stem) + r"-(\d+)", soubor.stem)
            if not m:
                continue
            m_sirka = int(m.group(1))
        klic = "webp" if soubor.suffix == ".webp" else "orig"
        if soubor.suffix not in (".webp", zdroj.suffix):
            continue
        out.setdefault(m_sirka, {})[klic] = soubor
    return {w: v for w, v in out.items() if "webp" in v}


def srcset(mapa, klic, adresar_prefix):
    kusy = []
    for sirka in sorted(mapa):
        soubor = mapa[sirka].get(klic)
        if soubor:
            kusy.append(f"{adresar_prefix}{soubor.relative_to(ROOT).as_posix()} {sirka}w")
    return ", ".join(kusy)


def zvol_sizes(html, pozice):
    """Najde nejblizsi obalovy element pred obrazkem a podle nej vybere sizes."""
    okoli = html[max(0, pozice - 400):pozice]
    nejlepsi, kde = VYCHOZI_SIZES, -1
    for vzor, hodnota in SIZES:
        i = okoli.rfind(vzor)
        if i > kde:
            kde, nejlepsi = i, hodnota
    return nejlepsi


def preved(soubor):
    html = soubor.read_text()
    prefix = "../../" if soubor.parent != ROOT else ""
    zmen = 0

    def sub(m):
        nonlocal zmen
        cely = m.group(0)
        src = m.group(1)
        # uz obalene v <picture> nebo cesta, kterou neumime prelozit
        if "${" in src:
            return cely
        pred = html[max(0, m.start() - 220):m.start()]
        if "<picture>" in pred and "</picture>" not in pred:
            return cely

        cesta = src[len(prefix):] if prefix and src.startswith(prefix) else src
        mapa = varianty(cesta)
        if len(mapa) < 2:
            return cely

        s = zvol_sizes(html, m.start())
        webp = srcset(mapa, "webp", prefix)
        orig = srcset(mapa, "orig", prefix)

        img = cely
        # Kdyz zdroj neni mezi variantami (logo — zdroj ma pres 4000 px, ale
        # zobrazuje se v par stovkach), prepiseme i src a rozmery na nejvetsi
        # variantu. Jinak by zaloha pro prohlizec bez WebP stahovala original.
        from PIL import Image
        nejvetsi = max(mapa)
        if not (ROOT / cesta).stat() or nejvetsi != Image.open(ROOT / cesta).width:
            nahrada = mapa[nejvetsi].get("orig")
            if nahrada:
                nova_cesta = prefix + nahrada.relative_to(ROOT).as_posix()
                img = img.replace(f'src="{src}"', f'src="{nova_cesta}"')
                with Image.open(nahrada) as im2:
                    img = re.sub(r'width="\d+" height="\d+"',
                                 f'width="{im2.width}" height="{im2.height}"', img)
        if orig:
            img = img[:-1] + f' srcset="{orig}" sizes="{s}">' 
        zmen += 1
        return (f'<picture>\n          <source type="image/webp" srcset="{webp}" sizes="{s}">\n'
                f'          {img}\n        </picture>')

    novy = re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', sub, html)
    if zmen:
        soubor.write_text(novy)
    return zmen


def main():
    celkem = 0
    for f in sorted(ROOT.glob("*.html")) + sorted(ROOT.glob("reference/*/index.html")):
        n = preved(f)
        celkem += n
        if n:
            print(f"{f.relative_to(ROOT)}: {n}")
    print(f"\ncelkem prevedeno obrazku: {celkem}")


if __name__ == "__main__":
    main()
