#!/usr/bin/env python3
"""Independent verification harness for findings 8.1-8.17.

Runs against the locally served site (python -m http.server 12000) with
Chromium + axe-core and records raw evidence in tests/evidence/verify_*.json.
Every check records what it actually observed; nothing is asserted as passing
without an observed value.
"""
import json, os, sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:12000"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")
AXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "axe.min.js")
PAGES = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
os.makedirs(EVID, exist_ok=True)

FORM_PAGES = ["index.html", "contact.html", "signin.html", "complaint_new.html"]
NAV_PAGES = ["index.html", "contact.html", "products.html", "signin.html"]

JS_HEADINGS = """() => {
  const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  return [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => ({
    level: +h.tagName[1], text: (h.textContent || '').trim().slice(0, 70), visible: vis(h)
  }));
}"""

JS_LABELS = """() => {
  const bad = [];
  document.querySelectorAll('input,select,textarea').forEach(el => {
    const t = (el.getAttribute('type') || '').toLowerCase();
    if (['hidden','submit','button','reset','image'].includes(t)) return;
    // Google's own injected translate/reCAPTCHA widgets are third-party DOM.
    if ((el.id || '').startsWith('goog-gt-')) return;
    if (el.name === 'g-recaptcha-response') return;
    if (el.closest('[id^="accessibilityPanel"]')) return;
    const hasLabel = (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')
      || el.closest('label') || (el.id && document.querySelector('label[for="'+CSS.escape(el.id)+'"]')));
    if (!hasLabel) bad.push({tag: el.tagName, type: el.getAttribute('type'),
      ph: el.getAttribute('placeholder'), id: el.id, outer: el.outerHTML.slice(0,160)});
  });
  return bad;
}"""

JS_AUTOCOMPLETE = """() => {
  const out = [];
  document.querySelectorAll('input').forEach(el => {
    const t = (el.getAttribute('type') || 'text').toLowerCase();
    if (['hidden','submit','button','reset','image','checkbox','radio','file'].includes(t)) return;
    out.push({id: el.id, name: el.getAttribute('name'), type: t,
      autocomplete: el.getAttribute('autocomplete')});
  });
  return out;
}"""

JS_TITLES = """() => document.title"""

JS_IDS = """() => {
  const c = {};
  document.querySelectorAll('[id]').forEach(e => c[e.id] = (c[e.id] || 0) + 1);
  return Object.entries(c).filter(([, n]) => n > 1);
}"""

JS_ALT = """() => [...document.querySelectorAll('img')].filter(i =>
  i.getAttribute('alt') === null && !i.getAttribute('aria-label')
  && i.getAttribute('role') !== 'presentation').map(i => i.getAttribute('src'))"""

JS_IFRAMES = """() => [...document.querySelectorAll('iframe')].map(f =>
  ({src: (f.getAttribute('src')||'').slice(0,90), title: f.getAttribute('title'),
    byScript: f.getAttribute('data-a11y-named') || null}))"""

JS_TARGETS = """() => {
  const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const out = [];
  document.querySelectorAll('a[href],button,input[type=submit],input[type=button],[role=button]').forEach(el => {
    if (!vis(el)) return;
    const r = el.getBoundingClientRect();
    if (r.width < 24 || r.height < 24)
      out.push({tag: el.tagName, text: (el.textContent || el.value || '').trim().slice(0, 45),
                w: Math.round(r.width), h: Math.round(r.height), cls: String(el.className).slice(0, 55)});
  });
  return out;
}"""

JS_OVERFLOW = """() => ({
  docScroll: document.documentElement.scrollWidth,
  docClient: document.documentElement.clientWidth,
  bodyScroll: document.body.scrollWidth,
  hasOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
})"""

JS_FOCUS_STYLES = """() => {
  const out = [];
  const sel = 'a[href],button,input:not([type=hidden]),select,textarea,[tabindex]:not([tabindex="-1"])';
  document.querySelectorAll(sel).forEach((el, i) => {
    if (i > 400) return;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;
    const s = getComputedStyle(el);
    const hasOutline = s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0;
    const hasShadow = s.boxShadow && s.boxShadow !== 'none';
    out.push({tag: el.tagName, cls: String(el.className).slice(0, 40),
      outlineStyle: s.outlineStyle, outlineWidth: s.outlineWidth,
      outlineColor: s.outlineColor, boxShadow: (s.boxShadow||'').slice(0,50),
      anyIndicator: hasOutline || hasShadow});
  });
  return out;
}"""

JS_LABEL_IN_NAME = """() => {
  const out = [];
  document.querySelectorAll('a,button,[role=button]').forEach(el => {
    const vis = (el.textContent || '').trim().replace(/\\s+/g, ' ');
    if (!vis) return;
    const aria = el.getAttribute('aria-label');
    const labelledby = el.getAttribute('aria-labelledby');
    let name = aria;
    if (!name && labelledby) {
      name = labelledby.split(/\\s+/).map(id => {
        const t = document.getElementById(id); return t ? (t.textContent || '').trim() : '';
      }).join(' ').trim();
    }
    if (!name) return; // visible text is the name -> inherently contains it
    const norm = s => s.toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\\s+/g, ' ').trim();
    const v = norm(vis), n = norm(name);
    if (v && !n.includes(v)) out.push({tag: el.tagName, visible: vis.slice(0, 45),
      ariaLabel: name.slice(0, 70), cls: String(el.className).slice(0, 40)});
  });
  return out;
}"""


def new_page(browser, w=1280, h=900):
    pg = browser.new_page(viewport={"width": w, "height": h})
    return pg


def main():
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])

        # ---------- 8.1 / 8.10 / 8.16 / 8.2 / 8.3 / 8.12 / 8.13 ----------
        per_page = {}
        for f in PAGES:
            pg = new_page(b)
            console = []
            pg.on("console", lambda m: console.append({"type": m.type, "text": m.text[:200]}))
            pg.on("pageerror", lambda e: console.append({"type": "pageerror", "text": str(e)[:300]}))
            try:
                pg.goto(f"{BASE}/{f}", wait_until="load", timeout=25000)
                pg.wait_for_timeout(1800)
                rec = {
                    "title": pg.title(),
                    "html_lang": pg.eval_on_selector("html", "e=>e.getAttribute('lang')"),
                    "headings": pg.evaluate(JS_HEADINGS),
                    "duplicate_ids": pg.evaluate(JS_IDS),
                    "images_missing_alt": pg.evaluate(JS_ALT),
                    "iframes": pg.evaluate(JS_IFRAMES),
                    "undersized": pg.evaluate(JS_TARGETS),
                    "overflow_1280": pg.evaluate(JS_OVERFLOW),
                    "label_in_name_violations": pg.evaluate(JS_LABEL_IN_NAME),
                    "console_errors": [c for c in console if c["type"] in ("error", "pageerror")],
                }
                if f in FORM_PAGES:
                    rec["unlabeled"] = pg.evaluate(JS_LABELS)
                    rec["autocomplete"] = pg.evaluate(JS_AUTOCOMPLETE)
            except Exception as e:
                rec = {"error": str(e)}
            per_page[f] = rec
            pg.close()
        out["per_page"] = per_page

        # ---------- 8.5 / 8.6 / reflow at multiple widths ----------
        widths = [320, 400, 640, 893, 894, 895, 1024, 1280, 1440]
        reflow = {}
        for f in ["index.html", "contact.html", "products.html", "news.html", "single.html"]:
            reflow[f] = {}
            for w in widths:
                pg = new_page(b, w, 800)
                pg.goto(f"{BASE}/{f}", wait_until="load")
                pg.wait_for_timeout(1200)
                reflow[f][str(w)] = pg.evaluate(JS_OVERFLOW)
                pg.close()
        out["reflow"] = reflow

        # 8.5 text-only resize 200%
        zoom = {}
        for f in ["index.html", "contact.html", "products.html", "signin.html"]:
            pg = new_page(b, 1280, 900)
            pg.goto(f"{BASE}/{f}", wait_until="load")
            pg.wait_for_timeout(1200)
            pg.evaluate("() => { document.documentElement.style.fontSize = '200%'; }")
            pg.wait_for_timeout(600)
            zoom[f] = pg.evaluate(JS_OVERFLOW)
            pg.close()
        out["text_resize_200pct"] = zoom

        # 8.6 text spacing overrides (WCAG 1.4.12 values)
        SPACING_CSS = """
        * { line-height: 1.5 !important; }
        p, li, h1, h2, h3, h4, h5, h6, div, span, a, label, td, th {
            letter-spacing: 0.12em !important; word-spacing: 0.16em !important; }
        p { margin-bottom: 2em !important; }
        """
        spacing = {}
        for f in ["index.html", "products.html", "news.html", "Currency.html", "Commodities.html", "contact.html"]:
            pg = new_page(b, 1280, 900)
            pg.goto(f"{BASE}/{f}", wait_until="load")
            pg.wait_for_timeout(1200)
            pg.add_style_tag(content=SPACING_CSS)
            pg.wait_for_timeout(800)
            spacing[f] = pg.evaluate(JS_OVERFLOW)
            pg.close()
        out["text_spacing"] = spacing

        b.close()
    json.dump(out, open(os.path.join(EVID, "verify_static.json"), "w"), indent=2)
    print("wrote tests/evidence/verify_static.json")
    # short summary
    print("pages:", len(out["per_page"]))
    print("dupIDs:", {f: r.get("duplicate_ids") for f, r in out["per_page"].items() if r.get("duplicate_ids")})
    print("titles unique:", len({r.get("title") for r in out["per_page"].values()}),
          "of", len(out["per_page"]))
    print("overflow:", {f: {w: v["hasOverflow"] for w, v in d.items() if v["hasOverflow"]}
                        for f, d in out["reflow"].items()})


if __name__ == "__main__":
    main()
