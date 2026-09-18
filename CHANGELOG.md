# Changelog — Cape Wine Atlas production site

Newest first. Each entry is one sync to `production site/`.

## v0.19.0 — 2026-09-18 — September 2026 edition
`versions/cape-wine-atlas_2026-09-18_v0.19.0_september-2026-edition.html`

Built against the atlas of 18 September. **The honours count goes down, and that is the release.**

- **2,586 honours, not 2,673.** Eighty-nine of them did not exist. The Veritas 2025 results booklet was read twice — once on 10 September at one archive address, once on 12 September at another — and each reading wrote the wine the way its own page printed it: "The Journal Sauvignon Blanc 2024" the first time, "Diemersdal The Journal Sauvignon Blanc 2024" the second. Neither reading was wrong. The check that was supposed to notice compared the two strings, saw two different wines, and kept both. Diemersdal was carrying twelve results twice over and now shows 67 honours instead of 79; KWV loses nine; forty-six producers are affected. Where a producer page showed the same wine twice on the same day from the same competition, it now shows it once, and the surviving entry carries both readings and both sources in its record.
- **Every published producer has now had its honours looked for.** The last 82 that had never been checked against the atlas's competition ledgers were checked: none of them appears in any of them. That is recorded as a finding — *searched, none found* — rather than left looking like work outstanding, and it is not a claim that those producers have never won anything: the ledgers are partial by competition, and each says where its own coverage ends.
- **One honour gained.** Blake Family Wines of Yzerfontein, which had none, takes a Veritas 2025 Double Gold for Blake's Tourmaline 2024. "Blake's" is the producer's own premium range, not a separate winery — its own wine list names Tourmaline among them and describes it as the white blend the award record describes.
- The atlas's build now refuses to produce a payload that records one result twice, so the count cannot drift upward again unnoticed.

## v0.18.0 — 2026-09-18 — September 2026 edition
`versions/cape-wine-atlas_2026-09-18_v0.18.0_september-2026-edition.html`

Same data as v0.17.x. A fourth kind of page.

- **Tour operators, all on one page** at `/tours/`. The atlas lists 30 operators — a hop-on hop-off tram, a tractor, a tuk-tuk, a steam train, cycling tours, private guides — but a visitor could only meet them region by region, and 22 regions have none, so most were effectively invisible. They are now filed under the first area each names, with every area it serves as a link, what it offers in the operator's own terms, where it is based, its website, and the page the atlas read to list it. An operator taken from an association's map rather than its own site is marked NOT YET CONFIRMED, as on the region pages. Harvest Fridays at Gabriëlskloof, which the atlas records as a route event rather than an operator, is shown as exactly that. The page opens like the licence page and closes back to wherever you were; every region page's tour block now ends with ALL 30 OPERATORS ACROSS THE ATLAS ▸, and the footer's count is the way in from the front page. It has its own address, its own listing in the sitemap, and structured data naming all thirty.
- **A fresh page over a stale script.** After a release, a returning visitor's browser could keep last week's stylesheet and script while fetching this week's page — which is how the region index came to be drawn twice, once as blue underlined links and once as the old list beneath them. The stylesheet and the script now carry a fingerprint of their own content in their names, and every data request carries the build's fingerprint, so anything that changed is a new address and anything cached is the right one. A hard refresh will no longer be needed after an update.
- **Counted as operators, not entries.** The footer and boot log said 31; one of the 31 is the route event. They now say 30.
- **The copy pass reads a bracket before it splits a sentence.** A bracketed source note with a dash inside it used to split the sentence in front of it, taking a fact with it — Ataraxia's history line ended "Founded 2004 when Kevin Grant." Three producers' history lines return from blank, thirty-odd read fuller, and two working-note phrases that had reached the site ("The location gap stands — the map is a query embed", Daschbosch's) are gone.

## v0.17.1 — 2026-09-18 — September 2026 edition
`versions/cape-wine-atlas_2026-09-18_v0.17.1_september-2026-edition.html`

Same data as v0.17.0. **The site can now be walked from the front page to any producer without a script**, which it could not before — and that, not the sitemap, is what a search engine reads as evidence that a page is worth having.

- **The front page linked to nothing.** The region index was drawn by the script as buttons, so the published home page carried four links, two of them email addresses. Every region and every producer page existed only in the sitemap: findable, but with nothing on the site pointing at them. The index is now written into the page as thirty-two real links, which the script still replaces with its own — also links — so nothing about how it looks or behaves changes.
- **A producer page could not be walked back up.** The trail at the top said CAPE WINE ATLAS / STELLENBOSCH / KANONKOP and none of it was a link, so all 651 producer pages were leaves with no parent. Both earlier segments are now links; inside the running atlas they still step back through the views rather than reloading, and a middle-click or ⌘-click opens a tab as you would expect.
- Same on a region page: the trail's first segment returns to the chart.
- The NOT ON THE CHART label under the shelf's index row was being clipped to an ellipsis at narrow widths; it now sits on its own line.

## v0.17.0 — 2026-09-17 — September 2026 edition
`versions/cape-wine-atlas_2026-09-17_v0.17.0_september-2026-edition.html`

Includes the tasting-hours fix prepared as v0.16.2, which was never pushed. Built against the atlas export of 17 September: **651 producers** (up from 644) · 2,673 verified honours · 1,702 wines on record · 207 held back. The first release built on the atlas's own decision that a producer it can name, source and reach — and cannot place closer than the province — is published at the province (ADR-150).
- **No fixed place.** A new entry at the foot of the region list, marked NOT ON THE CHART: nineteen producers whose own websites say where their grapes come from and not where they are. They were on the site until the atlas's placement re-test found no source for the regions they had been given; now they are back, placed where they can honestly be placed. The region page opens like any other, with the atlas's own explanation in place of a map; each producer page reads "WESTERN CAPE · NO FIXED PLACE" where a ward would stand, shows the locality the producer itself states under VISIT — marked as the producer's word, not a place the atlas could confirm — and says nothing finer anywhere, including in what it tells a search engine. No marker is drawn on the chart for them, and the headline count of regions stays at 31.
- **Eight producers join** — Lammershoek, Signal Hill, The Drift, Dunstone, Von Family Wines, Mudita Cap Classique, Seven Oaks, Jacques Smit — and **one leaves**: Rivendell's only contact route turned out to be the route association's page about it rather than a page of its own, so it is held back until a real one is found. Its address no longer resolves.
- **192 records read cleaner.** The atlas's evidence-repair pass rewrote the hours, people, locality and venue notes on 192 producers, replacing working prose with the fact; the site now shows tasting hours on 395 producer pages. Eagles' Nest's tasting room is shown closed for now, as it is.
- **Regions carry the atlas's own introduction** where it has written one, in place of a filtered terroir note.
- **Tasting hours were being dropped.** The pass that keeps a producer's facts and discards the working notes around them was tuned for history paragraphs, and it treated anything under 25 characters as not worth keeping. Opening hours are short by nature — "Mon–Fri 08:00–17:00", "By appointment only.", "Daily 10:00–17:00." — so it discarded them, and the VISIT column on 114 producer pages stood empty where the atlas had hours on file. The same pass also mistook "BY APPOINTMENT ONLY" for a heading and cut it off, read "prior arrangement", "winter closure", "one Saturday per month" and "cheese platters" as research vocabulary, and took a bracketed source note with a semicolon inside it as two clauses and lost the hours with them. Hours now have their own rules: no minimum length, a capital letter supplied where the note began without one, a bracketed source dropped whole before the sentence is read, and no heading rule. **Hours are shown on 386 producer pages instead of 294**; the 22 still withheld are the ones where the atlas itself records a conflict between sources or an alert rather than a schedule, and those stay off the page until the atlas settles them. No history paragraph changes except Eikehof's, which had been left with an unclosed bracket.
- **The build reads the atlas's new date field.** The export now says when its data was last read rather than when it was built; the site takes the edition from that. It also no longer stops on a region file with nothing published in it and no fixed position on the chart.

## v0.16.1 — 2026-09-15 — September 2026 edition
`versions/cape-wine-atlas_2026-09-15_v0.16.1_september-2026-edition.html`

Built against the same atlas export as v0.16.0 — 644 producers, 2,668 honours, 1,685 wines, unchanged. **Nothing visible on a page changes and no record moves.** What changes is what the site tells a search engine is true, brought into line with the atlas's own written account of what the site may claim on a producer's behalf.

- **A winery is a place. Not every producer has one.** The structured data on a producer page said *Winery* for all 644 — an assertion, in machine-readable form, that a physical place exists at that name. For 146 producers it does not: 109 whose premises the atlas has not established, 18 with no public venue, 10 pouring at somebody else's venue and 9 selling only off-site. A producer who buys in fruit and works out of a shared cellar is a producer and is not a place. Those 146 now say *Organization* — this is a producer, this is its name, this is its site, this is the area it belongs to — and claim no premises. The other 498 still say *Winery*.
- **No invented address.** Every producer page carried a postal address built out of the ward and the region — "Simonsberg-Stellenbosch, Western Cape, ZA" — which no source ever said. The atlas holds no street addresses for these records, so the address is gone. The area a producer belongs to is stated as an area, which is what is actually known.
- **A coordinate only where it marks the producer's own gate.** The position now appears in the structured data for 437 producers rather than 477: only on a producer with premises of its own, and only where the pin is one the atlas calls clean. The pins that mark somebody else's tasting venue are still drawn on the page — they are useful, and the page says whose venue it is — but they are no longer offered to a search engine as that producer's location.
- **The varieties a producer works with** are now stated in the structured data, as cultivars the producer works with rather than vines it is claimed to grow — many published producers own no vineyard at all.
- **The sitemap no longer carries a date.** Every one of the 676 addresses was stamped with the build date, which said only that the site had been rebuilt — not that anything on the page had changed. One date across a whole site is a freshness claim nothing supports, and a crawler that learns to distrust it discounts it everywhere. The sitemap now gives locations and relative weight, and says nothing it cannot stand behind.
- **Descriptions that finish their sentences.** The line a search engine shows under the title was assembled by cutting the history at 150 characters, which landed mid-word ("…over granitic clay — the granite is the"). It is now built in a fixed order — where the producer is, whether you can visit, honours, wines, the varieties on record — and the variety list is the part that shortens, one at a time, saying how many were left out. A producer with no honours no longer advertises "0 honours". Nothing is cut mid-word and the whole line stays within what a search result will show.
- **Page and crawler housekeeping.** Pages declare South African English, state that they may be indexed and that a large preview image is welcome, and name the locale for a shared link. The data files under `/data/` are asked not to be indexed — they are published for reuse under the Open Database Licence, and they are the same facts as the pages in a form meant for machines — with one exception: the producer list the home page names as this atlas's download stays fetchable, because a dataset whose download cannot be fetched is a dataset nobody can check.
- The build no longer stops when the atlas holds a region with no published records in it.

## v0.16.0 — 2026-09-12 — September 2026 edition
`versions/cape-wine-atlas_2026-09-12_v0.16.0_september-2026-edition.html`

Built against the atlas export of 12 September (evening): 644 producers · **2,668 verified honours** (up from 1,326; Michelangelo and the National Wine Challenge join the competitions consulted, Platter's and Veritas deepen) · 24 under review · 144 held back · and, for the first time, **the producers' own wine lists: 1,685 names and 797 range labels across 523 producers**, each read from the producer's own pages and cited.
- **The wines, as the producer prints them.** THE WINES on a producer page now opens with the range labels (RANGES · Kadette Range · Estate Range) and lists every wine the producer names on its own site, marked ON THE PRODUCER'S OWN LIST. Where the honours ledger names one of them, the honours sit under it — and a ledger entry such as "Kanonkop Black Label Pinotage 2017" is recognised as the listed "Black Label", the producer's name lifted off the front and the vintage folded in. A range label becomes a card of its own only when an honour names it (Simonsig's Kaapse Vonkel). Signature wines follow, then wines only the ledger names, marked as such. Where the producer gives its own account of a name, it is quoted on the card in the producer's words: "— THE PRODUCER'S OWN ACCOUNT OF THE NAME".
- **Saying where the list came from.** The note under the wines states the reading, not a promise: "THE RANGE AS THE PRODUCER PRINTS IT, READ FROM KANONKOP.CO.ZA ON 2026-09-12 · 2 NAMES IN 2 RANGES". For the 97 producers whose own pages name no wines it says so and why that is a finding, not a gap ("some sell by grape variety alone and do so deliberately; the atlas does not guess"); for the 24 with no readable page on their own domain it says that. PROVENANCE gains a **Wines** line with the same facts in prose. The working note behind each reading stays in the atlas and is never published.
- **Counted on the home page.** The boot log, the live terminal and the footer now carry WINES ON RECORD (1,685 names · 523 producers); the page description says so too. Search knows every listed wine name (2,483 entries now), so "john x merriman" opens Rustenberg's page.
- Region cards show the new honours in their summaries; the lenses count them.

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
