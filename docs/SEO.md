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

Extras: JSON-LD (`LocalBusiness` with address and departments on the home page,
`BreadcrumbList` elsewhere), `robots.txt`, `theme-color`, font and LCP preloads.

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
