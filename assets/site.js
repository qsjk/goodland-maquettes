(function () {
  // --- Settings Zaid can fill in later ---
  var WHATSAPP = ''; // international format without "+", e.g. '306900000000'. Leave empty to hide the WhatsApp buttons.

  var html = document.documentElement;

  // Language: saved choice, else the browser language (French or English)
  function setLang(l) {
    html.setAttribute('data-lang', l);
    html.setAttribute('lang', l);
    document.querySelectorAll('.lang button').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-lang') === l ? 'true' : 'false');
    });
    try { localStorage.setItem('zaid-lang', l); } catch (e) {}
  }
  var saved = null;
  try { saved = localStorage.getItem('zaid-lang'); } catch (e) {}
  setLang(saved || ((navigator.language || 'fr').toLowerCase().indexOf('fr') === 0 ? 'fr' : 'en'));
  document.querySelectorAll('.lang button').forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.getAttribute('data-lang')); });
  });

  // Header: transparent over the hero photo, solid once scrolled
  var hdr = document.querySelector('.hdr');
  function onScroll() { hdr.classList.toggle('solid', window.scrollY > 40); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu
  var mb = document.querySelector('.menu-btn');
  mb.addEventListener('click', function () {
    var open = hdr.classList.toggle('open');
    mb.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  document.querySelectorAll('.nav a').forEach(function (a) {
    a.addEventListener('click', function () { hdr.classList.remove('open'); mb.setAttribute('aria-expanded', 'false'); });
  });

  // WhatsApp buttons appear only once a number is set
  if (WHATSAPP) {
    document.querySelectorAll('[data-wa]').forEach(function (a) {
      a.href = 'https://wa.me/' + WHATSAPP;
      a.hidden = false;
    });
  }

  // Lightbox for every [data-full] photo
  var items = Array.prototype.slice.call(document.querySelectorAll('[data-full]'));
  var lb = document.createElement('div');
  lb.className = 'lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.innerHTML = '<img alt="">' +
    '<button class="lb-x" aria-label="Fermer / Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6 6 18"/></svg></button>' +
    '<button class="lb-p" aria-label="Précédente / Previous"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 6l-6 6 6 6"/></svg></button>' +
    '<button class="lb-n" aria-label="Suivante / Next"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 6l6 6-6 6"/></svg></button>';
  document.body.appendChild(lb);
  var lbImg = lb.querySelector('img'), idx = 0, last = null;
  function show(i) {
    idx = (i + items.length) % items.length;
    lbImg.src = items[idx].getAttribute('data-full');
    var im = items[idx].querySelector('img');
    lbImg.alt = im ? im.alt : '';
  }
  function close() { lb.classList.remove('on'); lbImg.removeAttribute('src'); if (last) last.focus(); }
  items.forEach(function (el, i) {
    el.addEventListener('click', function () { last = el; show(i); lb.classList.add('on'); lb.querySelector('.lb-x').focus(); });
  });
  lb.querySelector('.lb-x').addEventListener('click', close);
  lb.querySelector('.lb-p').addEventListener('click', function () { show(idx - 1); });
  lb.querySelector('.lb-n').addEventListener('click', function () { show(idx + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('on')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(idx - 1);
    if (e.key === 'ArrowRight') show(idx + 1);
  });
})();
