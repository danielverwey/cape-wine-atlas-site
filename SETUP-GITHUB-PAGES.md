# Putting the atlas on the web — GitHub Pages at capewineatlas.co.za

Everything below is a one-time setup; after it, publishing is `build → commit → push`.

## 1. Make this folder a repository and push it

In PowerShell, in `C:\Users\Daniel\cape-wine-atlas\production site`:

    git init
    git add .
    git commit -m "Cape Wine Atlas site, v0.10.0"
    git branch -M main

On github.com: **New repository** → name it `cape-wine-atlas-site` (any name works), leave it empty
(no README, no licence — the folder has both), create it, then:

    git remote add origin https://github.com/danielverwey/cape-wine-atlas-site.git
    git push -u origin main

The repository can be public or private; GitHub Pages serves either (private needs a paid plan for
Pages, so public is the simpler choice — and the site is open data anyway).

## 2. Turn on Pages

Repository → **Settings → Pages** → under *Build and deployment*: Source **Deploy from a branch**,
Branch **main**, Folder **/docs** → Save. Within a minute the site is live at
`https://danielverwey.github.io/cape-wine-atlas-site/` — it will look wrong there (the page is
built for the domain's root), which is expected; the domain fixes it.

## 3. Point the domain at it

At your domain registrar's DNS panel for `capewineatlas.co.za`, add:

| type | host | value |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `danielverwey.github.io` |

(Those four addresses are GitHub Pages' published ones; check
docs.github.com → "Managing a custom domain for your GitHub Pages site" if they have changed.)

Then in **Settings → Pages → Custom domain** enter `capewineatlas.co.za` and Save. The `docs/CNAME`
file the build writes keeps this setting from being lost on later deploys. Tick **Enforce HTTPS**
once GitHub has issued the certificate (it can take up to an hour after DNS propagates).

## 4. Check

- `https://capewineatlas.co.za/` shows the boot screen.
- `https://capewineatlas.co.za/region/constantia/` opens straight onto Constantia.
- `https://capewineatlas.co.za/anything-else/` shows the "Not on the record" page.
- `https://capewineatlas.co.za/sitemap.xml` lists 32 addresses.

## Publishing a new edition, ever after

    cd "C:\Users\Daniel\cape-wine-atlas\production site"
    python3 build_pages.py C:\Users\Daniel\cape-wine-atlas\atlas
    git add docs cape-wine-atlas.html
    git commit -m "September 2026 edition, refreshed"
    git push

If the build says REFUSED, it has found something the atlas's own rules would not publish; fix the
atlas build first rather than overriding.

## Search engines

Submit `https://capewineatlas.co.za/sitemap.xml` once in Google Search Console (Settings → Sitemaps)
after the domain is live; the region pages are pre-rendered, so they index without special handling.
