// Header dropdowns (desktop) and the slide-out phone menu.
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
    it.addEventListener('pointerenter', function (e) { if (e.pointerType !== 'mouse') return; clearTimeout(t); var was = it.classList.contains('open'); closeAll(it); it.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); if (!was) it.dataset.hover = '1'; });
    it.addEventListener('pointerleave', function (e) { if (e.pointerType !== 'mouse') return; t = setTimeout(function () { it.dataset.hover = '0'; it.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }, 180); });
  });
  document.addEventListener('click', function (e) { if (!e.target.closest('.nav-item')) closeAll(); });
  document.addEventListener('focusin', function (e) { if (!e.target.closest('.nav-item')) closeAll(); });

  // ---- phone side panel ----
  var root = document.documentElement;
  var mbtn = document.querySelector('.menu-btn'), panel = document.getElementById('mnav');
  var scrim = document.querySelector('.mnav-scrim'), closeBtn = document.querySelector('.mnav-close');
  var isOpen = false;
  function setOpen(open, focusBack) {
    if (!panel) return;
    isOpen = open;
    panel.style.transform = '';
    root.classList.toggle('mnav-open', open);
    panel.inert = !open;
    mbtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) setTimeout(function () { closeBtn && closeBtn.focus({ preventScroll: true }); }, 60);
    else if (focusBack) mbtn.focus({ preventScroll: true });
  }
  if (mbtn && panel) {
    mbtn.addEventListener('click', function () { setOpen(!isOpen); });
    closeBtn && closeBtn.addEventListener('click', function () { setOpen(false, true); });
    scrim && scrim.addEventListener('click', function () { setOpen(false, true); });
    panel.addEventListener('click', function (e) { var a = e.target.closest('a'); if (a) setOpen(false); });

    // Smooth accordion sections
    [].forEach.call(panel.querySelectorAll('.mnav-sum'), function (b) {
      b.addEventListener('click', function () {
        var g = b.parentElement, open = !g.classList.contains('open');
        [].forEach.call(panel.querySelectorAll('.mnav-group.open'), function (o) { if (o !== g) { o.classList.remove('open'); o.querySelector('.mnav-sum').setAttribute('aria-expanded', 'false'); } });
        g.classList.toggle('open', open); b.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    });

    // Swipe right to close: the panel follows your finger
    var x0 = null, y0 = 0, dx = 0, dragging = false;
    panel.addEventListener('touchstart', function (e) { if (!isOpen) return; x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; dx = 0; dragging = false; }, { passive: true });
    panel.addEventListener('touchmove', function (e) {
      if (x0 === null) return;
      var mx = e.touches[0].clientX - x0, my = e.touches[0].clientY - y0;
      if (!dragging && Math.abs(mx) > 10 && Math.abs(mx) > Math.abs(my)) { dragging = true; panel.classList.add('dragging'); }
      if (dragging) { dx = Math.max(0, mx); panel.style.transform = 'translateX(' + dx + 'px)'; scrim.style.opacity = String(Math.max(0, 1 - dx / panel.offsetWidth)); }
    }, { passive: true });
    panel.addEventListener('touchend', function () {
      if (dragging) { panel.classList.remove('dragging'); scrim.style.opacity = ''; if (dx > panel.offsetWidth * 0.25) setOpen(false); else panel.style.transform = ''; }
      x0 = null; dragging = false;
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = document.querySelector('.nav-item.open');
    closeAll(); if (open) open.querySelector('.nav-caret').focus();
    if (isOpen) setOpen(false, true);
  });
  // Close the panel if the screen gets wide enough for the desktop menu
  window.addEventListener('resize', function () { if (isOpen && window.innerWidth > 1000) setOpen(false); });
})();
