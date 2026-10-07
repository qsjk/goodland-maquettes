"""Builds the static Goodland site from src/data/*.json into the repository root.

Usage: python3 src/build.py
All content (texts, prices, lots, image ids) lives in src/data; this script only lays it out.
"""
import html
import json
import pathlib
import re
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'src' / 'data'

PROGRAM_ORDER = [
    'alkamenous-4-peristeri', 'andrea-dimitriou-87-nea-iwnia', 'olimpoy-21-marousi', 'bizantiou-56-papagou',
    'katswnh-5-mosxato', 'dikaiarxou-79-pagrati', 'olympou-23-vrilhssia', 'kalirrois-80-koukaki',
    'verginas-130-agios-dimitrios', 'kekropos-4-6-kallithea', 'kallirrois-100-koykaki', 'evkalyptwn-7-marousi',
]
COMPLETED_ORDER = ['xolargos', 'papagou', 'zografou', 'nikea', 'keratsini', 'agia-paraskevi', 'peukh', 'palaio-faliro']
INTERIOR = [  # slug, el, en, card image (from the current /projects page)
    ('kouzines', 'Κουζίνες', 'Kitchens', '3c238e_d6984b209df94ad68e192c144bb5b339~mv2.jpg'),
    ('saloni', 'Σαλόνια', 'Living rooms', '3c238e_f708d80f8a4c404f86c4866306288453~mv2.jpg'),
    ('upnodomatia', 'Υπνοδωμάτια', 'Bedrooms', '3c238e_9a587a2611294659b3d7980ad2fa1cb9~mv2.jpg'),
    ('wc', 'Μπάνια', 'Bathrooms', '3c238e_ba83666ecf0d409aadeb6b1076cabde9~mv2.jpg'),
]
LOGO = '3c238e_fe85326121a14193bf1f4de266797e7a~mv2.png'
EMAIL = 'goodlandcon@gmail.com'
PHONES = [('2130996050', '213 099 6050'), ('2130354695', '213 035 4695'), ('6945135770', '694 513 5770')]
ADDRESS_EL, ADDRESS_EN = 'Ύδρας 14, Μοσχάτο', 'Ydras 14, Moschato'
FACEBOOK, INSTAGRAM = 'https://www.facebook.com/evgeios/', 'https://www.instagram.com/goodland_constructions/'

TITLE_CASE = {
    'ΤΕΡΨΙΘΕΑΣ 27, ΑΓ. ΠΑΡΑΣΚΕΥΗ': 'Τερψιθέας 27, Αγ. Παρασκευή',
    'ΔΕΛΦΩΝ 13 & ΙΘΑΚΗΣ, ΚΕΡΑΤΣΙΝΙ': 'Δελφών 13 & Ιθάκης, Κερατσίνι',
    'ΑΔΡΑΜΥΤΙΟΥ 15, ΝΙΚΑΙΑ': 'Αδραμυτίου 15, Νίκαια',
    'ΑΙΑΝΤΟΣ 81, ΠΑΛΑΙΟ ΦΑΛΗΡΟ': 'Αίαντος 81, Παλαιό Φάληρο',
    'ΧΕΙΜΑΡΡΑΣ 36, ΠΑΠΑΓΟΥ': 'Χειμάρρας 36, Παπάγου',
    'ΕΘΝΙΚΗΣ ΑΜΥΝΗΣ 1, ΠΑΠΑΓΟΥ': 'Εθνικής Αμύνης 1, Παπάγου',
    'ΚΩΝΣΤΑΝΤΙΝΟΥΠΟΛΕΩΣ 67, ΠΕΥΚΗ': 'Κωνσταντινουπόλεως 67, Πεύκη',
    'ΠΥΘΑΓΟΡΑ 20, ΧΟΛΑΡΓΟΣ': 'Πυθαγόρα 20, Χολαργός',
    'ΑΝΑΣΤΑΣΕΩΣ 55, ΧΟΛΑΡΓΟΣ': 'Αναστάσεως 55, Χολαργός',
    'ΛΟΧΑΓΟΥ ΓΙΑΝΝΟΠΟΥΛΟΥ 11, ΖΩΓΡΑΦΟΥ': 'Λοχαγού Γιαννοπούλου 11, Ζωγράφου',
}
TYPE_EL = {'ΔΙΑΜΕΡΙΣΜΑ': 'Διαμέρισμα', 'ΜΕΖΟΝΕΤΑ': 'Μεζονέτα', 'ΔΙΑΜΕΡΙΣΜΑ-ΜΕΖΟΝΕΤΑ': 'Διαμέρισμα-μεζονέτα',
           'ΔΙΑΜΕΡΙΣΜΑ ΜΕ ΣΟΦΙΤΑ': 'Διαμέρισμα με σοφίτα'}

# ---------- helpers ----------
LATIN2GREEK = str.maketrans('ABEHIKMNOPTXYZoν', 'ΑΒΕΗΙΚΜΝΟΡΤΧΥΖον')
GREEK = re.compile('[Ͱ-Ͽἀ-῿]')


def fix(s):
    """Normalise whitespace and Latin look-alike letters typed inside Greek words."""
    if s is None:
        return None
    s = re.sub(r'[​ ]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    words = s.split(' ')
    out = []
    for i, w in enumerate(words):
        if GREEK.search(w) and re.search('[A-Za-z]', w) and not re.search('[a-z]{2,}', w.replace('ν', '')):
            w = w.translate(LATIN2GREEK)
        elif w == 'H' and i + 1 < len(words) and GREEK.match(words[i + 1]):
            w = 'Η'
        out.append(w)
    return ' '.join(out)


def e(s):
    return html.escape(s or '', quote=True)


def t(el, en=None):
    el, en = fix(el), fix(en)
    if not en or en == el:
        return e(el)
    return f'<span class="el">{e(el)}</span><span class="en">{e(en)}</span>'


def img(mid, w, h, mode='fill'):
    ext = mid.rsplit('.', 1)[-1]
    return f'https://static.wixstatic.com/media/{mid}/v1/{mode}/w_{w},h_{h},al_c,q_80,enc_auto/img.{ext}'


def full(mid):
    return img(mid, 1800, 1800, 'fit')


def price_num(p):
    d = re.sub(r'[^0-9]', '', p or '')
    return int(d) if d else None


def fmt_price(n):
    return f'{n:,}'.replace(',', '.') + ' €'


def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))


def caps_to_title(s):
    s = fix(s)
    return TITLE_CASE.get(s, s)


ICON = {
    'phone': '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    'pin': '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'check': '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    'chev': '<path d="m6 9 6 6 6-6"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
    'bolt': '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    'expand': '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
}


def icon(name, size=18, color='currentColor', cls=''):
    return (f'<svg class="ico {cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[name]}</svg>')


SECTION_TITLES = {
    'ΤΡΙΣΔΙΑΣΤΑΤΕΣ ΑΠΕΙΚΟΝΙΣΕΙΣ': ('Τρισδιάστατες απεικονίσεις', '3D renders'),
    'ΤΟ ΚΤΗΡΙΟ': ('Το κτήριο', 'The building'),
    'ΦΩΤΟΓΡΑΦΙΕΣ': ('Φωτογραφίες', 'Photos'),
}


NAV = [
    ('pros-polisi.html', 'Ακίνητα προς πώληση', 'Properties for sale', 'sale'),
    ('olokliromena-erga.html', 'Ολοκληρωμένα έργα', 'Completed projects', 'done'),
    ('projects.html', 'Εσωτερικοί χώροι', 'Interior design', 'interior'),
    ('contact.html', 'Επικοινωνία', 'Contact', 'contact'),
]


def layout(title, body, active=None, description=None):
    nav = ''.join(
        f'<a href="{h}"{" aria-current=\"page\"" if k == active else ""}>{t(el, en)}</a>' for h, el, en, k in NAV)
    desc = description or 'Εύγειος Goodland Μ. ΕΠΕ | Κατασκευαστική Εταιρία | Κατασκευές Κατοικιών, Πωλήσεις Κατοικιών, Ανακαινίσεις Κατοικιών'
    phones = ''.join(f'<li><a href="tel:+30{p}">{d}</a></li>' for p, d in PHONES)
    return f'''<!doctype html>
<html lang="el" data-lang="el">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="icon" href="{img(LOGO, 64, 64, 'fit')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Commissioner:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<link rel="preconnect" href="https://static.wixstatic.com">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="hdr">
  <div class="wrap hdr-in">
    <a class="brand" href="index.html" aria-label="Εύγειος Goodland – Αρχική">
      <img src="{img(LOGO, 160, 160, 'fit')}" alt="" width="52" height="52">
      <span class="brand-txt"><b>ΕΥΓΕΙΟΣ</b><small>GOODLAND · ΚΑΤΑΣΚΕΥΕΣ</small></span>
    </a>
    <nav class="nav" aria-label="Κύριο μενού">{nav}</nav>
    <div class="hdr-actions">
      <div class="lang" role="group" aria-label="Γλώσσα / Language">
        <button type="button" data-lang="el" aria-pressed="true">ΕΛ</button>
        <button type="button" data-lang="en" aria-pressed="false">EN</button>
      </div>
      <a class="btn btn-navy btn-sm hdr-call" href="tel:+30{PHONES[0][0]}" aria-label="Κλήση {PHONES[0][1]}">{icon('phone')}<span>{PHONES[0][1]}</span></a>
      <button class="menu-btn" type="button" aria-label="Μενού" aria-expanded="false">{icon('menu', 22)}</button>
    </div>
  </div>
</header>
<main>
{body}
</main>
<footer class="ftr">
  <div class="wrap">
    <div class="ftr-grid">
      <div style="display:flex;flex-direction:column;gap:16px">
        <a class="ftr-brand" href="index.html"><img src="{img(LOGO, 160, 160, 'fit')}" alt="" width="56" height="56"><span style="display:flex;flex-direction:column;line-height:1.15"><b style="font-size:18px;letter-spacing:.14em">ΕΥΓΕΙΟΣ GOODLAND</b><small style="color:#9FB0BC;letter-spacing:.12em">Μ. ΕΠΕ</small></span></a>
        <p style="font-size:15px;line-height:1.6">{t('Κατασκευές κατοικιών, πωλήσεις κατοικιών, ανακαινίσεις κατοικιών.', 'Residential construction, home sales and renovations.')}</p>
      </div>
      <div><h3>{t('Σελίδες', 'Pages')}</h3><ul>{''.join(f'<li><a href="{h}">{t(el, en)}</a></li>' for h, el, en, _ in NAV)}</ul></div>
      <div><h3>{t('Επικοινωνία', 'Contact')}</h3><ul><li>{t(ADDRESS_EL, ADDRESS_EN)}</li>{phones}<li><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
      <div><h3>Social</h3><ul><li><a href="{FACEBOOK}" rel="noopener" target="_blank">Facebook</a></li><li><a href="{INSTAGRAM}" rel="noopener" target="_blank">Instagram</a></li></ul></div>
    </div>
    <div class="ftr-bottom"><span>© 2026 ΕΥΓΕΙΟΣ GOODLAND Μ. ΕΠΕ</span><span>{t('Ύδρας 14, Μοσχάτο · Αθήνα', 'Ydras 14, Moschato · Athens')}</span></div>
  </div>
</footer>
<div class="mbar">
  <a class="btn btn-navy" href="tel:+30{PHONES[0][0]}">{icon('phone')}{t('Κλήση', 'Call')}</a>
  <a class="btn btn-olive" href="contact.html">{icon('mail')}{t('Μήνυμα', 'Message')}</a>
</div>
<script src="assets/site.js"></script>
</body>
</html>
'''


# ---------- data ----------
def load_program(slug):
    d = load(DATA / 'programs' / f'{slug}.json')
    lots = []
    for l in d['lots']:
        if l.get('status') == 'unknown' and not l.get('floor_el'):
            continue  # stray element on the current page, no floor / price / plan
        if not l.get('floor_el') and slug == 'kallirrois-100-koykaki':
            l.update(floor_el='6ος ΟΡΟΦΟΣ', floor_en='6th FLOOR', type_el='ΔΙΑΜΕΡΙΣΜΑ', type_en='APARTMENT')
        lots.append(l)
    d['lots'] = lots
    sections, seen = [], set()
    first = [i for i in d.get('building_images') or [] if i['id'] not in seen]
    gal = d.get('galleries') or []
    for g in gal:
        ims = []
        for i in g['images']:
            if i['id'] not in seen:
                seen.add(i['id'])
                ims.append(i)
        if ims:
            sections.append((g.get('title_el') or 'ΦΩΤΟΓΡΑΦΙΕΣ', g.get('title_en') or 'PHOTOS', ims))
    first = [i for i in first if i['id'] not in seen]
    if first:
        sections.insert(0, ('ΤΟ ΚΤΗΡΙΟ', 'THE BUILDING', first))
    d['sections'] = sections
    d['all_images'] = [i for s in sections for i in s[2]]
    avail = [l for l in lots if l.get('status') == 'available']
    prices = [price_num(l.get('price')) for l in avail if price_num(l.get('price'))]
    m2 = [l['m2'] for l in lots if l.get('m2')]
    d['n_avail'] = len(avail)
    d['price_from'] = min(prices) if prices else None
    d['m2_range'] = (min(m2), max(m2)) if m2 else None
    d['title_el'] = f"{fix(d['street_el'])}, {fix(d['area_el'])}"
    d['href'] = f'{slug}.html'
    return d


def floor_el(s):
    s = fix(s or '')
    s = s.replace('ΟΡΟΦΟΣ', 'όροφος').replace('ΙΣΟΓΕΙΟ', 'Ισόγειο')
    return re.sub(r'\s*-\s*', '–', s)


def floor_en(s):
    s = fix(s or '')
    s = re.sub(r'GROUND ?FLOOR', 'Ground floor', s).replace('FLOOR', 'floor').replace('Tth', 'th')
    s = re.sub(r'(\d)(st|nd|rd|th)', lambda m: m.group(1) + m.group(2).lower(), s, flags=re.I)
    return re.sub(r'\s*-\s*', '–', s)


def type_el(s):
    s = fix(s or '')
    s = re.sub('MEZONET+A', 'ΜΕΖΟΝΕΤΑ', s)
    return TYPE_EL.get(s, s.capitalize())


def type_en(s):
    s = fix(s or '')
    return s[:1].upper() + s[1:].lower()


def short_desc(d):
    return fix((d.get('description_el') or [''])[0]).rstrip('.')


# ---------- pieces ----------
def prog_card(d):
    thumb = d['all_images'][0]['id'] if d['all_images'] else None
    if d['n_avail']:
        badge = f'<span class="badge">{d["n_avail"]} {t("διαθέσιμα" if d["n_avail"] > 1 else "διαθέσιμο", "available")}</span>'
    else:
        badge = f'<span class="badge badge-grey">{t("Μη διαθέσιμο", "Not available")}</span>'
    bits = []
    if d['price_from']:
        bits.append(t(f'από {fmt_price(d["price_from"])}', f'from {fmt_price(d["price_from"])}'))
    if d['m2_range']:
        a, b = d['m2_range']
        bits.append(f'{a}–{b} {t("τ.μ.", "m²")}' if a != b else f'{a} {t("τ.μ.", "m²")}')
    info = ' · '.join(bits) or e(short_desc(d))
    im = f'<img src="{img(thumb, 720, 540)}" alt="" loading="lazy">' if thumb else ''
    return (f'<a class="card" href="{d["href"]}"><div class="card-img">{im}{badge}</div>'
            f'<div class="card-body"><small>{t(d["area_el"], d.get("area_en"))}</small><b>{e(fix(d["street_el"]))}</b>'
            f'<span>{info}</span></div></a>')


def parse_completed(d):
    """Turn the flat text list of a completed-project page into blocks: heading, paragraphs, spec lines."""
    blocks, cur = [], {'title': caps_to_title(d['title_el']), 'paras': [], 'specs': []}
    in_specs = False
    for raw in d.get('text_el') or []:
        s = fix(raw)
        if not s or s == '.':
            continue
        if 'INTERIOR VIEWS' in s or s.startswith('ΕΣΩΤΕΡΙΚΕΣ ΛΗΨΕΙΣ'):
            continue
        if s == 'ΠΛΗΡΟΦΟΡΙΕΣ ΕΡΓΟΥ':
            in_specs = True
            continue
        if re.search(r'\d', s) and ',' in s and not re.search('[a-zά-ώ]', s):
            blocks.append(cur)
            cur = {'title': caps_to_title(s), 'paras': [], 'specs': []}
            in_specs = False
            continue
        if not re.search('[a-zά-ώ]', s):
            if cur['specs'] and in_specs:
                cur['specs'][-1] += ' ' + s
            else:
                cur['specs'].append(s)
            in_specs = True
            continue
        in_specs = False
        cur['paras'].append(s)
    blocks.append(cur)
    return blocks


def completed_card(d):
    thumb = d['images'][0]['id'] if d['images'] else None
    im = f'<img src="{img(thumb, 720, 540)}" alt="" loading="lazy">' if thumb else ''
    spec = d['blocks'][0]['specs'][0] if d['blocks'][0]['specs'] else ''
    return (f'<a class="card" href="{d["slug"]}.html"><div class="card-img">{im}</div>'
            f'<div class="card-body"><small>{t(d["area_el"], d.get("area_en"))}</small><b>{e(d["blocks"][0]["title"])}</b>'
            f'<span class="caps">{e(spec)}</span></div></a>')


def page_head(crumbs, h1, sub=None, chips=''):
    cr = ''.join(f'<a href="{h}">{lbl}</a><span aria-hidden="true">/</span>' for h, lbl in crumbs)
    s = f'<p>{sub}</p>' if sub else ''
    return f'<section class="phead"><div class="wrap"><nav class="crumbs" aria-label="Διαδρομή">{cr}</nav>{chips}<h1>{h1}</h1>{s}</div></section>'


HOME_CRUMB = ('index.html', t('Αρχική', 'Home'))


def info_rows():
    ph = ' · '.join(f'<a href="tel:+30{p}">{d}</a>' for p, d in PHONES)
    return f'''<div class="info">
  <div class="info-row"><span class="ic">{icon('pin', 20)}</span><div><small>{t('ΔΙΕΥΘΥΝΣΗ', 'ADDRESS')}</small><span>{t(ADDRESS_EL, ADDRESS_EN)}</span></div></div>
  <div class="info-row"><span class="ic">{icon('phone', 20)}</span><div><small>{t('ΤΗΛΕΦΩΝΑ', 'PHONE')}</small><span>{ph}</span></div></div>
  <div class="info-row"><span class="ic">{icon('mail', 20)}</span><div><small>EMAIL</small><a href="mailto:{EMAIL}">{EMAIL}</a></div></div>
</div>'''


def map_iframe(q, title):
    return (f'<iframe class="map" title="{e(title)}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
            f'src="https://maps.google.com/maps?q={quote(q)}&amp;z=15&amp;output=embed"></iframe>')


def gallery_buttons(images, group, cls='gal-grid', size=(720, 540), mode='fill'):
    out = []
    for i in images:
        alt = fix(i.get('alt') or '')
        out.append(f'<button type="button" data-lb="{group}" data-full="{full(i["id"])}" data-alt="{e(alt)}" aria-label="Μεγέθυνση εικόνας">'
                   f'<img src="{img(i["id"], size[0], size[1], mode)}" alt="{e(alt)}" loading="lazy"></button>')
    return f'<div class="{cls}">{"".join(out)}</div>'


# ---------- pages ----------
def build_home(programs, completed):
    home = load(DATA / 'pages' / 'home.json')
    tx = [fix(x) for x in home['texts']]
    about_el = [x for x in tx if x.startswith('Η εταιρεία') or x.startswith('Απευθυνθείτε')]
    about_en = [x for x in tx if x.startswith('The "EVGIOS') or x.startswith('Contact our people')]
    feat = next(p for p in programs if p['n_avail'])
    avail_total = sum(p['n_avail'] for p in programs)
    buildings = sum(len(c['blocks']) for c in completed)
    featured = sorted([p for p in programs if p['n_avail']], key=lambda p: -p['n_avail'])[:6]
    services = [
        ('ΜΕΛΕΤΗ & ΚΑΤΑΣΚΕΥΗ ΚΤΗΡΙΩΝ', 'Μελέτη & κατασκευή κτηρίων', 'Analysis, design & construction', '3c238e_f0b299d4ffcd4a7190ca0c3b09ab1e01~mv2.jpg', 'olokliromena-erga.html'),
        ('ΔΙΑΜΟΡΦΩΣΗ ΕΣΩΤΕΡΙΚΩΝ ΧΩΡΩΝ', 'Διαμόρφωση εσωτερικών χώρων', 'Interior design', '3c238e_2904ae49426d4356b3e4021ed4d17aae~mv2.jpg', 'projects.html'),
        ('ΑΝΑΚΑΙΝΙΣΕΙΣ', 'Ανακαινίσεις', 'Renovations', '3c238e_b9bf9a774f0a4bc3871f7e3af02dee1e~mv2.jpg', 'contact.html'),
        ('ΞΥΛΟΥΡΓΙΚΕΣ ΚΑΤΑΣΚΕΥΕΣ', 'Ξυλουργικές κατασκευές', 'Wooden constructions', '3c238e_d6984b209df94ad68e192c144bb5b339~mv2.jpg', 'kouzines.html'),
    ]
    svc_html = ''.join(
        f'<a class="svc" href="{h}"><img src="{img(i, 600, 600)}" alt="" loading="lazy"><b>{t(el, en)}</b></a>'
        for _, el, en, i, h in services)
    katalogos = [('Κατασκευές νέων έργων', 'Construction of new buildings'), ('Λύσεις για ενεργειακή αναβάθμιση', 'Solutions for energy upgrade'),
                 ('Ανακαινίσεις', 'Renovations'), ('Επισκευές', 'Repairs')]
    checks = ''.join(f'<li>{icon("check", 22, "#3E4A16")}<span>{t(el, en)}</span></li>' for el, en in katalogos)
    tiles = ''.join(
        f'<a class="tile" href="{c["slug"]}.html"><img src="{img(c["images"][0]["id"], 640, 480)}" alt="" loading="lazy"><span>{t(c["area_el"], c.get("area_en"))}</span></a>'
        for c in completed if c['images'])
    interior_tiles = ''.join(
        f'<a class="tile" href="{s}.html"><img src="{img(i, 640, 480)}" alt="" loading="lazy"><span>{t(el, en)}</span></a>' for s, el, en, i in INTERIOR)
    hero_img = '3c238e_b82cff7520054f2b9f38b078fe271ceb~mv2.jpg'
    body = f'''
<section class="hero"><div class="wrap hero-grid">
  <div class="hero-copy">
    <span class="chip chip-olive">{icon('bolt', 16)}{t('25+ χρόνια εμπειρίας · Ενεργειακή κλάση Α', '25+ years of experience · Energy class A')}</span>
    <h1>{t('Αναζητάτε ένα νέο ενεργειακό σπίτι;', 'Are you looking for a new energy-apartment?')}</h1>
    <p class="lead">{t(about_el[1], about_en[1])}</p>
    <div class="ctas">
      <a class="btn btn-olive" href="pros-polisi.html">{t('Ακίνητα προς πώληση', 'Properties for sale')}{icon('arrow')}</a>
      <a class="btn btn-line" href="contact.html">{t('Επικοινωνία', 'Contact us')}</a>
    </div>
  </div>
  <div class="hero-media">
    <img src="{img(hero_img, 1200, 1200)}" alt="Πολυκατοικία Εύγειος στου Παπάγου" fetchpriority="high">
    <a class="float-card" href="{feat['href']}">
      <small>{t(feat['area_el'], feat.get('area_en'))} · {t('Νέο έργο', 'New project')}</small>
      <b>{e(fix(feat['street_el']))}</b>
      <span>{feat['n_avail']} {t('διαθέσιμα', 'available')}{(' · ' + t('από ' + fmt_price(feat['price_from']), 'from ' + fmt_price(feat['price_from']))) if feat['price_from'] else ''}</span>
    </a>
  </div>
</div></section>

<section><div class="wrap"><div class="stats">
  <div class="stat"><b>25+</b><span>{t('χρόνια στις κατασκευές', 'years in construction')}</span></div>
  <div class="stat"><b>{len(programs)}</b><span>{t('έργα προς πώληση', 'projects for sale')}</span></div>
  <div class="stat"><b>{avail_total}</b><span>{t('διαθέσιμα ακίνητα', 'homes available')}</span></div>
  <div class="stat"><b>{buildings}</b><span>{t('ολοκληρωμένα κτήρια', 'completed buildings')}</span></div>
</div></div></section>

<section class="sec"><div class="wrap two">
  <div class="prose">
    <span class="kicker">{t('Η εταιρεία', 'The company')}</span>
    <h2>{t('Η εταιρεία «Εύγειος»', 'The “Evgios Goodland” company')}</h2>
    <p>{t(about_el[0], about_en[0])}</p>
  </div>
  <img src="{img('3c238e_99edb9a26c8345b18ddbe6e03d89c01c~mv2.jpg', 900, 700)}" alt="" loading="lazy" style="width:100%;border-radius:24px;aspect-ratio:9/7;object-fit:cover;background:#F2F5F1">
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><div><span class="kicker">{t('Προς πώληση', 'For sale')}</span><h2>{t('Διαθέσιμα ακίνητα', 'Available properties')}</h2></div>
  <a class="more" href="pros-polisi.html">{t(f'Όλα τα {len(programs)} έργα →', f'All {len(programs)} projects →')}</a></div>
  <div class="grid">{''.join(prog_card(p) for p in featured)}</div>
</div></section>

<section id="services" class="sec" style="padding-top:0"><div class="wrap">
  <div class="panel"><div class="two" style="align-items:start">
    <div style="display:flex;flex-direction:column;gap:16px"><span class="kicker">{t('Υπηρεσίες', 'Services')}</span>
    <h2>{t('Από το οικόπεδο μέχρι τους εσωτερικούς χώρους', 'From the plot to the interior')}</h2></div>
    <ul class="checks">{checks}</ul>
  </div>
  <div class="grid grid-4" style="margin-top:40px">{svc_html}</div></div>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap"><div class="panel-navy"><div class="two">
  <div style="display:flex;flex-direction:column;gap:14px"><span class="kicker">{t('Για ιδιοκτήτες', 'For owners')}</span>
    <h2 style="font-size:clamp(28px,3.4vw,40px)">{t('Είστε ιδιοκτήτης ακινήτου ή οικοπέδου;', 'Are you a land owner?')}</h2>
    <p style="font-size:20px;color:#D5DEE5">{t('Μπορούμε να συνεργαστούμε.', 'We can cooperate.')}</p></div>
  <div class="ctas"><a class="btn btn-white" href="contact.html">{t('Επικοινωνήστε μαζί μας', 'Get in touch')}</a>
    <a class="btn btn-ghost-w" href="tel:+30{PHONES[2][0]}">{icon('phone')}{PHONES[2][1]}</a></div>
</div></div></div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><div><span class="kicker">{t('Ολοκληρωμένα έργα', 'Completed projects')}</span><h2>{t('Έργα που έχουμε παραδώσει', 'Projects we have delivered')}</h2></div>
  <a class="more" href="olokliromena-erga.html">{t('Όλα τα έργα →', 'All projects →')}</a></div>
  <div class="grid grid-4">{tiles}</div>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><div><span class="kicker">{t('Εσωτερικοί χώροι', 'Interior design')}</span><h2>{t('Διαμόρφωση εσωτερικών χώρων', 'Interior design')}</h2>
  <p style="margin-top:12px;font-size:17px;color:#3B4A54;max-width:640px">{t('Η εταιρεία «Εύγειος» είναι σε θέση να προτείνει λύσεις εσωτερικών διαρρυθμίσεων, σύμφωνα με τις δικές σας ανάγκες.', 'We are able to propose and design the appropriate configuration of interior spaces, always according to the needs of our client.')}</p></div>
  <a class="more" href="projects.html">{t('Δείτε περισσότερα →', 'See more →')}</a></div>
  <div class="grid grid-4">{interior_tiles}</div>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap two" style="align-items:stretch">
  <div style="display:flex;flex-direction:column;gap:24px;justify-content:center"><span class="kicker" style="margin:0">{t('Επικοινωνία', 'Contact')}</span>
    <h2>{t('Ελάτε στο γραφείο μας', 'Visit our office')}</h2>{info_rows()}
    <div class="ctas"><a class="btn btn-olive" href="contact.html">{t('Στείλτε μήνυμα', 'Send a message')}</a></div></div>
  {map_iframe('Ύδρας 14, Μοσχάτο 183 45', 'Χάρτης γραφείου')}
</div></section>
'''
    return layout('Κατασκευαστική Εταιρία | Εύγειος Goodland ΕΠΕ', body, None, home.get('meta_description'))


def build_sale_list(programs):
    head = page_head([HOME_CRUMB], t('Ακίνητα προς πώληση', 'Properties for sale'),
                     t('Απευθυνθείτε στο γραφείο μας για να βρείτε το ακίνητο που ταιριάζει απόλυτα στα μέτρα σας, νεόδμητο ή παλαιότητος, σε τιμές χαμηλότερες από της αγοράς.',
                       'Contact our people to find the property that perfectly suits your needs, newly built or old, at lower than market prices.'))
    body = head + f'<section class="sec" style="padding-top:12px"><div class="wrap"><div class="grid">{"".join(prog_card(p) for p in programs)}</div></div></section>'
    return layout('Ακίνητα προς πώληση | Εύγειος Goodland ΕΠΕ', body, 'sale')


def build_program(d):
    imgs = d['all_images']
    desc_el, desc_en = d.get('description_el') or [], d.get('description_en') or []
    chips = []
    for b in desc_el:
        b = fix(b)
        if b.startswith('Ενεργειακή κλάση'):
            en = next((fix(x) for x in desc_en if x.lower().startswith('energy class')), None)
            chips.append(f'<span class="chip chip-olive">{icon("bolt", 15)}{t(b.rstrip("."), en.rstrip(".") if en else None)}</span>')
        if 'υπό κατασκευή' in b:
            chips.append(f'<span class="chip chip-blue">{t("Υπό κατασκευή", "Under construction")}</span>')
    chips.append(f'<span class="chip chip-grey">{d["n_avail"]} {t("διαθέσιμα", "available")}</span>' if d['n_avail']
                 else f'<span class="chip chip-grey">{t("Μη διαθέσιμο", "Not available")}</span>')
    head = page_head([HOME_CRUMB, ('pros-polisi.html', t('Ακίνητα προς πώληση', 'Properties for sale'))],
                     e(d['title_el']), None, f'<div class="chips">{"".join(chips)}</div>')

    main = ''
    if imgs:
        thumbs = ''.join(
            f'<button type="button" data-i="{n}" data-src="{img(i["id"], 1400, 900)}" aria-current="{"true" if n == 0 else "false"}" aria-label="Εικόνα {n + 1}">'
            f'<img src="{img(i["id"], 240, 180)}" alt="" loading="lazy"></button>' for n, i in enumerate(imgs[:6]))
        main = (f'<button type="button" class="gal-main" data-start="0" aria-label="Άνοιγμα γκαλερί">'
                f'<img src="{img(imgs[0]["id"], 1400, 900)}" alt="{e(d["title_el"])}" fetchpriority="high">'
                f'<span class="gal-count">{icon("expand", 16)} {len(imgs)} {t("εικόνες", "images")}</span></button>'
                f'<div class="thumbs">{thumbs}</div>')

    def kpi(v, lbl_el, lbl_en, cls=''):
        return f'<div><b class="{cls}">{v}</b><span>{t(lbl_el, lbl_en)}</span></div>'
    m2 = d['m2_range']
    kpis = (kpi(len(d['lots']), 'κατοικίες', 'homes') + kpi(d['n_avail'], 'διαθέσιμες', 'available', 'ok') +
            kpi(f'{m2[0]}–{m2[1]}' if m2 and m2[0] != m2[1] else (m2[0] if m2 else '—'), 'τ.μ.', 'm²') +
            kpi(fmt_price(d['price_from']) if d['price_from'] else '—', 'τιμή από', 'price from'))
    desc_items = ''.join(
        f'<li>{icon("check", 20, "#3E4A16")}<span>{t(el, desc_en[k] if k < len(desc_en) else None)}</span></li>'
        for k, el in enumerate(desc_el))
    aside = f'''<aside class="aside">
  <div class="kpis">{kpis}</div>
  <ul class="checks">{desc_items}</ul>
  <a class="btn btn-olive" href="#interest">{t('Ενδιαφέρομαι', "I'm interested")}</a>
  <div class="row2"><a class="btn btn-line btn-sm" href="tel:+30{PHONES[2][0]}">{icon('phone')}{t('Κλήση', 'Call')}</a><a class="btn btn-line btn-sm" href="#lots">{t('Κατόψεις', 'Floor plans')}</a></div>
</aside>'''

    rows = []
    for n, l in enumerate(d['lots']):
        ok = l.get('status') == 'available'
        p = price_num(l.get('price'))
        price = fmt_price(p) if (ok and p) else (t('Κατόπιν επικοινωνίας', 'On request') if ok else '—')
        st = (f'<span class="st st-ok">{t("Διαθέσιμο", "Available")}</span>' if ok else f'<span class="st st-na">{t("Μη διαθέσιμο", "Not available")}</span>')
        fl = t(floor_el(l.get('floor_el')), floor_en(l.get('floor_en')))
        ty = t(type_el(l.get('type_el')), type_en(l.get('type_en')))
        label = f"{d['title_el']} – {floor_el(l.get('floor_el'))}, {type_el(l.get('type_el'))} {l.get('m2')} τ.μ." + (f' – {fmt_price(p)}' if p else '')
        txt = t(l.get('text_el'), l.get('text_en')) if l.get('text_el') or l.get('text_en') else ''
        txt = f'<p>{txt}</p>' if txt else ''
        plans = gallery_buttons(l.get('images') or [], f'lot{n}', 'plans', (420, 315), 'fit') if l.get('images') else ''
        acts = (f'<div class="lot-actions"><a class="btn btn-olive btn-sm" href="#interest" data-interest="{e(label)}">{t("Ενδιαφέρομαι για αυτό", "I am interested")}</a>'
                f'<a class="btn btn-line btn-sm" href="tel:+30{PHONES[2][0]}">{icon("phone")}{t("Κλήση", "Call")}</a></div>') if ok else ''
        rows.append(f'''<details class="lot {'ok' if ok else 'na'}"><summary>
  <div><span class="lab">{t('Όροφος', 'Floor')}</span>{fl}</div>
  <div class="type"><span class="lab">{t('Τύπος', 'Type')}</span>{ty}</div>
  <div><span class="lab">{t('Εμβαδόν', 'Area')}</span>{l.get('m2') or '—'} {t('τ.μ.', 'm²')}</div>
  <div><span class="lab">{t('Υπνοδωμάτια', 'Bedrooms')}</span>{l.get('bedrooms') or '—'}</div>
  <div><span class="lab">{t('Μπάνια', 'Bathrooms')}</span>{e(str(l.get('bathrooms') or '—'))}</div>
  <div class="price"><span class="lab">{t('Τιμή', 'Price')}</span>{price}</div>
  <div>{st}</div>
  {icon('chev', 20, 'currentColor', 'chev')}
</summary><div class="lot-body"><div>{txt}{acts}</div>{plans}</div></details>''')
    lots_html = f'''<section id="lots" class="sec" style="padding-bottom:40px"><div class="wrap">
  <div class="sec-head"><div><span class="kicker">{t('Κατοικίες', 'Homes')}</span><h2>{t('Διαθέσιμα ακίνητα προς πώληση', 'Available apartments for sale')}</h2>
  <p style="margin-top:10px;color:#4A5A64">{t('Πατήστε σε μια κατοικία για περιγραφή και κάτοψη.', 'Tap a home to see its description and floor plan.')}</p></div>
  <div class="filters" role="group" aria-label="Φίλτρο"><button type="button" data-f="all" aria-pressed="true">{t('Όλες', 'All')} ({len(d['lots'])})</button><button type="button" data-f="ok" aria-pressed="false">{t('Διαθέσιμες', 'Available')} ({d['n_avail']})</button></div></div>
  <div class="lots"><div class="lot-h"><span>{t('Όροφος', 'Floor')}</span><span>{t('Τύπος', 'Type')}</span><span>{t('Εμβαδόν', 'Area')}</span><span>{t('Υπνοδ.', 'Beds')}</span><span>{t('Μπάνια', 'Baths')}</span><span>{t('Τιμή', 'Price')}</span><span>{t('Κατάσταση', 'Status')}</span><span></span></div>
  {''.join(rows)}</div>
</div></section>'''

    gal_html = ''
    for tel, ten, ims in d['sections']:
        tel = fix(tel).rstrip(':')
        tel, ten = SECTION_TITLES.get(tel, (tel, fix(ten) if ten else None))
        gal_html += (f'<div style="margin-bottom:44px"><h3 class="subhead" style="margin-bottom:18px">{t(tel, ten)}</h3>'
                     f'{gallery_buttons(ims, "prog")}</div>')
    gal_html = f'<section class="sec" style="padding-top:40px;padding-bottom:20px"><div class="wrap">{gal_html}</div></section>' if gal_html else ''

    street_q = fix(d['street_el']).split('&')[0].strip() + ', ' + fix(d['area_el']) + ', Αττική'
    form = f'''<section id="interest" class="sec" style="padding-top:40px"><div class="wrap two" style="align-items:stretch">
  {map_iframe(street_q, 'Χάρτης ' + d['title_el'])}
  <form class="form" data-mail="{EMAIL}">
    <h2>{t('Ενδιαφέρομαι', "I'm interested")}</h2>
    <div id="sel-lot" class="sel-lot" style="display:none"></div>
    <input type="hidden" name="subject" value="{e('Ενδιαφέρον: ' + d['title_el'])}">
    <input type="hidden" id="f-lot" name="Ακίνητο" value="{e(d['title_el'])}">
    <div class="fgrid"><label>{t('Όνομα', 'Name')}<input name="Όνομα" autocomplete="name" required></label>
    <label>{t('Τηλέφωνο', 'Phone')}<input name="Τηλέφωνο" type="tel" autocomplete="tel"></label></div>
    <label>Email<input name="Email" type="email" autocomplete="email"></label>
    <label>{t('Μήνυμα', 'Message')}<textarea name="Μήνυμα"></textarea></label>
    <button class="btn btn-olive" type="submit">{t('Αποστολή', 'Send')}</button>
    <span class="note">{t('Ή καλέστε μας', 'Or call us')}: <a href="tel:+30{PHONES[0][0]}">{PHONES[0][1]}</a> · <a href="tel:+30{PHONES[2][0]}">{PHONES[2][1]}</a></span>
  </form>
</div></section>'''
    body = head + f'<section><div class="wrap prog-top"><div class="gal">{main}</div>{aside}</div></section>' + lots_html + gal_html + form
    return layout(fix(d.get('page_title') or d['title_el']), body, 'sale')


def build_completed_list(completed):
    head = page_head([HOME_CRUMB], t('Ολοκληρωμένα έργα', 'Completed projects'),
                     t('Κτήρια κατοικιών που έχουμε μελετήσει, κατασκευάσει και παραδώσει σε όλη την Αθήνα.', 'Residential buildings we have designed, built and delivered across Athens.'))
    body = head + f'<section class="sec" style="padding-top:12px"><div class="wrap"><div class="grid">{"".join(completed_card(c) for c in completed)}</div></div></section>'
    return layout('Ολοκληρωμένα Έργα | Εύγειος Goodland ΕΠΕ', body, 'done')


def build_completed(c):
    head = page_head([HOME_CRUMB, ('olokliromena-erga.html', t('Ολοκληρωμένα έργα', 'Completed projects'))], e(c['blocks'][0]['title']))
    info = ''
    for k, b in enumerate(c['blocks']):
        h = f'<h2 class="subhead">{e(b["title"])}</h2>' if k else ''
        paras = ''.join(f'<p>{e(p)}</p>' for p in b['paras'])
        specs = ''.join(f'<span>{e(s)}</span>' for s in b['specs'])
        specs = f'<div class="specs"><small>{t("ΠΛΗΡΟΦΟΡΙΕΣ ΕΡΓΟΥ", "PROJECT INFO")}</small>{specs}</div>' if specs else ''
        info += f'<div class="prose" style="margin-bottom:28px">{h}{paras}{specs}</div>'
    cover = c['images'][0]['id'] if c['images'] else None
    top = f'''<section><div class="wrap two" style="align-items:start">
  <div>{info}<a class="btn btn-olive" href="contact.html" style="margin-top:4px">{t('Θέλω κάτι παρόμοιο', 'I want something similar')}</a></div>
  {f'<button type="button" class="gal-main" data-lb="cover" data-full="{full(cover)}" aria-label="Μεγέθυνση"><img src="{img(cover, 1200, 900)}" alt="{e(c["blocks"][0]["title"])}"></button>' if cover else ''}
</div></section>'''
    rest = c['images'][1:]
    gal = (f'<section class="sec"><div class="wrap"><h2 style="margin-bottom:24px">{t("Φωτογραφίες", "Photos")} <span style="color:#4A5A64;font-weight:500">({len(c["images"])})</span></h2>'
           f'{gallery_buttons(rest, "done", "masonry", (900, 900), "fit")}</div></section>') if rest else '<div style="height:60px"></div>'
    return layout(fix(c.get('page_title') or c['blocks'][0]['title']), head + top + gal, 'done')


def build_interior_list():
    head = page_head([HOME_CRUMB], t('Διαμόρφωση εσωτερικών χώρων', 'Interior design'),
                     t('Η εταιρεία «Εύγειος» είναι σε θέση να προτείνει λύσεις εσωτερικών διαρρυθμίσεων, σύμφωνα με τις δικές σας ανάγκες.',
                       'We are able to propose and design the appropriate configuration of interior spaces, always according to the needs of our client.'))
    cards = ''
    for s, el, en, i in INTERIOR:
        n = len(load(DATA / 'interior' / f'{s}.json')['images'])
        cards += (f'<a class="card" href="{s}.html"><div class="card-img"><img src="{img(i, 720, 540)}" alt="" loading="lazy"></div>'
                  f'<div class="card-body"><b>{t(el, en)}</b><span>{n} {t("φωτογραφίες", "photos")}</span></div></a>')
    body = head + f'<section class="sec" style="padding-top:12px"><div class="wrap"><div class="grid grid-4">{cards}</div></div></section>'
    return layout('Εσωτερικοί χώροι | Εύγειος Goodland ΕΠΕ', body, 'interior')


def build_interior(slug, el, en):
    d = load(DATA / 'interior' / f'{slug}.json')
    ims = [i for i in d['images'] if not i.get('stock')]
    head = page_head([HOME_CRUMB, ('projects.html', t('Εσωτερικοί χώροι', 'Interior design'))], t(el, en),
                     f'{len(ims)} {t("φωτογραφίες από έργα μας", "photos from our projects")}')
    others = ''.join(f'<a class="btn btn-line btn-sm" href="{s}.html">{t(a, b)}</a>' for s, a, b, _ in INTERIOR if s != slug)
    body = head + (f'<section style="padding-bottom:80px"><div class="wrap">{gallery_buttons(ims, "int", "masonry", (900, 900), "fit")}'
                   f'<div class="ctas" style="margin-top:40px">{others}<a class="btn btn-olive btn-sm" href="contact.html">{t("Ζητήστε πρόταση", "Ask for a proposal")}</a></div></div></section>')
    return layout(f'{el} | Εύγειος Goodland ΕΠΕ', body, 'interior')


def build_contact():
    head = page_head([HOME_CRUMB], t('Επικοινωνία', 'Contact'),
                     t('Απευθυνθείτε στο γραφείο μας για να βρείτε το ακίνητο που ταιριάζει απόλυτα στα μέτρα σας.', 'Contact our people to find the property that perfectly suits your needs.'))
    form = f'''<form class="form" data-mail="{EMAIL}">
  <h2>{t('Στείλτε μας μήνυμα', 'Send us a message')}</h2>
  <input type="hidden" name="subject" value="Μήνυμα από το site">
  <div class="fgrid"><label>{t('Όνομα', 'First name')}<input name="Όνομα" autocomplete="given-name" required></label>
  <label>{t('Επώνυμο', 'Last name')}<input name="Επώνυμο" autocomplete="family-name"></label></div>
  <div class="fgrid"><label>Email<input name="Email" type="email" autocomplete="email"></label>
  <label>{t('Τηλέφωνο', 'Phone')}<input name="Τηλέφωνο" type="tel" autocomplete="tel"></label></div>
  <label>{t('Ενδιαφέρομαι για', "I'm interested in")}<select name="Θέμα">
    <option>Αγορά κατοικίας</option><option>Συνεργασία ως ιδιοκτήτης οικοπέδου / ακινήτου</option>
    <option>Ανακαίνιση / ενεργειακή αναβάθμιση</option><option>Εσωτερικοί χώροι / ξυλουργικές κατασκευές</option><option>Άλλο</option></select></label>
  <label>{t('Μήνυμα', 'Message')}<textarea name="Μήνυμα" required></textarea></label>
  <button class="btn btn-olive" type="submit">{t('Αποστολή', 'Send')}</button>
</form>'''
    body = head + f'''<section class="sec" style="padding-top:12px"><div class="wrap two" style="align-items:start">
  <div style="display:flex;flex-direction:column;gap:28px">{info_rows()}
    <div class="ctas"><a class="btn btn-line btn-sm" href="{FACEBOOK}" target="_blank" rel="noopener">Facebook</a><a class="btn btn-line btn-sm" href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a></div>
    <div style="height:360px">{map_iframe('Ύδρας 14, Μοσχάτο 183 45', 'Χάρτης γραφείου')}</div></div>
  {form}
</div></section>'''
    return layout('Επικοινωνία | Εύγειος Goodland ΕΠΕ', body, 'contact')


def redirect(to):
    return f'<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={to}"><link rel="canonical" href="{to}"><a href="{to}">{to}</a>\n'


def main():
    programs = [load_program(s) for s in PROGRAM_ORDER]
    completed = []
    for s in COMPLETED_ORDER:
        c = load(DATA / 'completed' / f'{s}.json')
        c['blocks'] = parse_completed(c)
        completed.append(c)
    pages = {
        'index.html': build_home(programs, completed),
        'pros-polisi.html': build_sale_list(programs),
        'olokliromena-erga.html': build_completed_list(completed),
        'projects.html': build_interior_list(),
        'contact.html': build_contact(),
        'katalogos.html': redirect('index.html#services'),
    }
    for p in programs:
        pages[p['href']] = build_program(p)
    for c in completed:
        pages[f'{c["slug"]}.html'] = build_completed(c)
    for s, el, en, _ in INTERIOR:
        pages[f'{s}.html'] = build_interior(s, el, en)
    for name, content in pages.items():
        (ROOT / name).write_text(content, encoding='utf-8')
    print(f'{len(pages)} pages written')


if __name__ == '__main__':
    main()
