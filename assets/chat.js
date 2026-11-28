// "Ask a question" chat bubble.
// Answers common questions instantly from the site's own information. Anything it can't
// answer is handed to Jeff as a text message. It never makes up an answer.
(function () {
  var me = document.currentScript;
  var BASE = (me && me.getAttribute('data-base')) || '';
  var PHONE = '(757) 749-9274', TEL = '+17577499274';
  var u = function (p) { return BASE + p; };

  // Each topic: words that trigger it, the answer, and optional links.
  var TOPICS = [
    { k: ['hi', 'hello', 'hey', 'good morning', 'good afternoon'], a: 'Hi! Ask me anything about Priority Window Cleaning, or tap a topic below.' },
    { k: ['thank', 'thanks', 'appreciate'], a: "You're welcome! If you think of anything else, I'm here. Jeff is just a text away too." },
    { k: ['service', 'offer', 'what do you do', 'do you clean', 'what can you'], a: 'We do window cleaning (residential, commercial and water-fed pole), pressure washing (driveways, concrete, commercial), soft washing (house, roof, gutters, awnings) and holiday lighting.', l: [['All services', 'services/']] },
    { k: ['price', 'cost', 'how much', 'quote', 'estimate', 'charge', 'rate', 'expensive', 'cheap'], a: "Estimates are free. Our online estimator shows a price range in seconds, and Jeff confirms your exact price before any work starts.", l: [['Get my estimate', '#estimate'], ['Contact Jeff', 'contact-us/']] },
    { k: ['coupon', 'discount', 'deal', 'promo', 'offer code', 'refer', 'referral', 'save'], a: 'First-time customers get $25 off any one service. Refer a friend and you get $30 off your next service. Just mention it when you book.', l: [['Coupon details', 'coupons/']] },
    { k: ['area', 'serve', 'service area', 'where', 'location', 'come to', 'travel', 'near me', 'town', 'city'], a: 'We serve Virginia Beach, Chesapeake, Norfolk, Suffolk, Portsmouth, Newport News, Williamsburg and Cape Charles in Virginia, plus Moyock and the Outer Banks in North Carolina. Type your zip code and I’ll check it.', l: [['Service areas', 'service-areas/']] },
    { k: ['guarantee', 'not happy', 'unhappy', 'satisf', 'redo', 'missed', 'make it right', 'warranty'], a: 'Satisfaction is guaranteed. If you aren’t thrilled with the work, Jeff will do everything he can to make it right. He wants you as a client for life.' },
    { k: ['water-fed', 'water fed', 'pole', 'purified', 'pure water', 'spot', 'streak', 'high window', 'second story', '2nd story', 'third story', '3 story', 'three story', '2 story', 'two story', 'stories', 'story house', 'tall', 'ladder'], a: 'Water-fed pole cleaning uses purified water and extendable poles to clean glass from the ground. The water is filtered, so it dries clear with no spots or streaks, and it reaches second- and third-story windows without ladders.', l: [['Water-fed pole cleaning', 'services/waterfed-pole-window-cleaning/']] },
    { k: ['soft wash', 'softwash', 'damage', 'siding', 'vinyl', 'paint', 'pressure vs', 'difference', 'safe for'], a: 'High pressure can damage siding, so we soft wash siding, roofs and awnings: a cleaning solution does the work and we rinse at low pressure. Concrete and other hard surfaces get full pressure because they can take it.', l: [['Soft washing', 'services/soft-washing/'], ['Pressure vs soft washing', 'window-cleaning-articles/pressure-washing-vs-soft-washing-understanding-the-difference/']] },
    { k: ['how often', 'how frequently', 'schedule regular', 'every year', 'maintenance plan', 'recurring'], a: 'Near the water, salt and humidity build up fast. Many coastal homeowners clean windows a few times a year and wash the house about once a year. Jeff can recommend a schedule for your home.' },
    { k: ['inside', 'interior', 'indoor'], a: 'Yes, we clean interior windows as well as exterior. Some customers book inside-only before the holidays; others do full inside-and-out service.', l: [['Residential window washing', 'services/residential-window-washing/']] },
    { k: ['commercial', 'business', 'storefront', 'office', 'restaurant', 'property manager', 'hoa'], a: 'Yes. We clean storefronts, offices, restaurants and other commercial properties, and schedule around your business hours.', l: [['Commercial window washing', 'services/commercial-window-washing/'], ['Commercial pressure washing', 'services/pressure-washing/commercial-pressure-washing/']] },
    { k: ['holiday', 'christmas', 'lights', 'lighting', 'decorat'], a: 'We design, install, maintain, take down and store holiday lighting using commercial-grade LEDs and timers. Installs book up fast, so reach out early.', l: [['Holiday lighting', 'services/holiday-lighting/']] },
    { k: ['roof', 'shingle', 'black streak', 'moss'], a: 'We soft wash roofs to remove black streaks, algae and moss without high pressure that can damage shingles.', l: [['Roof cleaning', 'services/soft-washing/roof-cleaning/']] },
    { k: ['gutter'], a: 'We clean gutters and brighten the outside faces to remove the black "tiger stripes."', l: [['Gutter cleaning', 'services/soft-washing/gutter-cleaning/']] },
    { k: ['driveway', 'concrete', 'patio', 'sidewalk', 'walkway', 'pavers', 'deck', 'fence'], a: 'Driveways, walkways, patios, decks and fences get pressure washed to remove dirt, algae, oil and stains.', l: [['Pressure washing', 'services/pressure-washing/'], ['See before & afters', 'projects/']] },
    { k: ['house wash', 'wash my house', 'mildew', 'algae', 'green', 'mold'], a: 'Our soft wash house washing removes algae, mildew and grime gently, so siding, trim and seals stay protected.', l: [['House washing', 'services/soft-washing/house-washing/']] },
    { k: ['book', 'schedule', 'appointment', 'available', 'availability', 'soon', 'this week', 'tomorrow'], a: 'The fastest way to book is to call or text Jeff. You can also use the online estimate and send it to him in one tap.', l: [['Get my estimate', '#estimate']] , jeff: true },
    { k: ['photo', 'picture', 'before and after', 'before & after', 'work', 'example', 'portfolio'], a: 'Here are real before-and-after photos from Jeff’s jobs.', l: [['Our work', 'projects/']] },
    { k: ['review', 'rating', 'stars', 'google'], a: 'Every review on Google is 5 stars. Customers mention Jeff being on time, thorough and fairly priced.', l: [['Read reviews', 'reviews/']] },
    { k: ['who', 'owner', 'jeff', 'experience', 'how long', 'years'], a: 'Priority Window Cleaning is owner-operated by Jeff Parks, with more than 20 years of experience and a focus on high-end residential homes.', l: [['About us', 'about-us/']] },
    { k: ['phone', 'call', 'number', 'contact', 'text', 'reach'], a: 'Call or text Jeff at ' + PHONE + '.', jeff: true }
  ];
  var CHIPS = [['What services do you offer?', 'services'], ['Do you serve my area?', 'area'], ['How do I get a price?', 'price'], ['Any coupons?', 'coupon']];

  function norm(s) { return ' ' + s.toLowerCase().replace(/[^a-z0-9&' -]+/g, ' ') + ' '; }
  function match(q) {
    var t = norm(q), best = null, score = 0;
    var zip = q.match(/\b(\d{5})\b/);
    if (zip) {
      var p = +zip[1].slice(0, 3), ok = (p >= 233 && p <= 236) || p === 279;
      return { a: ok ? 'Yes, ' + zip[1] + ' is in our service area.' : zip[1] + ' is outside our usual area, but Jeff may still be able to help.', l: ok ? [['Get my estimate', '#estimate']] : null, jeff: !ok };
    }
    TOPICS.forEach(function (tp) {
      var s = 0;
      tp.k.forEach(function (w) { if (t.indexOf(w.length < 5 ? ' ' + w : w) > -1) s += w.length; });
      if (s > score) { score = s; best = tp; }
    });
    return best;
  }

  // ---- UI ----
  var css = document.createElement('div');
  css.innerHTML =
    '<button class="chat-fab" type="button" aria-expanded="false" aria-controls="chat-box"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v10H9l-5 4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M8 9h8M8 12h5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg><span>Ask a question</span></button>' +
    '<section class="chat-box" id="chat-box" role="dialog" aria-label="Ask a question" hidden>' +
      '<header class="chat-head"><div><b>Questions? Ask here.</b><span>Instant answers · Jeff replies by text</span></div><button class="chat-x" type="button" aria-label="Close chat"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button></header>' +
      '<div class="chat-log" role="log" aria-live="polite"></div>' +
      '<div class="chat-chips"></div>' +
      '<form class="chat-form"><label class="sr" for="chat-in">Type your question</label><input id="chat-in" type="text" autocomplete="off" placeholder="Type a question or your zip code" maxlength="300"><button type="submit" aria-label="Send"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></button></form>' +
      '<p class="chat-note">Automated answers from our website. For anything else, Jeff will text you back.</p>' +
    '</section>';
  while (css.firstChild) document.body.appendChild(css.firstChild);

  var fab = document.querySelector('.chat-fab'), box = document.getElementById('chat-box');
  var log = box.querySelector('.chat-log'), chips = box.querySelector('.chat-chips');
  var form = box.querySelector('.chat-form'), input = document.getElementById('chat-in');
  var started = false;

  function add(who, text, links, askJeff, question) {
    var m = document.createElement('div'); m.className = 'msg ' + who;
    var p = document.createElement('p'); p.textContent = text; m.appendChild(p);
    if (links && links.length) {
      var row = document.createElement('div'); row.className = 'msg-links';
      links.forEach(function (l) { var a = document.createElement('a'); a.href = l[1].charAt(0) === '#' ? (BASE || './') + l[1] : u(l[1]); a.textContent = l[0]; row.appendChild(a); });
      m.appendChild(row);
    }
    if (askJeff) {
      var j = document.createElement('div'); j.className = 'msg-jeff';
      var body = question ? 'Hi Jeff, question from your website: ' + question : 'Hi Jeff, I have a question:';
      j.innerHTML = '<a class="mj-text" href="sms:' + TEL + '?&body=' + encodeURIComponent(body) + '">Text Jeff</a><a class="mj-call" href="tel:' + TEL + '">Call ' + PHONE + '</a>';
      m.appendChild(j);
    }
    log.appendChild(m); log.scrollTop = log.scrollHeight;
  }
  function reply(q) {
    var r = match(q);
    var typing = document.createElement('div'); typing.className = 'msg bot typing'; typing.innerHTML = '<p><i></i><i></i><i></i></p>';
    log.appendChild(typing); log.scrollTop = log.scrollHeight;
    setTimeout(function () {
      typing.remove();
      if (r) add('bot', r.a, r.l, r.jeff, q);
      else add('bot', "I don't have an answer for that one, but Jeff does. Send him your question and he'll text you back.", null, true, q);
    }, 550);
  }
  function renderChips() {
    chips.innerHTML = '';
    CHIPS.forEach(function (c) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = c[0];
      b.addEventListener('click', function () { add('me', c[0]); reply(c[1]); });
      chips.appendChild(b);
    });
  }
  function open(v) {
    box.hidden = !v; fab.setAttribute('aria-expanded', v ? 'true' : 'false');
    document.documentElement.classList.toggle('chat-open', v);
    if (v) {
      if (!started) { started = true; add('bot', 'Hi! I can answer common questions about Priority Window Cleaning right away. What can I help with?'); renderChips(); }
      setTimeout(function () { input.focus({ preventScroll: true }); }, 50);
    } else fab.focus({ preventScroll: true });
  }
  fab.addEventListener('click', function () { open(box.hidden); });
  box.querySelector('.chat-x').addEventListener('click', function () { open(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !box.hidden) open(false); });
  form.addEventListener('submit', function (e) {
    e.preventDefault(); var q = input.value.trim(); if (!q) return;
    add('me', q); input.value = ''; reply(q);
  });
  box.addEventListener('click', function (e) { var a = e.target.closest('.msg-links a'); if (a && a.getAttribute('href').indexOf('#') > -1) open(false); });
})();
