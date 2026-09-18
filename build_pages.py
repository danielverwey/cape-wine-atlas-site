#!/usr/bin/env python3
"""
build_pages.py — build the Cape Wine Atlas site from the atlas record.

    python3 build_pages.py <atlas-project-folder> [--root /] [--domain capewineatlas.co.za]
                                                  [--out docs] [--allow-preview]

Reads <project>/dist/atlas.json and <project>/data/regions/*.json, applies the
publication gate, and writes a static site to <out>/ (GitHub Pages serves it):

    <out>/index.html                   the atlas
    <out>/region/<key>/index.html      one pre-rendered page per region, with a real URL
    <out>/producer/<id>/index.html     one pre-rendered page per producer (the third level)
    <out>/data/index.json              region index, statistics, map geometry, lens figures
    <out>/data/search.json             the search index (producers, regions, wards, grapes, wines)
    <out>/data/regions/<key>.json      one file per region, fetched when opened
    <out>/assets/…                     stylesheet, script, typefaces, textures
    <out>/sitemap.xml  robots.txt  CNAME  404.html  .nojekyll

It also writes a single self-contained HTML file (everything inlined) next to
<out>/ for the archival copy in versions/. Standard library only.

THE GATE refuses a build if any published record carries a contact key, if any
published record has a field whose provenance names a licence-restricted source
(the atlas's own export_producers.py test), or if buildMode is not "public".
"""
import base64, datetime, html, json, os, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / 'src'

# ---------------------------------------------------------------- arguments
# accepts both `--out docs` and `--out=docs`; `--allow-preview` is a bare flag
args, opts, VALUED = [], {}, ('--root', '--domain', '--out')
_argv = sys.argv[1:]
i = 0
while i < len(_argv):
    a = _argv[i]
    if a.startswith('--'):
        if '=' in a:
            k, v = a.split('=', 1); opts[k] = v
        elif a in VALUED and i + 1 < len(_argv) and not _argv[i + 1].startswith('--'):
            opts[a] = _argv[i + 1]; i += 1
        else:
            opts[a] = True
    else:
        args.append(a)
    i += 1
if not args:
    sys.exit(__doc__)
PROJECT = Path(args[0]).resolve()
ROOT = str(opts.get('--root', '/'))
if not ROOT.endswith('/'): ROOT += '/'
DOMAIN = str(opts.get('--domain', 'capewineatlas.co.za'))
OUT = HERE / str(opts.get('--out', 'docs'))
ALLOW_PREVIEW = '--allow-preview' in opts
BASE_URL = f'https://{DOMAIN}{ROOT}'

atlas = json.loads((PROJECT / 'dist' / 'atlas.json').read_text(encoding='utf-8'))

# ---------------------------------------------------------------- the gate
RESTRICTED = ("google_places", "LICENCE RESTRICTED")
DROP = {"phone", "email", "tel", "telephone", "mobile", "cell", "whatsapp", "fax"}
def walk_keys(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k; yield from walk_keys(v)
    elif isinstance(o, list):
        for v in o: yield from walk_keys(v)
published = {f['id'] for r in atlas['regions'] for f in r['farms']}
contact_keys = sorted({k for k in walk_keys(atlas['regions']) if k.lower() in DROP})
prov_by_id = {}
region_files = {}
for fn in sorted(os.listdir(PROJECT / 'data' / 'regions')):
    doc = json.loads((PROJECT / 'data' / 'regions' / fn).read_text(encoding='utf-8'))
    region_files[fn[:-5]] = doc
    for f in doc.get('farms', []):
        prov_by_id[f['id']] = f.get('provenance') or {}
restricted = []
for fid in sorted(published):
    bad = [k for k, v in prov_by_id.get(fid, {}).items() if any(t in str(v) for t in RESTRICTED)]
    if bad: restricted.append((fid, bad))
mode = atlas.get('buildMode')
print(f"gate: {len(published)} published records checked · contact keys found: {len(contact_keys)} · "
      f"restricted-provenance records: {len(restricted)} · buildMode: {mode}")
problems = []
if contact_keys: problems.append(f"contact keys present in the build: {contact_keys}")
if restricted: problems.append("licence-restricted provenance on published records: " + ", ".join(f"{i} ({', '.join(b)})" for i, b in restricted[:12]))
if mode not in ("public", "production"):
    msg = f"buildMode is '{mode}', not 'public' — a preview build is for development only"
    if ALLOW_PREVIEW: print("WARNING:", msg, "(overridden with --allow-preview)")
    else: problems.append(msg + " (pass --allow-preview to override while testing)")
if problems:
    sys.exit("REFUSED — the build does not pass the gate:\n  - " + "\n  - ".join(problems))
print("gate: passed")

# ---------------------------------------------------------------- extraction (the same shaping the prototype used)
SHORT = {
 'Cape South Coast remainder — Overberg, Swellendam & Napier': ('Overberg & Swellendam', 20.25, -34.22),
 'Cape Town — Hout Bay, Philadelphia & the city': ('Cape Town', 18.42, -33.92),
 'Olifants River — Lutzville Valley, Citrusdal Valley remainder & stand-alone wards': ('Olifants River', 18.35, -31.55),
 'Klein Karoo — the remainder beyond Calitzdorp': ('Klein Karoo', 20.35, -33.75),
 'Citrusdal Mountain / Piekenierskloof': ('Citrusdal Mountain', 18.86, -32.39),
 'Stanford & the Walker Bay remainder': ('Stanford & Walker Bay', 19.45, -34.41),
 'Elim & Cape Agulhas': ('Elim & Cape Agulhas', 19.70, -34.61),
 'Ceres Plateau': ('Ceres Plateau', 19.31, -33.37),
 'Prince Albert': ('Prince Albert', 22.03, -33.22),
 "Lambert's Bay": ("Lambert's Bay", 18.31, -32.09),
}
SLUG = {(d['region'].get('name') or d['region'].get('wo_district')): k for k, d in region_files.items()}
# Publication copy: every free-text field the atlas carries is a working note, so the page runs it through
# copytext.history(), which keeps the facts and drops the method (see copytext.py).
from copytext import history as _copy, lowercase_vocabulary
VOCAB = lowercase_vocabulary(
    [f.get('note') for r in atlas['regions'] for f in r['farms']] + [f.get('family') for r in atlas['regions'] for f in r['farms']]
    + [r['meta'].get('terroir') for r in atlas['regions']] + [rt.get('blurb') for rt in atlas['routes']])
def copy(t, budget): return _copy(t, VOCAB, budget)
def intornull(v): return v if isinstance(v, int) else None

routes_by = {}
for r in atlas['routes']:
    if r.get('regionKey'): routes_by.setdefault(r['regionKey'], []).append(r)
route_region = {r['id']: r.get('regionKey') for r in atlas['routes']}
def tour_regions(t):
    ks = set()
    for k in t['routesServed']:
        if k in SLUG.values(): ks.add(k)
        elif route_region.get(k): ks.add(route_region[k])
        elif k == 'walker-bay': ks.update(['hemel-en-aarde', 'stanford-walker-bay'])
    return ks

regions, idx = {}, []
skipped = []
for r in atlas['regions']:
    m = r['meta']; name = m.get('name') or m.get('wo_district')
    # The atlas may carry a holding area that is not a place on the chart (producers with no vineyard of
    # their own, say). With nothing published in it there is nothing to draw, so it is noted and passed over
    # — but if it ever holds a published record the build stops rather than dropping that record silently.
    if name not in SLUG:
        if r['farms']: sys.exit(f"REFUSED — '{name}' holds {len(r['farms'])} published records but has no region file to place them in")
        skipped.append(name); continue
    # A holding area placed at the geographical unit and nothing narrower — the atlas's "No fixed place"
    # shelf, whose producers it can name, source and reach but cannot place closer than the Western Cape.
    # It is listed and its records have pages, but it has no position on the chart and is never drawn there.
    nochart = bool(m.get('geographicalUnit')) and not (m.get('wo_region') or m.get('wo_district') or m.get('wo_ward'))
    if not r['farms'] and name not in SHORT:
        # Nothing published in it and no fixed position on the chart: there is nowhere to draw it, so it is
        # noted and passed over. A real place with everything withheld — Lambert's Bay — keeps its position.
        skipped.append(name); continue
    key = SLUG[name]
    fs = [f for f in r['farms'] if f['lat'] is not None]
    if nochart: short, lng, lat = name, None, None
    elif name in SHORT: short, lng, lat = SHORT[name]
    else: short = name; lat = sum(f['lat'] for f in fs)/len(fs); lng = sum(f['lng'] for f in fs)/len(fs)
    if fs and name in SHORT and name != "Lambert's Bay":
        lat = sum(f['lat'] for f in fs)/len(fs); lng = sum(f['lng'] for f in fs)/len(fs)
    if short == 'Constantia': lng, lat = 18.42, -34.04
    farms = []
    for f in r['farms']:
        rec = {k: f.get(k) for k in ('id','name','ward','lat','lng','geoConfidence','founded','hours','venue','access','varieties','signatureWines','web','routeMember','oldVineFlag','awardsCollected','pendingClaims','locality','contactHeld','coordsClean')}
        rec['awards'] = [{k: aw.get(k) for k in ('body','year','wine','award','sourceUrl','sourceName')} | {'corr': bool(aw.get('_corroborated'))} for aw in f['awards']]
        # the producer's own range, as printed on its own pages: names and range labels, the producer's own
        # account of a name where it gives one, and where and when the atlas read it. The working note behind
        # the reading stays in the atlas.
        ws = f.get('winesSource') or {}
        rec['wines'] = [{'name': w['name'], 'kind': w.get('kind') or 'wine'} for w in (f.get('wines') or []) if isinstance(w, dict) and w.get('name')]
        rec['wineNotes'] = [{'wine': n['wine'], 'note': n['note']} for n in (f.get('wineNotes') or []) if isinstance(n, dict) and n.get('wine') and n.get('note')]
        rec['winesRead'] = ws.get('read'); rec['winesUrls'] = [u for u in (ws.get('urls') or []) if isinstance(u, str)]
        rec['winesAbsent'] = not rec['wines'] and not rec['winesUrls'] and bool(f.get('winesCollected'))   # nothing readable on the producer's own domain
        rec['winesCollected'] = bool(f.get('winesCollected'))
        rec['history'] = copy(f.get('note'), 230)
        rec['people'] = copy(f.get('family'), 150)
        rec['hours'] = _copy(rec['hours'], VOCAB, 190, mode='hours') if rec['hours'] else rec['hours']
        farms.append(rec)
    rts = []
    for rt in routes_by.get(key, []):
        b = copy(rt.get('blurb'), 300)
        rts.append({k: rt.get(k) for k in ('id','name','area','status','web','sourceUrl','retrieved')} | {'blurb': b if len(b) >= 60 else '', 'membersRecorded': intornull(rt.get('membersRecorded')), 'membersExpected': intornull(rt.get('membersExpected'))})
    tours = [{k: t.get(k) for k in ('name','type','base','web','verified')} for t in atlas['tourOperators'] if key in tour_regions(t)]
    district = (m.get('wo_district') or '').split(' (')[0].strip() or None
    ward = (m.get('wo_ward') or '').split(' (')[0].split(' | ')[0].strip() or None
    withheld = atlas.get('withheld', {}).get('byRegion', {}).get(name, 0)
    terroir = copy(m.get('terroir'), 380)
    # the atlas may publish an introduction of its own for a region (ADR-119); where it does, that is the
    # lede as written. Where it only has a terroir note, the note goes through the copy pass as before.
    intro = ' '.join((r.get('intro') or '').split()) if r.get('introFrom') == 'intro' else ''
    n_f = len(r['farms']); where = f"the {district or short} district of the {m.get('wo_region') or 'Cape'}"
    fallback = (f"No producer is yet on record in {where}." if n_f == 0 else f"One producer on record in {where}." if n_f == 1 else f"{n_f} producers on record in {where}.")
    lede = intro or terroir or (rts[0]['blurb'] if rts else '') or fallback
    wo_region = m.get('wo_region') or (m.get('geographicalUnit') if nochart else None) or '—'
    regions[key] = {'key': key, 'name': short, 'full': name, 'woRegion': wo_region, 'district': district or '—', 'ward': ward, 'nochart': nochart,
                    'withheld': withheld, 'status': m['status'], 'collected': m.get('collected'), 'expected': intornull(m.get('producer_count_expected')),
                    'terroir': terroir, 'lede': lede, 'routes': rts, 'tours': tours, 'farms': farms}
    idx.append({'key': key, 'name': short, 'district': district or '—', 'woRegion': wo_region, 'farms': len(r['farms']), 'pinned': len(fs),
                'awards': sum(len(f['awards']) for f in r['farms']), 'pending': sum(f['pendingClaims'] or 0 for f in r['farms']),
                'researched': sum(1 for f in r['farms'] if f['awardsCollected']), 'status': m['status'],
                'lat': None if nochart else round(lat, 4), 'lng': None if nochart else round(lng, 4), 'withheld': withheld, 'nochart': nochart})
if skipped: print('note: nothing published in ' + ', '.join(skipped) + ' — not drawn on the chart')

# ---------------------------------------------------------------- the tour operators, as one roster
# Every operator the atlas lists, on one page, grouped by the area it serves. A region page shows only
# the operators serving that region; 22 regions have none, so most of the roster was invisible.
def op_record(t):
    # in the order the operator itself names its areas — the first is where it is filed
    keys, seen = [], set()
    for rk in t['routesServed']:
        for k in tour_regions({'routesServed': [rk]}):
            if k in regions and k not in seen: seen.add(k); keys.append(k)
    detail = copy(t.get('detail'), 260)
    # a line that only says where the operator was listed is provenance, and the source chip already carries it
    if re.match(r'^(Listed|Named) (on|under|by|in|among)\b', detail) and detail.count('. ') == 0: detail = ''
    return {'id': t['id'], 'name': t['name'], 'type': t.get('type') or '', 'base': t.get('base') or '', 'web': t.get('web'),
            'detail': detail, 'verified': bool(t.get('verified')), 'regions': [{'key': k, 'name': regions[k]['name']} for k in keys],
            'source': t.get('sourceUrl'), 'retrieved': t.get('retrieved'),
            'event': str(t.get('type') or '').lower().startswith('route event')}
OPS = [op_record(t) for t in atlas['tourOperators']]
def op_group(o):
    if o['event']: return ('zz-event', 'ROUTE EVENTS')
    if not o['regions']: return ('zy-none', 'AREA NOT STATED')
    if len(o['regions']) >= 4: return ('zx-across', 'ACROSS THE WINELANDS')
    return (o['regions'][0]['name'].lower(), o['regions'][0]['name'].upper())
TOUR_GROUPS = []
for o in sorted(OPS, key=lambda o: (op_group(o)[0], not o['verified'], o['name'].lower())):
    g = op_group(o)
    if not TOUR_GROUPS or TOUR_GROUPS[-1]['label'] != g[1]: TOUR_GROUPS.append({'label': g[1], 'ops': []})
    TOUR_GROUPS[-1]['ops'].append(o)
N_OPS = sum(1 for o in OPS if not o['event'])
TOURS_DATA = {'groups': TOUR_GROUPS, 'operators': N_OPS, 'read': max((o['retrieved'] or '') for o in OPS)}
idx.sort(key=lambda x: (x['nochart'], x['name']))   # the shelf lists last
stats = dict(atlas['stats'])
stats.update({'regions': sum(1 for x in idx if not x['nochart']), 'routes': len(atlas['routes']), 'tours': len(atlas['tourOperators']), 'built': atlas.get('dataAsAt') or atlas['built'], 'buildMode': mode,
              'competitions': [{'body': x['body'], 'year': x['year'], 'records': x['records']} for x in atlas['competitions']],
              'tourDisclaimer': atlas['tourOperatorDisclaimer'], 'withheld': atlas.get('withheld', {}).get('total', 0),
              'industry': {'cellars': atlas.get('industry', {}).get('cellarsCrushing2024', {}).get('total'), 'source': 'SAWIS, SA Wine Industry Statistics 2024'}})
stats['tours'] = N_OPS   # operators, not entries: the atlas also records one route event, which is shown as such
_w = atlas['stats'].get('wines') or {}
stats['wines'] = {k: _w.get(k) for k in ('brands', 'ranges', 'notes', 'producersWithBrands', 'namelessByChoice')}
LON0, LON1, LAT0, LAT1 = 17.6, 23.75, 31.25, 35.05        # the Western Cape chart's bounding box
marks = {r['key']: [(r['lng']-LON0)/(LON1-LON0), (-r['lat']-LAT0)/(LAT1-LAT0)] for r in idx if r['lat'] is not None}
geo = json.loads((SRC / 'geo.json').read_text())

# ---------------------------------------------------------------- lenses & search
# Lenses re-weight the chart by one attribute; the per-region figures are counted here so the chart page
# needs nothing but the index. Everything is counted from the record as it stands — nothing inferred.
def strip_vintage(w): return re.sub(r'\s+\((19|20)\d\d\)$', '', re.sub(r'\s+(19|20)\d\d\s*$', '', str(w or ''))).strip()
def fold_name(w): return re.sub(r'[^a-z0-9]+', ' ', strip_vintage(w).lower()).strip()
def norm_grape(v):
    v = re.sub(r'\s+', ' ', str(v or '').strip())
    if re.fullmatch(r'(?i)syrah|shiraz', v): return 'Shiraz / Syrah'
    return ' '.join(w[:1].upper() + w[1:].lower() for w in v.split(' '))
grape_count = {}
for R in regions.values():
    for f in R['farms']:
        for g in {norm_grape(v) for v in (f['varieties'] or []) if v}: grape_count[g] = grape_count.get(g, 0) + 1
LENS_GRAPES = [g for g, _ in sorted(grape_count.items(), key=lambda x: -x[1])[:12]]
def lens_of(farms):
    fs = farms
    founded = [f['founded'] for f in fs if f.get('founded')]
    return {'honours': sum(len(f['awards']) for f in fs), 'pending': sum(f['pendingClaims'] or 0 for f in fs),
            'grapes': {g: sum(1 for f in fs if g in {norm_grape(v) for v in (f['varieties'] or [])}) for g in LENS_GRAPES},
            'withVar': sum(1 for f in fs if f['varieties']), 'walkIn': sum(1 for f in fs if f.get('access') == 'walk_in'),
            'appt': sum(1 for f in fs if f.get('access') == 'appointment'), 'unknownAccess': sum(1 for f in fs if not f.get('access') or f.get('access') == 'unknown'),
            'pre1900': sum(1 for y in founded if y < 1900), 'withFounded': len(founded), 'oldest': min(founded) if founded else None,
            'oldVines': sum(1 for f in fs if f.get('oldVineFlag')), 'researched': sum(1 for f in fs if f['awardsCollected']),
            'pinned': sum(1 for f in fs if f['lat'] is not None)}
for r in idx: r['lens'] = lens_of(regions[r['key']]['farms'])
ALL_FARMS = [f for R in regions.values() for f in R['farms']]
lens_totals = lens_of(ALL_FARMS) | {'farms': len(ALL_FARMS), 'withheld': sum(r['withheld'] for r in idx)}
SHORT_SUFFIX = re.compile(r' (Estate|Vineyards|Wines|Wine Estate|Wine Cellar|Organic Wine Estate|Family Wines|Winery|Wine Farm|Private Cellar)$')
def producer_prefixes(f):
    short = SHORT_SUFFIX.sub('', re.sub(r' \(.*\)$', '', f['name']))
    cands = {fold_name(f['name']), fold_name(short)}
    first = fold_name(short).split(' ')[0] if fold_name(short) else ''
    if len(first) >= 5: cands.add(first)
    return sorted((c for c in cands if c), key=len, reverse=True)
def fold_wine(name, prefixes):
    """A wine's name as the ledger or the list gives it, folded, with the producer's own name lifted off the front
    ('Kanonkop Black Label' and 'Black Label' are the same wine)."""
    k = fold_name(name)
    for p in prefixes:
        if k == p: return ''
        if k.startswith(p + ' '): return k[len(p) + 1:]
    return k
def tidy_name(n, prefixes=()):
    n = strip_vintage(n)
    for p in prefixes:   # the producer's own name lifted off the front, as printed
        m = re.match(r'(?i)^' + r'\W+'.join(map(re.escape, p.split(' '))) + r'\W+(?=\S)', n)
        if m: n = n[m.end():]; break
    if len(n) > 3 and n.isupper(): n = ' '.join(w if len(w) <= 2 else w.title() for w in n.split(' '))
    return n
def wines_of(f):
    """The wines on record: the producer's own list, each with the honours the ledger names for it (a range label
    becomes a card only when an honour names it), then the signature wines, then wines only the ledger names."""
    pre = producer_prefixes(f)
    wines, order = {}, 0
    def put(k, name, src):
        nonlocal order
        if k not in wines: wines[k] = {'name': tidy_name(name, pre), 'src': src, 'honours': [], 'note': None, 'order': order}; order += 1
        return wines[k]
    def find(k):
        if k in wines: return wines[k]
        for x in sorted(wines, key=len, reverse=True):
            if len(x) >= 4 and (k.startswith(x + ' ') or (len(x) >= 5 and ' ' + x + ' ' in ' ' + k + ' ')): return wines[x]
        return None
    ranges = {fold_wine(w['name'], pre): w['name'] for w in (f.get('wines') or []) if w['kind'] == 'range' and fold_wine(w['name'], pre)}
    for w in (f.get('wines') or []):
        k = fold_wine(w['name'], pre)
        if w['kind'] == 'wine' and k: put(k, w['name'], 'list')
    for w in (f['signatureWines'] or []):
        k = fold_wine(w, pre)
        if k: put(k, w, 'signature')
    for a in f['awards']:
        if not a['wine'] or re.fullmatch(r'(?i)winery', a['wine']): continue
        k = fold_wine(a['wine'], pre)
        if not k: continue
        hit = find(k)
        if not hit:
            r = next((x for x in sorted(ranges, key=len, reverse=True) if k == x or k.startswith(x + ' ')), None)
            hit = put(r, ranges[r], 'range') if r else put(k, a['wine'], 'ledger')
        hit['honours'].append(a)
    for n in (f.get('wineNotes') or []):
        hit = find(fold_wine(n['wine'], pre))
        if hit and not hit['note']: hit['note'] = n['note']
    rank_src = {'list': 0, 'range': 0, 'signature': 1, 'ledger': 2}
    return sorted(wines.values(), key=lambda w: (rank_src[w['src']], -len(w['honours']), w['order']))
def ranges_of(f): return [tidy_name(w['name']) for w in (f.get('wines') or []) if w['kind'] == 'range']
# the search index: producers, regions, wards, grapes and the producers' own wine names, with the region key to open
search = []
name_of = {r['key']: r['name'] for r in idx}
for r in idx: search.append({'t': 'REGION', 'l': r['name'], 's': f"{r['farms']} producers", 'k': r['key']})
wards = {}
for key, R in regions.items():
    for f in R['farms']:
        search.append({'t': 'PRODUCER', 'l': f['name'], 's': name_of[key], 'k': key, 'id': f['id']})
        if f.get('ward'): wards.setdefault(f['ward'], {'n': 0, 'k': key}); wards[f['ward']]['n'] += 1
        seen = set(); pre = producer_prefixes(f)
        for w in [x['name'] for x in (f.get('wines') or []) if x['kind'] == 'wine'] + list(f.get('signatureWines') or []):
            k = fold_wine(w, pre)
            if not k or k in seen: continue
            seen.add(k); search.append({'t': 'WINE', 'l': tidy_name(w, pre), 's': f['name'], 'k': key, 'id': f['id']})
for w, x in wards.items(): search.append({'t': 'WARD', 'l': w, 's': f"{x['n']} producers · {name_of[x['k']]}", 'k': x['k']})
for g, n in sorted(grape_count.items(), key=lambda x: -x[1]): search.append({'t': 'GRAPE', 'l': g, 's': f"{n} producers grow it", 'g': g})
# every producer, compactly, so the producer page can find its region and its neighbours across region borders
producers = [[f['id'], key, f['name'], f['lat'], f['lng']] for key, R in regions.items() for f in R['farms']]
index = {'idx': idx, 'stats': stats, 'geo': geo, 'marks': marks, 'lensGrapes': LENS_GRAPES, 'lensTotals': lens_totals, 'producers': producers}

# ---------------------------------------------------------------- the producer record (shared by the region cards and the producer page)
import math
def km(a, b):
    dlat = math.radians(b['lat'] - a['lat']); dlng = math.radians(b['lng'] - a['lng'])
    x = math.sin(dlat/2)**2 + math.cos(math.radians(a['lat'])) * math.cos(math.radians(b['lat'])) * math.sin(dlng/2)**2
    return 2 * 6371 * math.asin(math.sqrt(x))
LOCATED = [(key, f) for key, R in regions.items() for f in R['farms'] if f['lat'] is not None]
def neighbours_of(f, n=6):
    if f['lat'] is None: return []
    return sorted(({'key': k, 'f': x, 'd': km(f, x)} for k, x in LOCATED if x['id'] != f['id']), key=lambda z: z['d'])[:n]
def rank(a):
    t = (a['award'] + ' ' + a['body']).lower()
    if re.search(r'winery of the year|trophy|best in show', t): return 6
    if re.search(r'double gold|5 star|five star|platinum|grand gold', t): return 5
    if re.search(r'gold|9[5-9]/100|9[5-9] points|9[5-9]pts', t): return 4
    if re.search(r'silver|9[0-4]', t): return 3
    if re.search(r'bronze', t): return 2
    return 1
PAREN = re.compile(r'\s*\(.*?\)\s*')
def award_of(a):
    # some sources name the critic in both fields; the ledger says it once
    t = a['award'] or ''; b = a['body'] or ''
    return t[len(b):].strip() if b and t.lower().startswith(b.lower() + ' ') else t
def top_honours(f, n=3): return sorted(f['awards'], key=lambda a: (-rank(a), -(a['year'] or 0)))[:n]

built = datetime.date.fromisoformat(stats['built'])
EDITION = built.strftime('%B %Y').upper() + ' EDITION'

# ---------------------------------------------------------------- pre-rendering (what a crawler or a no-script visitor reads; the script re-renders on load)
esc = lambda s: html.escape(str(s if s is not None else ''), quote=True)
def host(u):
    try: return re.sub(r'^www\.', '', u.split('//', 1)[1].split('/', 1)[0])
    except Exception: return u
ACCESS = {'walk_in': 'WALK-IN TASTING', 'appointment': 'TASTING BY APPOINTMENT', 'scheduled': 'TASTING ON ANNOUNCED DATES', 'closed_temporarily': 'TASTING CLOSED FOR NOW', 'closed_permanently': 'TASTING PERMANENTLY CLOSED', 'none': 'NO TASTING ROOM', 'unknown': 'ACCESS NOT CONFIRMED'}
STATUS = {'complete_pending_verification': 'recorded · awaiting independent review', 'over_enumerated_pending_verification': 'recorded · awaiting independent review', 'in_progress': 'research in progress', 'audited': 'independently reviewed', 'not_started': 'not yet researched'}

def chain_of(R):
    ward = R['ward'] if R['ward'] and '(' not in R['ward'] else None
    chain = [x for x in (R['woRegion'], R['district']) if x and x != '—' and x.upper() != R['name'].upper()]
    return ward, [esc(x.upper()) for x in chain]

def crumb_html(R):
    ward, chain = chain_of(R)
    return crumb_home() + ''.join(f'<span>/</span>{x}' for x in chain) + f'<span>/</span><b>{esc((ward or R["name"]).upper())}{" WARD" if ward else ""}</b>'

NOCHART_MAP = '''<div class="rv-map nochart" id="rvMap" role="note"><div class="nopins mono">NOT ON THE CHART<br>THESE PRODUCERS CANNOT BE PLACED<br>NARROWER THAN THE WESTERN CAPE</div><span class="corner tl"></span><span class="corner br"></span></div>'''
TOURS_NOTE = ('<b>LISTED, NOT ENDORSED.</b> An operator appears here because it publicly offers winelands tours and the atlas can point to '
              'where it says so. Inclusion says nothing about licensing, insurance or safety — please confirm operating permits, prices and '
              'current schedules with the operator directly. What is shown is what the operator or its association had published on the day it was read.')
def op_html(o):
    flag = ('<span class="flag gold mono">EVENT · NOT AN OPERATOR</span>' if o['event'] else
            '' if o['verified'] else '<span class="flag dim mono">NOT YET CONFIRMED</span>')
    web = f'<a href="{esc(o["web"])}" target="_blank" rel="noopener">{esc(host(o["web"]))}</a>' if o['web'] else '<span class="dim">No website on record</span>'
    regs = ' · '.join(f'<a href="{ROOT}region/{r["key"]}/">{esc(r["name"].upper())}</a>' for r in o['regions']) or 'NOT STATED'
    src = f'<a class="src mono" href="{esc(o["source"])}" target="_blank" rel="noopener">SEEN AT · {esc(host(o["source"]).upper())}{(" · " + esc(o["retrieved"])) if o["retrieved"] else ""}</a>' if o['source'] else ''
    return (f'<article class="op" id="op-{esc(o["id"])}"><div class="op-bar mono"><span>$ OPERATOR.{esc(o["id"].upper())}</span></div>'
            f'<h3>{esc(o["name"])}</h3><div class="op-type mono">{esc(o["type"].upper())}</div>'
            + (f'<p class="op-detail">{esc(o["detail"])}</p>' if o['detail'] else '')
            + f'<div class="op-row"><span class="k mono">BASED</span><span>{esc(o["base"])}</span></div>'
            f'<div class="op-row"><span class="k mono">SERVES</span><span class="mono op-regions">{regs}</span></div>'
            f'<div class="op-row"><span class="k mono">WEBSITE</span><span>{web}</span></div>'
            f'<div class="op-foot">{flag}{src}</div></article>')
def prerender_tours():
    groups = ''.join(f'<section class="op-group"><h2 class="mono"><span class="h3l">{esc(g["label"])} <span>{len(g["ops"])}</span></span></h2><div class="op-grid">'
                     + ''.join(op_html(o) for o in g['ops']) + '</div></section>' for g in TOUR_GROUPS)
    return f'''
      <div class="lv-head tv-head">
        <div class="rv-eyebrow mono">EVERY OPERATOR THE ATLAS LISTS · {N_OPS} ACROSS {len([g for g in TOUR_GROUPS if g["label"] not in ("ROUTE EVENTS", "AREA NOT STATED")])} AREAS · READ TO {esc(TOURS_DATA["read"])}</div>
        <h2 class="display" id="tvTitle" tabindex="-1">Tour<br>operators</h2>
        <p class="lv-lede">{N_OPS} operators publicly offer tours of the Cape winelands, from a hop-on hop-off tram to a steam train to a private guide. They are listed here under the first area each names, with every area it serves and the page that says so. <b>A region page shows only the operators serving that region; this page shows them all.</b></p>
        <div class="rv-note tv-note">{TOURS_NOTE}</div>
      </div>
      {groups}'''
def tours_crumb(): return crumb_home() + '<span>/</span><b>TOUR OPERATORS</b>'

def region_index_html():
    """The home page's way in, as real links.

    The index is drawn as an interactive list by the script, but a page whose only route to 651
    producer pages is a script is a page that links to nothing: a crawler reads four links, two of
    them mailto, and every region and producer below is reachable only from the sitemap. These
    anchors are the same rows the script renders, written at build time; the script replaces them
    with its own, which are also anchors.
    """
    NC = '<em class="nc">NOT ON THE CHART</em>'
    out = []
    for i, r in enumerate(idx):
        cls = 'rl nochart' if r['nochart'] else 'rl'
        num = '··' if r['nochart'] else str(i + 1).zfill(2)
        tag = NC if r['nochart'] else ''
        out.append(f'<a class="{cls}" href="{ROOT}region/{r["key"]}/" data-key="{r["key"]}">'
                   f'<span class="n">{num} {esc(r["name"].upper())}</span>'
                   f'<span class="c">{r["farms"]}</span>{tag}</a>')
    return ''.join(out)

def crumb_home():
    return f'<a href="{ROOT}"><b>CAPE WINE ATLAS</b></a>'

def prerender(R):
    farms = R['farms']; S = stats
    pinned = sum(1 for f in farms if f['lat'] is not None)
    awards = sum(len(f['awards']) for f in farms); pending = sum(f['pendingClaims'] or 0 for f in farms)
    researched = sum(1 for f in farms if f['awardsCollected']); walk = sum(1 for f in farms if f['access'] == 'walk_in')
    founded = [f['founded'] for f in farms if f['founded']]; oldest = min(founded) if founded else None
    wards = sorted({f['ward'] for f in farms if f['ward']})
    ward, chain = chain_of(R)
    eyebrow = ' · '.join([*chain, *( [esc(ward.upper()) + ' WARD'] if ward else []), *( [esc(R['routes'][0]['name'].upper())] if R['routes'] else [])]) or 'WESTERN CAPE'
    recs = []
    for f in farms:
        meta = [x for x in [
            f'EST {f["founded"]}' if f['founded'] else None,
            f'<span class="{"ok" if f["access"] in ("walk_in","appointment") else ""}">{ACCESS.get(f["access"], "ACCESS NOT CONFIRMED")}</span>',
            (f'WARD · {esc(f["ward"].upper())}' if (f['ward'] and (not R['ward'] or f['ward'] != R['ward'])) else (esc(f['locality'].split('(')[0].split('—')[0].strip().upper()) if (f['locality'] and not f['ward'] and not R['nochart']) else None)),
            'ROUTE MEMBER' if f['routeMember'] == 'yes' else None,
            f'LOCATION · {str(f["geoConfidence"] or "").upper()}' if f['lat'] is not None else 'LOCATION NOT YET RESOLVED',
            '<span class="gold">OLD VINES</span>' if f['oldVineFlag'] else None] if x]
        # the card carries a summary of the honours; the full ledger, each with its source, is on the producer's own page
        n_aw = len(f['awards'])
        led = (f'<div class="rec-sum mono"><span class="g">{n_aw} HONOUR{"" if n_aw == 1 else "S"} VERIFIED</span>'
               + ''.join(f' · {esc(a["body"])} {esc(PAREN.sub("", award_of(a))[:42])}{" " + str(a["year"]) if a["year"] else ""}' for a in top_honours(f))
               + (f' · and {n_aw - 3} more' if n_aw > 3 else '') + '</div>') if n_aw else ''
        flags = ''.join([
            '<span class="flag warn mono">AWARDS NOT YET RESEARCHED</span>' if not f['awardsCollected'] else '',
            '<span class="flag dim mono">NO VERIFIED HONOUR ON FILE</span>' if (f['awardsCollected'] and not f['awards'] and not f['pendingClaims']) else '',
            f'<span class="flag gold mono">{f["pendingClaims"]} CLAIM{"S" if f["pendingClaims"] > 1 else ""} UNDER REVIEW</span>' if f['pendingClaims'] else ''])
        contact = ''.join([
            f'<a href="{esc(f["web"])}" target="_blank" rel="noopener">{esc(host(f["web"]))}</a>' if f['web'] else '',
            f'<span>{esc(str(f["contactHeld"]).upper())} ON FILE · NOT REPUBLISHED</span>' if f['contactHeld'] else ''])
        recs.append(f'''<article class="rec" id="rec-{f['id']}" data-id="{f['id']}">
        <div class="rec-bar mono"><span>$ record.{f['id']}</span><a class="rec-open mono" href="{ROOT}producer/{f['id']}/" data-region="{R['key']}" data-open="{f['id']}">OPEN THE RECORD ▸</a><span class="term-dots"><span></span><span></span><span></span></span></div>
        <div class="rec-body">
          <div class="rec-name display" data-region="{R['key']}" data-open="{f['id']}">{esc(f['name'])}</div>
          <div class="rec-meta mono">{''.join(f'<span>{x}</span>' for x in meta)}</div>
          {f'<p class="rec-hist">{esc(f["history"])}</p>' if f['history'] else ''}
          {f'<div class="rec-row"><span class="k mono">PEOPLE</span><span>{esc(f["people"])}</span></div>' if f.get('people') else ''}
          {f'<div class="rec-row"><span class="k mono">HOURS</span><span>{esc(f["hours"])}</span></div>' if f['hours'] else ''}
          {('<div class="rec-row"><span class="k mono">VARIETIES</span><div class="tags mono">' + ''.join(f'<span>{esc(v)}</span>' for v in f['varieties']) + '</div></div>') if f['varieties'] else ''}
          {('<div class="rec-row"><span class="k mono">SIGNATURE</span><span>' + ' · '.join(esc(x) for x in f['signatureWines']) + '</span></div>') if f['signatureWines'] else ''}
          <div class="rec-awards">{led}{flags}</div>
          <div class="rec-contact mono">{contact}</div>
        </div></article>''')
    routes = ''.join(
        f'<p><b>{esc(rt["name"])}</b>{" — " + esc(rt["area"]) if rt["area"] else ""}. '
        + (f'{rt["membersRecorded"]}{" of " + str(rt["membersExpected"]) if rt["membersExpected"] else ""} members on record; ' if rt['membersRecorded'] is not None else '')
        + 'membership ' + ('confirmed against the route’s own listing' if rt['status'] == 'verified' else 'not applicable — no association exists' if rt['status'] == 'no_association' else 'still being confirmed') + '.'
        + (' ' + esc(rt['blurb'].rstrip(';') + ('.' if rt['blurb'].endswith(';') else '')) if rt['blurb'] else '') + '</p>'
        + (f'<p class="mono" style="font-size:10px;letter-spacing:.12em;color:var(--muted)">SOURCE · <a style="color:inherit" href="{esc(rt["sourceUrl"])}" target="_blank" rel="noopener">{esc(host(rt["sourceUrl"]))}</a>{" · CONSULTED " + esc(rt["retrieved"]) if rt["retrieved"] else ""}</p>' if rt['sourceUrl'] else '')
        for rt in R['routes']) or '<p>No route association is on file for this area; the producers below were gathered from the wine industry’s own records and their own websites.</p>'
    def tour_html(t):
        unv = '' if t['verified'] else ' <span class="flag dim mono">NOT YET CONFIRMED</span>'
        web = f' · <a href="{esc(t["web"])}" target="_blank" rel="noopener">{esc(host(t["web"]))}</a>' if t['web'] else ''
        return f'<div class="tour"><b>{esc(t["name"])}</b>{unv}<span class="t mono">{esc(t["type"])} · {esc(t["base"])}{web}</span></div>'
    tours = (''.join(tour_html(t) for t in R['tours']) or '<div class="tour"><span class="t mono">NO TOUR OPERATOR IS YET LISTED FOR THIS ROUTE</span></div>') \
            + f'<div class="tour tour-all"><a class="mono" href="{ROOT}tours/">ALL {N_OPS} OPERATORS ACROSS THE ATLAS ▸</a></div>'
    comps = ' · '.join(f'{esc(c["body"])} {c["year"]}' for c in S['competitions'])
    return f'''
      <div class="rv-head">
        <div>
          <div class="rv-eyebrow mono">{eyebrow}</div>
          <h2 class="display" id="rvTitle" tabindex="-1">{esc(R['name'])}</h2>
          <p class="rv-lede" id="rvLede">{esc(R['lede'])}</p>
          <div class="rv-stats mono">
            <div><span class="v">{len(farms)}</span><span class="k">PRODUCERS ON RECORD</span></div>
            <div><span class="v">{pinned}</span><span class="k">WITH A LOCATION</span></div>
            <div><span class="v g">{awards}</span><span class="k">HONOURS VERIFIED</span></div>
            <div><span class="v">{pending}</span><span class="k">CLAIMS UNDER REVIEW</span></div>
            <div><span class="v">{researched}/{len(farms)}</span><span class="k">AWARD RESEARCH COMPLETE</span></div>
            <div><span class="v">{walk}</span><span class="k">WALK-IN TASTING ROOMS</span></div>
            <div><span class="v">{oldest or '—'}</span><span class="k">OLDEST FOUNDING ON FILE</span></div>
            <div><span class="v">{len(wards) or '—'}</span><span class="k">{'WARD' if len(wards) == 1 else 'WARDS'} REPRESENTED</span></div>
          </div>
          {f'<div class="rv-withheld mono">{R["withheld"]} FURTHER {"RECORD IS" if R["withheld"] == 1 else "RECORDS ARE"} HELD BACK UNTIL {"IT MEETS" if R["withheld"] == 1 else "THEY MEET"} THE PUBLICATION STANDARD</div>' if R['withheld'] else ''}
        </div>
        {NOCHART_MAP if R['nochart'] else f"""<div class="rv-map" id="rvMap"><canvas id="miniCanvas" role="img" aria-label="Tactical map of {esc(R['name'])}: producers with a published position"></canvas><span class="corner tl"></span><span class="corner br"></span>
          <div class="hud mono">TACTICAL · {esc(R['name'].upper())}<br><b>{pinned}/{len(farms)}</b> POSITIONS LOCATED</div>
          <div class="scale mono"><i style="width:60px"></i><span>≈ 1 KM</span></div></div>"""}
      </div>
      <section class="rv-block">
        <h3 class="mono"><span class="h3l">PRODUCER RECORDS <span>{len(farms)} ON RECORD · {esc(STATUS.get(R['status'], R['status']).upper())}</span></span></h3>
        <div class="rv-grid" id="recGrid">{''.join(recs)}</div>
      </section>
      <section class="rv-block rv-two">
        <div>
          <h4 class="mono">THE ROUTE</h4>{routes}
          <h4 class="mono" style="margin-top:26px">TOUR OPERATORS SERVING THIS AREA · {len(R['tours'])}</h4>
          <div class="rv-note" style="margin-bottom:10px"><b>LISTED, NOT ENDORSED.</b> An operator appears here because it publicly offers winelands tours and we can point to where it says so. Inclusion says nothing about licensing, insurance or safety — please confirm operating permits and current schedules with the operator directly. Details are as published at the source on the day we consulted it.</div>
          {tours}
        </div>
        <div>
          <h4 class="mono">THE HONOURS LEDGER</h4>
          <p>{'Every producer in this region has had its honours researched' if researched == len(farms) else f'{researched} of the {len(farms)} producers here have had their honours researched so far'}: {awards} {'award stands' if awards == 1 else 'awards stand'} verified against {'its source' if awards == 1 else 'their sources'}{f', and {pending} further {"claim waits" if pending == 1 else "claims wait"} for confirmation' if pending else ''}. Competitions consulted: {comps}.</p>
          <h4 class="mono" style="margin-top:26px">HOW TO READ THIS PAGE</h4>
          <div class="rv-note"><b>NOTHING IS WRITTEN HERE WITHOUT A SOURCE.</b> Every honour links to the page where it was found. Our researchers may only record what they can cite; an entry is promoted to “confirmed” only once a second, independent reviewer has gone back to the source.<br><br><b>“NOT YET RESEARCHED” IS NOT “NO AWARDS”.</b> The atlas is careful to tell “nobody has looked yet” apart from “nothing was won” — many fine producers simply never enter competitions.<br><br><b>WHAT IS HELD BACK.</b> Where a detail rests on a source the atlas is not free to republish, it is withheld until the producer’s own site or an open record confirms it. Claims still under review are counted, never presented as fact.</div>
          {f'<h4 class="mono" style="margin-top:26px">TERROIR</h4><p>{esc(R["terroir"])}</p>' if (R['terroir'] and R['lede'] != R['terroir']) else ''}
        </div>
      </section>
      <div class="rv-foot mono"><span>THE ATLAS RECORD · {EDITION}</span><span>DATA UNDER ODbL 1.0 · CONTAINS INFORMATION FROM OPENSTREETMAP, © OPENSTREETMAP CONTRIBUTORS</span><span>{' · '.join([*chain, *([esc(ward.upper())] if ward else [])]) or esc(R['name'].upper())}</span><span>RECORDS GATHERED {esc(R['collected'] or '—')}</span><span>ACROSS THE ATLAS · {S['farms']} FARMS · {S['regions']} REGIONS · {S['verifiedAwards']} HONOURS VERIFIED</span></div>'''

# ---------------------------------------------------------------- the producer page (the third level: chart → region → producer)
VENUE = {'hosted': 'TASTED AT A HOST VENUE', 'outlet': 'TASTED AT AN OUTLET', 'none': 'NO TASTING VENUE'}
def src_chip(a):
    if not a.get('sourceUrl'): return ''
    label = (a.get('sourceName') or host(a['sourceUrl'])).upper()
    label = label[:30] + '…' if len(label) > 30 else label
    return (f'<a class="src mono" href="{esc(a["sourceUrl"])}" target="_blank" rel="noopener" title="{esc(a.get("sourceName") or "")}">SOURCE · {esc(label)}</a>'
            + ('<span class="corr mono">✓✓ CORROBORATED</span>' if a.get('corr') else ''))
def pv_crumb_html(R, f):
    # the region segment is a real link: a producer page that cannot be walked back up to its region
    # is a leaf with no parent, and 651 of them were exactly that
    return (crumb_home() + f'<span>/</span><a href="{ROOT}region/{R["key"]}/"><b>{esc(R["name"].upper())}</b></a>'
            + f'<span>/</span><b>{esc(f["name"].upper())}</b>')
def prerender_producer(R, f):
    region = R['name']; located = f['lat'] is not None
    neigh = neighbours_of(f); wines = wines_of(f)
    by_year = {}
    for a in f['awards']: by_year.setdefault(a['year'] if a['year'] is not None else '—', []).append(a)
    years = sorted(by_year, key=lambda y: -1 if y == '—' else -int(y))
    # a producer on the shelf is placed at the province and nothing narrower: the eyebrow says exactly that, and
    # the locality the producer itself states goes under VISIT, where it reads as the producer's word rather than ours
    eyebrow = ('WESTERN CAPE · NO FIXED PLACE' if R['nochart'] else
               ' · '.join(esc(str(x).upper()) for x in [R['woRegion'], R['district'], f['ward']] if x and x != '—') + (' · ' + esc(str(f['locality']).upper()) if f['locality'] else ''))
    flags = ''.join(x for x in [
        f'<span class="flag gold mono">{ACCESS.get(f["access"], esc(str(f["access"]).upper()))}</span>' if f['access'] else '',
        '<span class="flag dim mono">ROUTE MEMBER</span>' if f['routeMember'] == 'yes' else '',
        '<span class="flag gold mono">OLD VINES</span>' if f['oldVineFlag'] else '',
        f'<span class="flag dim mono">LOCATION · {esc(str(f["geoConfidence"] or "on record").upper()) if located else "AWAITING A PUBLISHED POSITION"}</span>',
        '' if f['awardsCollected'] else '<span class="flag warn mono">AWARD RESEARCH NOT YET REACHED</span>',
        f'<span class="flag warn mono">{f["pendingClaims"]} CLAIM{"" if f["pendingClaims"] == 1 else "S"} UNDER REVIEW</span>' if f['pendingClaims'] else ''] if x)
    SRC_LABEL = {'list': 'ON THE PRODUCER’S OWN LIST', 'range': 'A RANGE ON THE PRODUCER’S OWN LIST', 'signature': 'SIGNATURE WINE', 'ledger': 'NAMED IN THE HONOURS LEDGER'}
    def wine_card(w):
        hs = w['honours']
        li = ''.join(f'<li><span class="y mono">{esc(a["year"] or "")}</span><span><b>{esc(a["body"])}</b> — {esc(award_of(a))}' + (f' <span class="vint">({m.group(0)})</span>' if (m := re.search(r'(19|20)\d\d', a['wine'] or '')) else '') + '</span></li>' for a in hs[:4])
        more = f'<li><span class="y"></span><span class="vint">and {len(hs) - 4} more in the ledger below</span></li>' if len(hs) > 4 else ''
        note = f'<div class="note">“{esc(w["note"].strip().rstrip(".") )}.” <span class="mono">— THE PRODUCER’S OWN ACCOUNT OF THE NAME</span></div>' if w['note'] else ''
        return (f'<div class="pv-wine"><div class="n display">{esc(w["name"])}</div><div class="m mono">{SRC_LABEL[w["src"]]}'
                + (f' · <span class="g">{len(hs)} HONOUR{"" if len(hs) == 1 else "S"}</span>' if hs else '') + '</div>' + note + (f'<ul>{li}{more}</ul>' if hs else '') + '</div>')
    ranges = ranges_of(f)
    n_listed = sum(1 for w in wines if w['src'] in ('list', 'range'))
    read_on = esc(f.get('winesRead') or '')
    src_links = ' · '.join(f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(h.upper())}</a>' for h, u in {host(u): u for u in reversed(f.get('winesUrls') or [])}.items())
    n_r = len(ranges); pl = lambda n: '' if n == 1 else 'S'
    when = (' ON ' + read_on) if read_on else ''
    in_ranges = f' IN {n_r} RANGE{pl(n_r)}' if ranges else ''
    if n_listed:
        wines_src = f'THE RANGE AS THE PRODUCER PRINTS IT, READ FROM {src_links or "ITS OWN PAGES"}{when} · {n_listed} NAME{pl(n_listed)}{in_ranges}'
    elif f.get('winesAbsent'):
        wines_src = f'NO READABLE PAGE ON THE PRODUCER’S OWN DOMAIN{when} · ' + ('THE WINES ABOVE ARE THOSE THE HONOURS LEDGER NAMES' if wines else 'THE HONOURS LEDGER NAMES NONE EITHER')
    elif f.get('winesCollected'):
        wines_src = f'THE PRODUCER’S OWN PAGES ({src_links or "ITS OWN SITE"}{", READ ON " + read_on if read_on else ""}) PUBLISH NO WINE NAMES — SOME SELL BY GRAPE VARIETY ALONE AND DO SO DELIBERATELY; THE ATLAS DOES NOT GUESS' + ('' if wines else '. THE HONOURS LEDGER NAMES NONE EITHER')
    else:
        wines_src = 'THE PRODUCER’S OWN RANGE HAS NOT YET BEEN READ' + ('; THE WINES ABOVE ARE THOSE THE HONOURS LEDGER NAMES' if wines else '')
    n_more = len(wines) - n_listed
    range_txt = f' and {n_r} range label{pl(n_r).lower()}' if ranges else ''
    wines_prov = (f'{n_listed} name{pl(n_listed).lower()}{range_txt} read from the producer’s own pages' + ((' on ' + read_on) if read_on else '')) if n_listed else \
                 ('no readable page on the producer’s own domain' if f.get('winesAbsent') else ('the producer publishes no wine names on its own site' if f.get('winesCollected') else 'range not yet read'))
    if n_more: wines_prov += f'; {n_more} further name{pl(n_more).lower()} from the honours ledger'
    ranges_html = ('<div class="pv-ranges mono"><span class="k">RANGES</span>' + ''.join(f'<span>{esc(r)}</span>' for r in ranges) + '</div>') if ranges else ''
    lede = esc(f['history']) if f['history'] else (('A producer the atlas can name, source and reach, and cannot place narrower than the Western Cape. ' if R['nochart'] else f'A producer on the {esc(region)} record. ') + 'The atlas holds its hours, varieties and honours; a history line will follow when the record has one that meets the publication standard.')
    row = lambda k, v: f'<div class="pv-row"><span class="k mono">{k}</span><span>{v}</span></div>'
    visit = ''.join([
        row('HOURS', esc(f['hours']) if f['hours'] else 'No public tasting schedule on record.'),
        row('VENUE', VENUE[f['venue']]) if f['venue'] in VENUE else '',
        row('WEBSITE', f'<a href="{esc(f["web"])}" target="_blank" rel="noopener">{esc(host(f["web"]))}</a>') if f['web'] else '',
        row('CONTACT', (esc(str(f['contactHeld']).upper()) + ' on file, not republished — reach the producer through its own site.') if f['contactHeld'] else 'Not held; reach the producer through its own site.'),
        row('LOCALITY', esc(f['locality']) + ' — as the producer states it; not a place the atlas could confirm.') if (R['nochart'] and f['locality']) else '',
        '' if located else row('POSITION', 'None published by the producer or an association; the atlas does not invent one.')])
    vineyard = ''.join([
        (f'<div class="pv-row"><span class="k mono">VARIETIES</span><div class="tags mono">' + ''.join(f'<span>{esc(v)}</span>' for v in f['varieties']) + '</div></div>') if f['varieties'] else row('VARIETIES', 'None on record yet.'),
        row('SIGNATURE', ' · '.join(esc(x) for x in f['signatureWines'])) if f['signatureWines'] else '',
        row('OLD VINES', 'Old-vine bottlings on record.') if f['oldVineFlag'] else '',
        row('FOUNDED', esc(f['founded'])) if f['founded'] else ''])
    def neigh_row(n):
        far = regions[n['key']]['name'] if n['key'] != R['key'] else (n['f']['ward'] or '')
        return (f'<span class="d">{n["d"]:.1f}' if n['d'] < 10 else f'<span class="d">{round(n["d"])}') + f' KM</span><a href="{ROOT}producer/{n["f"]["id"]}/" data-open="{n["f"]["id"]}" data-region="{n["key"]}">{esc(n["f"]["name"])}</a><span class="d">{esc(far.upper())}</span>'
    neigh_html = ('<div class="pv-neigh mono">' + ''.join(neigh_row(n) for n in neigh) + '</div>') if neigh else '<p class="pv-prov">Neighbours are listed once the producer has a published position.</p>'
    ledger = ''.join(
        f'<div class="yr mono">{esc(y)}</div><div class="rv-grid pv-ledger-grid">' + ''.join(
            f'<div class="aw pv-aw"><span><b>{esc(a["body"])}</b> — {esc(award_of(a))}</span><span class="w">{esc(a["wine"])}</span><span>{src_chip(a)}</span></div>' for a in by_year[y]) + '</div>'
        for y in years) if f['awards'] else f'<p class="pv-prov">{"No verified honours on record." if f["awardsCollected"] else "Award research has not yet reached this producer; the ledger is empty rather than guessed."}</p>'
    n_aw = len(f['awards']); pc = f['pendingClaims'] or 0
    return f'''
      <div class="pv-head{'' if located else ' nomap'}">
        <div>
          <div class="rv-eyebrow mono">{eyebrow or 'WESTERN CAPE'}</div>
          <h2 class="display" id="pvTitle" tabindex="-1">{esc(f['name'])}</h2>
          <p class="pv-lede">{lede}</p>
          {f'<div class="pv-people"><span class="k mono">PEOPLE</span>{esc(f["people"])}</div>' if f.get('people') else ''}
          <div class="pv-flags">{flags}</div>
          <div class="pv-stats mono">
            <div><span class="v{'' if f['founded'] else ' dim'}">{esc(f['founded']) if f['founded'] else '—'}</span><span class="k">FOUNDED</span></div>
            <div><span class="v g">{n_aw}</span><span class="k">HONOURS VERIFIED</span></div>
            <div><span class="v">{len(f['varieties'] or [])}</span><span class="k">VARIETIES ON RECORD</span></div>
            <div><span class="v">{len(wines)}</span><span class="k">WINES ON RECORD</span></div>
          </div>
        </div>
        {f'<div class="pv-map" id="pvMap"><canvas id="pvCanvas" role="img" aria-label="Tactical map around {esc(f["name"])}"></canvas><span class="corner tl"></span><span class="corner br"></span><div class="hud mono">TACTICAL · {esc(f["name"].upper())}<br><b>{f["lat"]:.4f}, {f["lng"]:.4f}</b><br>{len(neigh)} NEIGHBOURS WITHIN VIEW</div><div class="scale mono"><i style="width:53px"></i><span>≈ 1 KM</span></div></div>' if located else ''}
      </div>
      <section class="rv-block pv-three">
        <div><h3 class="mono"><span class="h3l">VISIT</span></h3>{visit}</div>
        <div><h3 class="mono"><span class="h3l">THE VINEYARD</span></h3>{vineyard}</div>
        <div><h3 class="mono"><span class="h3l">NEIGHBOURS</span></h3>{neigh_html}</div>
      </section>
      <section class="rv-block pv-wines-block">
        <h3 class="mono"><span class="h3l">THE WINES</span><span>{len(wines)} ON RECORD</span></h3>
        {ranges_html}
        {('<div class="pv-wines">' + ''.join(wine_card(w) for w in wines) + '</div>') if wines else '<p class="pv-prov">No wines are named on this record yet.</p>'}
        <div class="pv-soon mono">{wines_src}</div>
      </section>
      <section class="rv-block pv-ledger">
        <h3 class="mono"><span class="h3l">THE HONOURS LEDGER</span><span>{n_aw} VERIFIED · EACH WITH ITS SOURCE{f' · {pc} UNDER REVIEW, NOT SHOWN' if pc else ''}</span></h3>
        {ledger}
      </section>
      <section class="rv-block rv-two pv-prov-block">
        <div>
          <h3 class="mono"><span class="h3l">PROVENANCE</span></h3>
          <p class="pv-prov"><b>Record</b> · {esc(region)}{', ' + esc(f['ward']) + ' ward' if f['ward'] else ''} · gathered {esc(R['collected'] or '—')}.<br>
          <b>Position</b> · {f'published, confidence {esc(str(f["geoConfidence"] or "—"))}' if located else 'none published by the producer or an association; the atlas does not invent one'}.<br>
          <b>Honours</b> · {f'research complete · {n_aw} verified, each cited to the page that announced it' if f['awardsCollected'] else 'research not yet reached'}{f' · {pc} claim{"" if pc == 1 else "s"} awaiting a publishable source' if pc else ''}.<br>
          <b>Wines</b> · {wines_prov}.<br>
          <b>Contact</b> · {'held on file, never republished' if f['contactHeld'] else 'not held'}.</p>
        </div>
        <div>
          <h3 class="mono"><span class="h3l">CORRECTIONS</span></h3>
          <p class="pv-prov">If you make wine here and this record is wrong, incomplete or out of date, write to <a class="lv-link" href="mailto:capewineatlas@gmail.com">capewineatlas@gmail.com</a>. A correction is made against a source and the record then cites it.</p>
        </div>
      </section>
      <div class="rv-foot mono"><span>THE ATLAS RECORD · {EDITION}</span><span>DATA UNDER ODbL 1.0 · CONTAINS INFORMATION FROM OPENSTREETMAP, © OPENSTREETMAP CONTRIBUTORS</span><span>{esc(f['name'].upper())} · {esc(region.upper())}</span><span>RECORDS GATHERED {esc(R['collected'] or '—')}</span></div>'''

# ---------------------------------------------------------------- structured data (what a search engine reads; nothing here that the page does not already say)
def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'
def ld_breadcrumb(items):
    return {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}
def ld_home(desc):
    return ld({'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', 'name': 'Cape Wine Atlas', 'url': BASE_URL, 'description': desc},
        {'@type': 'Dataset', 'name': f'Cape Wine Atlas — {EDITION.title()}', 'description': desc, 'url': BASE_URL, 'license': 'https://opendatacommons.org/licenses/odbl/1-0/',
         'creator': {'@type': 'Organization', 'name': 'the Cape Wine Atlas project, maintained by MDRF'}, 'spatialCoverage': 'Western Cape, South Africa', 'dateModified': stats['built'],
         'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'application/json', 'contentUrl': BASE_URL + 'data/index.json'}]}]})
def ld_region(R):
    url = f'{BASE_URL}region/{R["key"]}/'
    return ld({'@context': 'https://schema.org', '@graph': [
        ld_breadcrumb([('Cape Wine Atlas', BASE_URL), (R['name'], url)]),
        {'@type': 'ItemList', 'name': ('Wine producers on record in the Western Cape with no fixed place' if R['nochart'] else f'Wine producers on record in {R["name"]}'), 'url': url, 'numberOfItems': len(R['farms']),
         'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': f['name'], 'url': f'{BASE_URL}producer/{f["id"]}/'} for i, f in enumerate(R['farms'])]}]})
DESC_MAX = 300
ACCESS_SENT = {'walk_in': 'open for walk-in tasting', 'appointment': 'tasting by appointment',
               'scheduled': 'tasting on announced dates', 'closed_temporarily': 'tasting closed for now',
               'closed_permanently': 'tasting permanently closed', 'none': 'no tasting room'}

def clip(text, room):
    """Cut on a word boundary and say nothing that was half-said. Never mid-word."""
    text = ' '.join((text or '').split())
    if len(text) <= room: return text
    cut = text[:room].rsplit(' ', 1)[0].rstrip(' ,;:—-')
    return cut + '…' if cut else ''

def meta_desc(R, f, shown=4):
    """Factual, built from what the record holds, in a fixed order. No marketing language.

    Long names and long variety lists overflow what a search engine shows, so the VARIETY LIST is
    the part that shortens — one cultivar at a time, always saying how many were not listed.
    Nothing else is rephrased to fit, and a count of nothing is left unsaid rather than printed
    as a zero.
    """
    if R['nochart']:
        s = f"{f['name']} — wine producer in the Western Cape; the atlas has not established where its premises are."
    else:
        place = f['ward'] or R['name']
        s = f"{f['name']} — wine producer in {place}, Western Cape."
    acc = ACCESS_SENT.get(f.get('access'))
    if acc: s += f' Visit: {acc}.'
    n_aw = len(f['awards'])
    if n_aw: s += f" {n_aw} honour{'' if n_aw == 1 else 's'} verified against {'its source' if n_aw == 1 else 'their sources'}."
    n_w = len(wines_of(f))
    if n_w: s += f" {n_w} wine{'' if n_w == 1 else 's'} on record."
    v = f['varieties'] or []
    if v:
        n = max(min(shown, len(v)), 1)
        s += ' Varieties on record: ' + ', '.join(v[:n]) + ('.' if len(v) <= n else f' and {len(v) - n} more.')
    if len(s) > DESC_MAX and shown > 1:
        return meta_desc(R, f, shown - 1)
    if f['history'] and len(s) < DESC_MAX - 40:
        tail = clip(f['history'], DESC_MAX - len(s) - 1)
        if tail: s += ' ' + tail
    return clip(s, DESC_MAX)

def ld_tours():
    url = BASE_URL + 'tours/'
    items = [o for g in TOUR_GROUPS for o in g['ops'] if not o['event']]
    return ld({'@context': 'https://schema.org', '@graph': [ld_breadcrumb([('Cape Wine Atlas', BASE_URL), ('Tour operators', url)]),
        {'@type': 'ItemList', 'name': 'Tour operators serving the Cape winelands, as listed in the Cape Wine Atlas', 'url': url, 'numberOfItems': len(items),
         'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': o['name'], **({'url': o['web']} if o['web'] else {})} for i, o in enumerate(items)]}]})
def ld_producer(R, f):
    """Machine-readable claims a reader could check. Nothing here is inferred or filled in.

    Winery descends from Place, so emitting it asserts that the producer has premises of its own.
    That holds where the record establishes a venue of its own and nowhere else: a producer that
    buys in fruit and makes wine in somebody else's cellar is a producer and is not a place, and
    saying otherwise in machine-readable form is the same kind of error as inventing an address.
    Organization says what is actually known — this is a producer, this is its name, this is its
    site, this is the area it belongs to — and claims no place.

    A postal address is never emitted. The atlas does not hold street addresses for these records,
    and a region name dressed up as addressLocality is a fact nobody sourced.
    """
    url = f'{BASE_URL}producer/{f["id"]}/'
    own = f.get('venue') == 'own'
    w = {'@type': 'Winery' if own else 'Organization', 'name': f['name'], 'url': url, 'mainEntityOfPage': url}
    if f['web']: w['sameAs'] = [f['web']]
    # A coordinate is a property of a place. It goes on the Winery branch only, and only on a pin
    # the atlas calls clean — never on a pin that marks somebody else's tasting venue.
    if own and f['lat'] is not None and f.get('coordsClean'):
        w['geo'] = {'@type': 'GeoCoordinates', 'latitude': round(f['lat'], 6), 'longitude': round(f['lng'], 6)}
    area = 'Western Cape' if R['nochart'] else (f['ward'] or R['name'])
    if area: w['areaServed'] = {'@type': 'AdministrativeArea', 'name': area}
    if f['varieties']:
        # These are the cultivars the producer works with — grown, bought in, or vinified under
        # contract. knowsAbout says that and claims nothing about who planted the vines.
        w['knowsAbout'] = list(f['varieties'])
    if f['founded']: w['foundingDate'] = str(f['founded'])
    if f['history']: w['description'] = f['history']
    w['containedInPlace' if own else 'location'] = {'@type': 'Place', 'name': 'Western Cape' if R['nochart'] else R['name'], 'url': f'{BASE_URL}region/{R["key"]}/'}
    return ld({'@context': 'https://schema.org', '@graph': [ld_breadcrumb([('Cape Wine Atlas', BASE_URL), (R['name'], f'{BASE_URL}region/{R["key"]}/'), (f['name'], url)]), w]})

# ---------------------------------------------------------------- templating
template = (SRC / 'index.template.html').read_text(encoding='utf-8')
site_css = (SRC / 'site.css').read_text(encoding='utf-8')
app_js = (SRC / 'app.js').read_text(encoding='utf-8')
S = stats
COMMON = {
    'ROOT': ROOT, 'BUILT': S['built'], 'EDITION': EDITION, 'EDITION_LOWER': EDITION.lower(),
    'FARMS': S['farms'], 'REGIONS': S['regions'], 'ROUTES': S['routes'], 'TOURS': S['tours'],
    'AWARDS': S['verifiedAwards'], 'PENDING': S['pendingClaims'], 'WITHHELD': S['withheld'], 'WINES': (S.get('wines') or {}).get('brands') or 0,
    'OG_IMAGE': BASE_URL + 'assets/img/og.jpg',
    'REGION_INDEX': region_index_html(),
    'TOURS_URL': ROOT + 'tours/',
}
PV_BLANK = {'PRODUCER': '', 'PV_OPEN': '', 'PV_CRUMB': '', 'PV_PRERENDER': '', 'JSONLD': '', 'PAGE': '', 'TV_OPEN': '', 'TV_PRERENDER': '', 'TV_CRUMB': ''}
def render(page):
    vals = {**COMMON, **PV_BLANK, **page}
    out = template
    for k, v in vals.items(): out = out.replace('{{' + k + '}}', str(v))
    leftover = re.findall(r'\{\{[A-Z_]+\}\}', out)
    if leftover: sys.exit(f'unfilled placeholders: {sorted(set(leftover))}')
    return out

site_desc = f"An open record of South Africa’s wine farms — {S['farms']} producers across {S['regions']} regions, {S['verifiedAwards']} honours and {(S.get('wines') or {}).get('brands') or 0} wines on record, every entry traceable to its source. {EDITION.title()}."

# ---------------------------------------------------------------- write the site
if OUT.exists(): shutil.rmtree(OUT)
(OUT / 'assets' / 'img').mkdir(parents=True); (OUT / 'assets' / 'fonts').mkdir(parents=True)
(OUT / 'data' / 'regions').mkdir(parents=True)
(OUT / 'assets' / 'site.css').write_text(site_css.replace('{{ROOT}}', ROOT), encoding='utf-8')
(OUT / 'assets' / 'app.js').write_text(app_js, encoding='utf-8')
for f in (SRC / 'assets' / 'fonts').iterdir(): shutil.copy(f, OUT / 'assets' / 'fonts' / f.name)
for f in (SRC / 'assets' / 'img').iterdir(): shutil.copy(f, OUT / 'assets' / 'img' / f.name)
(OUT / 'data' / 'index.json').write_text(json.dumps(index, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
(OUT / 'data' / 'search.json').write_text(json.dumps(search, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
for key, R in regions.items():
    (OUT / 'data' / 'regions' / f'{key}.json').write_text(json.dumps(R, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

(OUT / 'index.html').write_text(render({'TITLE': 'Cape Wine Atlas', 'DESCRIPTION': site_desc, 'CANONICAL': BASE_URL, 'REGION': '', 'RV_OPEN': '', 'CRUMB': '', 'PRERENDER': '', 'JSONLD': ld_home(site_desc)}), encoding='utf-8')
urls = [(BASE_URL, '1.0')]
(OUT / 'tours').mkdir(parents=True)
(OUT / 'data' / 'tours.json').write_text(json.dumps(TOURS_DATA, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
(OUT / 'tours' / 'index.html').write_text(render({'TITLE': 'Tour operators — Cape Wine Atlas',
    'DESCRIPTION': f"{N_OPS} tour operators publicly offering tours of the Cape winelands — trams, shuttles, cycling tours, private guides — listed by the area they serve, each with its source. Listed, not endorsed.",
    'CANONICAL': BASE_URL + 'tours/', 'REGION': '', 'RV_OPEN': '', 'CRUMB': '', 'PRERENDER': '', 'JSONLD': ld_tours(),
    'PAGE': 'tours', 'TV_OPEN': 'open', 'TV_PRERENDER': prerender_tours(), 'TV_CRUMB': tours_crumb()}), encoding='utf-8')
urls.append((BASE_URL + 'tours/', '0.8'))
n_pv = 0
for key, R in regions.items():
    d = OUT / 'region' / key; d.mkdir(parents=True)
    head = f"{R['name']} — {len(R['farms'])} wine producers on record, {sum(len(f['awards']) for f in R['farms'])} honours verified against their sources."
    desc = clip(head + ' ' + (R['lede'] or ''), DESC_MAX)
    (d / 'index.html').write_text(render({'TITLE': f"{R['name']} — Cape Wine Atlas", 'DESCRIPTION': desc, 'CANONICAL': f'{BASE_URL}region/{key}/', 'REGION': key, 'RV_OPEN': 'open', 'CRUMB': crumb_html(R), 'PRERENDER': prerender(R), 'JSONLD': ld_region(R)}), encoding='utf-8')
    urls.append((f'{BASE_URL}region/{key}/', '0.8'))
    # one page per producer: the region opens beneath it on load, so BACK lands on the region it came from
    for f in R['farms']:
        pd = OUT / 'producer' / f['id']; pd.mkdir(parents=True)
        pdesc = meta_desc(R, f)
        (pd / 'index.html').write_text(render({'TITLE': f"{f['name']} — {'Western Cape · no fixed place' if R['nochart'] else R['name']} · Cape Wine Atlas", 'DESCRIPTION': pdesc, 'CANONICAL': f'{BASE_URL}producer/{f["id"]}/', 'REGION': key, 'RV_OPEN': '', 'CRUMB': crumb_html(R), 'PRERENDER': '',
                                                'PRODUCER': f['id'], 'PV_OPEN': 'open', 'PV_CRUMB': pv_crumb_html(R, f), 'PV_PRERENDER': prerender_producer(R, f), 'JSONLD': ld_producer(R, f)}), encoding='utf-8')
        urls.append((f'{BASE_URL}producer/{f["id"]}/', '0.7')); n_pv += 1

# No modification date. The atlas knows when a record was last READ, not when its content last
# changed, and one build date stamped across every URL is a freshness claim nothing supports —
# crawlers discount a lastmod they learn to distrust, so the honest sitemap omits it.
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{u}</loc><changefreq>monthly</changefreq><priority>{p}</priority></url>\n' for u, p in urls) + '</urlset>\n', encoding='utf-8')
(OUT / 'robots.txt').write_text(
    f'''# Cape Wine Atlas — {BASE_URL}
# The producer and region pages are the public record. The data files under /data/ are published
# for reuse under the Open Database Licence, not as pages to index — they are the same facts in a
# form meant for machines, and indexing them would compete with the pages that explain them.
# The one exception is the producer list, which the home page names as this atlas's download: a
# dataset whose download cannot be fetched is a dataset nobody can check.
User-agent: *
Allow: /
Allow: /data/index.json
Disallow: /data/

Sitemap: {BASE_URL}sitemap.xml
''', encoding='utf-8')
if DOMAIN and ROOT == '/': (OUT / 'CNAME').write_text(DOMAIN + '\n', encoding='utf-8')
(OUT / '.nojekyll').write_text('', encoding='utf-8')
(OUT / '404.html').write_text(f'''<!DOCTYPE html><html lang="en" data-root="{ROOT}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Not on the record — Cape Wine Atlas</title><link rel="stylesheet" href="{ROOT}assets/site.css"><meta name="robots" content="noindex"></head>
<body style="background:#0a0a0a;color:#eaeaea;min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:40px">
<div class="frame"><i class="tl"></i><i class="tr"></i><i class="bl"></i><i class="br"></i></div>
<div><div class="mono" style="font-size:10px;letter-spacing:.2em;color:#c9a227;margin-bottom:18px">// SIGNAL LOST</div>
<h1 class="display" style="font-size:clamp(28px,6vw,72px);line-height:1;margin-bottom:18px">Not on<br>the record</h1>
<p style="color:#8a8a8a;max-width:420px;margin:0 auto 26px;line-height:1.7">There is no page at this address. The atlas may have moved it, or it was never here.</p>
<a class="mono" href="{ROOT}" style="color:#eaeaea;text-decoration:none;border:1px solid rgba(234,234,234,.18);padding:10px 16px;font-size:10px;letter-spacing:.18em">◂ BACK TO THE ATLAS</a></div>
</body></html>''', encoding='utf-8')

# ---------------------------------------------------------------- the archival single file
def data_uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(Path(path).read_bytes()).decode()
css_inline = site_css
for name in ('orbitron-900', 'jetbrains-mono-400', 'jetbrains-mono-700'):
    css_inline = css_inline.replace(f'url({{{{ROOT}}}}assets/fonts/{name}.woff2)', f'url({data_uri(SRC / "assets" / "fonts" / (name + ".woff2"), "font/woff2")})')
assets_inline = {f'img/{n}': data_uri(SRC / 'assets' / 'img' / n, 'image/jpeg') for n in ('hero-tex.jpg', 'map-tex.jpg', 'footer-halftone.jpg')}
single = render({'TITLE': 'Cape Wine Atlas', 'DESCRIPTION': site_desc, 'CANONICAL': BASE_URL, 'REGION': '', 'RV_OPEN': '', 'CRUMB': '', 'PRERENDER': ''})
single = single.replace(f'<link rel="stylesheet" href="{ROOT}assets/site.css">', '<style>' + css_inline + '</style>')
single = single.replace(f'<script src="{ROOT}assets/app.js"></script>',
    '<script>window.__CWA = ' + json.dumps({'index': index, 'regions': regions, 'search': search, 'assets': assets_inline}, ensure_ascii=False) + ';</script>\n<script>' + app_js + '</script>')
single = single.replace('<html lang="en" data-root="/" data-region="" data-producer="">', '<html lang="en" data-root="./" data-region="" data-producer="">')
single_path = HERE / 'cape-wine-atlas.html'
single_path.write_text(single, encoding='utf-8')

n_files = sum(1 for _ in OUT.rglob('*') if _.is_file())
print(f"built: {S['farms']} farms · {S['regions']} regions · {n_pv} producer pages · {S['verifiedAwards']} honours · {EDITION} → {OUT} ({n_files} files) + {single_path.name} ({single_path.stat().st_size//1024} KB)")
