#!/usr/bin/env python3
"""Normalise and compress every image, then rewrite the markup to match.

Rerunnable and idempotent.

  - caps originals at MAX_W (nothing on the page renders wider)
  - converts opaque PNGs to progressive JPEG; keeps PNG only where alpha is
    actually used (the logo and the footer mark)
  - builds 480 / 960 / 1440 variants
  - rewrites every <img>: src, srcset, width, height (sizes is left alone —
    it encodes layout intent, not file facts)

    python3 tools/images.py            # compress + rewrite markup
    python3 tools/images.py --report   # show what would change
"""
import argparse
import glob
import json
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ["index.html", "anti-light.html", "anti-motion.html", "anti-dote.html"]
VARIANTS = (480, 960, 1440)
MAX_W = 1600
JPEG_Q = 78
SKIP = {"assets/img/00-3.png", "assets/img/11-6.png"}     # transparent brand marks


def variant_path(src, w):
    return f"{os.path.splitext(src)[0]}-{w}w.jpg"


def is_variant(path):
    return re.search(r"-\d+w\.jpg$", path) is not None


def has_real_alpha(im):
    if im.mode not in ("RGBA", "LA"):
        return False
    lo, _ = im.getchannel("A").getextrema()
    return lo < 250


def originals():
    out = []
    for f in sorted(glob.glob("assets/img/**/*.*", recursive=True)):
        if not f.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        if is_variant(f):
            continue
        out.append(f)
    return out


def process(report=False):
    renames, saved_before, saved_after = {}, 0, 0

    for src in originals():
        before = os.path.getsize(src)
        saved_before += before
        im = Image.open(src)

        if src in SKIP:
            if not report:
                im.save(src, optimize=True)
            saved_after += os.path.getsize(src)
            continue

        keep_png = has_real_alpha(im)
        dst = src if keep_png else os.path.splitext(src)[0] + ".jpg"

        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)

        if not report:
            if keep_png:
                im.save(dst, optimize=True)
            else:
                im.convert("RGB").save(dst, "JPEG", quality=JPEG_Q,
                                       optimize=True, progressive=True)
                if dst != src:
                    os.remove(src)
            for w in VARIANTS:
                if im.width <= w:
                    v = variant_path(dst, w)
                    if os.path.exists(v):
                        os.remove(v)
                    continue
                im.convert("RGB").resize(
                    (w, round(im.height * w / im.width)), Image.LANCZOS
                ).save(variant_path(dst, w), "JPEG", quality=76,
                       optimize=True, progressive=True)

        if dst != src:
            renames[src] = dst
        saved_after += os.path.getsize(dst) if os.path.exists(dst) else before

    # the video poster rides along
    poster = "assets/video/spaces-poster.jpg"
    if os.path.exists(poster) and not report:
        Image.open(poster).convert("RGB").save(
            poster, "JPEG", quality=80, optimize=True, progressive=True)

    return renames, saved_before, saved_after


def rewrite_markup(renames):
    """Point every <img> at the current files and rebuild its srcset."""
    for page in PAGES:
        s = open(page, encoding="utf-8").read()
        for old, new in renames.items():
            s = s.replace(old, new)

        def fix(m):
            tag = m.group(0)
            src = re.search(r'src="([^"?]+)"', tag)
            if not src or not os.path.exists(src.group(1)):
                return tag
            path = src.group(1)
            w, h = Image.open(path).size

            parts = [f"{variant_path(path, v)} {v}w"
                     for v in VARIANTS if os.path.exists(variant_path(path, v))]
            parts.append(f"{path} {w}w")
            srcset = ", ".join(parts)

            if "srcset=" in tag:
                tag = re.sub(r'srcset="[^"]*"', f'srcset="{srcset}"', tag)
            elif len(parts) > 1:
                tag = tag[:-1] + f' srcset="{srcset}"' + ">"

            tag = re.sub(r'\swidth="\d+"', "", tag)
            tag = re.sub(r'\sheight="\d+"', "", tag)
            return tag[:4] + f' width="{w}" height="{h}"' + tag[4:]

        s = re.sub(r"<img\b[^>]*>", fix, s)
        open(page, "w", encoding="utf-8").write(s)

    credits = "reference/image-credits.json"
    if os.path.exists(credits):
        data = json.load(open(credits))
        for old, new in renames.items():
            if old in data:
                data[new] = data.pop(old)
        json.dump(data, open(credits, "w"), indent=2)
    if os.path.exists("docs-meta/image-credits.json"):
        data = json.load(open("docs-meta/image-credits.json"))
        for old, new in renames.items():
            if old in data:
                data[new] = data.pop(old)
        json.dump(data, open("docs-meta/image-credits.json", "w"), indent=2)


if __name__ == "__main__":
    os.chdir(ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    renames, before, after = process(report=args.report)
    if not args.report:
        rewrite_markup(renames)
        total = sum(os.path.getsize(f) for f in
                    glob.glob("assets/img/**/*.*", recursive=True)
                    if f.lower().endswith((".jpg", ".jpeg", ".png")))
        print(f"originals {before/1e6:.2f} MB -> {after/1e6:.2f} MB")
        print(f"converted to jpeg: {len(renames)}")
        print(f"assets/img total (originals + variants): {total/1e6:.2f} MB")
    else:
        print(f"would process {len(originals())} originals, {before/1e6:.2f} MB")
