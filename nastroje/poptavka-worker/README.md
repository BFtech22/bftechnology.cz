# Poptávkový e-mail bez PHP serveru

Web zůstává na GitHub Pages. GitHub Pages umí jen statické soubory (žádné PHP),
proto formulář odesílá data na **Cloudflare Worker** – malý kus JavaScriptu, který
běží u Cloudflare zdarma a nepotřebuje vlastní server. Worker složí e-mail a odešle
ho přes **Resend** (poštovní API, zdarma 3 000 e-mailů měsíčně / 100 denně).

Co z toho vyjde:

- notifikace do firmy celá česky, v barvách BFT, s tlačítky **Zavolat** a **Odpovědět e-mailem**
- `Reply-To` je zákazník, takže odpověď na notifikaci jde rovnou jemu
- předmět `Poptávka z webu – Fotovoltaická elektrárna – Jméno Příjmení`
- automatické české potvrzení zákazníkovi, že poptávka dorazila
- žádná cizí značka v patičce, žádný měsíční poplatek

Náhled obou e-mailů: spusť v kořeni webu `python3 -m http.server 8899` a otevři
<http://localhost:8899/nastroje/poptavka-worker/nahled.html>.

## 1. Resend – odesílání pošty

1. Založ účet na <https://resend.com> (free plán stačí).
2. **Domains → Add domain** → zadej **`send.bftechnology.cz`**.
   Schválně subdoménu: hlavní doména má SPF pro Google Workspace a ta se tím nechá být.
3. Resend vypíše tři DNS záznamy (MX, TXT se SPF, TXT s DKIM). Přidej je v **Webglobe**
   do zóny `bftechnology.cz` – v názvu záznamu bude `send`, resp. `resend._domainkey.send`.
4. Počkej na **Verified** (obvykle pár minut).
5. **API Keys → Create API Key**, oprávnění *Sending access*. Klíč `re_…` si zkopíruj,
   ukáže se jen jednou.

## 2. Cloudflare Worker – logika formuláře

Bez instalace čehokoli, přes web:

1. Založ účet na <https://dash.cloudflare.com> (free).
2. **Workers & Pages → Create → Worker**, jméno např. `poptavka-bft`, **Deploy**.
3. **Edit code** → smaž ukázkový kód → vlož obsah [`worker.js`](worker.js) → **Deploy**.
4. **Settings → Variables and Secrets**:

   | Typ      | Název            | Hodnota                                              |
   |----------|------------------|------------------------------------------------------|
   | Secret   | `RESEND_API_KEY` | `re_…` z kroku 1.5                                    |
   | Text     | `MAIL_FROM`      | `BF technology <poptavky@send.bftechnology.cz>`        |
   | Text     | `MAIL_TO`        | `info@bftechnology.cz`                                 |
   | Text     | `MAIL_CC`        | nepovinné, další adresy oddělené čárkou                |

5. Adresa Workeru je `https://poptavka-bft.<účet>.workers.dev` – tu si poznač.

Kdo má nainstalovaný Node, může místo dashboardu použít `npx wrangler deploy`
(konfigurace je ve [`wrangler.toml`](wrangler.toml), klíč se nahraje přes
`npx wrangler secret put RESEND_API_KEY`).

## 3. Přepnutí webu na Worker

V `index.html` a `kontakt.html` je ve formuláři jediná věc k úpravě:

```html
<!-- staré -->
<form ... action="https://api.web3forms.com/submit" ...>
<!-- nové -->
<form ... action="https://poptavka-bft.ÚČET.workers.dev" ...>
```

Skrytá pole `access_key`, `subject`, `from_name` a `replyto` můžou zůstat – Worker si
předmět i reply-to skládá sám a ostatní pole ignoruje. Pole `redirect` a `botcheck`
používá dál (přesměrování pro prohlížeč bez JavaScriptu, past na roboty).

**Zároveň s přepnutím uprav `zasady-zpracovani-osobnich-udaju.html`:** místo Web3Forms
tam patří Cloudflare (provoz formuláře) a Resend (doručení e-mailu) jako zpracovatelé.

## 4. Test

1. Odešli poptávku z `/kontakt` a zkontroluj, že přišla notifikace i potvrzení.
2. Odpověz na notifikaci – musí se předvyplnit adresa zákazníka.
3. Ve formuláři nevyplňuj skryté pole „Nevyplňujte" – když ho vyplní robot,
   Worker odpoví `success`, ale e-mail neodešle.

## Limity a poznámky

- Free tier Resend: 3 000 e-mailů/měsíc, 100/den. Jedna poptávka = 2 e-maily.
- Free tier Cloudflare Workers: 100 000 požadavků/den.
- Nedoručení potvrzení zákazníkovi neshodí poptávku – notifikace do firmy má přednost.
- Změna textů e-mailů = úprava funkcí `htmlNotifikace` / `htmlPotvrzeni` ve `worker.js`
  a nové **Deploy** (nebo `npx wrangler deploy`).
