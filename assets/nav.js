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

// Mobilni celoobrazovkove menu.
//
// Otevrene menu je modalni dialog pres celou obrazovku, takze musi:
//   - hlasit stav na hamburgeru (aria-expanded),
//   - presunout focus dovnitr a po zavreni ho vratit na hamburger,
//   - drzet focus uvnitr (jinak by tabulator utekl na skryty obsah pod menu),
//   - zavirat se Escapem,
//   - zablokovat rolovani stranky pod sebou.
// Driv to byly dva inline onclick handlery, ktere neresily nic z toho.
(function mobileMenu() {
  const menu = document.getElementById('mmenu');
  const open = document.getElementById('menu-open');
  const close = document.getElementById('menu-close');
  if (!menu || !open || !close) return;

  const FOCUSABLE = 'a[href], button:not([disabled]), input, select, textarea, [tabindex]:not([tabindex="-1"])';
  const jeOtevreno = () => menu.classList.contains('open');

  const otevri = () => {
    menu.classList.add('open');
    open.setAttribute('aria-expanded', 'true');
    document.documentElement.classList.add('menu-open');
    close.focus();
  };

  const zavri = ({ vratitFocus = true } = {}) => {
    menu.classList.remove('open');
    open.setAttribute('aria-expanded', 'false');
    document.documentElement.classList.remove('menu-open');
    if (vratitFocus) open.focus();
  };

  open.addEventListener('click', otevri);
  close.addEventListener('click', () => zavri());

  // Kliknuti na polozku menu vede na jinou stranku nebo kotvu — menu zaviráme,
  // ale focus nevracime na hamburger, at neprebliká pred odchodem.
  menu.querySelectorAll('a').forEach((a) => {
    a.addEventListener('click', () => zavri({ vratitFocus: false }));
  });

  document.addEventListener('keydown', (e) => {
    if (!jeOtevreno()) return;

    if (e.key === 'Escape') {
      e.preventDefault();
      zavri();
      return;
    }

    if (e.key !== 'Tab') return;
    const prvky = [...menu.querySelectorAll(FOCUSABLE)].filter((el) => el.offsetParent !== null);
    if (!prvky.length) return;
    const prvni = prvky[0];
    const posledni = prvky[prvky.length - 1];

    if (e.shiftKey && document.activeElement === prvni) {
      e.preventDefault();
      posledni.focus();
    } else if (!e.shiftKey && document.activeElement === posledni) {
      e.preventDefault();
      prvni.focus();
    } else if (!menu.contains(document.activeElement)) {
      e.preventDefault();
      prvni.focus();
    }
  });

  // Pri prechodu na sirsi displej se hamburger schova — menu by pak zustalo
  // viset pres obsah a rolovani zablokovane.
  window.matchMedia('(min-width: 1081px)').addEventListener('change', (e) => {
    if (e.matches && jeOtevreno()) zavri({ vratitFocus: false });
  });
})();
