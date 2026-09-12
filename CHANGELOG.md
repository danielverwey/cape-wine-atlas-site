# Changelog — Cape Wine Atlas production site

Newest first. Each entry is one sync to `production site/`.

## v0.15.0 — 2026-09-12 — September 2026 edition
`versions/cape-wine-atlas_2026-09-12_v0.15.0_september-2026-edition.html`

The producer record, from the prototype reviewed on 12 September: a third level, chart → region → producer, and with it the first pages a search engine can index one producer at a time.
- **Producer pages.** Every producer has its own address, `/producer/<id>/`, pre-rendered by the build (644 pages, about 75 KB each). At the top: the eyebrow (Wine of Origin chain, ward, locality), the name, the history line, PEOPLE, the flags (tasting access, route member, old vines, location confidence, research status, claims under review), four figures (FOUNDED · HONOURS VERIFIED · VARIETIES ON RECORD · WINES ON RECORD) and, only where the record has a published position, a tactical map about 8 km across with the six nearest producers named. Below, three columns on one horizontal — VISIT (hours, venue, website, contact status, and POSITION when there is none), THE VINEYARD (varieties, signature wines, old vines, founded) and NEIGHBOURS (the six nearest located producers across the whole atlas, so they cross region borders; the region is named when it differs) — then THE WINES (the signature list plus every wine named in an honour, vintages folded together, each card with up to four honours), THE HONOURS LEDGER by year with a source chip on every entry, and PROVENANCE / CORRECTIONS. No position → no map, said plainly instead of drawn.
- **Region cards carry a summary.** Each record card now says "15 HONOURS VERIFIED · Platter's Winery of the Year 2009 · … · and 12 more" (the three highest-ranked honours, trophies before double golds before golds) instead of the full ledger; the flags stay. OPEN THE RECORD ▸ on the card's bar, or the producer's name, opens the page.
- **Ways in.** From a card; from a search hit (a producer or a wine now opens the producer page directly); from a neighbour on another producer's page; or by address. A page opened by address opens its region beneath it, so [ BACK TO STELLENBOSCH ] always has somewhere to go; [ CLOSE ] returns to the chart. Browser back and forward walk the same path; Escape steps back one level.
- **Search engines.** Every page carries structured data: the home page a WebSite and a Dataset (ODbL, creator "the Cape Wine Atlas project, maintained by MDRF"); each region page a breadcrumb trail and an ItemList of its producers; each producer page a breadcrumb trail and a Winery (name, address locality and region, position where published, founding year, website, description, the region it sits in). Titles read "Kanonkop Wine Estate — Stellenbosch · Cape Wine Atlas"; the sitemap lists 676 addresses. The atlas's own JSON now ships a compact producer list (`data/index.json`, 72 KB) so the site can place a neighbour without opening its region.
- **Copy.** A few history lines that had leaked a working note ("… is a coverage statement …") are filtered out by the copy pass. Where a critic's name was recorded in both the body and the award, the ledger says it once.
- Accessibility carried through: the producer view is a modal dialog with the region made inert beneath it, focus lands on the title and returns to the card that opened it, Tab stays inside, Escape closes one level, and the OPEN link is a real link (a modified click opens it in a new tab). Phones: the columns stack, the crumb keeps region / producer, and the buttons shorten to [ BACK ] and ✕.

## v0.14.1 — 2026-09-12 — September 2026 edition
`versions/cape-wine-atlas_2026-09-12_v0.14.1_september-2026-edition.html`

- Hover card on the chart: the status is a phrase, not a figure, so it now sits on its own line under its label instead of being squeezed into the figures column (where it stacked four deep, or, in the first attempt at a fix, stretched the card to 560 px). The card sizes to its text between 340 and 460 px; a region with no district no longer shows a stray dash.

## v0.14.0 — 2026-09-12 — September 2026 edition
`versions/cape-wine-atlas_2026-09-12_v0.14.0_september-2026-edition.html`

Lenses and search, from the prototype reviewed on 11–12 September. Built against the 12 September atlas export (644 producers · 1,326 verified honours · 24 under review · 144 held back).
- **Lenses.** A rail under "Explore the regions" — PRODUCERS · HONOURS · GRAPE · TASTING · AGE · OLD VINES · COVERAGE, with a second row of the twelve most-grown grapes (Shiraz and Syrah counted together). A lens re-weights the markers by its metric (regions with nothing to show drop to the dormant rings), swaps the index's FARMS column for the metric, and turns the hint line into a legend stated the honest way ("308 producers grow it, of 644 with varieties on record"; "24 under review, not counted"). Opening a region while a lens is active carries it inside: pins dim and records hide for producers that don't qualify, with a line saying "LENS · GRAPE · CHENIN BLANC · 42 of 55 producers shown · CLEAR". The lens lives in the address (`#lens=honours`, `#lens=grape:Chenin%20Blanc`) so a view can be shared, and survives closing a region. Figures are counted by the build into `data/index.json`; nothing is inferred.
- **Search.** One box for producers, regions, wards, grapes and signature wines (about 2,000 entries in `data/search.json`, fetched on first use), forgiving of spelling: exact, prefix and substring matches first, then edit distance (a swapped pair counts as one slip) and letter-trigram overlap. When nothing matched exactly the list says so in gold rather than substituting silently. A FIND strip sits above the lens rail on the chart page; a corner control top-left (or `/` from anywhere) drops the same box from the top of any page, region readouts included. A producer or wine opens its region and lands on the record, which glows for a few seconds; a region or ward opens the region; a grape sets the Grape lens.
- **Corner controls.** The emblem returns to the top of the atlas (closing a region or the licence page first); the full-screen box shows its state, gold and pointing inward while active; each carries a tooltip.
- **Layout.** With the strip and rail under the title, the chart moves up and to the right into the ground below the radar; sized to fit at 1920×1080, 1877×870, 1440×900, 1366×768 and 1500×700; the strip, rail and grape row wrap on tablets and phones; the hover card sits below the rail, never over it.
- Accessibility carried through: the rail and grape buttons are toggle buttons with pressed state; both search boxes are labelled comboboxes with keyboard selection; the panel returns focus to where it was opened from; marker names follow the lens ("Stellenbosch — 530 honours").

## v0.13.3 — 2026-09-11 — September 2026 edition
`versions/cape-wine-atlas_2026-09-11_v0.13.3_september-2026-edition.html`

Small screens, refined rather than coarsened.
- **Coast, ridges and roads on every screen.** The dot grid stays exactly as it was (the grain is the look). On top of the finished bake, the coast, ridges and roads are laid as dotted hairlines in the weight of the HUD geometry, fading in only as the dots get small: full on a phone, about half on a 13-inch laptop, nothing on a big screen. On the tactical maps the hairlines dissolve at the frame with the drawing's own edge fade.
- **HUD geometry.** Rings, crosses, boot-screen circles and section frames keep their hairline weight but lift in tone on laptops and tablets (≈24 % white) and phones (≈32 %), so they read as they do on a large monitor.
- "Explore the regions" set flat, in line with every other heading.

## v0.13.2 — 2026-09-11 — September 2026 edition
`versions/cape-wine-atlas_2026-09-11_v0.13.2_september-2026-edition.html`

- Closing a region page returns the reader to the top of the chart, exactly, on every screen size — whether closed with the button, Escape or the browser's back button.
- Closing page: where the halftone reveal darkens the gold around the cursor, the text beneath it turns pale (with a soft shadow) so it stays legible, and returns to ink as the trail fades.

## v0.13.1 — 2026-09-11 — September 2026 edition
`versions/cape-wine-atlas_2026-09-11_v0.13.1_september-2026-edition.html`

Short laptop screens (13-inch, ~700–770 px tall). The chart's size was tied only to the width, so on a wide, short screen it ran off the bottom and the region index ran under the footer line.
- The chart now also scales with the viewport height and sits under the title on any laptop.
- The region index scrolls within itself when 31 rows will not fit, and tightens slightly below 820 px tall.
- No change on phones or on 900 px+ screens.

## v0.13.0 — 2026-09-11 — September 2026 edition
`versions/cape-wine-atlas_2026-09-11_v0.13.0_september-2026-edition.html`

Accessibility pass. No visual change except a gold focus ring for keyboard users.
- **Real controls.** Region markers, index rows and tactical-map pins are buttons with spoken names ("Stellenbosch — 210 producers. Open the region"); the full-screen corner box is a working button; the record filter is labelled. Everything the mouse can do, the keyboard and a screen reader can do.
- **Dialogs that behave.** The region readout and the licence page are modal: focus moves to the title on open, Tab stays inside, Escape closes, and focus returns to the marker, row or link that opened them. The page behind is made inert while a dialog is open.
- **Landmarks and structure.** A skip link to the regions; a `main` landmark; the closing page as `contentinfo`; the boot log announced as it fills; heading levels made consecutive on the licence page; duplicate banner/footer landmarks inside dialogs removed. The hero and tactical maps carry text descriptions; the chart canvas defers to the index beside it.
- **Reduced motion.** When the reader asks for it, the hero stops breathing, the radar and markers hold still, and the typewriter and reveal effects complete instantly.
- **Contrast.** Index counts and the map's attribution line lifted to meet the 4.5:1 minimum.
- Automated audit (axe-core 4.10) reports no violations across boot, home, region and licence states; keyboard walk-through verified in Chromium.
- MIT licence text: copyright holder is now "the Cape Wine Atlas project, maintained by MDRF".

## v0.12.0 — 2026-09-11 — September 2026 edition
`versions/cape-wine-atlas_2026-09-11_v0.12.0_september-2026-edition.html`

Copy pass over every producer record.
- **History lines.** The atlas's note on each producer is a working log — facts about the farm interleaved with how they were found, checked and ruled on. The page used to show its first 210 characters, so 251 lines ended mid-phrase and about 260 carried research vocabulary. `copytext.py` now splits each note into sentences and clauses, drops every clause that speaks about the method (a blocklist of some 300 terms), keeps the leading run of clean clauses, un-shouts capitalised words using the corpus's own casing, and cuts only at a sentence or clause boundary. 473 producers keep a history line (median 131 characters, none truncated); 171 whose note holds nothing publishable yet show none rather than a fragment.
- **People.** A new PEOPLE row on the record, from the atlas's family field, cleaned the same way — 301 producers.
- **Hours** go through the same filter in an hours-aware mode, so "(route member listing)" and the like are gone and nothing is cut with an ellipsis.
- **Region ledes and route paragraphs** cleaned likewise; the fallback sentence handles none/one/many correctly ("No producer is yet on record…").
- **"55 of 48 expected" retired.** The record header now reads "PRODUCER RECORDS 55 ON RECORD · <status>"; the expected count was a planning estimate and confused more than it explained.
- Review sheet of every published line delivered alongside this sync (not part of the repository).

## v0.11.1 — 2026-09-11 — September 2026 edition
`versions/cape-wine-atlas_2026-09-11_v0.11.1_september-2026-edition.html`

Phone review of v0.11.0 (Android, upright): three pages tidied.
- **Boot screen.** Counter top right; the log sits in the lower half with each result on its own gold line (the dotted leaders are dropped on phones); the button is a full-width pill along the bottom, so nothing overlaps.
- **Hero.** A phone held upright was cropping the picture to a third. It is now fitted a little wider than the screen — stadium and mountain both kept — with fewer, never finer, dots. Landscape and desktop unchanged.
- **Closing page.** Contribute block centred on the same line as Provenance; the stamp wraps naturally.

## v0.11.0 — 2026-09-11 — September 2026 edition
`versions/cape-wine-atlas_2026-09-11_v0.11.0_september-2026-edition.html`

Launch items 4 and 5 closed — Safari and hand-held screens. Site live at capewineatlas.co.za since v0.10.0.
- **Safari.** WebKit has never enabled canvas filters (every iPhone and iPad, Mac Safari included), so the brightness/contrast and bloom passes in the hero, chart and closing-page bakes now take a pixel path where the filter API is absent: a tone lookup for brightness and contrast, and a successive-halving downscale with a smooth upscale for the glow. Same picture, one-time cost at bake; verified against Chromium with the filter API removed. `-webkit-backdrop-filter` added for the corner boxes.
- **Phones and small tablets.** One-column composition below 900 px for the chart (title, chart scaled to the width, the full region index beneath it) and below 760 px for the rest (hero, terminal window, closing page); region readout and licence page re-stacked below 640 px (single column of records, two-column stats, square tactical map, full-width filter). Nothing changes above those widths.
- **Marker selection.** A press on the chart now opens the marker nearest the finger or pointer, measured on screen after the 3-D projection, so the dense Stellenbosch–Cape Town cluster and a phone-sized chart open the region you aimed at. The chart hint reads "select" rather than "hover … click".
- `build_pages.py` accepts `--out docs` as well as `--out=docs` (the bare form previously wrote to a folder named `True`).
- Rebuilt against the same 10 September atlas build (gate: 644 records, 0 contact keys, 0 restricted, public).

## v0.10.0 — 2026-09-11 — September 2026 edition
`versions/cape-wine-atlas_2026-09-11_v0.10.0_september-2026-edition.html`

Launch items 2 and 3 closed — the page is now a site, built for GitHub Pages at capewineatlas.co.za.
- **Taken apart.** `src/` holds the template, script, stylesheet, map geometry and assets; `build_pages.py` builds `docs/` from them plus the atlas record. Typefaces and textures are files; each region's records are a separate file fetched only when that region is opened. A first visit is ~560 KB instead of 1.5 MB.
- **Addresses.** Every region has its own URL (`/region/<key>/`), pre-rendered for search engines and readable without script; opening a region updates the address, the back button closes it, and arriving on a region address opens it directly without the boot sequence. The licence page answers to `#licence`.
- **Page metadata:** titles, descriptions, canonical addresses, a share image (`og.jpg`), `sitemap.xml` with all 32 addresses, `robots.txt`, `CNAME`, `.nojekyll`, and a "Not on the record" 404 page in the house style.
- **One build, one gate.** `build_pages.py` carries the publication gate and also writes the archival single file, so `scripts/refresh_terroir_grid.py` is now a stub pointing at it.
- Built against the atlas's first `buildMode: public` build (gate: 644 records, 0 contact keys, 0 restricted, public).
- `SETUP-GITHUB-PAGES.md` — repository, Pages, DNS records for the domain, and the publish routine.

## v0.9.0 — 2026-09-11 — September 2026 edition
`versions/cape-wine-atlas_2026-09-11_v0.9.0_september-2026-edition.html`

First sync of the production tree. Carries the 10 September atlas build (644 producers · 31 regions · 1,133 verified honours · 144 records held back).

Launch item 1 closed:
- "Preview edition" retired everywhere on the page in favour of the dated edition stamp (derived from the build date).
- Held-back wording softened ("144 further records held back until they meet the publication standard"); every per-record and per-region honesty flag kept.
- Licence & Credits page added (footer link, `#licence`): licensor "the Cape Wine Atlas project, maintained by MDRF"; data ODbL 1.0 with the OpenStreetMap notice, Wikidata (CC0) and SAWIS; prose CC BY 4.0; code MIT; typefaces OFL; Neon Grid acknowledgement; ChatGPT-generated hero image statement; hand-drawn maps; corrections & removal draft; attribution line; full licence texts.
- Refresh script gains the publication gate (contact keys, licence-restricted provenance, `buildMode`).
- Patch for the atlas project's `scripts/collate.py` retiring the hard-coded "preview" label (applied 2026-09-11).

Earlier, before this tree existed (2026-09-03 → 2026-09-10):
- Boot screen, breathing dot-screen hero, hairline HUD geometry, live progress terminal, 3D Western Cape map with pulsing region markers, region pages for every region with in-browser tactical maps, gold closing page with hidden-halftone pixel reveal, continuously sweeping radar with fixed blips.
- All copy sourced from the atlas record; no file names or research-process vocabulary in visible text.
- Updated to the 10 September build: contact details no longer republished, corroborated awards marked, withheld records counted, OSM attribution, award ledgers contained within their cards, footer alignment, personal name removed from the visible licence line.
