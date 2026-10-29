#!/usr/bin/env python3
"""Verify the smart_ODR.html 'Step-by-Step Process' contrast warning.

The heading is white text sitting on a `linear-gradient(135deg, #1a237e,
#0d47a1)` section background. A contrast checker that only reads the declared
background-color on the heading (rgba(0,0,0,0)) reports the ratio as
"undetermined", which is what the earlier run flagged.

This script reads the real gradient stops from the painted section, computes
the contrast against every stop (the worst case is the lightest stop), and
saves a screenshot crop of the heading as visual evidence.
"""
import io, json, os, collections
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")


def lum(c):
    def f(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def ratio(a, b):
    l1, l2 = lum(a), lum(b)
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def run(width, height, tag):
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": width, "height": height})
        pg.goto("http://localhost:12000/smart_ODR.html", wait_until="load", timeout=30000)
        pg.wait_for_timeout(2200)
        pg.evaluate("""() => { const h=[...document.querySelectorAll('h2')]
            .find(e=>/Step-by-Step/i.test(e.textContent)); if(h) h.scrollIntoView({block:'center'}); }""")
        pg.wait_for_timeout(700)
        info = pg.evaluate("""() => {
            const h = [...document.querySelectorAll('h2')].find(e => /Step-by-Step/i.test(e.textContent));
            const r = h.getBoundingClientRect();
            const cs = getComputedStyle(h);
            const sec = h.closest('section');
            const img = sec ? getComputedStyle(sec).backgroundImage : '';
            const stops = [...String(img).matchAll(/rgba?\\(([^)]+)\\)/g)]
                .map(m => m[1].split(',').slice(0,3).map(Number));
            return {x:r.left, y:r.top, w:r.width, h:r.height, text:h.textContent.trim(),
                    color:cs.color, fontSize:cs.fontSize, fontWeight:cs.fontWeight,
                    sectionImage: img, gradientStops: stops};
        }""")
        crop = pg.screenshot(clip={"x": info["x"], "y": info["y"],
                                   "width": info["w"], "height": info["h"]})
        img = Image.open(io.BytesIO(crop)).convert("RGB")
        q = collections.Counter((r >> 4 << 4, g >> 4 << 4, b >> 4 << 4) for r, g, b in img.getdata())
        b.close()

    fg = tuple(int(v) for v in info["color"].replace("rgb(", "").replace(")", "").split(","))
    px = float(info["fontSize"].replace("px", ""))
    bold = int(info["fontWeight"]) >= 700
    large = px >= 24 or (bold and px >= 18.66)
    required = 3.0 if large else 4.5
    per_stop = [{"stop": s, "ratio": ratio(fg, tuple(s))} for s in info["gradientStops"]]
    worst = min(x["ratio"] for x in per_stop) if per_stop else None
    # also report the dominant painted background colour for cross-checking
    bg_px = q.most_common(1)[0][0]
    return {"viewport": f"{width}x{height}", "screenshot": tag,
            "text": info["text"], "text_color": info["color"],
            "font_size_px": px, "bold": bold, "large_text": large, "required": required,
            "section_background_image": info["sectionImage"],
            "contrast_vs_each_gradient_stop": per_stop,
            "worst_case_ratio": worst,
            "dominant_painted_bg_px": list(bg_px),
            "ratio_vs_dominant_painted_bg": ratio(fg, tuple(bg_px)),
            "pass": worst is not None and worst >= required,
            "dominant_clusters": [[list(c), n] for c, n in q.most_common(6)]}


if __name__ == "__main__":
    os.makedirs(EVID, exist_ok=True)
    out = [run(1280, 900, "smart_odr_step_heading_1280.png"),
           run(400, 800, "smart_odr_step_heading_400.png")]
    # save visual evidence
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        for w, h, name in [(1280, 900, "smart_odr_step_heading_1280.png"),
                           (400, 800, "smart_odr_step_heading_400.png")]:
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.goto("http://localhost:12000/smart_ODR.html", wait_until="load")
            pg.wait_for_timeout(2200)
            pg.evaluate("""() => { const x=[...document.querySelectorAll('h2')]
                .find(e=>/Step-by-Step/i.test(e.textContent)); if(x) x.scrollIntoView({block:'center'}); }""")
            pg.wait_for_timeout(700)
            box = pg.evaluate("""(vw) => { const x=[...document.querySelectorAll('h2')]
                .find(e=>/Step-by-Step/i.test(e.textContent)); const r=x.getBoundingClientRect();
                return {x:Math.max(0,r.left-20), y:Math.max(0,r.top-20),
                        width:Math.min(r.width+40, vw), height:r.height+40}; }""", w)
            pg.screenshot(path=os.path.join(EVID, name),
                          clip={"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]})
            pg.close()
        b.close()
    json.dump(out, open(os.path.join(EVID, "smart_odr_contrast.json"), "w"), indent=2)
    for r in out:
        print(json.dumps(r, indent=1))
