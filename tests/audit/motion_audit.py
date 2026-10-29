#!/usr/bin/env python3
"""Verify 2.2.2 Pause, Stop, Hide behaviour: hero slideshow (static?), price
ticker and scrolling-notice pause/play controls, plus prefers-reduced-motion.
Writes tests/evidence/motion.json.
"""
import json, os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:12000"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")

SAMPLE = """() => {
  const el = document.querySelector('.monee-price-ticker');
  const sc = document.querySelector('.scrolling-text, [class*=scrolling]');
  const t = (x) => x ? getComputedStyle(x).transform : null;
  return {ticker: t(el), scrolling: t(sc),
          tickerClass: el ? el.className : null,
          scrollingClass: sc ? sc.className : null};
}"""

SLIDES = """() => [...document.querySelectorAll('.uk-slideshow-items > li')].map(li => {
  const cs = getComputedStyle(li);
  return cs.opacity + '|' + cs.transform + '|' + cs.visibility;
})"""

out = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])

    # --- hero slideshow motion over 8s ---
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(f"{BASE}/index.html", wait_until="load")
    pg.wait_for_timeout(2000)
    a = pg.evaluate(SLIDES)
    pg.wait_for_timeout(8000)
    c = pg.evaluate(SLIDES)
    out["hero_slideshow"] = {
        "slides": len(a), "t0": a, "t8": c, "changed": a != c,
        "container_attrs": pg.evaluate("""() => { const e = document.querySelector('.in-slideshow');
            return e ? [...e.attributes].map(x => x.name + '=' + x.value.slice(0,60)) : null; }"""),
        "pause_control_present": pg.evaluate("""() => !!document.querySelector('.in-slideshow button[aria-label*=pause i], .in-slideshow [aria-pressed]')"""),
    }

    # --- ticker pause control ---
    out["ticker"] = pg.evaluate("""() => {
      const t = document.querySelector('.monee-price-ticker');
      if (!t) return {found: false};
      const btn = t.querySelector('button, [role=button]');
      if (!btn) return {found: true, control: null};
      return {found: true, tag: btn.tagName, cls: btn.className,
              pressed: btn.getAttribute('aria-pressed'),
              label: btn.getAttribute('aria-label'),
              accessibleText: btn.textContent.trim().slice(0, 60)};
    }""")
    if out["ticker"].get("found") and out["ticker"].get("tag"):
        before = pg.evaluate(SAMPLE)
        pg.eval_on_selector(".monee-price-ticker button", "e => e.click()")
        pg.wait_for_timeout(1200)
        after_pause = pg.evaluate(SAMPLE)
        pressed = pg.evaluate("""() => { const b = document.querySelector('.monee-price-ticker button');
            return {pressed: b.getAttribute('aria-pressed'), text: b.textContent.trim().slice(0,60)}; }""")
        pg.wait_for_timeout(2500)
        still = pg.evaluate(SAMPLE)
        pg.eval_on_selector(".monee-price-ticker button", "e => e.click()")
        pg.wait_for_timeout(1200)
        resumed = pg.evaluate(SAMPLE)
        pressed2 = pg.evaluate("""() => { const b = document.querySelector('.monee-price-ticker button');
            return {pressed: b.getAttribute('aria-pressed'), text: b.textContent.trim().slice(0,60)}; }""")
        out["ticker_pause_test"] = {"before": before, "after_pause": after_pause,
                                    "pressed_after_pause": pressed,
                                    "still_after_2.5s": still,
                                    "after_resume": resumed, "pressed_after_resume": pressed2,
                                    "pause_stopped_motion": before != after_pause,
                                    "motion_stayed_stopped": after_pause == still}
    pg.close()

    # --- reduced motion ---
    ctx = b.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
    pg = ctx.new_page()
    pg.goto(f"{BASE}/index.html", wait_until="load")
    pg.wait_for_timeout(2500)
    out["reduced_motion"] = pg.evaluate("""() => {
      const t = document.querySelector('.monee-price-ticker');
      const sc = document.querySelector('[class*=scrolling]');
      const btn = document.querySelector('.monee-price-ticker button');
      return {tickerClass: t ? t.className : null,
              scrollingClass: sc ? sc.className : null,
              tickerPausedClass: t ? t.classList.contains('scrolling-text-paused') : null,
              scrollingPausedClass: sc ? sc.classList.contains('scrolling-text-paused') : null,
              buttonPressed: btn ? btn.getAttribute('aria-pressed') : null,
              prefersReduce: window.matchMedia('(prefers-reduced-motion: reduce)').matches};
    }""")
    ctx.close()

    # --- desktop nav single row ---
    rows = {}
    for w in [1024, 1200, 1280, 1440]:
        pg = b.new_page(viewport={"width": w, "height": 900})
        pg.goto(f"{BASE}/index.html", wait_until="load")
        pg.wait_for_timeout(1800)
        rows[str(w)] = pg.evaluate("""() => {
          const nav = document.querySelector('.in-header-nav, .uk-navbar-nav, header nav');
          if (!nav) return null;
          const items = [...nav.querySelectorAll(':scope > li')].map(li => li.getBoundingClientRect().top);
          const uniq = [...new Set(items.map(t => Math.round(t)))];
          return {items: items.length, distinctRows: uniq.length, rows: uniq,
                  height: Math.round(nav.getBoundingClientRect().height)};
        }""")
        pg.close()
    out["desktop_nav_rows"] = rows
    b.close()

json.dump(out, open(os.path.join(EVID, "motion.json"), "w"), indent=2)
print(json.dumps(out, indent=1))
