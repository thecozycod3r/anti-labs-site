#!/usr/bin/env python3
"""Static SEO / asset audit. Exits non-zero on failure, so it can gate a deploy.

    python3 tools/audit.py                  # audit the files in this repo
    python3 tools/audit.py --live <url>     # also check HTTPS + headers live

Layout and responsiveness are verified in a browser, not here.
"""
import argparse
import glob
import json
import os
import re
import sys
import urllib.request

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "anti-light.html", "anti-motion.html", "anti-dote.html"]
MAX_IMG_W = 1800
MAX_IMG_KB = 400          # any single file larger than this is worth questioning
fails, warns = [], []


def fail(msg): fails.append(msg)
def warn(msg): warns.append(msg)


def audit_pages():
    for p in PAGES:
        s = open(p, encoding="utf-8").read()
        tag = f"{p}:"

        if re.search(r"noindex", s, re.I):
            fail(f"{tag} contains a noindex directive")

        title = re.search(r"<title>(.*?)</title>", s, re.S)
        if not title:
            fail(f"{tag} no <title>")
        else:
            t = title.group(1).replace("&amp;", "&")
            if len(t) > 60:
                fail(f"{tag} title {len(t)} chars (max 60)")

        desc = re.search(r'name="description" content="(.*?)"', s, re.S)
        if not desc:
            fail(f"{tag} no meta description")
        elif not 70 <= len(desc.group(1)) <= 155:
            fail(f"{tag} description {len(desc.group(1))} chars (want 70-155)")

        if len(re.findall(r'rel="canonical"', s)) != 1:
            fail(f"{tag} expected exactly one canonical")
        if not re.search(r'property="og:image" content="https?://', s):
            fail(f"{tag} no absolute og:image")

        heads = re.findall(r"<h([1-6])[^>]*>", s)
        if heads.count("1") != 1:
            fail(f"{tag} {heads.count('1')} h1 tags (want exactly 1)")
        for a, b in zip(heads, heads[1:]):
            if int(b) - int(a) > 1:
                fail(f"{tag} heading level skips h{a} -> h{b}")
                break

        for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                json.loads(blob)
            except json.JSONDecodeError as e:
                fail(f"{tag} invalid JSON-LD: {e}")
        if "application/ld+json" not in s:
            fail(f"{tag} no schema markup")

        for img in re.findall(r"<img\b[^>]*>", s):
            if "alt=" not in img:
                fail(f"{tag} <img> without alt: {img[:60]}")
            if " width=" not in img or " height=" not in img:
                warn(f"{tag} <img> without width/height: {img[:60]}")
            src = re.search(r'src="([^"?]+)"', img)
            if src and not os.path.exists(src.group(1)):
                fail(f"{tag} missing image file {src.group(1)}")
            for part in re.findall(r'srcset="([^"]+)"', img):
                for cand in part.split(","):
                    f = cand.strip().split(" ")[0]
                    if f and not os.path.exists(f):
                        fail(f"{tag} missing srcset file {f}")


def audit_images():
    for f in glob.glob("assets/img/**/*.*", recursive=True) + glob.glob("assets/og/*.jpg"):
        if not f.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        kb = os.path.getsize(f) / 1024
        w, _ = Image.open(f).size
        if w > MAX_IMG_W:
            fail(f"{f} is {w}px wide (max {MAX_IMG_W})")
        if kb > MAX_IMG_KB:
            warn(f"{f} is {kb:.0f}KB")
        if f.lower().endswith(".png"):
            im = Image.open(f)
            opaque = im.mode not in ("RGBA", "LA") or im.getchannel("A").getextrema()[0] >= 250
            if opaque:
                fail(f"{f} is an opaque PNG — should be JPEG")


def audit_site_files():
    for f in ("robots.txt", "sitemap.xml"):
        if not os.path.exists(f):
            fail(f"{f} missing")
    if os.path.exists("sitemap.xml"):
        sm = open("sitemap.xml").read()
        if sm.count("<loc>") != len(PAGES):
            fail(f"sitemap lists {sm.count('<loc>')} URLs, expected {len(PAGES)}")
        for loc in re.findall(r"<loc>(.*?)</loc>", sm):
            if not loc.startswith("https://"):
                fail(f"sitemap URL is not HTTPS: {loc}")
    if os.path.exists("robots.txt"):
        rb = open("robots.txt").read()
        if "Sitemap:" not in rb:
            fail("robots.txt has no Sitemap line")
        if re.search(r"^Disallow: /$", rb, re.M):
            fail("robots.txt disallows the whole site")


def audit_live(base):
    base = base.rstrip("/")
    http = base.replace("https://", "http://")
    try:
        req = urllib.request.Request(http, method="HEAD")
        with urllib.request.urlopen(req, timeout=20) as r:
            if not r.url.startswith("https://"):
                fail(f"http does not redirect to https (landed on {r.url})")
    except Exception as e:
        warn(f"could not check http->https: {e}")
    for path in ["/", "/anti-light", "/anti-motion", "/anti-dote",
                 "/sitemap.xml", "/robots.txt"]:
        try:
            with urllib.request.urlopen(base + path, timeout=20) as r:
                if r.status != 200:
                    fail(f"live {path} -> {r.status}")
        except Exception as e:
            fail(f"live {path} -> {e}")


if __name__ == "__main__":
    os.chdir(ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", default="")
    a = ap.parse_args()

    audit_pages()
    audit_images()
    audit_site_files()
    if a.live:
        audit_live(a.live)

    for w in warns:
        print(f"warn  {w}")
    for f in fails:
        print(f"FAIL  {f}")
    print(f"\n{len(fails)} failures, {len(warns)} warnings")
    sys.exit(1 if fails else 0)
