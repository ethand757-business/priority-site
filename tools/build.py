#!/usr/bin/env python3
"""Builds the service and service-area pages from tools/content.json.

The text comes from Priority Window Cleaning's existing pages on windowcleaningva.com.
Each page is written to the same path it has on that site (for example
services/residential-window-washing/index.html), so the web addresses stay the same.

Run from the repository root:  python3 tools/build.py
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, 'tools', 'content.json'), encoding='utf-8'))
DOMAIN = 'https://windowcleaningva.com'
PHONE_TEL = '+17577499274'
PHONE = '(757) 749-9274'
GMAPS = 'https://www.google.com/maps?cid=9292761169929349653'
FB = 'https://www.facebook.com/profile.php?id=61586062044409'

SERVICES = [
    ('services/residential-window-washing', 'Residential Window Washing'),
    ('services/commercial-window-washing', 'Commercial Window Washing'),
    ('services/waterfed-pole-window-cleaning', 'Water-Fed Pole Window Cleaning'),
    ('services/pressure-washing', 'Pressure Washing'),
    ('services/soft-washing', 'Soft Washing'),
    ('services/holiday-lighting', 'Holiday Lighting'),
]
SUBS = {
    'services/pressure-washing': [
        ('services/pressure-washing/driveway-cleaning', 'Driveway Cleaning'),
        ('services/pressure-washing/concrete-cleaning', 'Concrete Cleaning'),
        ('services/pressure-washing/commercial-pressure-washing', 'Commercial Pressure Washing'),
    ],
    'services/soft-washing': [
        ('services/soft-washing/house-washing', 'House Washing'),
        ('services/soft-washing/roof-cleaning', 'Roof Cleaning'),
        ('services/soft-washing/gutter-cleaning', 'Gutter Cleaning'),
        ('services/soft-washing/awning-cleaning', 'Awning Cleaning'),
    ],
}
PARENT = {child: parent for parent, kids in SUBS.items() for child, _ in kids}
NAMES = dict(SERVICES + [k for kids in SUBS.values() for k in kids])
AREAS = [
    ('service-areas/virginia-beach-va-window-washing', 'Virginia Beach', 'VA'),
    ('service-areas/chesapeake-va-window-washing', 'Chesapeake', 'VA'),
    ('service-areas/norfolk-va-window-washing', 'Norfolk', 'VA'),
    ('service-areas/suffolk-va-window-washing', 'Suffolk', 'VA'),
    ('service-areas/portsmouth-nc-window-washing', 'Portsmouth', 'VA'),
    ('service-areas/newport-news-va-window-washing', 'Newport News', 'VA'),
    ('service-areas/williamsburg-va-window-washing', 'Williamsburg', 'VA'),
    ('service-areas/cape-charles-va-window-washing', 'Cape Charles', 'VA'),
    ('service-areas/moyock-nc-window-washing', 'Moyock', 'NC'),
    ('service-areas/outer-banks-nc-window-washing', 'Outer Banks', 'NC'),
]
AREA_NAMES = {p: f'{n}, {s}' for p, n, s in AREAS}
BLOG = 'window-cleaning-articles'
# Same order as the articles page on windowcleaningva.com (newest first there).
ARTICLES = [BLOG + '/' + slug for slug in [
    'top-7-signs-your-home-needs-professional-pressure-washing',
    'the-hidden-health-risks-of-mold-and-mildew-on-your-homes-exterior',
    'deck-and-patio-cleaning-get-your-outdoor-space-ready-for-summer-entertaining',
    'top-5-signs-your-home-needs-professional-pressure-washing-before-summer',
    'how-coastal-weather-affects-your-windows-and-what-to-do-about-it',
    'why-spring-is-the-best-time-to-pressure-wash-your-home-in-virginia-beach',
    'how-awning-cleaning-extends-the-life-of-your-outdoor-shades',
    'how-water-fed-pole-window-cleaning-reduces-risk-on-commercial-jobs',
    'pressure-washing-vs-soft-washing-understanding-the-difference',
]]


def article_title(path):
    # Short title from the page <title>, before the first " | "
    return html.unescape(DATA[path]['title'].split(' | ')[0]).strip()

REVIEWS = {
    'kevin': ("We've been using Priority for window cleaning and power washing our house for a couple of years. Jeff has always been on time and done an excellent job. He does quality work and a fair price.", 'Kevin L.'),
    'kara': ("I hired these guys to clean the windows, siding, decking and trim on my house. Jeff always showed up on time… He takes pride in his work and made sure we were 100% happy with the job.", 'Kara M.'),
    'lauren': ("He cleans the windows of the business I work at inside and out (approximately 50 very large) and does a fantastic job every time. They always come out pristine and brand new looking.", 'Lauren A.'),
    'johnny': ("Priority Window Cleaning does great work. I've interacted with Jeff multiple times and he and Matt were 100% on point. I vouch for them wholeheartedly.", 'Johnny E.'),
    'lori': ("His attention to detail doesn't go unnoticed. I always know I can count on him to get the job done correctly and done in a timely manner.", 'Lori B., property manager'),
}


def review_for(path):
    if 'commercial' in path:
        return REVIEWS['lauren']
    if 'pressure' in path or 'house-washing' in path or 'soft-washing' == path.split('/')[-1]:
        return REVIEWS['kevin']
    if 'soft-washing' in path or 'deck' in path:
        return REVIEWS['kara']
    if 'holiday' in path or 'roof' in path:
        return REVIEWS['lori']
    return REVIEWS['johnny']


# Higgsfield-generated photos for the main service pages (replacing stock images).
IMG_OVERRIDE = {
    'services/residential-window-washing': 'images/site/hf-residential-wfp.jpg',
    'services/commercial-window-washing': 'images/site/hf-commercial.jpg',
    'services/waterfed-pole-window-cleaning': 'images/site/hf-waterfed.jpg',
    'services/pressure-washing': 'images/site/hf-driveway.jpg',
    'services/pressure-washing/driveway-cleaning': 'images/site/hf-driveway.jpg',
    'services/soft-washing': 'images/site/hf-softwash.jpg',
    'services/soft-washing/house-washing': 'images/site/hf-softwash.jpg',
    'services/holiday-lighting': 'images/site/hf-holiday.jpg',
}
# Service icon (symbol id in assets/icons.txt) for each service page.
ICON = {
    'services/residential-window-washing': 'window', 'services/commercial-window-washing': 'store',
    'services/waterfed-pole-window-cleaning': 'pole', 'services/pressure-washing': 'drive',
    'services/pressure-washing/driveway-cleaning': 'drive', 'services/pressure-washing/concrete-cleaning': 'drive',
    'services/pressure-washing/commercial-pressure-washing': 'store', 'services/soft-washing': 'house',
    'services/soft-washing/house-washing': 'house', 'services/soft-washing/roof-cleaning': 'roof',
    'services/soft-washing/gutter-cleaning': 'gutter', 'services/soft-washing/awning-cleaning': 'gutter',
    'services/holiday-lighting': 'lights',
}
LANDMARK = {p: 'lm-' + p.split('/')[1].rsplit('-', 3)[0] for p, n, st in AREAS}
AREA_MAP = open(os.path.join(ROOT, 'assets', 'area-map.txt'), encoding='utf-8').read()


def area_map(pre):
    return AREA_MAP.replace('__PRE__', pre)


def landmark(path, cls='lm'):
    lm = LANDMARK.get(path)
    return f'<svg class="{cls}" aria-hidden="true"><use href="#ic-{lm}"/></svg>' if lm else ''


ICONS_SPRITE = open(os.path.join(ROOT, 'assets', 'icons.txt'), encoding='utf-8').read()


def icon(path, cls='ic'):
    i = ICON.get(path) or (LANDMARK.get(path) if 'LANDMARK' in globals() else None)
    return f'<svg class="{cls}" aria-hidden="true"><use href="#ic-{i}"/></svg>' if i else ''


def image_for(path):
    if path in IMG_OVERRIDE:
        return IMG_OVERRIDE[path]
    img = DATA[path].get('img')
    return 'images/site/' + os.path.basename(img) if img else None


def prefix_for(path):
    return '../' * (path.count('/') + 1)


def rewrite_links(h, pre):
    def fix(m):
        href = html.unescape(m.group(1))
        inner = m.group(2)
        if href.startswith(('tel:', 'mailto:', 'http://', 'https://')):
            if href.startswith('tel:'):
                href = 'tel:' + PHONE_TEL
            return f'<a href="{html.escape(href, quote=True)}">{inner}</a>'
        p = href.strip('/').split('#')[0].split('?')[0]
        if p == '':
            return f'<a href="{pre}">{inner}</a>'
        if p in DATA:
            return f'<a href="{pre}{p}/">{inner}</a>'
        if p == 'contact-us':
            return f'<a href="{pre}#estimate">{inner}</a>'
        if p == 'about-us':
            return f'<a href="{pre}#about">{inner}</a>'
        if p == 'coupons':
            return f'<a href="{pre}#reviews">{inner}</a>'
        return inner  # pages not rebuilt here (articles, projects): keep the words, drop the link
    return re.sub(r'<a href="([^"]*)">(.*?)</a>', fix, h)


def clean_blocks(blocks):
    """Drop truncated teaser blurbs ("... [...]") and headings that have no content after them."""
    trimmed = []
    for b in blocks:
        if b['tag'] == 'p' and re.search(r'\[(…|\.\.\.|&hellip;)\]\s*$', html.unescape(b['html'])):
            if trimmed and trimmed[-1]['tag'] == 'h3':
                trimmed.pop()
            continue
        trimmed.append(b)
    blocks = trimmed
    out = []
    rank = {'h1': 1, 'h2': 2, 'h3': 3}
    for i, b in enumerate(blocks):
        if b['tag'] in rank:
            nxt = blocks[i + 1] if i + 1 < len(blocks) else None
            if nxt is None or (nxt['tag'] in rank and rank[nxt['tag']] <= rank[b['tag']]):
                continue
        out.append(b)
    return out


def render_blocks(blocks, pre):
    out = []
    for b in blocks:
        t = b['tag']
        if t in ('ul', 'ol'):
            items = ''.join(f'<li>{rewrite_links(i, pre)}</li>' for i in b['items'])
            out.append(f'<{t}>{items}</{t}>')
        else:
            out.append(f'<{t}>{rewrite_links(b["html"], pre)}</{t}>')
    return '\n          '.join(out)


def strip_tags(h):
    return re.sub(r'<[^>]+>', '', html.unescape(h)).strip()


def first_sentence(path):
    for b in DATA[path]['blocks']:
        if b['tag'] == 'p':
            t = strip_tags(b['html'])
            m = re.match(r'(.+?[.!?])(\s|$)', t)
            return m.group(1) if m else t
    return ''


LOGO = ('<svg class="logo-mark" viewBox="0 0 120 120" aria-hidden="true"><polygon points="60,2 118,60 60,118 2,60" fill="{d}"/>'
        '<polygon points="60,14 84,38 60,62 36,38" fill="#BDEBFA"/><polygon points="86,40 106,60 86,80 66,60" fill="#1E9BD7"/>'
        '<polygon points="34,40 54,60 34,80 14,60" fill="#6FD0EE"/><polygon points="60,64 82,86 60,108 38,86" fill="#1E9BD7"/>{star}</svg>')
STAR = '<path d="M60 44 L62.5 57.5 L76 60 L62.5 62.5 L60 76 L57.5 62.5 L44 60 L57.5 57.5 Z" fill="#FFFFFF"/>'
WORDMARK = '<span class="logo-text">Priority<small>Window Cleaning</small><small class="sub2">&amp; Pressure Washing</small></span>'


def nav_menus(pre):
    """Menu groups shared by the desktop dropdowns and the phone menu."""
    L = lambda p: f'{pre}{p}/' if p else pre
    services = [
        ('Window cleaning', [('services/residential-window-washing', 'Residential window washing'),
                             ('services/commercial-window-washing', 'Commercial window washing'),
                             ('services/waterfed-pole-window-cleaning', 'Water-fed pole cleaning')]),
        ('Pressure washing', [('services/pressure-washing', 'Pressure washing'),
                              ('services/pressure-washing/driveway-cleaning', 'Driveway cleaning'),
                              ('services/pressure-washing/concrete-cleaning', 'Concrete cleaning'),
                              ('services/pressure-washing/commercial-pressure-washing', 'Commercial pressure washing')]),
        ('Soft washing', [('services/soft-washing', 'Soft washing'),
                          ('services/soft-washing/house-washing', 'House washing'),
                          ('services/soft-washing/roof-cleaning', 'Roof cleaning'),
                          ('services/soft-washing/gutter-cleaning', 'Gutter cleaning'),
                          ('services/soft-washing/awning-cleaning', 'Awning cleaning')]),
        ('More', [('services/holiday-lighting', 'Holiday lighting'), ('services', 'All services')]),
    ]
    areas = [('Virginia', [(p, n) for p, n, st in AREAS if st == 'VA']),
             ('North Carolina', [(p, n) for p, n, st in AREAS if st == 'NC'] + [('service-areas', 'All service areas')])]
    about = [('', [('about-us', 'About us'), ('reviews', 'Reviews'), ('coupons', 'Coupons'), (BLOG, 'Tips & articles')])]
    return [('Services', 'services', services, 'wide'), ('Areas', 'service-areas', areas, ''),
            ('Our work', 'projects', None, ''), ('About', 'about-us', about, ''), ('Contact', 'contact-us', None, '')], L


def header(pre):
    menus, L = nav_menus(pre)
    desk, phone = [], []
    for i, (label, path, groups, cls) in enumerate(menus):
        if not groups:
            desk.append(f'<a class="nav-top" href="{L(path)}">{label}</a>')
            phone.append(f'<a class="mnav-link" href="{L(path)}">{label}</a>')
            continue
        cols = ''.join(
            f'<div class="menu-col">{"<p class=\"menu-h\">" + html.escape(h) + "</p>" if h else ""}<ul>'
            + ''.join(f'<li><a href="{L(p)}">{icon(p)}{html.escape(n)}</a></li>' for p, n in items) + '</ul></div>'
            for h, items in groups)
        mid = f'menu-{i}'
        desk.append(f'''<div class="nav-item">
        <a class="nav-top" href="{L(path)}">{label}</a><button class="nav-caret" type="button" aria-expanded="false" aria-controls="{mid}" aria-label="{label} menu"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        <div class="menu {cls}" id="{mid}">{cols}</div>
      </div>''')
        links = ''.join(f'<li><a href="{L(p)}">{icon(p)}{html.escape(n)}</a></li>' for h, items in groups for p, n in items)
        phone.append(f'<div class="mnav-group"><button class="mnav-sum" type="button" aria-expanded="false" aria-controls="m{mid}">{label}<span class="mnav-pm" aria-hidden="true"></span></button><div class="mnav-sub" id="m{mid}"><ul>{links}</ul></div></div>')
    return f'''<header class="top">
  <div class="wrap">
    <a class="logo" href="{pre}" aria-label="Priority Window Cleaning and Pressure Washing, home">
      {LOGO.format(d="var(--logo-diamond)", star=STAR)}
      {WORDMARK}
    </a>
    <nav class="links" aria-label="Main">
      {"".join(desk)}
    </nav>
    <a class="top-phone num" href="tel:{PHONE_TEL}">{PHONE}</a>
    <a class="btn btn-primary btn-sm" href="{pre}#estimate">Free estimate</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mnav" aria-label="Open menu"><span></span><span></span><span></span></button>
  </div>
  <div class="mnav-scrim" aria-hidden="true"></div>
  <nav class="mnav" id="mnav" aria-label="Main" inert>
    <div class="mnav-head">
      <a class="logo" href="{pre}" aria-label="Home">{LOGO.format(d="var(--logo-diamond)", star=STAR)}{WORDMARK}</a>
      <button class="mnav-close" type="button" aria-label="Close menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>
    </div>
    <div class="mnav-body">
      <a class="mnav-link" href="{pre}">Home</a>
      {"".join(phone)}
      <a class="btn btn-primary" href="{pre}#estimate">Get my estimate</a>
      <a class="btn btn-line num" href="tel:{PHONE_TEL}">Call {PHONE}</a>
    </div>
  </nav>
</header>
<script src="{pre}assets/nav.js?v={NAV_V}" defer></script>
<script src="{pre}assets/chat.js?v={CHAT_V}" data-base="{pre}" defer></script>'''


def footer(pre):
    svc = ''.join(f'<li><a href="{pre}{p}/">{n}</a></li>' for p, n in SERVICES)
    areas = ''.join(f'<li><a href="{pre}{p}/">{n}</a></li>' for p, n, s in AREAS[:6])
    return f'''<section class="final" aria-label="Get an estimate" style="padding-block:64px">
  <div class="wrap">
    <div>
      <h2>Ready for flawless windows?</h2>
      <p>Free estimates. Satisfaction guaranteed.</p>
    </div>
    <div class="ctas" style="margin:0">
      <a class="btn btn-light" href="{pre}#estimate">Get my estimate</a>
      <a class="btn btn-line num" href="tel:{PHONE_TEL}">Call {PHONE}</a>
    </div>
  </div>
</section>
<footer>
  <div class="wrap">
    <div class="grid">
      <div>
        <a class="logo" href="{pre}">{LOGO.format(d="#FFFFFF", star="")}{WORDMARK}</a>
        <ul>
          <li><a class="num" href="tel:{PHONE_TEL}">{PHONE}</a></li>
          <li>Virginia Beach, VA</li>
          <li><a href="{GMAPS}" target="_blank" rel="noopener">Google reviews</a> · <a href="{FB}" target="_blank" rel="noopener">Facebook</a></li>
        </ul>
      </div>
      <div><h4>Services</h4><ul>{svc}</ul></div>
      <div><h4>Areas</h4><ul>{areas}<li><a href="{pre}service-areas/">All areas</a></li></ul></div>
      <div><h4>Company</h4><ul><li><a href="{pre}about-us/">About us</a></li><li><a href="{pre}projects/">Our work</a></li><li><a href="{pre}reviews/">Reviews</a></li><li><a href="{pre}coupons/">Coupons</a></li><li><a href="{pre}{BLOG}/">Tips &amp; articles</a></li><li><a href="{pre}contact-us/">Contact</a></li></ul></div>
    </div>
    <p class="legal">© 2026 Priority Window Cleaning &amp; Pressure Washing · Virginia Beach, VA · Licensed &amp; insured · <a href="{pre}privacy/">Privacy</a> · <a href="{pre}terms/">Terms</a> · <a href="{pre}sitemap/">Sitemap</a></p>
  </div>
</footer>
<div class="mbar">
  <a class="btn btn-line" href="tel:{PHONE_TEL}">Call</a>
  <a class="btn btn-line" href="sms:{PHONE_TEL}">Text</a>
  <button class="btn btn-line mbar-ask" type="button" data-chat-open><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v10H9l-5 4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>Ask</button>
  <a class="btn btn-primary" href="{pre}#estimate">Estimate</a>
</div>'''


FAVICON = None
import hashlib
CHAT_V = hashlib.md5(open(os.path.join(ROOT, 'assets', 'chat.js'), 'rb').read()).hexdigest()[:8]
NAV_V = hashlib.md5(open(os.path.join(ROOT, 'assets', 'nav.js'), 'rb').read()).hexdigest()[:8]
CSS_V = hashlib.md5(open(os.path.join(ROOT, 'assets', 'site.css'), 'rb').read()).hexdigest()[:8]


def head(path, pre, title, desc, faq):
    biz = {
        '@context': 'https://schema.org', '@type': 'LocalBusiness',
        'name': 'Priority Window Cleaning', 'telephone': '+1-757-749-9274', 'url': DOMAIN + '/',
        'address': {'@type': 'PostalAddress', 'addressLocality': 'Virginia Beach', 'addressRegion': 'VA', 'addressCountry': 'US'},
        'areaServed': [n for _, n, _ in AREAS],
        'aggregateRating': None,
    }
    del biz['aggregateRating']
    ld = [biz]
    if faq:
        ld.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': strip_tags(f['q']),
             'acceptedAnswer': {'@type': 'Answer', 'text': ' '.join(strip_tags(a) for a in f['a'])}} for f in faq]})
    ld_html = '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="{DOMAIN}/{path}">
{FAVICON}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..112,500..900&family=Public+Sans:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="{pre}assets/site.css?v={CSS_V}">
{ld_html}
</head>
<body>
{ICONS_SPRITE}{header(pre)}
<main>'''


def card_grid(items, pre):
    cards = []
    for p, name, sub in items:
        img = image_for(p) if p in DATA else None
        im = f'<img src="{pre}{img}" width="450" height="300" alt="" loading="lazy">' if img else ''
        if p in LANDMARK:
            im = f'<span class="lm-panel lm-card">{landmark(p)}</span>'
        cards.append(f'<a class="pcard" href="{pre}{p}/">{im}<span class="pcard-body"><b>{name}</b><span>{html.escape(sub)}</span></span></a>')
    return '<div class="pcards">' + ''.join(cards) + '</div>'


def faq_html(faq, pre):
    if not faq:
        return ''
    items = ''.join(
        f'<details><summary>{strip_tags(f["q"])}</summary>{"".join("<p>" + rewrite_links(a, pre) + "</p>" for a in f["a"])}</details>'
        for f in faq)
    return f'''<section aria-labelledby="faq-h" style="padding-top:0">
  <div class="wrap">
    <div class="head"><p class="kicker">Questions</p><h2 id="faq-h">Common questions</h2></div>
    <div class="faq">{items}</div>
  </div>
</section>'''


def sidebar(path, pre):
    q, who = review_for(path)
    if path in SUBS or path in PARENT:
        parent = PARENT.get(path, path)
        links = [(parent, NAMES[parent])] + SUBS[parent]
        title = NAMES[parent] + ' services'
    elif path.startswith(BLOG + '/'):
        links = [(a, article_title(a)) for a in ARTICLES if a != path][:5]
        title = 'More tips & articles'
    elif path.startswith('service-areas'):
        links = SERVICES
        title = 'Services in ' + AREA_NAMES.get(path, 'your area').split(',')[0]
    else:
        links = SERVICES
        title = 'Our services'
    lis = ''.join(f'<li><a href="{pre}{p}/"{" aria-current=\"page\"" if p == path else ""}>{icon(p)}{n}</a></li>' for p, n in links)
    return f'''<aside class="side">
        <div class="side-cta">
          <p class="lbl">Free estimate</p>
          <h3>See your price range in seconds</h3>
          <a class="btn btn-light" href="{pre}#estimate">Get my estimate</a>
          <a class="side-phone num" href="tel:{PHONE_TEL}">or call {PHONE}</a>
          <p class="side-li"><svg class="ic" aria-hidden="true"><use href="#ic-tb-guarantee"/></svg>Licensed &amp; insured</p>
        </div>
        <nav class="side-box" aria-label="{html.escape(title)}"><h3>{html.escape(title)}</h3><ul>{lis}</ul></nav>
        <figure class="side-box side-review"><span class="rstars" aria-label="5 out of 5 stars">★★★★★</span><blockquote>{q}</blockquote><figcaption>{who} · Google review</figcaption></figure>
      </aside>'''


def crumbs(path, pre, name):
    parts = [f'<a href="{pre}">Home</a>']
    if path.startswith('services/'):
        parts.append(f'<a href="{pre}services/">Services</a>')
        if path in PARENT:
            parts.append(f'<a href="{pre}{PARENT[path]}/">{NAMES[PARENT[path]]}</a>')
    elif path.startswith('service-areas/'):
        parts.append(f'<a href="{pre}service-areas/">Service areas</a>')
    elif path.startswith(BLOG + '/'):
        parts.append(f'<a href="{pre}{BLOG}/">Tips &amp; articles</a>')
    parts.append(f'<span aria-current="page">{name}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(parts) + '</nav>'


def areas_strip(pre):
    links = ''.join(f'<a href="{pre}{p}/">{landmark(p, "lm lm-pill")}{n}<i>{s}</i></a>' for p, n, s in AREAS)
    return f'''<section class="est-band" aria-labelledby="ar-h" style="padding-block:56px">
  <div class="wrap">
    <div class="head" style="margin-bottom:24px"><p class="kicker">Service area</p><h2 id="ar-h">Serving coastal Virginia and North Carolina</h2></div>
    <div class="area-links">{links}</div>
  </div>
</section>'''


def build_page(path):
    d = DATA[path]
    pre = prefix_for(path)
    blocks = clean_blocks(d['blocks'])
    h1 = next((b for b in blocks if b['tag'] == 'h1'), None)
    rest = [b for b in blocks if b is not h1]
    intro = None
    if rest and rest[0]['tag'] == 'p':
        intro, rest = rest[0], rest[1:]
    if path == 'services':
        # the overview's per-service blurbs become cards, so drop those h3/p pairs
        keep, skip = [], False
        for b in rest:
            if b['tag'] == 'h3':
                skip = True
                continue
            if skip and b['tag'] == 'p':
                skip = False
                continue
            skip = False
            keep.append(b)
        rest = clean_blocks(keep)
    if path.startswith(BLOG + '/'):
        name = article_title(path)
    else:
        name = NAMES.get(path) or AREA_NAMES.get(path) or {'services': 'Services', 'service-areas': 'Service areas', BLOG: 'Tips & articles'}.get(path) or GENERAL[path][0]
    if path in GENERAL:
        kicker = GENERAL[path][1]
    else:
        kicker = 'Service area' if path.startswith('service-areas') else ('Tips &amp; articles' if path.startswith(BLOG) else 'Services')
    img = image_for(path)
    if path in ('service-areas', BLOG):
        img = None
    if path == 'about-us':
        img = 'images/jeff-about.jpg'
    fig = (f'<figure class="page-photo"><img src="{pre}{img}" width="450" height="300" alt="{html.escape(name)}"></figure>' if img else '')
    if path in LANDMARK:
        fig = f'<figure class="page-photo lm-panel">{landmark(path)}<figcaption>{html.escape(name)}</figcaption></figure>'
    out = [head(path, pre, d['title'], d['desc'], d['faq'])]
    out.append(f'''<section class="page-hero">
  <div class="wrap">
    {crumbs(path, pre, name)}
    <div class="page-hero-grid{' no-photo' if not fig else ''}">
      <div>
        <p class="kicker">{kicker}</p>
        {icon(path, 'ic ic-hero')}
        <h1>{rewrite_links(h1["html"], pre) if h1 else html.escape(name)}</h1>
        {('<p class="lede">' + rewrite_links(intro['html'], pre) + '</p>') if intro else ''}
        <div class="ctas">
          <a class="btn btn-primary" href="{pre}#estimate">Get my estimate</a>
          <a class="btn btn-line num" href="tel:{PHONE_TEL}">Call {PHONE}</a>
        </div>
      </div>
      {fig}
    </div>
  </div>
</section>''')
    grid = ''
    if path == 'services':
        items = [(p, n, first_sentence(p)) for p, n in SERVICES] + [(p, n, first_sentence(p)) for kids in SUBS.values() for p, n in kids]
        grid = card_grid(items, pre)
    elif path in SUBS:
        grid = card_grid([(p, n, first_sentence(p)) for p, n in SUBS[path]], pre)
    elif path == BLOG:
        grid = card_grid([(a, article_title(a), first_sentence(a)) for a in ARTICLES], pre)
    elif path == 'service-areas':
        grid = '<div class="map-wrap">' + area_map(pre) + '</div>' + card_grid([(p, f'{n}, {s}', first_sentence(p)) for p, n, s in AREAS], pre)
    if grid:
        out.append(f'<section style="padding-block:8px 56px"><div class="wrap">{grid}</div></section>')
    if path in EXTRAS:
        out.append(EXTRAS[path](pre))
        if path in ('sitemap', 'reviews', 'contact-us', 'projects'):
            rest = []
    if rest:
        out.append(f'''<section class="page-body" style="padding-top:{"0" if grid else "8px"}">
  <div class="wrap page-grid">
    <article class="prose">
          {render_blocks(rest, pre)}
    </article>
    {sidebar(path, pre)}
  </div>
</section>''')
    out.append(faq_html(d['faq'], pre))
    if not path.startswith('service-areas'):
        out.append(areas_strip(pre))
    out.append('</main>')
    out.append(footer(pre))
    out.append('</body>\n</html>\n')
    dest = os.path.join(ROOT, path, 'index.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, 'w', encoding='utf-8').write('\n'.join(x for x in out if x))
    return dest


GENERAL = {
    'about-us': ('About us', 'About'),
    'contact-us': ('Contact', 'Contact'),
    'coupons': ('Coupons', 'Offers'),
    'projects': ('Our work', 'Recent projects'),
    'reviews': ('Reviews', 'Reviews'),
    'privacy': ('Privacy policy', 'Legal'),
    'terms': ('Terms of use', 'Legal'),
    'sitemap': ('Sitemap', 'Sitemap'),
}
REVIEW_CARDS = [
    ("Johnny E.", "Priority Window Cleaning does great work. I've interacted with Jeff multiple times and he and Matt were 100% on point. I vouch for them wholeheartedly.", "Interior &amp; exterior window cleaning"),
    ("Christy J.", "Priority Window Cleaning did an amazing job on our home! Super friendly and professional!", "Interior &amp; exterior window cleaning"),
    ("Kevin L.", "We've been using Priority for window cleaning and power washing our house for a couple of years. Jeff has always been on time and done an excellent job. We would highly recommend him. He does quality work and a fair price.", "Window cleaning &amp; power washing"),
    ("Kara M.", "I hired these guys to clean the windows, siding, decking and trim on my house. Jeff always showed up on time and was efficient at getting me a quote and getting the work done. He takes pride in his work and made sure we were 100% happy with the job. I wouldn't hesitate to call them again.", "Windows, siding, deck &amp; trim"),
    ("Lori B.", "His attention to detail doesn't go unnoticed. I always know I can count on him to get the job done correctly and done in a timely manner. He's punctual, orderly, thorough and always checks his work after he has completed it… Thanks Jeff, you make my job as property manager so much easier!", "Property manager · rooftop, skylight &amp; window cleaning"),
    ("Lauren A.", "Jeff is one of the hardest workers that I know of today. He cleans the windows of the business I work at inside and out (approximately 50 very large) and does a fantastic job every time. They always come out pristine and brand new looking.", "Commercial window cleaning"),
    ("Filia A.", "Jeff is the most professional, gracious, responsible, on time person I have dealt with! In my business I am dealing with a lot of contractors, but Jeff is the one who deserves the five stars!!!", "Business owner"),
    ("Amy G.", "Jeff cleans the windows at our store and does an excellent job every time! He definitely goes above and beyond and is professional and friendly too!", "Commercial window cleaning"),
    ("Kendra P.", "The best I have used. Also cleaned gutters. Price is fair. Will be using again. Highly recommend.", "Windows &amp; gutters"),
    ("Robin R.", "Jeff Parks at Priority Window Cleaning has done a fabulous job for me. He is on time, efficient and goes the extra mile to make sure your windows and skylights shine.", "Windows &amp; skylights"),
    ("Troy W.", "Reasonably priced. Power washed my two story house quickly and quality. Super friendly.", "Pressure washing"),
]
# Strongest results first, alternating window and pressure-washing jobs.
PROJECT_ORDER = ['Window-Cleaning2-hd.jpg', 'Power-Wasing3-hd.jpg', 'Window-Cleaning8-hd.jpg', 'Power-Wasing8-hd.jpg',
                 'Window-Cleaning7-hd.jpg', 'Power-Wasing5-hd.jpg', 'Window-Cleaning45.jpg', 'Power-Wasing4.jpg',
                 'Window-Cleaning6.jpg', 'Power-Wasing6.jpg', 'Window-Cleaning1.jpg', 'Power-Wasing9.jpg',
                 'Window-Cleaning3.jpg', 'Power-Wasing7.jpg', 'Window-Cleaning4.jpg', 'Power-Wasing1.jpg']
_have = set(os.listdir(os.path.join(ROOT, 'images', 'projects')))
PROJECTS = [f for f in PROJECT_ORDER if f in _have] + sorted(_have - set(PROJECT_ORDER))


def extra_reviews(pre):
    cards = '\n'.join(f'''<figure class="review"><span class="rstars" aria-label="5 out of 5 stars">★★★★★</span><blockquote>{t}</blockquote><figcaption><b>{n}</b><span>{sv}</span></figcaption></figure>''' for n, t, sv in REVIEW_CARDS)
    return f'''<section style="padding-block:8px 72px"><div class="wrap">
  <div class="rv-head"><a class="gscore" href="{GMAPS}" target="_blank" rel="noopener" aria-label="Rated 5.0 out of 5 on Google"><b>5.0</b><span class="rstars" aria-hidden="true">★★★★★</span><span>Every review on Google is 5 stars</span></a>
  <div class="row" style="display:flex;flex-wrap:wrap;gap:10px"><a class="btn btn-primary btn-sm" href="{GMAPS}" target="_blank" rel="noopener">All Google reviews</a><a class="btn btn-line btn-sm" href="{GMAPS}" target="_blank" rel="noopener">Leave a review</a></div></div>
  <div class="reviews">{cards}</div>
</div></section>'''


def extra_projects(pre):
    items = []
    for f in PROJECTS:
        kind = 'Pressure washing' if f.lower().startswith('power') else 'Window cleaning'
        items.append(f'<figure class="proj"><a href="{pre}images/projects/{f}" target="_blank" rel="noopener"><img src="{pre}images/projects/{f}" width="600" height="350" alt="Before and after: {kind.lower()} by Priority Window Cleaning" loading="lazy"></a><figcaption>{kind}</figcaption></figure>')
    return f'''<section style="padding-block:8px 72px"><div class="wrap">
  <p class="lede" style="margin-bottom:24px">Real before-and-after photos from Priority Window Cleaning jobs. Tap a photo to see it larger.</p>
  <div class="projects">{"".join(items)}</div>
</div></section>'''


def extra_contact(pre):
    return f'''<section style="padding-block:8px 72px"><div class="wrap">
  <div class="contact-grid">
    <a class="ccard" href="tel:{PHONE_TEL}"><svg class="ic ic-card" aria-hidden="true"><use href="#ic-ct-phone"/></svg><span class="lbl">Call</span><b class="num">{PHONE}</b><span>Talk to Jeff directly.</span></a>
    <a class="ccard" href="sms:{PHONE_TEL}"><svg class="ic ic-card" aria-hidden="true"><use href="#ic-ct-text"/></svg><span class="lbl">Text</span><b class="num">{PHONE}</b><span>Send a photo of the job for a faster quote.</span></a>
    <a class="ccard" href="{pre}#estimate"><svg class="ic ic-card" aria-hidden="true"><use href="#ic-ct-estimate"/></svg><span class="lbl">Online</span><b>Free estimate</b><span>See a price range and send it to Jeff in a minute.</span></a>
    <a class="ccard" href="{GMAPS}" target="_blank" rel="noopener"><svg class="ic ic-card" aria-hidden="true"><use href="#ic-ct-map"/></svg><span class="lbl">Find us</span><b>Virginia Beach, VA</b><span>Open on Google Maps and see our reviews.</span></a>
    <a class="ccard" href="{FB}" target="_blank" rel="noopener"><svg class="ic ic-card" aria-hidden="true"><use href="#ic-ct-social"/></svg><span class="lbl">Follow</span><b>Facebook</b><span>Photos of recent jobs and seasonal offers.</span></a>
    <a class="ccard" href="{pre}service-areas/"><svg class="ic ic-card" aria-hidden="true"><use href="#ic-ct-area"/></svg><span class="lbl">Service area</span><b>10 towns in VA &amp; NC</b><span>Virginia Beach to Williamsburg and the Outer Banks.</span></a>
  </div>
  <div class="map"><iframe title="Priority Window Cleaning on Google Maps" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3196.4962390527767!2d-76.0048718!3d36.758661200000006!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x89bac170a4c8d639%3A0x80f6850c842eaa15!2sPriority%20Window%20Cleaning!5e0!3m2!1sen!2sus!4v1772738932569!5m2!1sen!2sus" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
</div></section>'''


def extra_coupons(pre):
    return f'''<section style="padding-block:8px 56px"><div class="wrap">
  <div class="coupons">
    <div class="coupon-card"><span class="lbl">First-time customers</span><b>$25 off</b><span>any one service</span><small>Mention this coupon when you book · {PHONE}</small></div>
    <div class="coupon-card"><span class="lbl">Refer a friend</span><b>$30 off</b><span>your next service</span><small>Mention your referral when you book · {PHONE}</small></div>
  </div>
</div></section>'''


def extra_sitemap(pre):
    def ul(items):
        return '<ul>' + ''.join(f'<li><a href="{pre}{p}">{html.escape(n)}</a></li>' for p, n in items) + '</ul>'
    groups = [
        ('Main pages', [('', 'Home'), ('about-us/', 'About us'), ('projects/', 'Our work'), ('reviews/', 'Reviews'), ('coupons/', 'Coupons'), ('contact-us/', 'Contact'), (BLOG + '/', 'Tips & articles')]),
        ('Services', [('services/', 'All services')] + [(p + '/', n) for p, n in SERVICES] + [(p + '/', n) for kids in SUBS.values() for p, n in kids]),
        ('Service areas', [('service-areas/', 'All service areas')] + [(p + '/', f'{n}, {s}') for p, n, s in AREAS]),
        ('Tips & articles', [(a + '/', article_title(a)) for a in ARTICLES]),
        ('Legal', [('privacy/', 'Privacy policy'), ('terms/', 'Terms of use')]),
    ]
    cols = ''.join(f'<div class="smap-col"><h2>{html.escape(t)}</h2>{ul(items)}</div>' for t, items in groups)
    return f'<section style="padding-block:8px 72px"><div class="wrap"><div class="smap">{cols}</div></div></section>'


EXTRAS = {'reviews': extra_reviews, 'projects': extra_projects, 'contact-us': extra_contact, 'coupons': extra_coupons, 'sitemap': extra_sitemap}


# Web path the site is served from. '/priority-site/' on GitHub Pages; change to '/' once it is on windowcleaningva.com.
SITE_BASE = '/priority-site/'


def write_404():
    pre = SITE_BASE
    body = f'''<section class="page-hero" style="padding-block:72px">
  <div class="wrap nf">
    <svg class="nf-ic" aria-hidden="true"><use href="#ic-window"/></svg>
    <p class="kicker">Page not found</p>
    <h1>We wiped this page clean.</h1>
    <p class="lede">The page you were looking for isn't here anymore. These will get you where you're going:</p>
    <div class="ctas"><a class="btn btn-primary" href="{pre}">Go to the homepage</a><a class="btn btn-line" href="{pre}#estimate">Get my estimate</a><a class="btn btn-line" href="{pre}services/">Services</a><a class="btn btn-line" href="{pre}contact-us/">Contact</a></div>
  </div>
</section>'''
    page = head('404', pre, 'Page not found | Priority Window Cleaning', 'This page could not be found.', []) + body + '</main>\n' + footer(pre) + '\n</body>\n</html>\n'
    page = page.replace(f'<link rel="canonical" href="{DOMAIN}/404">\n', '<meta name="robots" content="noindex">\n')
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(page)


def write_sitemap_xml():
    urls = [''] + [p + '/' for p in DATA]
    body = ''.join(f'<url><loc>{DOMAIN}/{u}</loc></url>' for u in urls)
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="utf-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n')


def main():
    global FAVICON
    idx = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    FAVICON = re.search(r'<link rel="icon"[^>]*>', idx).group(0)
    idx = re.sub(r'<header class="top">.*?</header>(\n<script src="assets/nav\.js[^"]*" defer></script>)?(\n<script src="assets/chat\.js[^"]*"[^>]*></script>)?', lambda m: header(''), idx, count=1, flags=re.S)
    idx = re.sub(r'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><symbol id="ic-.*?</defs></svg>\n', '', idx, flags=re.S)
    idx = idx.replace('<body>\n', '<body>\n' + ICONS_SPRITE, 1)
    idx = re.sub(r'href="assets/site\.css(\?v=\w+)?"', f'href="assets/site.css?v={CSS_V}"', idx)
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(idx)
    for path in DATA:
        build_page(path)
    write_sitemap_xml()
    write_404()
    print('built', len(DATA), 'pages')


if __name__ == '__main__':
    main()
