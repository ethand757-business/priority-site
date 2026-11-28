// Header dropdowns (desktop) and the phone menu.
(function () {
  var items = [].slice.call(document.querySelectorAll('.nav-item'));
  function closeAll(except) {
    items.forEach(function (it) {
      if (it === except) return;
      it.classList.remove('open');
      var b = it.querySelector('.nav-caret'); if (b) b.setAttribute('aria-expanded', 'false');
    });
  }
  items.forEach(function (it) {
    var btn = it.querySelector('.nav-caret'), t = null;
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      // If a mouse hover just opened it, a click keeps it open instead of closing it.
      var open = it.dataset.hover === '1' ? true : !it.classList.contains('open');
      it.dataset.hover = '0';
      closeAll(it); it.classList.toggle('open', open); btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    // Mouse users get the menu on hover, with a short delay before closing.
    it.addEventListener('pointerenter', function (e) { if (e.pointerType !== 'mouse') return; clearTimeout(t); var was = it.classList.contains('open'); closeAll(it); it.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); if (!was) it.dataset.hover = '1'; });
    it.addEventListener('pointerleave', function (e) { if (e.pointerType !== 'mouse') return; t = setTimeout(function () { it.dataset.hover = '0'; it.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }, 180); });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.nav-item')) closeAll(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = document.querySelector('.nav-item.open');
    closeAll(); if (open) open.querySelector('.nav-caret').focus();
    if (mbtn && mbtn.getAttribute('aria-expanded') === 'true') { toggleM(false); mbtn.focus(); }
  });
  document.addEventListener('focusin', function (e) { if (!e.target.closest('.nav-item')) closeAll(); });

  var mbtn = document.querySelector('.menu-btn'), mnav = document.getElementById('mnav');
  function toggleM(open) {
    mbtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    mbtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    mnav.hidden = !open;
    document.documentElement.classList.toggle('mnav-open', open);
  }
  if (mbtn && mnav) {
    mbtn.addEventListener('click', function () { toggleM(mbtn.getAttribute('aria-expanded') !== 'true'); });
    mnav.addEventListener('click', function (e) { if (e.target.closest('a')) toggleM(false); });
  }
})();
