// Odeslani kontaktniho formulare pres Web3Forms.
// Sdileno domovskou strankou a strankou kontakt.html — proto samostatny soubor
// a ne inline skript. Access key je v HTML formulare, ne tady.
// ---------- Odeslání formuláře přes Web3Forms ----------
const OK_MSG  = 'Děkujeme! Vaše poptávka byla odeslána. Ozveme se co nejdřív.';
const ERR_MSG = 'Odeslání se nepodařilo. Zkuste to prosím znovu, nebo nám zavolejte na +420 776 111 100.';

// Stav po návratu z Web3Forms (jen když uživatel nemá JS pro fetch — pak
// proběhne klasický POST a redirect zpět s ?sent=1).
(function contactStatusFromUrl() {
  const params = new URLSearchParams(location.search);
  if (!params.has('sent')) return;
  const el = document.getElementById('contact-status');
  const ok = params.get('sent') === '1';
  el.className = ok ? 'ok' : 'err';
  el.textContent = ok ? OK_MSG : ERR_MSG;
  el.scrollIntoView({ block: 'center' });
})();

(function contactSubmit() {
  const form = document.getElementById('contact-form');
  if (!form) return;
  const status = document.getElementById('contact-status');
  const button = form.querySelector('button[type="submit"]');
  const key = form.querySelector('input[name="access_key"]');

  if (!key || key.value.startsWith('PLACEHOLDER')) {
    console.warn('[BFT] Web3Forms access_key není vyplněný — formulář neodešle nic. Doplň ho v index.html.');
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const label = button.textContent;
    button.disabled = true;
    button.textContent = 'Odesílám…';
    status.className = '';
    status.textContent = '';

    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: new FormData(form)
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.success) {
        status.className = 'ok';
        status.textContent = OK_MSG;
        form.reset();
      } else {
        status.className = 'err';
        status.textContent = ERR_MSG;
        console.warn('[BFT] Web3Forms odpověď:', res.status, data);
      }
    } catch (err) {
      status.className = 'err';
      status.textContent = ERR_MSG;
      console.warn('[BFT] Odeslání selhalo:', err);
    } finally {
      button.disabled = false;
      button.textContent = label;
      status.scrollIntoView({ block: 'center' });
    }
  });
})();
