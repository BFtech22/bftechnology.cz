#!/usr/bin/env python3
# coding: utf-8
"""
Generator WebP variant a zmensenin pro <picture> / srcset.

Proc:
  - JPEG fotky z Instagramu i titulni fotka tvori vetsinu prenesenych dat.
    WebP je pri stejne kvalite o 25-35 % mensi.
  - Bez srcset stahuje mobil stejne velky soubor jako desktop, prestoze karta
    ma na uzkem displeji polovicni sirku.

Co dela:
  ke kazdemu zdroji vyrobi variantu v puvodni sirce a v polovicni sirce,
  a to jak ve WebP, tak (u zmensenin) v puvodnim formatu jako zaloha:

      foto/insta/DZjcImrIds9.jpg      (zdroj, zustava)
      foto/insta/DZjcImrIds9.webp     700w
      foto/insta/DZjcImrIds9-350.webp 350w
      foto/insta/DZjcImrIds9-350.jpg  350w

AVIF se negeneruje – Pillow v tomhle prostredi nema podporu (features.check('avif')
je False). Az bude, staci doplnit format do FORMATY; sablony v generuj-picture.py
uz s dalsim <source> pocitaji.

Spousti se z korene repozitare:  python3 nastroje/generuj-obrazky.py
"""

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

# Zdroje, ke kterym se varianty generuji.
# Jen zdrojove fotky – soubory s priponou "-<sirka>" jsou uz vygenerovane
# varianty a musi se preskocit, jinak by se generovaly varianty variant.
import re as _re
ZDROJE = sorted(f for f in ROOT.glob("foto/insta/*.jpg")
                if not _re.search(r"-\d+$", f.stem)) + [
    ROOT / "assets/title-photo.jpg",
    ROOT / "assets/sestava-fve.jpg",
    ROOT / "assets/sestava-fve-baterie.jpg",
    ROOT / "assets/BFT_LOGO_TRANSPARENT.png",
    ROOT / "assets/BFT_LOGO_WHITE.png",
]

# q75 je u uz jednou zkomprimovaneho JPEGu rozumny kompromis – nize uz jsou
# na fotkach strech videt artefakty kolem ramu panelu.
KVALITA_WEBP = 75
KVALITA_JPEG = 82

# Logo se nikde nezobrazuje siroke – v hlavicce ma 52 px, v paticce 62 px vysky.
# Puvodni soubor ma pres 4000 px, takze mu davame vlastni, mnohem mensi sirky.
SIRKY = {
    "BFT_LOGO_TRANSPARENT.png": (420, 210),
    "BFT_LOGO_WHITE.png": (420, 210),
}


def varianty(zdroj):
    with Image.open(zdroj) as im:
        im.load()
        puvodni_sirka = im.width
        pruhlednost = im.mode in ("RGBA", "LA", "P") and "transparency" in im.info or im.mode == "RGBA"

        sirky = SIRKY.get(zdroj.name) or (puvodni_sirka, max(1, puvodni_sirka // 2))
        vysledky = []

        for sirka in sirky:
            sirka = min(sirka, puvodni_sirka)
            kopie = im.copy()
            if sirka != puvodni_sirka:
                vyska = round(im.height * sirka / im.width)
                kopie = kopie.resize((sirka, vyska), Image.LANCZOS)

            # Priponu s sirkou nese kazda varianta, ktera neni v puvodni sirce.
            # Bez toho by se u loga (ktere zmensujeme vzdy) prepsal zdroj.
            pripona = "" if sirka == puvodni_sirka else f"-{sirka}"
            zaklad = zdroj.with_name(zdroj.stem + pripona)

            webp = zaklad.with_suffix(".webp")
            (kopie if pruhlednost else kopie.convert("RGB")).save(
                webp, "WEBP", quality=KVALITA_WEBP, method=6)
            vysledky.append((webp, sirka, kopie.height))

            # Zaloha v puvodnim formatu pro prohlizece bez WebP. U puvodni
            # sirky uz v repozitari je – je to zdrojovy soubor.
            if sirka != puvodni_sirka:
                zaloha = zaklad.with_suffix(zdroj.suffix)
                if zdroj.suffix.lower() in (".jpg", ".jpeg"):
                    kopie.convert("RGB").save(zaloha, "JPEG", quality=KVALITA_JPEG,
                                              optimize=True, progressive=True)
                else:
                    kopie.save(zaloha, optimize=True)
                vysledky.append((zaloha, sirka, kopie.height))

        return vysledky


def main():
    pred = po = 0
    for zdroj in ZDROJE:
        if not zdroj.exists():
            print(f"  !! chybi {zdroj.relative_to(ROOT)}")
            continue
        pred += zdroj.stat().st_size
        for soubor, w, h in varianty(zdroj):
            po += soubor.stat().st_size
        print(f"{zdroj.relative_to(ROOT)}")

    print(f"\nzdroje: {pred/1024/1024:.1f} MB   nove varianty: {po/1024/1024:.1f} MB")


if __name__ == "__main__":
    sys.exit(main())
