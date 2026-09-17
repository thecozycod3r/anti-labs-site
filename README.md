# Anti Labs Studios — site build

Static HTML / CSS / vanilla JS. No build step, no dependencies. Open `index.html`
or serve the folder (`python3 -m http.server 8777`).

## Pages

| File | What it is |
|---|---|
| `index.html` | Home — 1:1 replica of `theantilabs.com/home` |
| `anti-light.html` | Anti Light studio — 1:1 replica of `theantilabs.com/anti-light` |
| `anti-motion.html` | Anti Motion studio — **new page**, built in the same design language |
| `anti-dote.html` | Anti Dote cafe — **new page**, built in the same design language |

## The replication

The two replicated pages were measured against the live site rather than eyeballed.

The source runs on Squarespace's fluid layout engine. Reverse-engineering the grid
gave an exact model:

- **Desktop (≥768px):** 24 columns, 45.5px column, 12px gap, 36px page gutter at 1440
- **Mobile (<768px):** 8 columns, ~11px gap, 23px page gutter at 390
- Columns are fluid, row heights are fixed — so each block is placed by
  `grid-column` (fluid) plus `margin-top` (fixed), reproducing the source's
  overlapping type and imagery exactly.

Verified at 1440 and 390 against measurements taken from the live DOM:

| Page | Document height | Worst element deviation |
|---|---|---|
| Anti Light @1440 | 5683px (exact) | ≤1px |
| Anti Light @390 | 6842px (exact) | ≤1px |
| Home @1440 | 3942px (exact) | ≤1px |
| Home @390 | 3152px (exact) | ≤1px |

Section-by-section pixel diffs against screenshots of the live site: mean absolute
difference 1.4–4.5 / 255. The residual is image-rendition noise (the CDN serves
smaller renditions than the originals downloaded here) and text antialiasing.

Fonts are the **actual woff2 files** the source serves (Boldonse, Space Mono,
Space Grotesk), self-hosted in `assets/fonts/`. Squarespace focal points were read
off the live site's computed `object-position` and reapplied.

The untouched, verified replica is preserved in `_1to1-baseline/` — the
enhancements below were layered on afterwards, so the baseline is recoverable.

## What was added on top

Layered in `assets/css/enhance.css` + `assets/js/enhance.js`, so the replicated
layout files stay clean:

- **Navigation.** The source ships an empty `<nav>`; with four pages the site needs
  one. Logo stays centred, links sit right, full-screen overlay on mobile.
- **Header retraction.** Matches the source's own behaviour (retracts on scroll
  down, returns on scroll up) — this was reverse-engineered from the live site.
- **Numbered section eyebrows** (`01 — THE FLOOR`), mono, red index.
- A slow mono **marquee**, brand-coloured selection and focus rings.

### Motion system (`assets/css/motion.css` + `assets/js/motion.js`)

Entrances
- **Masked line reveal** on display headings — JS splits a `[data-split]` heading
  on `<br>` into overflow-clipped lines that rise in sequence.
- **Image wipe** — `clip-path` opens upward while the photo settles from a 1.09
  scale.
- Staggered fades for supporting copy (`.reveal`, `.reveal--delay-1..3`).

Hover
- Buttons fill with a **colour sweep from the left**, text inverts.
- Nav labels **swap upward**, revealing a blue duplicate; red rule draws under.
- Accordion rows step right and reveal a **red `01` index**; the +/chevron
  counter-shifts so the icon column stays aligned.
- Gallery strip cells **expand to ~2×** while their neighbours desaturate, with a
  caption rising in.
- Stat cards draw a red rule; menu rows step right and turn the price red.
- Inline links draw a red underline from 0 to 100% width.

Scroll / pointer
- Thin **red progress bar** at the top of the viewport.
- **Parallax** on every floating image. Each carries its own `data-parallax`
  speed and sign — positive runs ahead of the scroll, negative lags behind — so
  the collages separate as you move rather than sliding as one slab. Capped at
  ±110px.

  | | speed |
  |---|---|
  | Home hero: red dancer / motion blur / eye | `0.12` / `-0.06` / `0.16` |
  | Home manifesto: main / side / cafe | `-0.05` / `0.13` / `0.08` |
  | Home cards: left / right | `0.07` / `-0.06` |
  | Anti Light: eye / features / contact | `0.10` / `0.07` / `-0.05` |

  Parallax is a visual offset only — with the transforms cleared the replicated
  pages still measure exactly (5683px, worst deviation 1px), so the underlying
  1:1 geometry is intact.
- **Cursor spotlight** — a soft radial highlight tracking the pointer across hero
  imagery and the two photographic backgrounds on Anti Light. It suits a lighting
  studio; `sec__bg--spot` opts a background into it.
- **Page-transition wipe** between internal pages (ink panel + red edge).

Accessibility and safety
- Every effect is `prefers-reduced-motion` aware — verified under emulation:
  nothing stays hidden, the wipe is never injected, the marquee stops.
- The spotlight only runs on `(hover: hover) and (pointer: fine)`.
- Reveals carry a deterministic scroll-sweep fallback, because
  IntersectionObserver can drop entries under fast scrolling and would otherwise
  strand an element invisible.
- Everything resolves to an identity transform, so the replicated pages still
  measure exactly — re-verified after the motion layer landed (5683px / 3942px,
  worst deviation 1px).
- The replicas use reveals and wipes only; the DOM-splitting treatment is kept to
  the two new pages so the verified markup is untouched.

## Mobile

Below 768px the site no longer inherits the source's pinned mobile layout.
`assets/css/mobile.css` (loaded last) puts every section into flow — auto
height, natural rows — and rebuilds the compositions that matter: the hero
collage, the manifesto overlay, the blue image plate (an offset shadow on
phones), and the gallery strip (a swipeable, snapping row). The desktop sheets
are untouched, so the 1440 replica still measures exact.

Tested as a visitor sees it: scrolled screen by screen at 414 / 390 / 375 / 360 /
320, with touch and coarse-pointer emulation confirmed separately. Zero
horizontal overflow, zero sub-44px targets, zero clipped text at every width.


Audited at 390 / 360 / 320 px. Zero horizontal overflow, zero tap targets under
44px on all four pages.

**Payload.** The home page was shipping 12.4 MB. Now:

| | before | after |
|---|---|---|
| Mobile (390px) | 12.4 MB | **671 KB** |
| Desktop (1440px) | 12.4 MB | **1.39 MB** |

- Every photo has 480w / 960w variants and a `srcset` + `sizes` hint, so a phone
  fetches roughly 6% of the original bytes. Below-fold images are `loading="lazy"`.
- The background video was a 5.5 MB 1080p file at 3 Mbps. Re-encoded to 915 KB
  for desktop and a 960px, 298 KB version for phones, picked by viewport in JS,
  with a 38 KB poster frame behind it.

**Autoplay.** Browsers only honour muted autoplay when the *property* is set, not
just the attribute — and Safari still refuses under Low Power Mode or a per-site
auto-play setting, painting its own play button over the poster. The video now
sets the property explicitly and retries on the first user gesture, so it starts
in the cases where a plain `autoplay` attribute silently fails.

**Fixes the audit turned up that weren't visible by eye:**

- `.acc--features` / `.acc--faq` lived in `anti-light.css`, which Anti Motion and
  Anti Dote don't load — their accordions were rendering unstyled, with 23px tap
  targets. Moved to the shared sheet.
- The skip link sat at `left: -15000px`, which still counts toward `scrollWidth`
  and registered as phantom horizontal overflow. Uses the clip technique now.
- `t-fit` (nowrap, there to stop a sub-pixel wrap on desktop) forced long
  headings wider than a phone screen. Unset below 768px — the source wraps them
  there anyway.
- The manifesto scrim's -110px inset ran past a 390px viewport.
- The open accordion's index-shift pushed its row 26px past the right edge.

Desktop replicas re-verified after all of it: 5683px / 3942px exact.

## Content status — please read

The two new pages use **real copy** where it exists: the Anti Motion and Anti Dote
descriptions are lifted verbatim from the live site's "The Spaces" accordion, as
are the studio hours and address.

Everything else is written to demonstrate the design and **needs your sign-off**:

- **All rates say "rate on request"** rather than a number. I did not invent
  pricing for a real business — fill these in before this goes anywhere public.
- **Anti Dote menu prices** say "In store" for the same reason.
- **Anti Dote opening hours** currently mirror the studio hours (Mon–Sat 8–20,
  Sun 10–18) taken from the live FAQ. Confirm the cafe's actual hours.
- Facility details on Anti Motion (sound system, mats, crash mats, certified
  rigging) are extrapolated from the one-line description. Verify before publishing.
- Forms are front-end only — no backend is wired up.

## Contrast — a deliberate divergence from the original

The live site sets white type over photographs in several places. Auditing every
such overlay (hide the text, photograph the backdrop, measure the 95th-percentile
luminance under the type) found three that failed WCAG's 3:1 minimum for large
text:

| | before | after |
|---|---|---|
| Home — manifesto statement | 1.83:1 | 9.68:1 |
| Home — "STUDIOS" over the eye plate | 2.02:1 | 8.76:1 |
| Anti Light — first about paragraph | 2.11:1 | 6.00:1 |

Mean contrast looked fine in all three; the failure only shows at the bright end,
because the photos run from luminance 13 to 200 and the type crosses both.

Fixes are the lightest touch that works: a radial scrim behind the manifesto
text only, a shadow on "STUDIOS" (the chroma ghosts opt out so the colour
fringing stays clean), and a directional gradient over the about backdrop that
darkens the text column while leaving the heading side bright.

**This means those three spots intentionally differ from the live Squarespace
site, which has the same flaw.** Readability won. Everything else remains a
measured 1:1 match — verified after these changes: 5683px / 3942px exact, worst
deviation 1px.

## SEO

Titles, descriptions, canonicals, Open Graph, JSON-LD, sitemap and robots are
generated by `tools/seo.py`, which owns a managed block in each page's `<head>`.
Clean slugs (`/anti-light`), one `<h1>` per page, alt text on every image, CLS 0.

Absolute URLs point at **theantilabs.com**, not the GitHub Pages preview — a
preview that canonicalises to itself would compete with the client's real site.
One command moves them: `python3 tools/seo.py --site https://example.com`.

Run `python3 tools/audit.py` before any deploy — it fails on a noindex, a long
title, a missing canonical, a second h1, invalid JSON-LD, a missing alt or a
broken srcset.

Full status, launch steps and the backlink plan: `docs/SEO.md`.


## Images

Photography is from **Pexels** (free licence, no attribution required — credited
here as good practice). This matches how the live site sources its own imagery.

I deliberately did not pull from Pinterest or Google Images: those are third-party
copyrighted works and would be a real liability on a client site.

Per-image credits: `docs-meta/image-credits.json`.

The Higgsfield CLI is installed and credentialed on this machine if you'd prefer
bespoke, generated imagery instead of stock for the two new pages — say the word
and I'll regenerate them on-brand.

## Brand tokens

```
--ink    #0E0D0C   background
--paper  #F0F0F0   text
--red    #BB1122   accent (italic display, indices, rules)
--blue   #ABBCC4   secondary accent (eyebrows, plates, "ANTI" in lockups)

display  Boldonse        uppercase, letter-spacing -0.02em
body     Space Mono      15px / 22.5px
buttons  Space Grotesk   600, uppercase
```

Note: Boldonse has deep ascenders and descenders. Multi-line display settings need
`line-height` around **1.3** — anything tighter collides. The source uses 1.316.

## Folders

```
assets/css   style.css (base + grid) · anti-light.css · home.css
             pages.css (new pages) · enhance.css · motion.css · fonts.css
assets/js    main.js (accordions, header, video) · enhance.js (nav)
             motion.js (reveals, parallax, spotlight, page wipe)
assets/img   source-site images · motion/ · dote/
assets/fonts the source's own woff2 files
reference/   measurements, diffs and QA screenshots from the replication
_1to1-baseline/  the verified 1:1 replica before enhancements
```
