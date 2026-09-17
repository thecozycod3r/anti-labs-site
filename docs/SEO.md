# SEO

Everything in the checklist is implemented in the build. The one item that is
work rather than code — backlinks — is planned at the bottom.

## Status

| Item | State |
|---|---|
| Noindex tags | None. Every page is `index, follow, max-image-preview:large` |
| Meta titles | Unique per page, 49–57 chars |
| Meta descriptions | Unique per page, 133–139 chars |
| Alt text | Every `<img>` has `alt`; decorative backgrounds use `alt=""` |
| Core Web Vitals | CLS **0**, LCP 80–344ms, 342KB–1.4MB per page |
| sitemap.xml | Generated, all four URLs |
| og:image | Per-page 1200×630 card in `assets/og/`, plus Twitter cards |
| Broken links | None — 17 links, all anchors and every asset verified |
| Header hierarchy | One `<h1>` per page, no skipped levels |
| URL slugs | `/`, `/anti-light`, `/anti-motion`, `/anti-dote` |
| Internal links | Header nav, footer nav, contextual links from each space |
| Canonical tags | Absolute, one per page |
| Enforce HTTPS | GitHub Pages `https_enforced`; http 301s to https; no mixed content |
| Compress all images | Originals capped at 1600px, progressive JPEG; 17.6MB → 8.2MB |
| Schema markup | LocalBusiness, WebSite, BreadcrumbList, FAQPage |
| Search Console | Hook ready — `--gsc <token>`; verification needs the owner's account |
| Only 1 H1 per page | Enforced, and checked by `tools/audit.py` |
| robots.txt | Generated, references the sitemap |
| Mobile responsiveness | Rebuilt below 768px; verified 414→320px |

Extras: JSON-LD (`LocalBusiness` with address and departments on the home page,
`BreadcrumbList` elsewhere), `robots.txt`, `theme-color`, font and LCP preloads.

## Tools

| Command | Does |
|---|---|
| `python3 tools/seo.py` | Rebuilds head tags, sitemap, robots |
| `python3 tools/seo.py --gsc <token>` | Adds the Search Console verification meta |
| `python3 tools/images.py` | Compresses images, rebuilds variants, rewrites markup |
| `python3 tools/audit.py` | Static audit; non-zero exit on failure |
| `python3 tools/audit.py --live <url>` | Also checks HTTPS and that every URL is 200 |

`audit.py` is the guard: it fails on a noindex, a title over 60 chars, a missing
canonical or og:image, more or fewer than one h1, a skipped heading level,
invalid JSON-LD, a missing alt, a broken srcset file, an oversized image, an
opaque PNG, or a sitemap with a non-HTTPS URL.

## Images

`tools/images.py` caps originals at 1600px (nothing renders wider, even at 2×),
converts opaque PNGs to progressive JPEG, and builds 480/960/1440 variants. Two
files stay PNG because they genuinely use transparency: the logo and the footer
mark.

Over two passes: originals 17.6MB → 8.2MB. On the wire a phone pulls roughly
250–370KB of images per page.

WebP/AVIF would save perhaps another 30%, but it needs `<picture>` elements, and
several CSS rules select `.gallery img:nth-child(n)` — wrapping the images would
break them. Worth doing deliberately, not as a find-and-replace.

## Search Console

The markup hook exists; verifying needs access to the owner's Google account:

1. Search Console → Add property → **Domain** (covers all subdomains and both
   protocols) if you can add a DNS TXT record; otherwise URL prefix.
2. For the URL-prefix method, take the token and run
   `python3 tools/seo.py --gsc <token>`, deploy, then press Verify.
3. Submit `sitemap.xml`, then request indexing for the four URLs.

## The domain

`tools/seo.py` owns every absolute URL. It currently points at
**`https://www.theantilabs.com`** — the site this is built for, not the GitHub
Pages preview. That is deliberate: this is a copy of a live business's content,
and a preview that canonicalises to itself would compete with the real site in
search results.

To change domain, one command rewrites canonicals, OG URLs, JSON-LD and the
sitemap:

```bash
python3 tools/seo.py --site https://www.theantilabs.com
```

Rerun it after editing any title or description — it refuses to build if a
title exceeds 60 characters or a description falls outside 70–155.

## At launch

1. Point `tools/seo.py` at the final domain and rerun.
2. Google Search Console: verify the domain property, submit `sitemap.xml`,
   request indexing for the four URLs.
3. Bing Webmaster Tools: import from Search Console.
4. If the old Squarespace URLs change, 301 them to the new slugs. `/home` should
   redirect to `/`, not 404 — it currently exists on the live site.
5. Confirm one canonical host: pick `www` or apex and redirect the other.
6. Re-run the checks in this repo against production, not localhost.

## Backlinks

Ordered by return, not by ease. Verify each platform still operates in Bangalore
before spending time on it — directory landscapes change.

**1. Own the entity first.** Links mean little if Google can't resolve who and
where the business is.
- Google Business Profile — the single highest-value asset for "studio near me".
  Three units at one address: GBP allows separate listings only for genuinely
  distinct businesses (own entrance, staff, hours, category). If that isn't
  true, run one listing with services for each space rather than risk
  suspension.
- Apple Business Connect, Bing Places.
- Justdial and Sulekha carry real local search volume in India.
- Zomato and Swiggy for Anti Dote specifically.

**2. The compounding one: creator credits.** Every photographer, videographer,
dancer and brand that shoots there is a natural, relevant linking domain. This
scales with bookings and needs no outreach budget.
- Add one line to the booking confirmation: *"Shot at Anti Light? A credit and a
  link to theantilabs.com helps us more than a tag."*
- Keep a page worth linking to — the studio page, not the home page.
- Ask at checkout, when goodwill is highest, not weeks later.

**3. Local discovery and press.** LBB Bangalore, Deccan Herald Metrolife,
Bangalore Mirror, What's Hot. Pitch the angle, not the opening: "three creative
spaces under one roof on New BEL Road" is a story; "new studio opens" isn't.

**4. Community and institutions.** MS Ramaiah is a seven-minute walk — student
film and design projects need studio space. Dance schools, photography
collectives, film and design colleges. Offer an off-peak student rate in
exchange for a listing on their resources page.

**5. Events create links automatically.** Workshops, cuppings, screenings and
open studios get listed on Insider.in, BookMyShow, Meetup and Eventbrite, each
carrying a link and bringing the exact audience.

**6. Suppliers and partners.** Equipment distributors, coffee roasters, rental
houses. Reciprocal "where to find us" and "who we work with" pages.

**7. One resource page worth citing.** A genuinely useful "guide to shooting in
Bangalore" — permits, locations, rates, what a cyclorama does — earns links for
years. This is the only content play worth the effort at this size.

**Avoid:** paid link packages, bulk directory submissions, guest-post farms.
They are the fastest way to a manual action, and for a local business with a
real address the upside was never there.

**Measure** in Search Console → Links, monthly. Track referring *domains*, not
total links; ten domains beat a hundred links from one.
