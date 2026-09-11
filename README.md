# Cape Wine Atlas — production site

The public face of the Cape Wine Atlas, built for GitHub Pages at **https://capewineatlas.co.za**.

## Layout

| path | what it is |
|---|---|
| `docs/` | **the built site** — what GitHub Pages serves. Never edit by hand; rebuild it. |
| `src/` | the sources the build reads: `index.template.html`, `app.js`, `site.css`, `geo.json`, `assets/` (typefaces, textures, share image) |
| `build_pages.py` | the build: publication gate → data extraction → `docs/` + the archival single file |
| `cape-wine-atlas.html` | the current page as **one self-contained file** (for offline use and for `versions/`) |
| `versions/` | a frozen single-file copy of every synced version, never edited |
| `patches/` | one-off changes to the atlas project's own scripts, as unified diffs |
| `SETUP-GITHUB-PAGES.md` | how to put `docs/` on the web at the domain, step by step |
| `CHANGELOG.md` | one entry per sync: version, date, edition, what changed |

## Rebuilding from a new atlas build

    python3 build_pages.py C:\Users\Daniel\cape-wine-atlas\atlas

It refuses any atlas build that carries contact keys, licence-restricted provenance on a
published record, or a `buildMode` other than `public`, and prints the counts it checked.
Then commit `docs/` and push — GitHub Pages redeploys in about a minute.

Options: `--root /` (use `--root /repo-name/` for a project page without the domain),
`--domain capewineatlas.co.za`, `--out docs`, `--allow-preview` (local testing only).

## What the build writes

    docs/index.html                   the atlas
    docs/region/<key>/index.html      one page per region with its own address, pre-rendered
    docs/data/index.json              region index, statistics, map geometry (12 KB)
    docs/data/regions/<key>.json      one file per region, fetched only when it is opened
    docs/assets/                      site.css, app.js, three typefaces, three textures, og.jpg
    docs/sitemap.xml · robots.txt · CNAME · 404.html · .nojekyll

A first visit downloads about 560 KB; a region's records arrive only when that region is opened.

## File naming for frozen versions

`cape-wine-atlas_<sync date>_v<major.minor.patch>_<edition>.html`, e.g.
`cape-wine-atlas_2026-09-11_v0.11.1_september-2026-edition.html`.
The date is ISO so the folder sorts; the version stays at 0.x until public launch (patch rises
with every sync, minor with a new structure or atlas edition, major to 1.0.0 at launch); the
edition is the one the page carries, derived from the atlas build date.
