#!/usr/bin/env python3
"""Interactive behaviour tests: skip link, mobile menu, carousel, ticker,
language toggle, focus visibility, accessible names (findings 8.7-8.17)."""
import json, os, sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:12000"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")
os.makedirs(EVID, exist_ok=True)
R = {}


def snap(page, name):
    page.screenshot(path=os.path.join(EVID, name))


def run():
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])

        # ---------- 8.9 skip link ----------
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(BASE + "/index.html", wait_until="load")
        pg.wait_for_timeout(800)
        sl = pg.query_selector(".skip-link")
        R["skip_link"] = {}
        if sl:
            box_before = sl.bounding_box()
            pg.keyboard.press("Tab")
            pg.wait_for_timeout(400)
            focused = pg.evaluate("() => {const a=document.activeElement; return {cls:a.className, tag:a.tagName, text:(a.textContent||'').trim().slice(0,40), rect:a.getBoundingClientRect().toJSON()};}")
            R["skip_link"] = {"exists": True, "box_unfocused": box_before, "after_tab": focused}
            snap(pg, "skiplink_focused.png")
            # activate
            pg.keyboard.press("Enter")
            pg.wait_for_timeout(600)
            R["skip_link"]["after_enter_hash"] = pg.evaluate("()=>location.hash")
            R["skip_link"]["active_after_enter"] = pg.evaluate("()=>{const a=document.activeElement; return a.id||a.tagName}")
        else:
            R["skip_link"] = {"exists": False}
        pg.close()

        # ---------- 8.7 mobile menu ----------
        for w in [893, 894, 895, 400, 320]:
            pg = b.new_page(viewport={"width": w, "height": 900})
            pg.goto(BASE + "/index.html", wait_until="load")
            pg.wait_for_timeout(900)
            btn = pg.query_selector('[data-uk-toggle="target: #mobile-nav-modal"]')
            rec = {"width": w, "toggle_present": bool(btn)}
            if btn:
                rec["visible"] = btn.is_visible()
                rec["name"] = btn.get_attribute("aria-label")
                rec["expanded_before"] = btn.get_attribute("aria-expanded")
                try:
                    btn.click()
                    pg.wait_for_timeout(700)
                    rec["expanded_after_click"] = btn.get_attribute("aria-expanded")
                    rec["modal_open"] = pg.evaluate("()=>{const m=document.getElementById('mobile-nav-modal'); return m? m.className + ' | display='+getComputedStyle(m).display : null;}")
                    # keyboard open test
                    pg.keyboard.press("Escape")
                    pg.wait_for_timeout(400)
                    rec["expanded_after_esc"] = btn.get_attribute("aria-expanded")
                except Exception as e:
                    rec["click_error"] = str(e)
            R.setdefault("mobile_menu", []).append(rec)
            pg.close()

        # keyboard-only open at 400
        pg = b.new_page(viewport={"width": 400, "height": 900})
        pg.goto(BASE + "/index.html", wait_until="load")
        pg.wait_for_timeout(900)
        # tab to the toggle
        found = False
        for i in range(60):
            pg.keyboard.press("Tab")
            cur = pg.evaluate("()=>{const a=document.activeElement; return {tag:a.tagName, label:a.getAttribute&&a.getAttribute('aria-label'), cls:(a.className||'').toString().slice(0,40)};}")
            if cur.get("label") == "Open mobile navigation menu":
                found = True
                break
        kb = {"reached_toggle_by_tab": found, "tabs": i + 1}
        if found:
            pg.keyboard.press("Enter")
            pg.wait_for_timeout(700)
            kb["expanded_after_enter"] = pg.evaluate("()=>document.querySelector('[data-uk-toggle=\\'target: #mobile-nav-modal\\']').getAttribute('aria-expanded')")
            kb["nav_visible"] = pg.evaluate("()=>{const m=document.getElementById('mobile-nav-modal'); const r=m.getBoundingClientRect(); return r.width>0&&getComputedStyle(m).display!=='none';}")
            # is About Us reachable?
            kb["about_link_present"] = pg.evaluate("()=>!!document.querySelector('#mobile-nav-modal a[href=\\'about.html\\']')")
        R["mobile_menu_keyboard"] = kb
        pg.close()

        # ---------- 8.8 carousel + ticker ----------
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(BASE + "/index.html", wait_until="load")
        pg.wait_for_timeout(1500)
        R["motion"] = pg.evaluate(r"""() => {
          const out = {};
          const slides = document.querySelectorAll('.uk-slideshow-items > li');
          out.slide_count = slides.length;
          out.slideshow_autoplay_attr = !!document.querySelector('[data-uk-slideshow*="autoplay"]');
          out.slider_autoplay_attr = !!document.querySelector('[data-uk-slider*="autoplay"]');
          const toggles = [...document.querySelectorAll('.moving-content-toggle')];
          out.pause_buttons = toggles.map(t => ({label:(t.textContent||'').trim(), aria_pressed:t.getAttribute('aria-pressed'), name:t.getAttribute('aria-label')}));
          return out;
        }""")
        # test pause actually stops ticker: sample transform over time
        def ticker_pos():
            return pg.evaluate("()=>{const el=document.querySelector('.uk-slider-items'); return el? el.getBoundingClientRect().x : null;}")
        t0 = ticker_pos(); pg.wait_for_timeout(1200); t1 = ticker_pos()
        btn = pg.query_selector(".moving-content-toggle")
        R["motion"]["ticker_moving_before_pause"] = (t0 != t1)
        if btn:
            btn.click(); pg.wait_for_timeout(300)
            R["motion"]["aria_pressed_after"] = btn.get_attribute("aria-pressed")
            a0 = ticker_pos(); pg.wait_for_timeout(1200); a1 = ticker_pos()
            R["motion"]["ticker_moving_while_paused"] = (a0 != a1)
            btn.click(); pg.wait_for_timeout(300)
            R["motion"]["aria_pressed_resumed"] = btn.get_attribute("aria-pressed")
        pg.close()

        # ---------- 8.12 accessible names (label in name) ----------
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(BASE + "/index.html", wait_until="load")
        pg.wait_for_timeout(900)
        R["label_in_name"] = pg.evaluate(r"""() => {
          const res = [];
          document.querySelectorAll('a[aria-label],button[aria-label]').forEach(el => {
            const vis = (el.textContent||'').trim();
            if (!vis) return;
            const name = el.getAttribute('aria-label');
            res.push({visible: vis.slice(0,40), name: name.slice(0,60), contains: name.toLowerCase().includes(vis.toLowerCase().slice(0,10))});
          });
          return res.filter(x => !x.contains);
        }""")
        pg.close()

        # ---------- 8.11 focus visibility ----------
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(BASE + "/index.html", wait_until="load")
        pg.wait_for_timeout(900)
        R["focus"] = pg.evaluate(r"""() => {
          const out = [];
          const els = [...document.querySelectorAll('a[href],button,input,select,textarea,[tabindex]')].slice(0,40);
          for (const el of els) {
            el.focus();
            const s = getComputedStyle(el);
            out.push({tag: el.tagName, text:(el.textContent||'').trim().slice(0,25),
                      outline: s.outlineStyle + ' ' + s.outlineWidth + ' ' + s.outlineColor});
          }
          const noOutline = out.filter(o => o.outline.startsWith('none') || o.outline.includes('0px'));
          return {tested: out.length, no_outline_count: noOutline.length, samples: noOutline.slice(0,8)};
        }""")
        pg.close()

        # ---------- 8.14 language toggle ----------
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(BASE + "/index.html", wait_until="load")
        pg.wait_for_timeout(2000)
        R["lang_toggle"] = pg.evaluate(r"""() => {
          const out = {};
          out.html_lang_before = document.documentElement.lang;
          const gt = document.querySelector('.goog-te-combo, select.goog-te-combo');
          out.google_translate_present = !!gt;
          out.lang_controls = [...document.querySelectorAll('[id*="lang"], [class*="lang"], a[onclick*="lang"], button[onclick*="lang"]')].slice(0,10).map(e => ({tag:e.tagName, id:e.id, cls:(e.className||'').toString().slice(0,40), text:(e.textContent||'').trim().slice(0,20)}));
          out.google_translate_script = !!document.querySelector('script[src*="translate.google"]');
          return out;
        }""")
        pg.close()

        # ---------- 8.17 console errors on load (index) ----------
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
        pg.on("console", lambda m: errs.append("CONSOLE-" + m.type + ": " + m.text) if m.type == "error" else None)
        pg.goto(BASE + "/index.html", wait_until="load")
        pg.wait_for_timeout(2500)
        R["console_index"] = errs
        pg.close()

        b.close()


if __name__ == "__main__":
    run()
    json.dump(R, open(os.path.join(EVID, "interactive.json"), "w"), indent=2)
    print(json.dumps(R, indent=2))
