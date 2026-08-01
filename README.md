# www.bftechnology.cz

Nový firemní web BF technology s.r.o. — statický web, aktuálně se rozšiřuje
z jednostránky na víc stránek (domovská jako rozcestník + tematické podstránky).
Barvy a typografii sdílí s cenovými nabídkami (bft_nabidka_html): Roboto,
BFT zelená `#8BB855`, žlutá `#FAB21A`, tmavě šedá `#3C3C3C`.

Hero je záměrně **webový, ne jako titulka nabídky**: logo je jen jednou (v hlavičce),
fotka zůstává čitelná pod jemným tmavým gradientem zleva a pod herem následuje
tmavý stats pruh. Sekce níž (karty služeb, tmavý pruh Dodavatel/Kontakty, pole
formuláře) jazyk nabídky drží dál.

> Tenhle README je technická dokumentace webu. Pracovní poznámky se do
> repozitáře nedávají — jsou v souboru uvedeném v `.gitignore`.

## Struktura

```
.
├── index.html                      # domovská (JS inline, styly už ne)
├── fotovoltaika-firmy.html         # firmy a průmysl 2–999 kWp
├── fotovoltaika-rodinne-domy.html  # rodinné domy
├── bytove-domy.html               # bytové domy (FO majitel, SVJ i družstvo)
├── simulacni-zkousky-rfg.html     # ověření souladu RfG — samostatná SEO stránka
├── bateriova-uloziste.html         # baterie 10 kWh – 5 MWh
├── ohrev-vody.html                 # fotovoltaický ohřev vody
├── inzenyrske-sluzby.html          # RfG simulace, řízení a monitoring, VN a trafostanice
├── kontakt.html                    # kontakt + formulář
├── reference.html                  # všechny realizace podle segmentu
├── zasady-zpracovani-osobnich-udaju.html  # GDPR — správce, účely, doba, příjemci, práva
├── robots.txt              # ZATÍM ZAKAZUJE procházení (staging), viz níže
├── 404.html                # chybová stránka (GitHub Pages ji servíruje sama)
├── sitemap.xml             # GENEROVANÁ, viz nastroje/generuj-reference.py
├── reference/<slug>/index.html  # GENEROVANÉ detaily realizací (25 stránek)
├── nastroje/
│   └── generuj-reference.py  # generuje reference/, přepisuje odkazy galerií, píše sitemap
├── CNAME.disabled          # vlastní doména — ZÁMĚRNĚ neaktivní, viz níže
├── POZNAMKY-INTERNI.md     # pracovní poznámky, v .gitignore (není v repu)
├── assets/
│   ├── style.css       # VŠECHNY styly (sdílené všemi stránkami)
│   ├── form.js         # odeslání kontaktního formuláře (index + kontakt)
│   ├── nav.js          # rozbalovací menu Fotovoltaika (všechny stránky)
│   ├── BFT_LOGO_TRANSPARENT.png
│   ├── BFT_LOGO_WHITE.png
│   ├── favicon.png
│   └── title-photo.jpg # titulní fotka z nabídky (hero + pozadí kontaktu)
└── foto/insta/         # reference z Instagramu (#FVE)
    ├── <shortcode>.jpg # 16 fotek postů (640px čtverce)
    └── posts.json      # metadata postů (kód, datum, titulek, kWp, detail, zdroj)
```

### Sdílené CSS

Styly byly vytaženy z `index.html` do `assets/style.css` — mění se **na jednom
místě pro celý web**. V `index.html` zůstává inline jen JS (insta lišta, taby
ceníku, akordeon FAQ).

Pro podstránky, které nemají hero, nese hlavní nadpis `.section-head h1`
(stejný vzhled jako `h2` včetně zeleného podtržení). Střídání pozadí sekcí
řeší `section.block.alt` (krémové) — domovská používá starší pojmenované
třídy `.why` a `.pricing`, ty zůstávají.

### Hlavička a patička se duplikují

Hosting je statický bez PHP a bez build kroku, takže `<header>`, mobilní menu
a `<footer>` jsou **zkopírované v každé stránce**. Při změně menu, telefonu,
adresy nebo odkazů v patičce je nutné projít všechny `.html` v korenu:

- `index.html`
- `fotovoltaika-firmy.html`
- `fotovoltaika-rodinne-domy.html`
- `bytove-domy.html`
- `simulacni-zkousky-rfg.html`
- `bateriova-uloziste.html`
- `ohrev-vody.html`
- `inzenyrske-sluzby.html`
- `kontakt.html`
- `reference.html`
- `zasady-zpracovani-osobnich-udaju.html`

Detaily realizací v `reference/<slug>/` se **needitují ručně** — hlavičku
i patičku si berou z `reference.html` a generují se skriptem. Po zásahu do menu
nebo patičky spusť z kořene repozitáře:

```
python3 nastroje/generuj-reference.py
```

Na podstránkách míří odkazy v menu na `index.html#…`, na domovské zůstávají
jako `#…`. Při kopírování hlavičky na novou podstránku tohle nezapomenout přepsat.

Podstránky `reference`, `fotovoltaika-rodinne-domy` a `bytove-domy-svj` byly
vygenerovány skriptem, který drží hlavičku a patičku v jednom zdroji. Skript není
součástí repozitáře (běžel jednorázově) — od té chvíle se stránky editují ručně.

### Navigace

Segmentová struktura — hlavní položka **Fotovoltaika** se rozbaluje:

```
Fotovoltaika ▾ ── Rodinné domy
               ├─ Bytové domy a SVJ
               ├─ Firmy a průmysl
               ├─ Fotovoltaický ohřev vody
               └─ Inženýrské služby
Bateriová úložiště | Ceník | Reference | Dotazy | Kontakt   + CTA
```

Rozbalování řeší CSS (`:hover` a `:focus-within`) **a** `assets/nav.js`. Bez JS
je menu použitelné na myši i klávesnici; skript přidává to, co CSS neumí —
otevření **klikem na dotykových zařízeních** (kde hover neexistuje), pravdivý
stav `aria-expanded`, zavření Escapem a klikem mimo. Otevřený stav = třída
`.open` na `.has-sub`.

Aktivní stav: podpoložka má `class="active"` + `aria-current="page"`, nadřazená
„Fotovoltaika" dostane `class="is-active"` (zezelená a podtrhne se).

Na mobilu se dropdown rozpadne do plochého seznamu s popisky skupin
(`.m-group`) a odsazenými podpoložkami (`.m-sub`) — žádné rozbalování.
Menu je vyšší než displej (na 375×812 asi 908 px), scrolluje se
(`overflow-y: auto` na `.mobile-menu`).

> **Přepnutí na hamburger je na 1080 px**, ne na 980 px jako ostatní mřížky.
> Po přidání rozbalovací položky je menu širší a mezi 980 a 1080 px se už
> mačkalo k logu (mezera pod 20 px). Je to samostatný `@media` blok.

Pozor na jednu výjimku: na **domovské** vede „Kontakt" i CTA na `#kontakt`,
protože formulář je hned na téže stránce. Na všech podstránkách vedou na
`kontakt.html`. Je to záměr, ne nedopatření.

### Skupina BFK systems + BF technology

Web patří **BF technology** (menší a flexibilní instalace, 2–999 kWp). Sesterská
**BFK systems** (IČO 23571853, stejné sídlo i telefon) dělá rozsáhlé a
technologicky náročné projekty — MWp elektrárny, BESS s vlastní EMS, ověřování
souladu výrobních modulů (RfG), dispečerské řízení, VN projekty a trafostanice,
průmyslovou automatizaci. Sekce `#skupina` na domovské a na stránce pro firmy to
vysvětluje a odkazuje na `BFKsystems.cz`.

FVE Vysonín (999 kWp + trafostanice, 2026) je projekt BFK systems, proto je na
stránce pro firmy uveden jako projekt skupiny. Odtud se bere i horní hranice
rozsahu „do 999 kWp".

### Fotky realizací

`foto/insta/posts.json` má u každého postu pole `kategorie`:
`rodinne-domy` (5), `bytove-domy` (6), `firmy` (4), `tym` (1). Podle něj se
skládají galerie na podstránkách — karty jsou v HTML **staticky**, aby je viděly
vyhledávače (lišta na domovské se naopak generuje z JS pole `INSTA_POSTS`).

Post `DV_7R2siK9j` (28,3 kWp, baterie 30 kWh) je zařazen jako bytový dům.

### Recenze (sekce `#recenze` na domovské)

Agregovaná čísla z veřejného profilu na
<https://refsite.info/companies/bf-technology/reviews> — **99 %, 16 ověřených
recenzí, 16 z 16 doporučuje**, stav 30. 7. 2026. Datum je i v textu pod čísly,
při aktualizaci ho nezapomenout přepsat.

Zobrazují se pouze agregovaná čísla a odkaz na zdroj, ne texty jednotlivých
recenzí.

### Nasazení na GitHub Pages

Web běží na Pages z branche `main`, složka `/ (root)`. Náhledová adresa:
<https://bftech22.github.io/bftechnology.cz/>

**Vlastní doména je zatím vypnutá.** Soubor s doménou je pojmenovaný
`CNAME.disabled`, aby si ho Pages nevšimly — jinak by náhledová adresa
přesměrovávala na `www.bftechnology.cz`, kde běží ještě starý web.

Až se bude přepínat doména:

1. `git mv CNAME.disabled CNAME` a pushnout
2. v *Settings → Pages* zkontrolovat, že se doména nastavila
3. u registrátora (DNS spravuje **Webglobe**) přesměrovat `www` na
   `bftech22.github.io`
4. zapnout *Enforce HTTPS*, až se DNS propíše

> Pozor: na `www.bftechnology.cz` **běží funkční starý web** (IP
> `195.181.248.157`, hosting Webglobe). Přepnutím DNS přestane být dostupný —
> předem zazálohovat. Alternativa: nový web nahrát na stávající hosting přes
> FTP a s DNS nehýbat vůbec.

Kanonické odkazy (`<link rel="canonical">`) a `og:url` na všech stránkách míří
na `https://www.bftechnology.cz/…`. Na náhledové adrese tedy ukazují „jinam" —
u krátkodobého náhledu to nevadí, před spuštěním na vlastní doméně to bude
správně.

### Plánované

Stránky na jednotlivé projekty (`reference/<projekt>`), kalkulačka návratnosti.

### Kontaktní formulář — Web3Forms

Formulář v sekci `#kontakt` odesílá přes **[Web3Forms](https://web3forms.com)**,
protože statický hosting neumí PHP. Odesílá se `fetch()`em na
`https://api.web3forms.com/submit`, uživatel zůstane na stránce a výsledek se
vypíše do `#contact-status` (třídy `ok` / `err`).

`access_key` je vyplněný (`91503d4e-…`) v `index.html` **i** v `kontakt.html`.
Patří k účtu na <https://app.web3forms.com/dashboard> — **tam** se nastavuje
e-mail, na který zprávy chodí, v kódu to není. Když by klíč chyběl nebo zůstal
zástupný, `assets/form.js` to napíše do konzole prohlížeče.

Detaily řešení:

- honeypot je `<input type="checkbox" name="botcheck">` — Web3Forms ho zpracuje
  nativně (dřív to bylo textové pole `website`, které řešil `send.php`)
- skryté pole `redirect` je záložní cesta pro prohlížeč bez JS: proběhne klasický
  POST a Web3Forms vrátí uživatele na `https://www.bftechnology.cz/?sent=1#kontakt`,
  kde se stav vypíše z URL
- e-mail, na který zprávy chodí, se nastavuje v dashboardu Web3Forms u daného
  klíče, **ne v kódu**

Původní `send.php` (PHP `mail()`) byl odstraněn — na statickém hostingu nemá co
dělat.

Skript `assets/form.js` je sdílený domovskou stránkou a `kontakt.html` — obě
mají formulář se stejným `id="contact-form"` a prvkem `#contact-status`.

**Web3Forms je z pohledu GDPR zpracovatel** — přes jeho API tečou jméno, telefon,
e-mail a text zprávy. Proto text pod formulářem službu jmenuje a odkazuje na
`zasady-zpracovani-osobnich-udaju.html`. Dřívější věta „Údaje nepředáváme třetím
stranám" byla zavádějící a je pryč. Zpracování stojí na krocích před uzavřením
smlouvy (čl. 6 odst. 1 písm. b GDPR), **ne na souhlasu** — souhlas si necháváme
odděleně pro marketing a pro zveřejnění fotek z realizace. Když se změní
poskytovatel formuláře, musí se změnit i bod 5 v zásadách.

## Ceník (sekce `#ceny`)

Taby segmentů — **Rodinné domy** (tři varianty + ohřev vody), **Bytové domy a SVJ**
a **Firmy a průmysl** (reálné realizace z IG + výzva k individuální kalkulaci).
Taby jsou přístupné z klávesnice (šipky vlevo/vpravo), přepínání řeší `segmentTabs()`.

Varianty pro rodinné domy — **Start** (4,5 kWp, od 189 tis.), **Optimal**
(10 kWp + 10 kWh, od 329 tis.) a **Max** (13 kWp + 15 kWh, od 379 tis.).
Každá má nad hlavičkou kompozici z produktových fotek v rámečku
`.tier-photo` (poměr 16:10, `object-fit: contain`):
`assets/sestava-fve.jpg` (panel + střídač) u varianty Start,
`assets/sestava-fve-baterie.jpg` (panel + střídač + baterie) u Optimal
a Max. Obrázky jsou v poměru **16:10 (1000×625)**, stejném jako rámeček —
podklad po stranách je dokreslený přímo v obrázku barvou jeho okraje, takže
nevzniká šev. Při výměně obrázku ten poměr dodržet. Výkon v hlavičce (`.tier-spec`) má žlutý rámeček.
Výkon je i v hlavičce karty (`.tier-spec`), aby ho zákazník viděl bez čtení
odrážek. Doplňky mimo cenu (baterie k Základu za 69 tis., wallbox od 19 tis.)
mají odrážku `li.plus` se žlutým plusem. K tomu **79 tis. Kč**
za fotovoltaický ohřev vody. Všechny jsou **včetně DPH 12 %** (snížená sazba pro
instalace na rodinných domech). Uvedeno v `price-note` u každé varianty, u ohřevu
vody ve `span.vat` a rozepsáno v disclaimeru pod ceníkem.

### Financování v textu ceníku

Disclaimer pod variantami popisuje stav NZÚ pro rok 2026: pro většinu domácností
**bezúročný úvěr** (ne přímá dotace), přímá dotace jen NZÚ Light pro nízkopříjmové.
Pokud se program změní, je potřeba tuhle větu aktualizovat.

## Jak to probíhá (`#postup`) a FAQ (`#faq`)

Pětikrokový proces (poptávka → obhlídka → nabídka → montáž → spuštění a servis)
a osm nejčastějších dotazů v `<details>` akordeonu (první je otevřený).
Obojí doplněno podle rešerše konkurence — chybělo to oproti běžnému standardu
českých FVE webů.

Informace o NZÚ v odpovědích platí k 7/2026 — při změně programu aktualizovat.

## Insta lišta (reference)

Sekce `#reference` — horizontální lišta karet generovaná z pole `INSTA_POSTS`
v `index.html`. Karta odkazuje na **detail realizace** `reference/<slug>/`, pokud
má záznam pole `slug`; jinak na příspěvek `https://www.instagram.com/p/<code>/`.
Odkaz na Instagram je pak až na detailu. Ikona Instagramu se u karet s detailem
záměrně nezobrazuje, aby neslibovala něco jiného, než kam odkaz vede.

**Přidání nové reference:**
1. stáhni fotku postu do `foto/insta/<code>.jpg` (čtverec ~640 px),
2. přidej záznam na ZAČÁTEK pole `INSTA_POSTS` v `index.html`,
3. doplň i `foto/insta/posts.json` (z něj se generují galerie na podstránkách),
4. přidej dvojici `code: slug` do `SLUGY` v `nastroje/generuj-reference.py`
   a skript spusť — vznikne detail realizace, přepíšou se odkazy v galeriích
   a přegeneruje se `sitemap.xml`.

Detail dostanou jen realizace se známou lokalitou — ze záznamu „Bytový dům"
bez města by vznikla stránka bez informační hodnoty. Takové karty zůstávají
odkázané na Instagram.

Zdroj: https://www.instagram.com/bftechnology_sro/ — posty s hashtagem #FVE
(staženo 29. 7. 2026, 16 postů z 24 celkem).

## Poznámky

- Formulář má honeypot pole `website`; po odeslání redirect `?sent=1` / `?sent=0`.
- Web musí běžet přes webserver kvůli `send.php` (statika jinak funguje i z file://).
- **Údaje ve stats pruhu pod herem** jsou zatím jen ty doložitelné (999 kWp = největší
  realizace, vlastní týmy, na klíč). Až budou k dispozici další reálná čísla
  (roky na trhu, celkový instalovaný výkon), patří sem.
- **Nároková tvrzení**: v heru je „Více než 150 realizací vlastními realizačními
  týmy". Číslo musí být doložitelné — dřívější „Stovky instalací po celé ČR"
  doložitelné nebylo a odporovalo i regionálnímu zaměření firmy.
- **Návratnost** se uvádí jako 7–10 let *u vhodně navrženého systému* a vždy
  s výčtem předpokladů. Jedno univerzální číslo bez podmínek se slibovat nedá.
- **Název firmy** se píše všude jednotně `BF technology s.r.o.`, značka `BF technology`
  (malé „t"), shodně s obchodním rejstříkem.
- **„SVJ" se v popisu segmentu nepoužívá** — bytový dům může patřit fyzické osobě,
  společenství vlastníků i bytovému družstvu. Segment se jmenuje jen „Bytové domy",
  soubor je `bytove-domy.html`.
- **`robots.txt` zatím obsahuje `Disallow: /`** — dokud web běží jen na github.io,
  nemá se indexovat (duplicitní obsah a špatná URL v indexu). **Při spuštění na
  vlastní doméně tenhle řádek smazat** a odkomentovat `Allow: /`.
- **Odborné texty mají datum technické kontroly** (`.reviewed`, `.spec-note`) —
  metodiky PDS i ceny elektřiny se mění a návštěvník musí vidět, k čemu se číslo
  váže. Při aktualizaci obsahu datum posunout.
- **Kategorie B1 (100 kW – 1 MW) NENÍ „od stolu"** — funkční zkoušky na celé
  výrobně se dělají už tam (řízení činného výkonu, regulace Q/U/cos φ, ochrany,
  komunikace, automatické opětovné připojení). Dřívější znění stránky bylo věcně
  chybné; hranice 1 MW rozšiřuje rozsah, ale zkoušky nezavádí.
- **Ekonomická čísla u BESS jsou modelová** a musí být uvedená s předpoklady
  (výkon, cyklus, účinnost, cenová úroveň). Nikdy je nepodávat jako záruku výnosu.
- **`simulacni-zkousky-rfg.html`** je samostatná stránka kvůli SEO: „simulační zkoušky
  RfG" a „dispečerské řízení" jsou jiné dotazy od jiných lidí a jedna stránka může mít
  jen jeden title a H1. `inzenyrske-sluzby.html` na ni odkazuje jako rozcestník.
  Obsah vychází z prezentace BFK systems (kategorie A1–D, proces SoP → UTP, WP1–WP6,
  Z1–Z5) — při změně metodiky PDS je nutné projít i tuhle stránku.
- **Ekonomika velkých BESS** v sekci `#ekonomika` na `bateriova-uloziste.html` vychází
  z reálné analýzy pro konkrétního zákazníka. Na webu je **anonymizovaně** — bez jména
  klienta, čísla smlouvy a konkrétní investice. Data o záporných hodinách spotu jsou
  veřejná (OTE, denní trh).
