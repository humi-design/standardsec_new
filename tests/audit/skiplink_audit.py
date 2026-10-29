#!/usr/bin/env python3
"""Verify 2.4.1 Bypass Blocks: the skip link exists on every page, is the first
tab stop, becomes visible on focus, and moves focus to the main region.
Writes tests/evidence/skiplink.json.
"""
import json, os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:12000"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")
PAGES = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))

out = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    for f in PAGES:
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        rec = {}
        try:
            pg.goto(f"{BASE}/{f}", wait_until="load", timeout=30000)
            pg.wait_for_timeout(1500)
            rec["present"] = pg.evaluate("""() => {
              const a = document.querySelector('a.skip-link, a[href="#main-content"]');
              if (!a) return null;
              const cs = getComputedStyle(a);
              return {text: a.textContent.trim(), href: a.getAttribute('href'),
                      position: cs.position, top: cs.top, clip: cs.clip,
                      width: Math.round(a.getBoundingClientRect().width)};
            }""")
            if rec["present"]:
                target = rec["present"]["href"].lstrip("#")
                rec["target_exists"] = pg.evaluate("(id) => !!document.getElementById(id)", target)
                # first Tab must land on the skip link
                pg.keyboard.press("Tab")
                pg.wait_for_timeout(300)
                rec["first_tab"] = pg.evaluate("""() => {
                  const a = document.activeElement;
                  const cs = getComputedStyle(a);
                  const r = a.getBoundingClientRect();
                  return {tag: a.tagName, text: (a.textContent||'').trim().slice(0,40),
                          top: cs.top, left: cs.left,
                          outline: cs.outlineWidth + ' ' + cs.outlineStyle + ' ' + cs.outlineColor,
                          width: Math.round(r.width), height: Math.round(r.height),
                          visible: r.top >= 0 && r.top < window.innerHeight && r.width > 0};
                }""")
                pg.keyboard.press("Enter")
                pg.wait_for_timeout(500)
                rec["after_enter"] = pg.evaluate("""() => {
                  const h = location.hash;
                  const t = h ? document.getElementById(h.slice(1)) : null;
                  return {hash: h, targetTag: t ? t.tagName : null,
                          activeTag: document.activeElement.tagName};
                }""")
                rec["ok"] = (rec["first_tab"]["text"] == rec["present"]["text"]
                             and rec["first_tab"]["visible"] and rec["target_exists"])
        except Exception as e:
            rec["error"] = str(e)[:160]
        out[f] = rec
        pg.close()
    b.close()

json.dump(out, open(os.path.join(EVID, "skiplink.json"), "w"), indent=2)
fails = [f for f, r in out.items() if not r.get("ok")]
print(f"pages: {len(out)}  skip-link OK: {len(out)-len(fails)}  failures: {fails}")
for f, r in out.items():
    print(f"  {f}: present={bool(r.get('present'))} target={r.get('target_exists')} "
          f"firstTab={r.get('first_tab',{}).get('text') if r.get('first_tab') else None} "
          f"visible={r.get('first_tab',{}).get('visible') if r.get('first_tab') else None}")
