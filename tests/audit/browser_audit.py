#!/usr/bin/env python3
"""Browser-based verification harness for the Standard Securities WCAG 2.2 audit.

Runs against the locally served site (python -m http.server 12000) and records
evidence for findings 8.1-8.17 in tests/evidence/browser_audit.json.
"""
import json, os, sys, re
from playwright.sync_api import sync_playwright

BASE = "http://localhost:12000"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")
PAGES = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))

os.makedirs(EVID, exist_ok=True)


def collect_console(page, sink):
    page.on("console", lambda m: sink.append({"type": m.type, "text": m.text}))
    page.on("pageerror", lambda e: sink.append({"type": "pageerror", "text": str(e)}))


JS_DOM_AUDIT = r"""
() => {
  const out = {};
  const vis = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
  };
  // duplicate ids
  const ids = {};
  document.querySelectorAll('[id]').forEach(e => ids[e.id] = (ids[e.id]||0)+1);
  out.duplicate_ids = Object.entries(ids).filter(([k,v]) => v>1);
  // headings
  out.headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => ({
    level: +h.tagName[1], text: (h.textContent||'').trim().slice(0,80), visible: vis(h)
  }));
  // images
  out.images_missing_alt = [...document.querySelectorAll('img')].filter(i =>
     i.getAttribute('alt')===null && !i.getAttribute('aria-label') && i.getAttribute('role')!=='presentation'
  ).map(i => i.getAttribute('src'));
  // iframes
  out.iframes = [...document.querySelectorAll('iframe')].map(f => ({
     src: f.getAttribute('src'), title: f.getAttribute('title')
  }));
  // inputs and labels
  out.unlabeled = [...document.querySelectorAll('input,select,textarea')].filter(el => {
    const t = (el.getAttribute('type')||'').toLowerCase();
    if (['hidden','submit','button','reset','image'].includes(t)) return false;
    if (el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')) return false;
    if (el.closest('label')) return false;
    if (el.id && document.querySelector('label[for="'+CSS.escape(el.id)+'"]')) return false;
    return true;
  }).map(el => ({tag: el.tagName, type: el.getAttribute('type'), ph: el.getAttribute('placeholder'),
                 outer: el.outerHTML.slice(0,180)}));
  // overflow
  out.overflow = {
    docScroll: document.documentElement.scrollWidth,
    docClient: document.documentElement.clientWidth,
    bodyScroll: document.body.scrollWidth,
    hasOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
  };
  // undersized interactive targets (2.5.8): links/buttons with rect < 24x24
  const targets = [...document.querySelectorAll('a[href],button,input[type=submit],input[type=button],[role=button]')];
  out.undersized = targets.filter(el => {
    if (!vis(el)) return false;
    const r = el.getBoundingClientRect();
    return (r.width < 24 || r.height < 24);
  }).map(el => {
    const r = el.getBoundingClientRect();
    return {tag: el.tagName, text: (el.textContent||el.value||'').trim().slice(0,40),
            w: Math.round(r.width), h: Math.round(r.height), cls: el.className && el.className.toString().slice(0,50)};
  });
  out.targets_total = targets.length;
  return out;
}
"""


def audit_page(browser, fname):
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    console = []
    collect_console(page, console)
    rec = {"file": fname, "console": console}
    try:
        page.goto(f"{BASE}/{fname}", wait_until="load", timeout=20000)
        page.wait_for_timeout(1200)
        rec["title"] = page.title()
        rec["html_lang"] = page.eval_on_selector("html", "e=>e.getAttribute('lang')")
        rec["dom"] = page.evaluate(JS_DOM_AUDIT)
    except Exception as e:
        rec["error"] = str(e)
    page.close()
    return rec


def main():
    out = {"pages": []}
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        for f in PAGES:
            print("audit", f, file=sys.stderr)
            out["pages"].append(audit_page(b, f))
        b.close()
    json.dump(out, open(os.path.join(EVID, "browser_audit.json"), "w"), indent=2)
    # summarize
    for r in out["pages"]:
        d = r.get("dom", {})
        print(f"{r['file']}: dupIDs={len(d.get('duplicate_ids',[]))} "
              f"unlabeled={len(d.get('unlabeled',[]))} noAlt={len(d.get('images_missing_alt',[]))} "
              f"iframeNoTitle={len([f for f in d.get('iframes',[]) if not (f.get('title') or '').strip()])} "
              f"under24={len(d.get('undersized',[]))} overflow={d.get('overflow',{}).get('hasOverflow')} "
              f"consoleErr={len([c for c in r['console'] if c['type'] in ('error','pageerror')])}")


if __name__ == "__main__":
    main()
