#!/usr/bin/env python3
"""Build the SEO layer for the static site.

Rerunnable. Rewrites a managed block in each page's <head> and regenerates
sitemap.xml and robots.txt, so moving to a different domain is one command:

    python3 tools/seo.py                                   # default domain
    python3 tools/seo.py --site https://staging.example.com

What it owns:
  - <title>, meta description, canonical, robots
  - Open Graph + Twitter card tags (per-page 1200x630 images in assets/og/)
  - theme-color, font + LCP preloads
  - JSON-LD (LocalBusiness on the home page, BreadcrumbList elsewhere)
  - clean internal links: anti-light.html -> anti-light (GitHub Pages and most
    static hosts serve the extensionless path)
  - sitemap.xml, robots.txt
"""
import argparse
import datetime as dt
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_SITE = "https://www.theantilabs.com"

BUSINESS = {
    "name": "Anti Labs Studios",
    "email": "theantilabs@gmail.com",
    "street": "No 108, AGS Layout, New BEL Road",
    "locality": "Bangalore",
    "region": "Karnataka",
    "postcode": "560094",
    "country": "IN",
}

# file -> clean slug, copy. Titles <= 60 chars, descriptions <= 155.
PAGES = {
    "index.html": {
        "slug": "",
        "name": "Home",
        "title": "Anti Labs Studios | Creative Spaces in North Bangalore",
        "description": "Three spaces in North Bangalore: Anti Light photo and video studio, "
                       "Anti Motion dance studio and Anti Dote coffee bar. Book the room.",
        "og": "assets/og/home.jpg",
        "lcp": None,
    },
    "anti-light.html": {
        "slug": "anti-light",
        "name": "Anti Light",
        "title": "Anti Light | Photo & Video Studio Hire in North Bangalore",
        "description": "Cyclorama, backdrops, props and pro lighting on New BEL Road. "
                       "Anti Light is a North Bangalore studio for photo, video and content shoots.",
        "og": "assets/og/anti-light.jpg",
        "lcp": None,
    },
    "anti-motion.html": {
        "slug": "anti-motion",
        "name": "Anti Motion",
        "title": "Anti Motion | Dance & Movement Studio Hire, Bangalore",
        "description": "Sprung hardwood floor, mirrored wall, aerial rigging and a pole. "
                       "Hire Anti Motion in North Bangalore for rehearsals, classes and workshops.",
        "og": "assets/og/anti-motion.jpg",
        "lcp": ("assets/img/motion/hero.jpg", "100vw"),
    },
    "anti-dote.html": {
        "slug": "anti-dote",
        "name": "Anti Dote",
        "title": "Anti Dote | Coffee Bar on New BEL Road, Bangalore",
        "description": "Rotating single origins, unexpected preparations and a menu built "
                       "for long creative sessions. Anti Dote is the coffee bar at Anti Labs.",
        "og": "assets/og/anti-dote.jpg",
        "lcp": ("assets/img/dote/hero.jpg", "100vw"),
    },
}

FONT_PRELOADS = [
    "assets/fonts/Boldonse-400-normal-33adfb58.woff2",
    "assets/fonts/SpaceMono-400-normal-8f403534.woff2",
]

START, END = "<!-- seo:start -->", "<!-- seo:end -->"

GSC_TOKEN = ""   # set with --gsc; Search Console gives you this string


def url(site, slug):
    return site.rstrip("/") + "/" + slug


def esc(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


def srcset_for(path):
    base, _ = os.path.splitext(path)
    parts = []
    for w in (480, 960):
        if os.path.exists(os.path.join(ROOT, f"{base}-{w}w.jpg")):
            parts.append(f"{base}-{w}w.jpg {w}w")
    return ", ".join(parts)


def faq_entries(html):
    """Pull Q&A out of the FAQ accordion only.

    Scoped to `.acc--faq`: the hire and spaces accordions share the same markup
    but are not questions, and marking them up as FAQPage would be wrong.
    """
    m = re.search(r'<ul class="acc acc--faq[^"]*"[^>]*>(.*?)</ul>', html, re.S)
    if not m:
        return []
    scope = m.group(1)
    out = []
    for block in re.findall(
            r'<button class="acc__btn"[^>]*>(.*?)<span class="acc__icon">.*?'
            r'<div class="acc__panel"><div>(.*?)</div></div>', scope, re.S):
        q = re.sub(r"<[^>]+>", "", block[0]).strip()
        a = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", block[1])).strip()
        if q and a:
            out.append((q, a))
    return out


def faq_schema(html):
    entries = faq_entries(html)
    if len(entries) < 3:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in entries
        ],
    }


def jsonld(site, file, meta):
    if meta["slug"] == "":
        data = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "LocalBusiness",
                    "@id": url(site, "") + "#business",
                    "name": BUSINESS["name"],
                    "url": url(site, ""),
                    "email": BUSINESS["email"],
                    "image": url(site, meta["og"]),
                    "logo": url(site, "assets/img/00-3.png"),
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": BUSINESS["street"],
                        "addressLocality": BUSINESS["locality"],
                        "addressRegion": BUSINESS["region"],
                        "postalCode": BUSINESS["postcode"],
                        "addressCountry": BUSINESS["country"],
                    },
                    "department": [
                        {"@type": "LocalBusiness", "name": PAGES[f]["name"],
                         "url": url(site, PAGES[f]["slug"])}
                        for f in ("anti-light.html", "anti-motion.html", "anti-dote.html")
                    ],
                },
                {
                    "@type": "WebSite",
                    "name": BUSINESS["name"],
                    "url": url(site, ""),
                    "publisher": {"@id": url(site, "") + "#business"},
                },
            ],
        }
    else:
        data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Anti Labs Studios",
                 "item": url(site, "")},
                {"@type": "ListItem", "position": 2, "name": meta["name"],
                 "item": url(site, meta["slug"])},
            ],
        }
    return json.dumps(data, indent=2, ensure_ascii=False)


def head_block(site, file, meta, html=""):
    canonical = url(site, meta["slug"])
    og_image = url(site, meta["og"])
    lines = [
        START,
        f'<title>{esc(meta["title"])}</title>',
        f'<meta name="description" content="{esc(meta["description"])}">',
        f'<link rel="canonical" href="{canonical}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        '<meta name="theme-color" content="#0e0d0c">',
    ]
    if GSC_TOKEN:
        lines.append(f'<meta name="google-site-verification" content="{GSC_TOKEN}">')
    lines += [
        "",
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{BUSINESS["name"]}">',
        '<meta property="og:locale" content="en_IN">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:title" content="{esc(meta["title"])}">',
        f'<meta property="og:description" content="{esc(meta["description"])}">',
        f'<meta property="og:image" content="{og_image}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(meta["name"])} — Anti Labs Studios">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(meta["title"])}">',
        f'<meta name="twitter:description" content="{esc(meta["description"])}">',
        f'<meta name="twitter:image" content="{og_image}">',
        "",
    ]
    for f in FONT_PRELOADS:
        lines.append(f'<link rel="preload" href="{f}" as="font" type="font/woff2" crossorigin>')
    if meta["lcp"]:
        src, sizes = meta["lcp"]
        ss = srcset_for(src)
        lines.append(f'<link rel="preload" as="image" href="{src}" imagesrcset="{ss}, {src} 1800w" '
                     f'imagesizes="{sizes}" fetchpriority="high">')
    lines += [
        "",
        '<script type="application/ld+json">',
        jsonld(site, file, meta),
        "</script>",
    ]
    faq = faq_schema(html)
    if faq:
        lines += ['<script type="application/ld+json">',
                  json.dumps(faq, indent=2, ensure_ascii=False),
                  "</script>"]
    lines.append(END)
    return "\n".join(lines)


def clean_links(s):
    # internal page links -> extensionless; home -> "./"
    s = re.sub(r'href="index\.html(#[^"]*)?"', lambda m: f'href="./{m.group(1) or ""}"', s)
    for f, meta in PAGES.items():
        if meta["slug"]:
            s = re.sub(rf'href="{re.escape(f)}(#[^"]*)?"',
                       lambda m, slug=meta["slug"]: f'href="{slug}{m.group(1) or ""}"', s)
    return s


def check_lengths():
    bad = []
    for f, m in PAGES.items():
        if len(m["title"]) > 60:
            bad.append(f"{f}: title {len(m['title'])} chars (max 60)")
        if not 70 <= len(m["description"]) <= 155:
            bad.append(f"{f}: description {len(m['description'])} chars (want 70-155)")
    if bad:
        raise SystemExit("length check failed:\n  " + "\n  ".join(bad))


def build(site):
    check_lengths()
    today = dt.date.today().isoformat()
    for file, meta in PAGES.items():
        path = os.path.join(ROOT, file)
        s = open(path, encoding="utf-8").read()
        block = head_block(site, file, meta, s)

        if START in s:
            s = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, s, flags=re.S)
        else:
            # first run: replace the hand-written title + description
            s = re.sub(r"<title>.*?</title>\s*", "", s, count=1, flags=re.S)
            s = re.sub(r'<meta name="description"[^>]*>\s*', "", s, count=1)
            s = s.replace('<meta name="viewport" content="width=device-width, initial-scale=1">',
                          '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                          + block, 1)

        s = clean_links(s)
        open(path, "w", encoding="utf-8").write(s)
        print(f"  {file:<18} -> /{meta['slug']}")

    urls = "\n".join(
        f"  <url>\n    <loc>{url(site, m['slug'])}</loc>\n    <lastmod>{today}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n    <priority>{'1.0' if not m['slug'] else '0.8'}</priority>\n  </url>"
        for m in PAGES.values()
    )
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n")

    open(os.path.join(ROOT, "robots.txt"), "w").write(
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /_1to1-baseline/\n"
        "Disallow: /docs-meta/\n"
        "Disallow: /tools/\n\n"
        f"Sitemap: {url(site, 'sitemap.xml')}\n")
    print("  sitemap.xml, robots.txt")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=DEFAULT_SITE)
    ap.add_argument("--gsc", default="", help="google-site-verification token")
    a = ap.parse_args()
    GSC_TOKEN = a.gsc
    globals()["GSC_TOKEN"] = a.gsc
    build(a.site)
