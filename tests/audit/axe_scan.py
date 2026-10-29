#!/usr/bin/env python3
"""Run axe-core (WCAG 2.0/2.1/2.2 A+AA) against every page on the local server.
Writes tests/evidence/axe_results.json and prints a per-page summary.
"""
import json, os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:12000"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")
AXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "axe.min.js")
PAGES = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))

RUN = """async () => {
  const r = await axe.run(document, {
    runOnly: { type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice'] }
  });
  return r.violations.map(v => ({id: v.id, impact: v.impact,
    help: v.help, count: v.nodes.length,
    targets: v.nodes.slice(0, 5).map(n => n.target)}));
}"""

out = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    for f in PAGES:
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        try:
            pg.goto(f"{BASE}/{f}", wait_until="load", timeout=30000)
            pg.wait_for_timeout(2000)
            pg.add_script_tag(path=AXE)
            out[f] = pg.evaluate(RUN)
        except Exception as e:
            out[f] = [{"id": "harness-error", "impact": "n/a", "help": str(e)[:160]}]
        pg.close()
    b.close()

json.dump(out, open(os.path.join(EVID, "axe_results.json"), "w"), indent=2)
total = sum(len(v) for v in out.values())
clean = [f for f, v in out.items() if not v]
print(f"pages scanned: {len(PAGES)}")
print(f"pages with zero violations: {len(clean)}/{len(PAGES)}")
print(f"total violation types: {total}")
for f, v in out.items():
    if v:
        print(f"  {f}:")
        for x in v:
            print(f"     {x['id']} ({x.get('impact')}) x{x.get('count','?')} {x.get('targets','')}")
