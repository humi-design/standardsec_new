#!/usr/bin/env python3
"""Verify the desktop navigation stays on one row, switches to the hamburger
before it can overflow, and never produces horizontal page overflow.

Writes tests/evidence/nav_layout.json and desktop/mobile screenshots.
"""
import json, os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:12000"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")
NAVDIR = os.path.join(EVID, "nav")
WIDTHS = [320, 375, 400, 640, 768, 894, 895, 959, 960, 1000, 1024, 1100, 1280, 1440, 1600, 1920]

PROBE = r"""
() => {
  const nav = document.querySelector('nav.uk-navbar-container');
  const ul = nav ? nav.querySelector('.uk-navbar-nav') : null;
  const mob = document.querySelector('.in-mobile-nav');
  const navVisible = nav && getComputedStyle(nav).display !== 'none' &&
                     nav.getBoundingClientRect().width > 0;
  const mobVisible = mob && getComputedStyle(mob).display !== 'none' &&
                     mob.getBoundingClientRect().width > 0;
  const links = ul ? [...ul.children].filter(li => li.textContent.trim()) : [];
  const rects = links.map(li => { const r = li.getBoundingClientRect();
      return {text: li.textContent.trim().slice(0, 14), top: Math.round(r.top),
              left: Math.round(r.left), w: Math.round(r.width)}; });
  const rows = [...new Set(rects.map(r => r.top))].sort((a, b) => a - b);
  // is the last link clipped by the nav box?
  let clipped = false;
  if (nav && links.length) {
    const nr = nav.getBoundingClientRect();
    const last = links[links.length - 1].getBoundingClientRect();
    clipped = last.right > nr.right + 1;
  }
  return {
    navVisible, mobileToggleVisible: mobVisible,
    links: rects.map(r => r.text), linkCount: rects.length,
    rows: rows.length, rowTops: rows,
    navW: nav ? Math.round(nav.getBoundingClientRect().width) : 0,
    navScrollW: nav ? nav.scrollWidth : 0,
    ulScrollW: ul ? ul.scrollWidth : 0,
    contentW: Math.round(rects.reduce((s, r) => s + r.w, 0)),
    clipped,
    docOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
    docScrollW: document.documentElement.scrollWidth,
    clientW: document.documentElement.clientWidth,
    flexWrap: ul ? getComputedStyle(ul).flexWrap : null,
  };
}
"""

out = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    for w in WIDTHS:
        pg = b.new_page(viewport={"width": w, "height": 900})
        pg.goto(f"{BASE}/index.html", wait_until="load", timeout=30000)
        pg.wait_for_timeout(1800)
        d = pg.evaluate(PROBE)
        # acceptance: desktop menu -> 1 row, no clip, no overflow.
        #             hamburger     -> no desktop row at all.
        if d["navVisible"]:
            d["layout"] = "desktop"
            d["ok"] = (d["rows"] == 1 and not d["clipped"] and not d["docOverflow"])
        elif d["mobileToggleVisible"]:
            d["layout"] = "mobile-hamburger"
            d["ok"] = not d["docOverflow"]
        else:
            d["layout"] = "unknown"
            d["ok"] = False
        out[str(w)] = d
        if w in (1280, 1440):
            pg.screenshot(path=os.path.join(NAVDIR, f"after_{w}.png"), clip={"x": 0, "y": 0, "width": w, "height": 280})
        if w in (375, 768):
            pg.screenshot(path=os.path.join(NAVDIR, f"mobile_{w}.png"), clip={"x": 0, "y": 0, "width": w, "height": 280})
        pg.close()
    b.close()

json.dump(out, open(os.path.join(EVID, "nav_layout.json"), "w"), indent=2)
fails = [w for w, d in out.items() if not d["ok"]]
print(f"{'width':>6} {'layout':<17} {'rows':>4} {'links':>5} {'contentW':>8} {'navW':>6} {'clip':>5} {'overflow':>8}  ok")
for w, d in out.items():
    print(f"{w:>6} {d['layout']:<17} {d['rows']:>4} {d['linkCount']:>5} {d['contentW']:>8} "
          f"{d['navW']:>6} {str(d['clipped']):>5} {str(d['docOverflow']):>8}  {d['ok']}")
print()
print("FAILURES:", fails if fails else "none")
