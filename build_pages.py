#!/usr/bin/env python3
"""
build_pages.py — build the Cape Wine Atlas site from the atlas record.

    python3 build_pages.py <atlas-project-folder> [--root /] [--domain capewineatlas.co.za]
                                                  [--out docs] [--allow-preview]

Reads <project>/dist/atlas.json and <project>/data/regions/*.json, applies the
publication gate, and writes a static site to <out>/ (GitHub Pages serves it):

    <out>/index.html                   the atlas
    <out>/region/<key>/index.html      one pre-rendered page per region, with a real URL
    <out>/data/index.json              region index, statistics, map geometry
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
for r in atlas['regions']:
    m = r['meta']; name = m.get('name') or m.get('wo_district'); key = SLUG[name]
    fs = [f for f in r['farms'] if f['lat'] is not None]
    if name in SHORT: short, lng, lat = SHORT[name]
    else: short = name; lat = sum(f['lat'] for f in fs)/len(fs); lng = sum(f['lng'] for f in fs)/len(fs)
    if fs and name in SHORT and name != "Lambert's Bay":
        lat = sum(f['lat'] for f in fs)/len(fs); lng = sum(f['lng'] for f in fs)/len(fs)
    if short == 'Constantia': lng, lat = 18.42, -34.04
    farms = []
    for f in r['farms']:
        rec = {k: f.get(k) for k in ('id','name','ward','lat','lng','geoConfidence','founded','hours','venue','access','varieties','signatureWines','web','routeMember','oldVineFlag','awardsCollected','pendingClaims','locality','contactHeld')}
        rec['awards'] = [{k: aw.get(k) for k in ('body','year','wine','award','sourceUrl','sourceName')} | {'corr': bool(aw.get('_corroborated'))} for aw in f['awards']]
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
    n_f = len(r['farms']); where = f"the {district or short} district of the {m.get('wo_region') or 'Cape'}"
    fallback = (f"No producer is yet on record in {where}." if n_f == 0 else f"One producer on record in {where}." if n_f == 1 else f"{n_f} producers on record in {where}.")
    lede = terroir or (rts[0]['blurb'] if rts else '') or fallback
    regions[key] = {'key': key, 'name': short, 'full': name, 'woRegion': m.get('wo_region') or '—', 'district': district or '—', 'ward': ward,
                    'withheld': withheld, 'status': m['status'], 'collected': m.get('collected'), 'expected': intornull(m.get('producer_count_expected')),
                    'terroir': terroir, 'lede': lede, 'routes': rts, 'tours': tours, 'farms': farms}
    idx.append({'key': key, 'name': short, 'district': district or '—', 'woRegion': m.get('wo_region') or '—', 'farms': len(r['farms']), 'pinned': len(fs),
                'awards': sum(len(f['awards']) for f in r['farms']), 'pending': sum(f['pendingClaims'] or 0 for f in r['farms']),
                'researched': sum(1 for f in r['farms'] if f['awardsCollected']), 'status': m['status'], 'lat': round(lat, 4), 'lng': round(lng, 4), 'withheld': withheld})
idx.sort(key=lambda x: x['name'])
stats = dict(atlas['stats'])
stats.update({'regions': len(atlas['regions']), 'routes': len(atlas['routes']), 'tours': len(atlas['tourOperators']), 'built': atlas['built'], 'buildMode': mode,
              'competitions': [{'body': x['body'], 'year': x['year'], 'records': x['records']} for x in atlas['competitions']],
              'tourDisclaimer': atlas['tourOperatorDisclaimer'], 'withheld': atlas.get('withheld', {}).get('total', 0),
              'industry': {'cellars': atlas.get('industry', {}).get('cellarsCrushing2024', {}).get('total'), 'source': 'SAWIS, SA Wine Industry Statistics 2024'}})
LON0, LON1, LAT0, LAT1 = 17.6, 23.75, 31.25, 35.05        # the Western Cape chart's bounding box
marks = {r['key']: [(r['lng']-LON0)/(LON1-LON0), (-r['lat']-LAT0)/(LAT1-LAT0)] for r in idx}
geo = json.loads((SRC / 'geo.json').read_text())
index = {'idx': idx, 'stats': stats, 'geo': geo, 'marks': marks}

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
    return '<b>CAPE WINE ATLAS</b>' + ''.join(f'<span>/</span>{x}' for x in chain) + f'<span>/</span><b>{esc((ward or R["name"]).upper())}{" WARD" if ward else ""}</b>'

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
            (f'WARD · {esc(f["ward"].upper())}' if (f['ward'] and (not R['ward'] or f['ward'] != R['ward'])) else (esc(f['locality'].split('(')[0].split('—')[0].strip().upper()) if (f['locality'] and not f['ward']) else None)),
            'ROUTE MEMBER' if f['routeMember'] == 'yes' else None,
            f'LOCATION · {str(f["geoConfidence"] or "").upper()}' if f['lat'] is not None else 'LOCATION NOT YET RESOLVED',
            '<span class="gold">OLD VINES</span>' if f['oldVineFlag'] else None] if x]
        led = ''.join(
            f'<div class="aw"><span class="y">{esc(a["year"]) if a["year"] is not None else "—"}</span><span><b>{esc(a["body"])}</b> — {esc(a["award"])}<br><span class="w">{esc(a["wine"])}</span>'
            + (f'<br><a class="src mono" href="{esc(a["sourceUrl"])}" target="_blank" rel="noopener" title="{esc(a.get("sourceName") or "")}">SOURCE · {esc(((a.get("sourceName") if a.get("sourceName") and len(a["sourceName"]) <= 32 else (a["sourceName"][:30].rstrip(" —–-") + "…") if a.get("sourceName") else host(a["sourceUrl"]))).upper())}</a>' if a.get('sourceUrl') else '')
            + ('<span class="corr mono">✓✓ CORROBORATED</span>' if a.get('corr') else '') + '</span></div>' for a in f['awards'])
        flags = ''.join([
            '<span class="flag warn mono">AWARDS NOT YET RESEARCHED</span>' if not f['awardsCollected'] else '',
            '<span class="flag dim mono">NO VERIFIED HONOUR ON FILE</span>' if (f['awardsCollected'] and not f['awards'] and not f['pendingClaims']) else '',
            f'<span class="flag gold mono">{f["pendingClaims"]} CLAIM{"S" if f["pendingClaims"] > 1 else ""} UNDER REVIEW</span>' if f['pendingClaims'] else ''])
        contact = ''.join([
            f'<a href="{esc(f["web"])}" target="_blank" rel="noopener">{esc(host(f["web"]))}</a>' if f['web'] else '',
            f'<span>{esc(str(f["contactHeld"]).upper())} ON FILE · NOT REPUBLISHED</span>' if f['contactHeld'] else ''])
        recs.append(f'''<article class="rec" id="rec-{f['id']}" data-id="{f['id']}">
        <div class="rec-bar mono"><span>$ record.{f['id']}</span><span class="term-dots"><span></span><span></span><span></span></span></div>
        <div class="rec-body">
          <div class="rec-name display">{esc(f['name'])}</div>
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
    tours = ''.join(tour_html(t) for t in R['tours']) or '<div class="tour"><span class="t mono">NO TOUR OPERATOR IS YET LISTED FOR THIS ROUTE</span></div>'
    comps = ' · '.join(f'{esc(c["body"])} {c["year"]}' for c in S['competitions'])
    return f'''
      <header class="rv-head">
        <div>
          <div class="rv-eyebrow mono">{eyebrow}</div>
          <h2 class="display">{esc(R['name'])}</h2>
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
        <div class="rv-map" id="rvMap"><canvas id="miniCanvas"></canvas><span class="corner tl"></span><span class="corner br"></span>
          <div class="hud mono">TACTICAL · {esc(R['name'].upper())}<br><b>{pinned}/{len(farms)}</b> POSITIONS LOCATED</div>
          <div class="scale mono"><i style="width:60px"></i><span>≈ 1 KM</span></div></div>
      </header>
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
      <footer class="rv-foot mono"><span>THE ATLAS RECORD · {EDITION}</span><span>DATA UNDER ODbL 1.0 · CONTAINS INFORMATION FROM OPENSTREETMAP, © OPENSTREETMAP CONTRIBUTORS</span><span>{' · '.join([*chain, *([esc(ward.upper())] if ward else [])]) or esc(R['name'].upper())}</span><span>RECORDS GATHERED {esc(R['collected'] or '—')}</span><span>ACROSS THE ATLAS · {S['farms']} FARMS · {S['regions']} REGIONS · {S['verifiedAwards']} HONOURS VERIFIED</span></footer>'''

# ---------------------------------------------------------------- templating
template = (SRC / 'index.template.html').read_text(encoding='utf-8')
site_css = (SRC / 'site.css').read_text(encoding='utf-8')
app_js = (SRC / 'app.js').read_text(encoding='utf-8')
S = stats
COMMON = {
    'ROOT': ROOT, 'BUILT': S['built'], 'EDITION': EDITION, 'EDITION_LOWER': EDITION.lower(),
    'FARMS': S['farms'], 'REGIONS': S['regions'], 'ROUTES': S['routes'], 'TOURS': S['tours'],
    'AWARDS': S['verifiedAwards'], 'PENDING': S['pendingClaims'], 'WITHHELD': S['withheld'],
    'OG_IMAGE': BASE_URL + 'assets/img/og.jpg',
}
def render(page):
    vals = {**COMMON, **page}
    out = template
    for k, v in vals.items(): out = out.replace('{{' + k + '}}', str(v))
    leftover = re.findall(r'\{\{[A-Z_]+\}\}', out)
    if leftover: sys.exit(f'unfilled placeholders: {sorted(set(leftover))}')
    return out

site_desc = f"An open record of South Africa’s wine farms — {S['farms']} producers across {S['regions']} regions, every entry traceable to its source. {EDITION.title()}."

# ---------------------------------------------------------------- write the site
if OUT.exists(): shutil.rmtree(OUT)
(OUT / 'assets' / 'img').mkdir(parents=True); (OUT / 'assets' / 'fonts').mkdir(parents=True)
(OUT / 'data' / 'regions').mkdir(parents=True)
(OUT / 'assets' / 'site.css').write_text(site_css.replace('{{ROOT}}', ROOT), encoding='utf-8')
(OUT / 'assets' / 'app.js').write_text(app_js, encoding='utf-8')
for f in (SRC / 'assets' / 'fonts').iterdir(): shutil.copy(f, OUT / 'assets' / 'fonts' / f.name)
for f in (SRC / 'assets' / 'img').iterdir(): shutil.copy(f, OUT / 'assets' / 'img' / f.name)
(OUT / 'data' / 'index.json').write_text(json.dumps(index, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
for key, R in regions.items():
    (OUT / 'data' / 'regions' / f'{key}.json').write_text(json.dumps(R, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

(OUT / 'index.html').write_text(render({'TITLE': 'Cape Wine Atlas', 'DESCRIPTION': site_desc, 'CANONICAL': BASE_URL, 'REGION': '', 'RV_OPEN': '', 'CRUMB': '', 'PRERENDER': ''}), encoding='utf-8')
urls = [BASE_URL]
for key, R in regions.items():
    d = OUT / 'region' / key; d.mkdir(parents=True)
    desc = f"{R['name']} — {len(R['farms'])} wine producers on record, {sum(len(f['awards']) for f in R['farms'])} honours verified against their sources. {R['lede'][:150]}"
    (d / 'index.html').write_text(render({'TITLE': f"{R['name']} — Cape Wine Atlas", 'DESCRIPTION': desc, 'CANONICAL': f'{BASE_URL}region/{key}/', 'REGION': key, 'RV_OPEN': 'open', 'CRUMB': crumb_html(R), 'PRERENDER': prerender(R)}), encoding='utf-8')
    urls.append(f'{BASE_URL}region/{key}/')

(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{u}</loc><lastmod>{S["built"]}</lastmod></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')
(OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n', encoding='utf-8')
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
    '<script>window.__CWA = ' + json.dumps({'index': index, 'regions': regions, 'assets': assets_inline}, ensure_ascii=False) + ';</script>\n<script>' + app_js + '</script>')
single = single.replace('<html lang="en" data-root="/" data-region="">', '<html lang="en" data-root="./" data-region="">')
single_path = HERE / 'cape-wine-atlas.html'
single_path.write_text(single, encoding='utf-8')

n_files = sum(1 for _ in OUT.rglob('*') if _.is_file())
print(f"built: {S['farms']} farms · {S['regions']} regions · {S['verifiedAwards']} honours · {EDITION} → {OUT} ({n_files} files) + {single_path.name} ({single_path.stat().st_size//1024} KB)")
