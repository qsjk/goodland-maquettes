(function () {
  var html = document.documentElement;

  // Language (EL/EN), remembered per visitor when storage is available
  function setLang(l) {
    html.setAttribute('data-lang', l);
    html.setAttribute('lang', l === 'en' ? 'en' : 'el');
    document.querySelectorAll('.lang button').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-lang') === l ? 'true' : 'false');
    });
    try { localStorage.setItem('gl-lang', l); } catch (e) {}
  }
  var saved = null;
  try { saved = localStorage.getItem('gl-lang'); } catch (e) {}
  setLang(saved === 'en' ? 'en' : 'el');
  document.querySelectorAll('.lang button').forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.getAttribute('data-lang')); });
  });

  // Mobile menu
  var hdr = document.querySelector('.hdr'), mb = document.querySelector('.menu-btn');
  if (mb) mb.addEventListener('click', function () {
    var open = hdr.classList.toggle('open');
    mb.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // Lightbox: any [data-lb="group"] element with data-full opens the group
  var lb = document.createElement('div');
  lb.className = 'lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.innerHTML = '<img alt=""><button class="lb-x" aria-label="Κλείσιμο"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6 6 18"/></svg></button>' +
    '<button class="lb-p" aria-label="Προηγούμενη"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 6l-6 6 6 6"/></svg></button>' +
    '<button class="lb-n" aria-label="Επόμενη"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 6l6 6-6 6"/></svg></button><div class="lb-c"></div>';
  document.body.appendChild(lb);
  var lbImg = lb.querySelector('img'), lbC = lb.querySelector('.lb-c'), items = [], idx = 0, lastFocus = null;
  function show(i) {
    idx = (i + items.length) % items.length;
    lbImg.src = items[idx].getAttribute('data-full');
    lbImg.alt = items[idx].getAttribute('data-alt') || '';
    lbC.textContent = (idx + 1) + ' / ' + items.length;
    lb.querySelector('.lb-p').style.display = lb.querySelector('.lb-n').style.display = items.length > 1 ? '' : 'none';
  }
  function open(el) {
    items = Array.prototype.slice.call(document.querySelectorAll('[data-lb="' + el.getAttribute('data-lb') + '"]'));
    lastFocus = el;
    show(items.indexOf(el));
    lb.classList.add('on');
    lb.querySelector('.lb-x').focus();
  }
  function close() { lb.classList.remove('on'); lbImg.src = ''; if (lastFocus) lastFocus.focus(); }
  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-lb]');
    if (t) { e.preventDefault(); open(t); }
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

  // Program gallery: thumbnails switch the main image
  var main = document.querySelector('.gal-main');
  document.querySelectorAll('.thumbs button').forEach(function (b) {
    b.addEventListener('click', function () {
      var i = +b.getAttribute('data-i');
      main.querySelector('img').src = b.getAttribute('data-src');
      main.setAttribute('data-start', i);
      document.querySelectorAll('.thumbs button').forEach(function (x) { x.setAttribute('aria-current', x === b ? 'true' : 'false'); });
    });
  });
  if (main) main.addEventListener('click', function () {
    var start = +(main.getAttribute('data-start') || 0);
    var all = document.querySelectorAll('[data-lb="prog"]');
    if (all[start]) open(all[start]);
  });

  // Lot filters
  document.querySelectorAll('.filters button').forEach(function (b) {
    b.addEventListener('click', function () {
      var f = b.getAttribute('data-f');
      document.querySelectorAll('.filters button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      document.querySelectorAll('.lot').forEach(function (l) {
        l.style.display = (f === 'all' || l.classList.contains('ok')) ? '' : 'none';
      });
    });
  });

  // "I'm interested" buttons fill the form
  document.querySelectorAll('[data-interest]').forEach(function (b) {
    b.addEventListener('click', function () {
      var box = document.getElementById('sel-lot'), inp = document.getElementById('f-lot');
      if (box) { box.textContent = b.getAttribute('data-interest'); box.style.display = ''; }
      if (inp) inp.value = b.getAttribute('data-interest');
    });
  });

  // Contact forms: open the visitor's email app with the message filled in
  document.querySelectorAll('form[data-mail]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var d = new FormData(f), lines = [];
      d.forEach(function (v, k) { if (v && k !== 'subject') lines.push(k + ': ' + v); });
      var subj = d.get('subject') || 'Μήνυμα από το site';
      window.location.href = 'mailto:' + f.getAttribute('data-mail') + '?subject=' + encodeURIComponent(subj) + '&body=' + encodeURIComponent(lines.join('\n'));
    });
  });
})();
