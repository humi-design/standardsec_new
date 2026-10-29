#!/usr/bin/env python3
"""Verify 3.1.2 Language of Parts / the language-switching control.

The previous English/Hindi toggle was replaced with a Google Translate widget
(EN <-> HI). This drives the widget for real: open the menu, choose Hindi,
check that the visible text changes and that <html lang> updates, then switch
back to English and confirm both revert. Writes tests/evidence/language.json.
"""
import json, os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:12000"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")

STATE = """() => ({
  htmlLang: document.documentElement.lang,
  htmlClass: document.documentElement.className,
  h1: (document.querySelector('h1') || {}).textContent?.trim().slice(0, 60) || null,
  h2: (document.querySelector('h2') || {}).textContent?.trim().slice(0, 60) || null,
  banner: !!document.querySelector('.goog-te-banner-frame'),
  controlText: (document.querySelector('.goog-te-gadget-simple') || {}).innerText?.trim() || null
})"""

out = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(f"{BASE}/index.html", wait_until="load")
    pg.wait_for_timeout(3500)

    out["control"] = pg.evaluate("""() => {
      const a = document.querySelector('.goog-te-gadget-simple a');
      const host = document.getElementById('google_translate_element_index');
      const dup = document.getElementById('google_translate_element_index_hidden');
      if (!a) return {found: false};
      const r = a.getBoundingClientRect();
      return {found: true, text: a.innerText.trim(), ariaLabel: a.getAttribute('aria-label'),
              ariaHaspopup: a.getAttribute('aria-haspopup'), href: a.getAttribute('href'),
              width: Math.round(r.width), height: Math.round(r.height),
              hostRole: host ? host.getAttribute('role') : null,
              hostLabel: host ? host.getAttribute('aria-label') : null,
              duplicateHiddenHost: dup ? {ariaHidden: dup.getAttribute('aria-hidden'),
                                          display: getComputedStyle(dup).display} : null};
    }""")
    out["english_initial"] = pg.evaluate(STATE)

    # keyboard: focus the widget and open it
    pg.evaluate("() => document.querySelector('.goog-te-gadget-simple a')?.focus()")
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(1500)
    out["menu_after_enter"] = pg.evaluate("""() => [...document.querySelectorAll('iframe.skiptranslate')]
        .map(f => ({w: Math.round(f.getBoundingClientRect().width),
                    h: Math.round(f.getBoundingClientRect().height)}))""")

    # choose Hindi inside the same-origin menu frame
    chosen = False
    for fr in pg.frames:
        try:
            if fr.locator("text=Hindi").count():
                fr.click("text=Hindi", timeout=5000)
                chosen = True
                break
        except Exception:
            continue
    out["hindi_selected"] = chosen
    pg.wait_for_timeout(4500)
    out["hindi_state"] = pg.evaluate(STATE)
    pg.screenshot(path=os.path.join(EVID, "language_hindi_index.png"), full_page=False)

    # switch back to English
    pg.evaluate("() => document.querySelector('.goog-te-gadget-simple a')?.focus()")
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(1500)
    back = False
    for fr in pg.frames:
        try:
            if fr.locator("text=English").count():
                fr.click("text=English", timeout=5000)
                back = True
                break
        except Exception:
            continue
    out["english_reselected"] = back
    pg.wait_for_timeout(4500)
    out["english_after_switch_back"] = pg.evaluate(STATE)
    pg.close()
    b.close()

json.dump(out, open(os.path.join(EVID, "language.json"), "w"), indent=2)
print(json.dumps(out, indent=1))
