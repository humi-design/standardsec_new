# Deliverable E — Test Execution Report

Environment: local static server `python -m http.server 12000` serving the repository root;
Chromium (Playwright, `--no-sandbox`); axe-core 4.x vendored at `tests/audit/axe.min.js`;
Pillow for pixel sampling. No network-dependent production endpoint was exercised.

## Commands run

| # | Command | Purpose |
|---|---------|---------|
| 1 | `python tests/audit/axe_scan.py` | axe-core WCAG A/AA/2.2 scan, all 32 pages |
| 2 | `python tests/audit/a11y_verify.py` | DOM audit: headings, IDs, alt, iframes, targets, overflow, reflow, resize, spacing |
| 3 | `python tests/audit/skiplink_audit.py` | Skip-link keyboard test, all 32 pages |
| 4 | `python tests/audit/interaction_audit.py` | Mobile menu, focus rings, form validation, console capture |
| 5 | `python tests/audit/motion_audit.py` | Hero static check, ticker pause/resume, reduced-motion |
| 6 | `python tests/audit/language_audit.py` | EN→HI→EN language switch |
| 7 | `python tests/audit/contrast_audit.py` | Pixel-sampled contrast of flagged elements |
| 8 | `python tests/audit/smartodr_contrast.py` | smart_ODR gradient heading verification |

## Build results
No build step: the site is static HTML/CSS/JS served directly. All 32 pages load with
HTTP 200 from the local server.

## Automated accessibility results
- `tests/evidence/axe_results.json`: **0 violations** on **32/32** pages
  (tags: wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa, best-practice).
- `tests/evidence/axe_contrast.json`: AA `color-contrast` = **0 violations**;
  1662 `color-contrast-enhanced` (AAA, out of scope) and 89 "undetermined"
  (image/gradient/pseudo-element backgrounds) — the undetermined ones were resolved
  individually by pixel sampling.

## Browser / DOM results (`verify_static.json`)
- Duplicate IDs: **0** on every page.
- Missing `alt`: **0** on every page.
- Untitled author iframes: **0** (third-party injected frames excluded).
- Undersized interactive targets: only 6 inline in-sentence links on `contact.html`
  (18px tall) — inline exception applies.
- Console errors: 1 external 403 per page (Google Translate `element.js`), plus
  `news.html` (404 media asset, YouTube frame refusal) — all pre-existing and external.

## Responsive / reflow results (`verify_static.json`)
Widths 320 / 400 / 640 / 893 / 894 / 895 / 1024 / 1280 / 1440 on
`index.html`, `contact.html`, `products.html`, `news.html`, `single.html`:
**no horizontal overflow at any width**.

## Text resize & spacing
- 200% text resize (`index.html`, `contact.html`, `products.html`, `signin.html`):
  no overflow/clipping.
- WCAG text-spacing overrides (`index.html`, `products.html`, `news.html`, `Currency.html`,
  `Commodities.html`, `contact.html`): no clipping introduced (only `sr-only` and
  decorative `overflow:hidden` heading rules reported, not text loss).

## Keyboard results (`interaction.json`, `skiplink.json`)
- Skip link: first tab stop, visible on focus, target exists — **32/32 pages**.
- Focus indicator: 3px solid `rgb(11,76,140)` on skip link, buttons, links, inputs,
  ticker control.
- Mobile menu: opens by pointer and by Enter/Space; `aria-expanded` false↔true;
  Escape closes and restores focus. Breakpoint between 895px and 960px.

## Form validation results (`interaction.json`)
| Form | Empty submit | Malformed input | Valid input | POST issued |
|------|--------------|-----------------|-------------|-------------|
| Create-Account | 3 fields `aria-invalid`, per-field errors, `#form-status` | email flagged, specific message | no `aria-invalid`, success status | **no** |
| Contact | 3 fields `aria-invalid`, `role=alert` summary, focus→first invalid | per-field messages | (not submitted) | **no** |

## Motion results (`motion.json`)
- Hero slideshow: 1 slide, transform unchanged over 8s → static.
- Ticker: pause → `aria-pressed="true"`, transform frozen; resume → `aria-pressed="false"`,
  autoplay continues.
- `prefers-reduced-motion: reduce`: scrolling notices start paused, ticker control
  `aria-pressed="true"`.

## Language results (`language.json`)
- EN → HI: `html lang="hi"`, `translated-ltr`, H1 "मजबूत नींव स्थापित करना".
- HI → EN: `html lang="en"`, English text restored.

## Contrast results
- `smart_odr_contrast.json`: white text on `linear-gradient(135deg,#1a237e,#0d47a1)` =
  **8.63:1** worst case (lightest stop) / 13.24:1 (darkest stop) → passes large-text 3:1.
  Screenshots: `smart_odr_step_heading_1280.png`, `smart_odr_step_heading_400.png`.
- `contrast.json` (pixel-sampled, computed text colour vs. dominant painted background):

| Element | Ratio | Requirement | Result |
|---------|-------|-------------|--------|
| Hero heading (Advisory/Currency/Commodities/Depository) | 9.00:1 | 3:1 (large) | PASS |
| Hero heading (Equity/IPOs) | 11.45:1 | 3:1 (large) | PASS |
| "Open an Account" button | 5.57:1 | 4.5:1 | PASS |
| Contact form field text | 9.98:1 | 4.5:1 | PASS |
| Accessibility toolbar button | 4.59:1 | 3:1 | PASS |
| smart_ODR "Step-by-Step Process" heading | 8.63:1 | 3:1 (large) | PASS |

  (A CSS-only heuristic is unreliable over images/gradients; axe AA plus this pixel
  sampling are authoritative. Elements reported "n/a" were simply not matched by the
  probe selector and are covered by axe.)

## Target-size measurements
- axe `target-size`: **0 violations**.
- Manual measurement: skip link 189×43; footer links ≥24px tall; 6 inline paragraph links
  18px tall (inline exception: parent line-height 24.75px, adjacent text present).

## Skipped / not-run tests
| Test | Reason |
|------|--------|
| Live screen-reader pass (NVDA/JAWS/VoiceOver) | No screen reader available in this environment |
| Physical touchscreen target measurement | No device available |
| Real form submission (mail.php + reCAPTCHA) | Production-safety constraint; not triggered |
| Native OS text-only zoom | Browser-based enlargement used instead |
