#!/usr/bin/env python3
"""Form validation, contrast, reflow, text-spacing, zoom tests (8.4, 8.5, 8.6, 8.13, 8.15)."""
import json, os, sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:12000"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVID = os.path.join(ROOT, "tests", "evidence")
os.makedirs(EVID, exist_ok=True)
R = {}

TEXT_SPACING_CSS = """
* { line-height: 1.5 !important; }
p, li, h1,h2,h3,h4,h5,h6, div, span, a, small, td, th { 
  letter-spacing: 0.12em !important; word-spacing: 0.16em !important; }
p { margin-bottom: 2em !important; }
"""


def contrast(pg, selector, prop="color"):
    return pg.evaluate("""([sel]) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const s = getComputedStyle(el);
      return {color: s.color, background: s.backgroundColor, fontSize: s.fontSize, fontWeight: s.fontWeight};
    }""", [selector])


def run():
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])

        # ---------- 8.15 Create Account form ----------
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(BASE + "/index.html", wait_until="load")
        pg.wait_for_timeout(1500)
        pg.eval_on_selector("#open-account-form", "f=>f.scrollIntoView()")
        pg.eval_on_selector("#open-account-form", "f=>f.requestSubmit ? f.requestSubmit() : f.dispatchEvent(new Event('submit',{cancelable:true,bubbles:true}))")
        pg.wait_for_timeout(500)
        R["create_account_empty"] = pg.evaluate("""() => ({
          invalid: [...document.querySelectorAll('#open-account-form [aria-invalid="true"]')].map(e=>e.id),
          status: (document.getElementById('form-status')||{}).textContent,
          status_role: (document.getElementById('form-status')||{}).getAttribute ? document.getElementById('form-status').getAttribute('role') : null,
          focused: document.activeElement.id
        })""")
        # malformed email
        pg.fill("#signup-name", "Test User")
        pg.fill("#signup-email", "not-an-email")
        pg.fill("#phone", "1234567890")
        pg.eval_on_selector("#open-account-form", "f=>f.requestSubmit ? f.requestSubmit() : f.dispatchEvent(new Event('submit',{cancelable:true,bubbles:true}))")
        pg.wait_for_timeout(400)
        R["create_account_bad_email"] = pg.evaluate("""() => ({
          invalid: [...document.querySelectorAll('#open-account-form [aria-invalid="true"]')].map(e=>e.id),
          focused: document.activeElement.id
        })""")
        # valid
        pg.fill("#signup-email", "test@example.com")
        pg.eval_on_selector("#open-account-form", "f=>f.requestSubmit ? f.requestSubmit() : f.dispatchEvent(new Event('submit',{cancelable:true,bubbles:true}))")
        pg.wait_for_timeout(400)
        R["create_account_valid"] = pg.evaluate("""() => ({
          status: (document.getElementById('form-status')||{}).textContent,
          invalid: [...document.querySelectorAll('#open-account-form [aria-invalid="true"]')].map(e=>e.id)
        })""")
        pg.close()

        # ---------- 8.15 Contact form (client-side only) ----------
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(BASE + "/contact.html", wait_until="load")
        pg.wait_for_timeout(1200)
        pg.eval_on_selector("#contact-form", "f=>f.scrollIntoView()")
        # Intercept submission to avoid real POST
        pg.route("**/mail.php", lambda route: route.fulfill(status=200, body="ok"))
        pg.eval_on_selector("#contact-form", "f=>f.requestSubmit ? f.requestSubmit() : f.dispatchEvent(new Event('submit',{cancelable:true,bubbles:true}))")
        pg.wait_for_timeout(500)
        R["contact_empty"] = pg.evaluate("""() => ({
          invalid: [...document.querySelectorAll('#contact-form [aria-invalid="true"]')].map(e=>e.id),
          nameError: (document.getElementById('nameError')||{}).textContent,
          emailError: (document.getElementById('emailError')||{}).textContent,
          messageError: (document.getElementById('messageError')||{}).textContent,
          summary: (document.getElementById('errorSummary')||{}).textContent,
          focused: document.activeElement.id
        })""")
        pg.fill("#name", "QA Test")
        pg.fill("#email", "bad@@x")
        pg.fill("#message", "short")
        pg.eval_on_selector("#contact-form", "f=>f.requestSubmit ? f.requestSubmit() : f.dispatchEvent(new Event('submit',{cancelable:true,bubbles:true}))")
        pg.wait_for_timeout(400)
        R["contact_bad"] = pg.evaluate("""() => ({
          invalid: [...document.querySelectorAll('#contact-form [aria-invalid="true"]')].map(e=>e.id),
          emailError: document.getElementById('emailError').textContent,
          messageError: document.getElementById('messageError').textContent,
          focused: document.activeElement.id
        })""")
        pg.close()

        # ---------- 8.4 contrast measurements ----------
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(BASE + "/index.html", wait_until="load")
        pg.wait_for_timeout(1500)
        R["contrast_index"] = pg.evaluate(r"""() => {
          const out = {};
          const grab = (sel, label) => {
            const el = document.querySelector(sel);
            if (!el) { out[label] = 'NOT FOUND'; return; }
            const s = getComputedStyle(el);
            // effective background: walk up until non-transparent
            let bg = s.backgroundColor, node = el;
            while (bg === 'rgba(0, 0, 0, 0)' && node.parentElement) {
              node = node.parentElement; bg = getComputedStyle(node).backgroundColor;
            }
            out[label] = {color: s.color, bg: bg, fontSize: s.fontSize, weight: s.fontWeight};
          };
          grab('.monee-slide1-text h1', 'hero_h1');
          grab('.monee-slide1-text a.uk-button-primary', 'open_account_btn');
          grab('.monee-price-ticker .uk-label-success', 'ticker_success');
          grab('.monee-price-ticker .uk-label-danger', 'ticker_danger');
          grab('#accessibilityToggle_index', 'a11y_fab');
          const nh = [...document.querySelectorAll('footer *')].find(e => /Need help/i.test(e.textContent||''));
          if (nh) { const s=getComputedStyle(nh); let bg=s.backgroundColor,n=nh; while(bg==='rgba(0, 0, 0, 0)'&&n.parentElement){n=n.parentElement;bg=getComputedStyle(n).backgroundColor;} out.footer_need_help={color:s.color,bg:bg,fontSize:s.fontSize}; }
          const ci = document.querySelector('.uk-input');
          if (ci) { const s=getComputedStyle(ci); out.contact_input_border={borderColor:s.borderTopColor, borderWidth:s.borderTopWidth, bg:s.backgroundColor}; }
          return out;
        }""")
        pg.close()

        # smart_ODR "Step-by-Step" heading
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        pg.goto(BASE + "/smart_ODR.html", wait_until="load")
        pg.wait_for_timeout(1500)
        R["smart_odr_contrast"] = pg.evaluate(r"""() => {
          const hits = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6,span,div,p')]
            .filter(e => /Step-by-Step/i.test(e.textContent||'') && e.children.length===0);
          return hits.slice(0,5).map(e => {
            const s = getComputedStyle(e);
            let bg = s.backgroundColor, n = e;
            while (bg === 'rgba(0, 0, 0, 0)' && n.parentElement) { n = n.parentElement; bg = getComputedStyle(n).backgroundColor; }
            const grad = getComputedStyle(n).backgroundImage;
            return {tag:e.tagName, text:(e.textContent||'').trim().slice(0,40), color:s.color, bg:bg, grad:grad.slice(0,120), fontSize:s.fontSize, weight:s.fontWeight};
          });
        }""")
        pg.close()

        # ---------- 8.5 zoom 200% & 8.6 text spacing ----------
        R["zoom200"] = {}
        R["textspacing"] = {}
        for f in ["index.html", "contact.html", "about.html", "smart_ODR.html", "news.html"]:
            pg = b.new_page(viewport={"width": 1280, "height": 900})
            pg.goto(BASE + "/" + f, wait_until="load")
            pg.wait_for_timeout(1000)
            # 200% zoom via device scale + set viewport to simulate: use CSS zoom on html
            pg.evaluate("()=>{document.documentElement.style.zoom='200%';}")
            pg.wait_for_timeout(600)
            R["zoom200"][f] = pg.evaluate("""()=>({sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth, overflow: document.documentElement.scrollWidth>document.documentElement.clientWidth+2})""")
            pg.close()

            pg = b.new_page(viewport={"width": 1280, "height": 900})
            pg.goto(BASE + "/" + f, wait_until="load")
            pg.wait_for_timeout(1000)
            pg.add_style_tag(content=TEXT_SPACING_CSS)
            pg.wait_for_timeout(600)
            R["textspacing"][f] = pg.evaluate("""()=>{
              const clipped = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,li,a,span')].filter(e=>{
                const s=getComputedStyle(e);
                return (e.scrollHeight > e.clientHeight+2 && e.clientHeight>0) || (e.scrollWidth > e.clientWidth+2 && s.overflow!=='visible' && e.clientWidth>0);
              }).map(e=>({tag:e.tagName, txt:(e.textContent||'').trim().slice(0,30), sh:e.scrollHeight, ch:e.clientHeight, sw:e.scrollWidth, cw:e.clientWidth}));
              return {overflow: document.documentElement.scrollWidth>document.documentElement.clientWidth+2, clipped_count: clipped.length, clipped: clipped.slice(0,8)};
            }""")
            pg.close()

        # ---------- 8.13 target size across viewports ----------
        R["targets"] = {}
        for w in [320, 400, 640, 894, 1280]:
            pg = b.new_page(viewport={"width": w, "height": 900})
            pg.goto(BASE + "/index.html", wait_until="load")
            pg.wait_for_timeout(1200)
            R["targets"][str(w)] = pg.evaluate(r"""() => {
              const targets=[...document.querySelectorAll('a[href],button,input[type=submit],input[type=button],[role=button]')];
              const under = targets.filter(el=>{
                const r=el.getBoundingClientRect(); const s=getComputedStyle(el);
                if (r.width===0||r.height===0||s.visibility==='hidden'||s.display==='none') return false;
                return r.width<24 || r.height<24;
              }).map(el=>{const r=el.getBoundingClientRect(); return {tag:el.tagName, txt:(el.textContent||el.value||'').trim().slice(0,30), w:Math.round(r.width), h:Math.round(r.height)};});
              return {total: targets.length, under24: under.length, items: under.slice(0,12)};
            }""")
            pg.close()

        # ---------- 7 reflow across breakpoints ----------
        R["reflow"] = {}
        for w in [320, 400, 640, 893, 894, 895, 1280]:
            pg = b.new_page(viewport={"width": w, "height": 900})
            pg.goto(BASE + "/index.html", wait_until="load")
            pg.wait_for_timeout(1000)
            R["reflow"][str(w)] = pg.evaluate("""()=>{
              const offenders=[...document.querySelectorAll('body *')].filter(e=>{
                const r=e.getBoundingClientRect();
                return r.right > document.documentElement.clientWidth+2 && r.width>0 && getComputedStyle(e).position!=='fixed';
              }).slice(0,6).map(e=>({tag:e.tagName, cls:(e.className||'').toString().slice(0,40), right:Math.round(e.getBoundingClientRect().right)}));
              return {sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth,
                      overflow: document.documentElement.scrollWidth>document.documentElement.clientWidth+2, offenders};
            }""")
            pg.close()

        b.close()


if __name__ == "__main__":
    run()
    json.dump(R, open(os.path.join(EVID, "forms_layout.json"), "w"), indent=2)
    print(json.dumps(R, indent=2))
