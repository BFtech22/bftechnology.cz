// Rozbalovaci polozka v hlavnim menu ("Fotovoltaika").
//
// CSS uz otevira na :hover a :focus-within, takze bez JS je menu pouzitelne.
// Tenhle skript resi to, co CSS neumi:
//   - dotykova zarizeni, kde zadny hover neexistuje (klik otevre)
//   - pravdivy stav aria-expanded pro odecitace obrazovky
//   - zavreni Escapem a klikem mimo
(function dropdownMenu() {
  const wraps = document.querySelectorAll('nav.primary .has-sub');
  if (!wraps.length) return;

  const zavriVse = (krome) => {
    wraps.forEach((w) => {
      if (w === krome) return;
      w.classList.remove('open');
      const b = w.querySelector('.sub-toggle');
      if (b) b.setAttribute('aria-expanded', 'false');
    });
  };

  wraps.forEach((wrap) => {
    const toggle = wrap.querySelector('.sub-toggle');
    if (!toggle) return;

    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      const otevreno = wrap.classList.toggle('open');
      toggle.setAttribute('aria-expanded', otevreno ? 'true' : 'false');
      zavriVse(wrap);
    });

    // Prochazeni klavesnici — jakykoli focus dovnitr blok otevre, odchod zavre.
    wrap.addEventListener('focusin', () => {
      wrap.classList.add('open');
      toggle.setAttribute('aria-expanded', 'true');
      zavriVse(wrap);
    });
    wrap.addEventListener('focusout', (e) => {
      if (wrap.contains(e.relatedTarget)) return;
      wrap.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const otevreny = document.querySelector('nav.primary .has-sub.open');
    if (!otevreny) return;
    otevreny.classList.remove('open');
    const b = otevreny.querySelector('.sub-toggle');
    if (b) { b.setAttribute('aria-expanded', 'false'); b.focus(); }
  });

  document.addEventListener('click', (e) => {
    if (e.target.closest('nav.primary .has-sub')) return;
    zavriVse(null);
  });
})();
