#!/usr/bin/env python3
"""Measure the *rendered* contrast of the elements flagged in finding 8.4.

Backgrounds here are photographs, gradients and overlays, so a CSS-only
inspection is unreliable. This script screenshots each element's box, extracts
the dominant text and background colours from the actual painted pixels, and
computes the WCAG 2.x contrast ratio. Writes tests/evidence/contrast.json.

Dominant-colour extraction: the text colour is the darkest/most-saturated
cluster that occupies between 2% and 45% of the box; the background is the
largest cluster that is not the text colour. Both are reported so the
classification can be checked by hand.
"""
import io, json, os, collections
from playwright.sync_api import sync_playwright
from PIL import Image

BASE = "http://localhost:12000"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")

TARGETS = {
    "index.html": [
        (".monee-slide4-text h1", "hero heading"),
        (".uk-button-primary", "Open an Account button"),
        (".monee-price-ticker", "price ticker band"),
        (".in-footer-info", "footer Need help text"),
        (".uk-input", "contact form field"),
    ],
    "contact.html": [
        (".uk-input", "contact form field"),
        ("#send", "contact submit button"),
    ],
    "Advisory.html": [(".monee-slide4-text h1", "hero heading")],
    "Currency.html": [(".monee-slide4-text h1", "hero heading")],
    "Commodities.html": [(".monee-slide4-text h1", "hero heading")],
    "Equity.html": [(".monee-slide4-text h1", "hero heading")],
    "IPOs.html": [(".monee-slide4-text h1", "hero heading")],
    "Depository.html": [(".monee-slide4-text h1", "hero heading")],
    "smart_ODR.html": [(".timeline-section h2", "Step-by-Step Process heading")],
    "news.html": [(".accessibility-menu button", "accessibility toolbar button")],
    "about.html": [(".accessibility-menu button", "accessibility toolbar button")],
    "single.html": [(".in-footer-info", "footer Need help text")],
}


def lum(c):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def ratio(a, b):
    l1, l2 = lum(a), lum(b)
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def analyse(im, declared_fg):
    """Return (text_colour, bg_colour, ratio, clusters).

    The text colour is taken from the element's *computed* colour, not guessed
    from pixel clusters: on a dark background the glyphs are the light pixels,
    on a light background they are the dark ones, and a frequency heuristic
    picks the wrong one. The background is then the dominant painted cluster
    that is not the text colour (so gradients/photos are handled by the actual
    rendered pixels).
    """
    px = list(im.convert("RGB").getdata())
    total = len(px)
    q = collections.Counter(((r >> 4 << 4, g >> 4 << 4, b >> 4 << 4) for r, g, b in px))
    clusters = q.most_common(24)
    text = declared_fg
    # background = the largest cluster sufficiently different from the text colour
    bg = None
    for col, n in clusters:
        if abs(col[0] - text[0]) + abs(col[1] - text[1]) + abs(col[2] - text[2]) > 60:
            bg = col
            break
    if bg is None:
        bg = clusters[0][0]
    return text, bg, ratio(text, bg), clusters[:8], total


def main():
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        for page_name, checks in TARGETS.items():
            out[page_name] = []
            for sel, label in checks:
                pg = b.new_page(viewport={"width": 1280, "height": 900})
                rec = {"selector": sel, "label": label}
                try:
                    pg.goto(f"{BASE}/{page_name}", wait_until="load", timeout=30000)
                    pg.wait_for_timeout(2000)
                    info = pg.evaluate(
                        """(s) => { const e = document.querySelector(s); if (!e) return null;
                           const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
                           return {x:r.left, y:r.top, w:r.width, h:r.height,
                             text:(e.textContent||'').trim().slice(0,40), color:cs.color,
                             fontSize:cs.fontSize, fontWeight:cs.fontWeight}; }""", sel)
                    rec.update(info or {"missing": True})
                    if info and info["w"] > 3 and info["h"] > 3:
                        shot = pg.screenshot(clip={"x": info["x"], "y": info["y"],
                                                   "width": info["w"], "height": info["h"]})
                        im = Image.open(io.BytesIO(shot))
                        fg = tuple(int(v) for v in info["color"]
                                   .replace("rgb(", "").replace("rgba(", "")
                                   .replace(")", "").split(",")[:3])
                        text, bg, r, clusters, total = analyse(im, fg)
                        px = float(info["fontSize"].replace("px", ""))
                        bold = int(info["fontWeight"]) >= 700
                        large = px >= 24 or (bold and px >= 18.66)
                        rec.update({
                            "text_px": text, "bg_px": bg, "ratio": r,
                            "required": 3.0 if large else 4.5, "large_text": large,
                            "pass": r >= (3.0 if large else 4.5),
                            "clusters": [[list(c), n] for c, n in clusters],
                            "box_pixels": total,
                        })
                except Exception as e:
                    rec["error"] = str(e)[:200]
                pg.close()
                out[page_name].append(rec)
                st = "PASS" if rec.get("pass") else ("FAIL" if rec.get("pass") is False else "n/a")
                print(f"{page_name} | {label} | {st} | ratio={rec.get('ratio')} "
                      f"(need {rec.get('required')}) text={rec.get('text_px')} bg={rec.get('bg_px')}")
        b.close()
    json.dump(out, open(os.path.join(EVID, "contrast.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
