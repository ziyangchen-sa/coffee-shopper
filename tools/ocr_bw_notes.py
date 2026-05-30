#!/usr/bin/env python3
"""Extract tasting notes from Black & White's product "card" images via OCR.

B&W renders each coffee's flavour notes onto its product image (not as text in
products.json). This downloads each in-stock B&W coffee's card image, boosts the
text contrast (the cards are dark text on coloured gradients), OCRs with
Tesseract, parses out the notes, and writes bw-notes.json ({handle: "A, B, C"})
which the web app reads at runtime.

Requires: Pillow (pip install pillow) and the tesseract binary on PATH
          (brew install tesseract / apt-get install tesseract-ocr).
Run:      python3 tools/ocr_bw_notes.py        # writes ./bw-notes.json
"""
import json, os, re, ssl, subprocess, sys, urllib.request
from io import BytesIO
from PIL import Image, ImageOps, ImageChops, ImageFilter

FEED = "https://www.blackwhiteroasters.com/collections/all-coffee/products.json"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "bw-notes.json")
TMP = os.path.join(ROOT, ".ocrtmp")            # temp images under repo (sandbox/CI both allow)
UA = {"User-Agent": "Mozilla/5.0 Chrome/124 Safari/537.36"}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

SKIP = re.compile(r"gift\s*card|drinkware|apparel|brewing|accessor|equipment|merch|sticker|mug|tumbler|hat|tee|shirt", re.I)
SCALE = re.compile(r"\b(light|dark|clean|funky|medium)\b", re.I)


def fetch_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX) as r:
        return json.load(r)


def fetch_bytes(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, context=CTX) as r:
        return r.read()


def preprocess(img):
    """Dark text on a coloured gradient -> clean black-on-white for OCR.
    Use the HSV value channel (dark text vs bright colour), flatten the
    background by subtracting a blurred copy (adaptive threshold), binarize."""
    v = img.convert("RGB").convert("HSV").getchannel(2)
    bg = v.filter(ImageFilter.GaussianBlur(18))
    diff = ImageChops.subtract(bg, v)              # bright where text is darker than local bg
    diff = ImageOps.autocontrast(diff, cutoff=0)
    binimg = diff.point(lambda p: 0 if p > 45 else 255)   # text -> black, bg -> white
    return binimg.resize((binimg.width * 2, binimg.height * 2))


def parse_notes(ocr, title):
    title_words = set(re.sub(r"[^a-z0-9 ]", " ", title.lower()).split())
    out = []
    for i, raw in enumerate([l.strip() for l in ocr.split("\n") if l.strip()]):
        if SCALE.search(raw):
            break                                  # slider labels & below: not notes
        if i == 0:
            continue                               # first line is the title
        words = re.sub(r"[^a-z0-9 ]", " ", raw.lower()).split()
        if len(words) >= 2 and words and all(w in title_words for w in words):
            continue                               # wrapped title remainder
        clean = re.sub(r"[^A-Za-z &'/-]", " ", raw)
        clean = re.sub(r"\s+", " ", clean).strip(" -&'/")
        if not re.search(r"[A-Za-z]{3,}", clean):
            continue                               # drop slider-knob junk ($e, _~, etc.)
        if re.search(r"(.)\1\1", clean.lower()):
            continue                               # drop gibberish like "Qwooo Oo" (3+ repeated chars)
        out.append(clean)
        if len(out) >= 6:
            break
    return ", ".join(w.title() for w in out)


def main():
    products = []
    for page in range(1, 7):
        ps = fetch_json(f"{FEED}?limit=250&page={page}").get("products", [])
        products += ps
        if len(ps) < 250:
            break
    coffees = [p for p in products
               if any(v.get("available") for v in p["variants"])
               and not SKIP.search((p.get("product_type") or "") + " " + p["title"])]

    os.makedirs(TMP, exist_ok=True)
    notes = {}
    for p in coffees:
        imgs = p.get("images") or []
        if not imgs:
            continue
        try:
            img = Image.open(BytesIO(fetch_bytes(imgs[0]["src"])))
            pre = os.path.join(TMP, p["handle"][:50] + ".png")
            preprocess(img).save(pre)
            ocr = subprocess.run(["tesseract", os.path.relpath(pre, ROOT), "stdout"],
                                 cwd=ROOT, capture_output=True, text=True).stdout
            n = parse_notes(ocr, p["title"])
            if n:
                notes[p["handle"]] = n
            print(f"{p['handle']:<42} {n or '(none)'}", file=sys.stderr)
        except Exception as e:
            print(f"{p['handle']:<42} ERROR {e}", file=sys.stderr)

    for f in os.listdir(TMP):
        try: os.remove(os.path.join(TMP, f))
        except OSError: pass
    try: os.rmdir(TMP)
    except OSError: pass

    notes = {k: notes[k] for k in sorted(notes)}
    with open(OUT, "w") as f:
        f.write(json.dumps(notes, indent=2) + "\n")
    print(f"\nWrote {len(notes)} notes -> bw-notes.json", file=sys.stderr)


if __name__ == "__main__":
    main()
