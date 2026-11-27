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


def image_for(path):
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


def header(pre):
    return f'''<header class="top">
  <div class="wrap">
    <a class="logo" href="{pre}" aria-label="Priority Window Cleaning and Pressure Washing, home">
      {LOGO.format(d="var(--logo-diamond)", star=STAR)}
      {WORDMARK}
    </a>
    <nav class="links" aria-label="Main">
      <a href="{pre}services/">Services</a>
      <a href="{pre}service-areas/">Areas</a>
      <a href="{pre}#about">About Jeff</a>
      <a href="{pre}#reviews">Reviews</a>
      <a href="{pre}#estimate">Estimate</a>
    </nav>
    <a class="top-phone num" href="tel:{PHONE_TEL}">{PHONE}</a>
    <a class="btn btn-primary btn-sm" href="{pre}#estimate">Free estimate</a>
  </div>
</header>'''


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
      <div><h4>Company</h4><ul><li><a href="{pre}#about">About Jeff</a></li><li><a href="{pre}#estimate">Free estimate</a></li><li><a href="{pre}#reviews">Reviews &amp; offers</a></li></ul></div>
    </div>
    <p class="legal">© 2026 Priority Window Cleaning &amp; Pressure Washing · Virginia Beach, VA</p>
  </div>
</footer>
<div class="mbar">
  <a class="btn btn-line" href="tel:{PHONE_TEL}">Call</a>
  <a class="btn btn-line" href="sms:{PHONE_TEL}">Text</a>
  <a class="btn btn-primary" href="{pre}#estimate">Estimate</a>
</div>'''


FAVICON = None


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
<link rel="stylesheet" href="{pre}assets/site.css">
{ld_html}
</head>
<body>
{header(pre)}
<main>'''


def card_grid(items, pre):
    cards = []
    for p, name, sub in items:
        img = image_for(p) if p in DATA else None
        im = f'<img src="{pre}{img}" width="450" height="300" alt="" loading="lazy">' if img else ''
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
    elif path.startswith('service-areas'):
        links = SERVICES
        title = 'Services in ' + AREA_NAMES.get(path, 'your area').split(',')[0]
    else:
        links = SERVICES
        title = 'Our services'
    lis = ''.join(f'<li><a href="{pre}{p}/"{" aria-current=\"page\"" if p == path else ""}>{n}</a></li>' for p, n in links)
    return f'''<aside class="side">
        <div class="side-cta">
          <p class="lbl">Free estimate</p>
          <h3>See your price range in seconds</h3>
          <a class="btn btn-light" href="{pre}#estimate">Get my estimate</a>
          <a class="side-phone num" href="tel:{PHONE_TEL}">or call {PHONE}</a>
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
    parts.append(f'<span aria-current="page">{name}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ' <span aria-hidden="true">/</span> '.join(parts) + '</nav>'


def areas_strip(pre):
    links = ''.join(f'<a href="{pre}{p}/">{n}<i>{s}</i></a>' for p, n, s in AREAS)
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
    name = NAMES.get(path) or AREA_NAMES.get(path) or ('Services' if path == 'services' else 'Service areas')
    kicker = 'Service area' if path.startswith('service-areas') else 'Services'
    img = image_for(path)
    if path == 'service-areas':
        img = None
    fig = (f'<figure class="page-photo"><img src="{pre}{img}" width="450" height="300" alt="{html.escape(name)}"></figure>' if img else '')
    out = [head(path, pre, d['title'], d['desc'], d['faq'])]
    out.append(f'''<section class="page-hero">
  <div class="wrap">
    {crumbs(path, pre, name)}
    <div class="page-hero-grid{' no-photo' if not fig else ''}">
      <div>
        <p class="kicker">{kicker}</p>
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
    elif path == 'service-areas':
        grid = card_grid([(p, f'{n}, {s}', first_sentence(p)) for p, n, s in AREAS], pre)
    if grid:
        out.append(f'<section style="padding-block:8px 56px"><div class="wrap">{grid}</div></section>')
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


def main():
    global FAVICON
    idx = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    FAVICON = re.search(r'<link rel="icon"[^>]*>', idx).group(0)
    for path in DATA:
        build_page(path)
    print('built', len(DATA), 'pages')


if __name__ == '__main__':
    main()
