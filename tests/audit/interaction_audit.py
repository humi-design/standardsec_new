#!/usr/bin/env python3
"""Keyboard, mobile-menu, focus-visibility, form-validation and console-error
audit. Records observed behaviour in tests/evidence/interaction.json.
"""
import json, os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:12000"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")
res = {}


def snap_menu(pg):
    return pg.evaluate("""() => {
      const t = document.querySelector('.in-mobile-nav button[data-uk-toggle]');
      const m = document.getElementById('mobile-nav-modal');
      if (!t || !m) return null;
      return {expanded: t.getAttribute('aria-expanded'),
              label: t.getAttribute('aria-label'),
              controls: t.getAttribute('aria-controls'),
              modalOpen: m.classList.contains('uk-open'),
              modalVisible: getComputedStyle(m).display !== 'none' && m.getBoundingClientRect().height > 0};
    }""")


def focus_ring(pg, sel):
    return pg.evaluate("""(s) => {
      const el = document.querySelector(s);
      if (!el) return null;
      el.focus();
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      return {tag: el.tagName, outlineStyle: cs.outlineStyle, outlineWidth: cs.outlineWidth,
              outlineColor: cs.outlineColor, boxShadow: (cs.boxShadow || '').slice(0, 70),
              rect: {w: Math.round(r.width), h: Math.round(r.height)},
              visible: r.width > 0 && r.height > 0};
    }""", sel)


with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])

    # ---- 8.7 mobile menu at the breakpoint ----
    menu = {}
    for w in [375, 640, 893, 894, 895, 960, 1024]:
        pg = b.new_page(viewport={"width": w, "height": 900})
        pg.goto(f"{BASE}/index.html", wait_until="load")
        pg.wait_for_timeout(1600)
        toggle_visible = pg.evaluate("""() => {
          const t = document.querySelector('.in-mobile-nav button[data-uk-toggle]');
          if (!t) return false;
          const r = t.getBoundingClientRect();
          return r.width > 0 && r.height > 0;
        }""")
        rec = {"toggle_visible": toggle_visible, "initial": snap_menu(pg)}
        if toggle_visible:
            pg.eval_on_selector('.in-mobile-nav button[data-uk-toggle]', 'e => e.click()')
            pg.wait_for_timeout(900)
            rec["after_pointer_open"] = snap_menu(pg)
            rec["nav_links_visible"] = pg.evaluate("""() => {
              const m = document.getElementById('mobile-nav-modal');
              return [...m.querySelectorAll('a[href]')].filter(a => {
                const r = a.getBoundingClientRect(); return r.width > 0 && r.height > 0;
              }).map(a => a.textContent.trim()).slice(0, 14);
            }""")
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(700)
            rec["after_escape"] = snap_menu(pg)
            rec["focus_after_escape"] = pg.evaluate("() => document.activeElement.tagName + '.' + document.activeElement.className.slice(0,40)")
        menu[str(w)] = rec
        pg.close()
    res["mobile_menu"] = menu

    # ---- 8.7 keyboard open with Enter / Space ----
    kb = {}
    for key in ["Enter", "Space"]:
        pg = b.new_page(viewport={"width": 375, "height": 900})
        pg.goto(f"{BASE}/index.html", wait_until="load")
        pg.wait_for_timeout(1600)
        pg.evaluate("""() => document.querySelector('.in-mobile-nav button[data-uk-toggle]').focus()""")
        pg.keyboard.press("Enter" if key == "Enter" else " ")
        pg.wait_for_timeout(800)
        kb[key] = snap_menu(pg)
        pg.close()
    res["keyboard_menu_open"] = kb

    # ---- 8.11 focus visible on key controls ----
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(f"{BASE}/index.html", wait_until="load")
    pg.wait_for_timeout(1800)
    sels = [".skip-link", "a.uk-button-primary", ".accessibility-menu .fab",
            ".moving-content-toggle", "footer a", ".in-mobile-nav button[data-uk-toggle]",
            "#open-account-form input", "#open-account-form button[type=submit]"]
    res["focus_rings"] = {s: focus_ring(pg, s) for s in sels}

    # ---- 8.15 form validation: homepage create-account ----
    pg.goto(f"{BASE}/index.html", wait_until="load")
    pg.wait_for_timeout(1800)
    pg.evaluate("() => document.getElementById('open-account-form').scrollIntoView()")
    pg.evaluate("() => document.getElementById('open-account-form').requestSubmit()")
    pg.wait_for_timeout(900)
    res["create_account_empty_submit"] = pg.evaluate("""() => {
      const f = document.getElementById('open-account-form');
      const errs = [...f.querySelectorAll('.form-error, [role=alert], [aria-live]')]
        .map(e => ({id: e.id, text: (e.textContent||'').trim().slice(0,80), live: e.getAttribute('aria-live')}))
        .filter(e => e.text);
      return {invalid: [...f.querySelectorAll('[aria-invalid=true]')].map(e => e.id),
              describedby: [...f.querySelectorAll('input')].map(e => ({id:e.id, d:e.getAttribute('aria-describedby')})),
              errors: errs, status: (document.getElementById('form-status')||{}).textContent,
              url: location.href};
    }""")
    # malformed email
    pg.fill("#signup-name", "Test User")
    pg.fill("#signup-email", "not-an-email")
    pg.fill("#phone", "12345")
    pg.evaluate("() => document.getElementById('open-account-form').requestSubmit()")
    pg.wait_for_timeout(900)
    res["create_account_bad_email"] = pg.evaluate("""() => {
      const f = document.getElementById('open-account-form');
      return {invalid: [...f.querySelectorAll('[aria-invalid=true]')].map(e => e.id),
              errors: [...f.querySelectorAll('.form-error')].map(e => ({id:e.id, t:(e.textContent||'').trim().slice(0,80)})).filter(e=>e.t),
              status: (document.getElementById('form-status')||{}).textContent};}""")
    # valid input (must not navigate / must not hit a backend)
    pg.fill("#signup-name", "Test User")
    pg.fill("#signup-email", "test@example.com")
    pg.fill("#phone", "9876543210")
    nav = []
    pg.on("request", lambda r: nav.append(r.url) if r.method == "POST" else None)
    pg.evaluate("() => document.getElementById('open-account-form').requestSubmit()")
    pg.wait_for_timeout(1200)
    res["create_account_valid"] = pg.evaluate("""() => {
      const f = document.getElementById('open-account-form');
      return {invalid: [...f.querySelectorAll('[aria-invalid=true]')].map(e => e.id),
              errors: [...f.querySelectorAll('.form-error')].map(e => (e.textContent||'').trim()).filter(Boolean),
              status: (document.getElementById('form-status')||{}).textContent, url: location.href};}""")
    res["create_account_valid"]["post_requests"] = nav
    pg.close()

    # ---- 8.15 contact form validation (no backend submit) ----
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(f"{BASE}/contact.html", wait_until="load")
    pg.wait_for_timeout(1800)
    pg.evaluate("() => document.getElementById('contact-form').scrollIntoView()")
    posts = []
    pg.on("request", lambda r: posts.append(r.url) if r.method == "POST" else None)
    pg.evaluate("() => document.getElementById('contact-form').requestSubmit()")
    pg.wait_for_timeout(900)
    res["contact_empty_submit"] = pg.evaluate("""() => {
      const f = document.getElementById('contact-form');
      return {invalid: [...f.querySelectorAll('[aria-invalid=true]')].map(e => e.id),
              errors: [...f.querySelectorAll('.form-error')].map(e => ({id:e.id,t:(e.textContent||'').trim().slice(0,70)})).filter(e=>e.t),
              summary: (document.getElementById('errorSummary')||{}).textContent,
              focused: document.activeElement.id, url: location.href};}""")
    pg.fill("#name", "Test User")
    pg.fill("#email", "bad-email")
    pg.fill("#message", "short")
    pg.evaluate("() => document.getElementById('contact-form').requestSubmit()")
    pg.wait_for_timeout(900)
    res["contact_invalid_submit"] = pg.evaluate("""() => {
      const f = document.getElementById('contact-form');
      return {invalid: [...f.querySelectorAll('[aria-invalid=true]')].map(e => e.id),
              errors: [...f.querySelectorAll('.form-error')].map(e => ({id:e.id,t:(e.textContent||'').trim().slice(0,70)})).filter(e=>e.t),
              summary: (document.getElementById('errorSummary')||{}).textContent,
              focused: document.activeElement.id, url: location.href};}""")
    res["contact_invalid_submit"]["post_requests"] = posts
    pg.close()

    # ---- 8.17 console errors on load + interaction ----
    console = {}
    for f in ["index.html", "contact.html", "signin.html", "smart_ODR.html", "news.html",
              "products.html", "about.html", "complaint_new.html"]:
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        logs = []
        pg.on("console", lambda m: logs.append({"type": m.type, "text": m.text[:220]}))
        pg.on("pageerror", lambda e: logs.append({"type": "pageerror", "text": str(e)[:300]}))
        pg.on("requestfailed", lambda r: logs.append({"type": "requestfailed",
                                                      "text": r.url[:160] + " :: " + str(r.failure)[:80]}))
        pg.goto(f"{BASE}/{f}", wait_until="load")
        pg.wait_for_timeout(2500)
        pg.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
        pg.wait_for_timeout(1200)
        console[f] = {
            "pageerrors": [x for x in logs if x["type"] == "pageerror"],
            "console_errors": [x for x in logs if x["type"] == "error"],
            "request_failed": [x for x in logs if x["type"] == "requestfailed"],
        }
        pg.close()
    res["console"] = console

    b.close()

json.dump(res, open(os.path.join(EVID, "interaction.json"), "w"), indent=2)

print("=== mobile menu (aria-expanded / modal) ===")
for w, r in res["mobile_menu"].items():
    print(f"  {w}px toggle={r['toggle_visible']} init={r['initial']}")
    if "after_pointer_open" in r:
        print(f"        open={r['after_pointer_open']}")
        print(f"        esc={r['after_escape']} focus={r.get('focus_after_escape')}")
print("=== keyboard menu open ===", json.dumps(res["keyboard_menu_open"]))
print("=== focus rings ===")
for s, r in res["focus_rings"].items():
    print(f"  {s}: {r}")
print("=== create account empty ===", json.dumps(res["create_account_empty_submit"])[:500])
print("=== create account bad email ===", json.dumps(res["create_account_bad_email"])[:400])
print("=== create account valid ===", json.dumps(res["create_account_valid"])[:400])
print("=== contact empty ===", json.dumps(res["contact_empty_submit"])[:500])
print("=== contact invalid ===", json.dumps(res["contact_invalid_submit"])[:500])
print("=== console ===")
for f, r in res["console"].items():
    print(f"  {f}: pageerrors={len(r['pageerrors'])} consoleErrors={len(r['console_errors'])} reqFailed={len(r['request_failed'])}")
    for x in r["pageerrors"][:3]:
        print("      PE:", x["text"][:160])
    for x in r["console_errors"][:3]:
        print("      CE:", x["text"][:160])
