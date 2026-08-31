// Poptavkovy formular bftechnology.cz — Cloudflare Worker.
//
// Web zustava na GitHub Pages (staticky, zadne PHP). Formular jen posle POST
// sem a Worker odesle dva e-maily pres Resend:
//   1. notifikaci do firmy (Reply-To = zakaznik, takze odpoved jde primo jemu)
//   2. potvrzeni zakaznikovi, ze poptavka dorazila
//
// Nastaveni (Workers -> Settings -> Variables):
//   RESEND_API_KEY  secret, klic z resend.com
//   MAIL_FROM       napr. BF technology <poptavky@send.bftechnology.cz>
//   MAIL_TO         info@bftechnology.cz
//   MAIL_CC         nepovinne, dalsi prijemci oddeleni carkou
//
// Podrobny postup nasazeni je v README.md vedle tohoto souboru.

const POVOLENE_ORIGINY = [
  'https://www.bftechnology.cz',
  'https://bftechnology.cz',
  'http://localhost:8899',
];

const WEB = 'https://www.bftechnology.cz';
const LOGO = WEB + '/assets/BFT_LOGO_TRANSPARENT-420.png';
const TELEFON = '+420 776 111 100';
const TELEFON_HREF = '+420776111100';
const MAIL_FIRMA = 'info@bftechnology.cz';

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const cors = korsHlavicky(origin);

    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    if (request.method !== 'POST') return odpoved({ success: false, message: 'Method not allowed' }, 405, cors);

    let data;
    try {
      data = await nactiData(request);
    } catch {
      return odpoved({ success: false, message: 'Neplatná data formuláře.' }, 400, cors);
    }

    // Honeypot — vyplneny znamena robota. Tvarime se, ze se odeslalo.
    if (data.botcheck) return dokonci(request, data, { success: true, message: 'Odesláno.' }, cors);

    const chyba = zkontroluj(data);
    if (chyba) return odpoved({ success: false, message: chyba }, 422, cors);

    const zakaznik = {
      jmeno: data['Jméno a příjmení'],
      telefon: data['Telefon'],
      email: data['E-mail'],
      zajem: data['Zájem o'] || 'Neuvedeno',
      zprava: data['Zpráva'] || '',
      zdroj: data['Odesláno z webu'] || 'BF technology',
      cas: cesky_cas(),
    };

    const notifikace = {
      from: env.MAIL_FROM,
      to: (env.MAIL_TO || MAIL_FIRMA).split(',').map((s) => s.trim()),
      reply_to: zakaznik.email,
      subject: `Poptávka z webu – ${zakaznik.zajem} – ${zakaznik.jmeno}`,
      html: htmlNotifikace(zakaznik),
      text: textNotifikace(zakaznik),
    };
    if (env.MAIL_CC) notifikace.cc = env.MAIL_CC.split(',').map((s) => s.trim());

    const poslano = await posli(env, notifikace);
    if (!poslano.ok) {
      return odpoved({ success: false, message: 'E-mail se nepodařilo odeslat.' }, 502, cors);
    }

    // Potvrzeni zakaznikovi je bonus — kdyz selze, poptavku uz mame.
    await posli(env, {
      from: env.MAIL_FROM,
      to: [zakaznik.email],
      reply_to: MAIL_FIRMA,
      subject: 'Děkujeme za poptávku – BF technology',
      html: htmlPotvrzeni(zakaznik),
      text: textPotvrzeni(zakaznik),
    }).catch(() => {});

    return dokonci(request, data, { success: true, message: 'Poptávka odeslána.' }, cors);
  },
};

// ---------- vstup ----------

async function nactiData(request) {
  const typ = request.headers.get('Content-Type') || '';
  const data = {};
  if (typ.includes('application/json')) {
    Object.assign(data, await request.json());
  } else {
    const fd = await request.formData();
    for (const [k, v] of fd.entries()) data[k] = typeof v === 'string' ? v : '';
  }
  for (const k of Object.keys(data)) if (typeof data[k] === 'string') data[k] = data[k].trim();
  return data;
}

function zkontroluj(d) {
  if (!d['Jméno a příjmení']) return 'Vyplňte prosím jméno.';
  if (!d['Telefon']) return 'Vyplňte prosím telefon.';
  if (!d['E-mail'] || !/^[^@\s]+@[^@\s.]+\.[^@\s]{2,}$/.test(d['E-mail'])) return 'Zadejte prosím platný e-mail.';
  if ((d['Zpráva'] || '').length > 5000) return 'Zpráva je příliš dlouhá.';
  if (d['Jméno a příjmení'].length > 200 || d['Telefon'].length > 60) return 'Neplatná data formuláře.';
  return null;
}

// Bez JavaScriptu prohlizec ceka presmerovani, ne JSON — stejne jako drive.
function dokonci(request, data, telo, cors) {
  const chceJson = (request.headers.get('Accept') || '').includes('json');
  if (!chceJson && data.redirect) {
    return new Response(null, { status: 303, headers: { ...cors, Location: data.redirect } });
  }
  return odpoved(telo, telo.success ? 200 : 400, cors);
}

function odpoved(telo, status, cors) {
  return new Response(JSON.stringify(telo), {
    status,
    headers: { ...cors, 'Content-Type': 'application/json; charset=utf-8' },
  });
}

function korsHlavicky(origin) {
  return {
    'Access-Control-Allow-Origin': POVOLENE_ORIGINY.includes(origin) ? origin : WEB,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Accept',
    'Access-Control-Max-Age': '86400',
  };
}

// ---------- odeslani ----------

async function posli(env, mail) {
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(mail),
  });
  return { ok: res.ok, status: res.status };
}

// ---------- pomocne ----------

function esc(s) {
  return String(s).replace(/[&<>"']/g, (z) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[z]));
}

function cesky_cas() {
  return new Intl.DateTimeFormat('cs-CZ', {
    dateStyle: 'long',
    timeStyle: 'short',
    timeZone: 'Europe/Prague',
  }).format(new Date());
}

function telHref(t) {
  return t.replace(/[^\d+]/g, '');
}

// ---------- sablony ----------

const HLAVA = `<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">`;
const FONT = `font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif`;

function obal(preheader, obsah) {
  return `<!doctype html><html lang="cs"><head>${HLAVA}</head>
<body style="margin:0;padding:0;background:#F5F8F0;${FONT};color:#4A4A4A;">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">${esc(preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F5F8F0;padding:24px 12px;">
  <tr><td align="center">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#FFFFFF;border-radius:14px;overflow:hidden;border:1px solid #E2E5DC;">
      <tr><td style="background:#FFFFFF;padding:22px 28px 18px;border-bottom:3px solid #8BB855;">
        <img src="${LOGO}" width="150" alt="BF technology" style="display:block;border:0;height:auto;max-width:150px;">
      </td></tr>
      ${obsah}
      <tr><td style="background:#F5F8F0;padding:18px 28px;border-top:1px solid #E2E5DC;font-size:12px;line-height:1.6;color:#6B6B6B;">
        <b style="color:#3C3C3C;">BF technology s.r.o.</b> · IČO 17258529<br>
        <a href="tel:${TELEFON_HREF}" style="color:#79A644;text-decoration:none;">${TELEFON}</a> ·
        <a href="mailto:${MAIL_FIRMA}" style="color:#79A644;text-decoration:none;">${MAIL_FIRMA}</a> ·
        <a href="${WEB}" style="color:#79A644;text-decoration:none;">bftechnology.cz</a>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>`;
}

function radek(popis, hodnota, odkaz) {
  const v = odkaz
    ? `<a href="${odkaz}" style="color:#79A644;text-decoration:none;">${esc(hodnota)}</a>`
    : esc(hodnota);
  return `<tr>
    <td style="padding:9px 0;border-bottom:1px solid #EFF2EA;font-size:13px;color:#8A8A8A;width:38%;vertical-align:top;">${esc(popis)}</td>
    <td style="padding:9px 0;border-bottom:1px solid #EFF2EA;font-size:15px;color:#3C3C3C;font-weight:600;">${v}</td>
  </tr>`;
}

function htmlNotifikace(z) {
  const predmet = encodeURIComponent(`Vaše poptávka – ${z.zajem} – BF technology`);
  const telo = encodeURIComponent(`Dobrý den,\n\nděkujeme za poptávku z našeho webu.\n\n`);
  const odpovedet = `mailto:${z.email}?subject=${predmet}&body=${telo}`;

  const zprava = z.zprava
    ? `<tr><td style="padding:0 28px 4px;">
         <div style="font-size:13px;color:#8A8A8A;margin:18px 0 8px;">Zpráva od zákazníka</div>
         <div style="background:#F5F8F0;border-left:3px solid #8BB855;border-radius:0 8px 8px 0;padding:14px 16px;font-size:15px;line-height:1.65;color:#3C3C3C;white-space:pre-wrap;">${esc(z.zprava)}</div>
       </td></tr>`
    : '';

  return obal(
    `${z.zajem} · ${z.jmeno} · ${z.telefon}`,
    `<tr><td style="padding:28px 28px 0;">
        <div style="display:inline-block;background:#8BB855;color:#FFFFFF;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:6px 12px;border-radius:20px;">Nová poptávka</div>
        <h1 style="margin:16px 0 4px;font-size:24px;line-height:1.25;color:#222222;">${esc(z.jmeno)}</h1>
        <p style="margin:0;font-size:15px;color:#6B6B6B;">${esc(z.zajem)}</p>
     </td></tr>
     <tr><td style="padding:20px 28px 0;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="padding-right:6px;" width="50%">
              <a href="tel:${telHref(z.telefon)}" style="display:block;text-align:center;background:#8BB855;color:#FFFFFF;font-size:15px;font-weight:700;text-decoration:none;padding:13px 10px;border-radius:10px;">Zavolat</a>
            </td>
            <td style="padding-left:6px;" width="50%">
              <a href="${odpovedet}" style="display:block;text-align:center;background:#FFFFFF;color:#3C3C3C;font-size:15px;font-weight:700;text-decoration:none;padding:12px 10px;border-radius:10px;border:2px solid #E2E5DC;">Odpovědět e-mailem</a>
            </td>
          </tr>
        </table>
     </td></tr>
     <tr><td style="padding:22px 28px 0;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
          ${radek('Telefon', z.telefon, 'tel:' + telHref(z.telefon))}
          ${radek('E-mail', z.email, 'mailto:' + z.email)}
          ${radek('Zájem o', z.zajem)}
          ${radek('Odesláno z webu', z.zdroj)}
          ${radek('Přijato', z.cas)}
        </table>
     </td></tr>
     ${zprava}
     <tr><td style="padding:18px 28px 26px;">
        <p style="margin:0;font-size:13px;line-height:1.6;color:#8A8A8A;">
          Když na tento e-mail odpovíte, odpověď jde přímo zákazníkovi na
          <a href="mailto:${z.email}" style="color:#79A644;text-decoration:none;">${esc(z.email)}</a>.
        </p>
     </td></tr>`
  );
}

function textNotifikace(z) {
  const radky = [
    'NOVÁ POPTÁVKA Z WEBU',
    '',
    `Jméno:    ${z.jmeno}`,
    `Telefon:  ${z.telefon}`,
    `E-mail:   ${z.email}`,
    `Zájem o:  ${z.zajem}`,
    `Web:      ${z.zdroj}`,
    `Přijato:  ${z.cas}`,
  ];
  if (z.zprava) radky.push('', 'Zpráva:', z.zprava);
  radky.push('', `Odpovědí na tento e-mail píšete přímo zákazníkovi (${z.email}).`);
  return radky.join('\n');
}

function htmlPotvrzeni(z) {
  const shrnuti = z.zprava
    ? `<div style="background:#F5F8F0;border-left:3px solid #8BB855;border-radius:0 8px 8px 0;padding:14px 16px;font-size:15px;line-height:1.65;color:#3C3C3C;white-space:pre-wrap;">${esc(z.zprava)}</div>`
    : '';

  return obal(
    'Vaši poptávku máme. Ozveme se do jednoho pracovního dne.',
    `<tr><td style="padding:28px 28px 0;">
        <h1 style="margin:0 0 12px;font-size:24px;line-height:1.3;color:#222222;">Děkujeme za poptávku</h1>
        <p style="margin:0 0 14px;font-size:16px;line-height:1.7;color:#4A4A4A;">
          Dobrý den, ${esc(z.jmeno)},<br>
          vaši poptávku (${esc(z.zajem.toLowerCase())}) jsme v pořádku přijali. Ozveme se vám
          <b>do jednoho pracovního dne</b> a domluvíme se na dalším postupu. Obhlídka i nabídka jsou zdarma a nezávazné.
        </p>
        <p style="margin:0 0 6px;font-size:16px;line-height:1.7;color:#4A4A4A;">
          Spěchá to? Zavolejte nám na
          <a href="tel:${TELEFON_HREF}" style="color:#79A644;text-decoration:none;font-weight:700;">${TELEFON}</a>.
        </p>
     </td></tr>
     ${
       shrnuti
         ? `<tr><td style="padding:16px 28px 0;">
              <div style="font-size:13px;color:#8A8A8A;margin-bottom:8px;">Co jste nám napsali</div>
              ${shrnuti}
            </td></tr>`
         : ''
     }
     <tr><td style="padding:22px 28px 4px;">
        <a href="${WEB}/reference" style="display:inline-block;background:#8BB855;color:#FFFFFF;font-size:15px;font-weight:700;text-decoration:none;padding:13px 22px;border-radius:10px;">Prohlédnout naše realizace</a>
     </td></tr>
     <tr><td style="padding:18px 28px 26px;">
        <p style="margin:0;font-size:13px;line-height:1.6;color:#8A8A8A;">
          Tento e-mail je automatické potvrzení. Odpovědět na něj samozřejmě můžete – přijde nám.
        </p>
     </td></tr>`
  );
}

function textPotvrzeni(z) {
  return [
    `Dobrý den, ${z.jmeno},`,
    '',
    `vaši poptávku (${z.zajem.toLowerCase()}) jsme v pořádku přijali.`,
    'Ozveme se vám do jednoho pracovního dne a domluvíme se na dalším postupu.',
    'Obhlídka i nabídka jsou zdarma a nezávazné.',
    '',
    `Spěchá to? Zavolejte nám na ${TELEFON}.`,
    '',
    'BF technology s.r.o.',
    `${TELEFON} · ${MAIL_FIRMA} · ${WEB}`,
  ].join('\n');
}

// Export kvuli nahledu sablon v prohlizeci (nastroje/poptavka-worker/nahled.html).
export { htmlNotifikace, htmlPotvrzeni, textNotifikace, textPotvrzeni };
