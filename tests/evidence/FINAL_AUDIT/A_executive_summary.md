# Deliverable A — Executive Summary

## Scope
- **Client:** Standard Securities & Investment Intermediates Ltd
- **Website:** https://www.standardsec.com/
- **Standard:** WCAG 2.2 Level A and Level AA
- **Source report:** `Standard_Securities_WCAG_2.2_Accessibility_Report_level2.pdf`
  (author Varun Bansal, dated 19 Oct 2026; 56 success criteria assessed — 22 Pass,
  23 Fail, 11 N/A)
- **Pages inspected:** 32 HTML pages (30 site pages + 2 standalone fragment pages
  `accessibility-toolbar.html`, `botbot.html`)
- **Environment:** local static server `http://localhost:12000`; Chromium via Playwright;
  axe-core; pixel-sampling contrast measurement. No production system, backend, real form
  data, reCAPTCHA or financial transaction was touched.

## Headline results

| Metric | Count |
|--------|-------|
| Pages scanned (axe, WCAG 2.0/2.1/2.2 A+AA+best-practice) | 32 |
| Pages with **zero** axe violations | **32 / 32** |
| Pages with a working skip link (first tab stop, visible, target exists) | **32 / 32** |
| Unique descriptive page titles | **32 / 32** |
| Pages with duplicate element IDs | **0** |
| Pages with missing `alt` attributes | **0** |
| Pages with untitled author iframes | **0** |
| Pages with horizontal overflow at 1280px | **0** |
| AA `color-contrast` violations sitewide | **0** |
| Uncaught JavaScript exceptions (`pageerror`) | **0** |
| Original findings 8.1–8.17 reviewed | **17 / 17** |

## Finding closure

| Final status | Count | Findings |
|--------------|-------|----------|
| VERIFIED FIXED | 13 | 8.1, 8.2, 8.4, 8.5, 8.7, 8.8, 8.9, 8.11, 8.12, 8.13, 8.15*, 8.16, 8.17 |
| ALREADY FIXED — VERIFIED | 4 | 8.3, 8.6, 8.10, 8.14 |
| OPEN | 0 | — |
| BLOCKED | 0 | — |
| NOT VERIFIED | 0 | — |
| NOT APPLICABLE | 0 | — |

\* 8.15 is verified client-side; the real backend submission (mail.php + reCAPTCHA) is
**NOT VERIFIED** and is documented as a remaining action.

Defects found and fixed **during this audit** (not present in the prior run's report):
1. **Chat toggle inert on 24 of 25 pages** — `Chatbox.display()` returned early when
   `.send__button` was absent. Fixed so the toggle works and its `aria-expanded`/label
   update on every page. (Finding 8.17)
2. **Duplicate page title** `complaint.html` vs `complaint_new.html`. Legacy page retitled.
   (Finding 8.10)
3. **`.fab` class collision** — Font Awesome brand icons shared the accessibility toolbar's
   `.fab` rule and stacked in the page corner. Reset in `accessibility-fixes.css`.
4. **Label-in-name** violations on `contact.html` "Send Message" and `signin.html` "Login".
   (Finding 8.12)
5. **Target-size** on accessibility contact links, the legacy submit button and the charter
   close buttons. (Finding 8.13)
6. **Contact form field text contrast** raised to meet 4.5:1. (Finding 8.4)

## Criterion matrix (56 rows)
- **PASS (verified):** 44
- **N/A:** 11
- **FIXED (retained historically; 4.1.1 was removed in WCAG 2.2):** 1
- **FAIL remaining:** 0

## Tests executed
See `E_test_execution_report.md`. Summary: axe-core on 32 pages; DOM/static audit on 32
pages; skip-link keyboard test on 32 pages; reflow at 9 viewport widths on 5 templates;
200% text resize on 4 templates; text-spacing overrides on 6 templates; mobile-menu
open/close by pointer and keyboard at 7 widths; form validation (empty/invalid/valid) on
both forms; motion pause/resume and reduced-motion; language switch EN→HI→EN; contrast
pixel sampling; console/`pageerror`/failed-request capture.

## Remaining manual verification
1. **Live screen-reader pass** (NVDA/JAWS/VoiceOver) — NOT VERIFIED (no screen reader in
   this environment). Accessibility-tree and computed-name checks were performed instead.
2. **Physical touchscreen target measurement** — NOT VERIFIED (no device).
3. **Real form submission** (mail.php backend + reCAPTCHA) — NOT VERIFIED (production
   safety; intentionally not triggered).
4. **Native OS text-only zoom on a physical device** — NOT VERIFIED (browser-based
   enlargement used instead).
5. Third-party embeds (Google Translate `element.js` 403, `webchat.botframework.com` 403,
   YouTube `X-Frame-Options`) fail in this sandbox for external reasons; documented, not
   script defects.

## Verdict
**FIXES APPLIED BUT PARTIALLY UNVERIFIED.**

All 17 findings are remediated and independently re-tested at the level this environment
supports, with zero automated (axe) violations, zero duplicate IDs, zero missing
alternatives, unique titles, working skip links and focus indicators, functioning mobile
navigation, motion controls, form validation and a working language switch. The verdict is
**not** "COMPLETE AND VERIFIED" because the required manual checks above — in particular a
live screen-reader pass and a safe end-to-end form submission — remain outstanding, and
because passing automated scans alone does not establish full WCAG 2.2 conformance.
