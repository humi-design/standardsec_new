# Deliverable B — 17-Finding Closure Tracker

Website: Standard Securities & Investment Intermediates Ltd — https://www.standardsec.com/
Source report: `Standard_Securities_WCAG_2.2_Accessibility_Report_level2.pdf`
Audit environment: local static server `http://localhost:12000` (Chromium 140 via Playwright,
axe-core 4.x). No production system, backend, real form data or reCAPTCHA was touched.

Status vocabulary: VERIFIED FIXED · ALREADY FIXED — VERIFIED · FIXED — RETEST FAILED · OPEN ·
BLOCKED · NOT VERIFIED · NOT APPLICABLE.

---

## 8.1 — Broken heading hierarchy and duplicate heading content
- Original: OPEN · WCAG 1.3.1 (A)
- Affected: all pages; hero on `index.html` and the six product templates
- Changes: single logical H1 per page; duplicate hero H1s removed; statistic values
  (`#1`, `~30ms`, `0.0`) converted to styled paragraphs; repeated service blocks normalised
- Test: heading outline extracted from the rendered DOM on all 32 pages
- Result: exactly one **visible** H1 on every page; no skipped levels; no heading-only stat values
- Evidence: `tests/evidence/verify_static.json` → `per_page.*.headings`; analysis script
  `tests/audit/a11y_verify.py`
- **Final status: VERIFIED FIXED** (static DOM + axe `heading-order` clean)

## 8.2 — Contact form fields have no programmatic or visible labels
- Original: OPEN · WCAG 1.3.1 (A) / 2.4.6 (AA) / 3.3.2 (A)
- Affected: `contact.html` (and the shared Create-Account form)
- Changes: visible `<label for>` on Name/Email/Message; `sr-only` "(required)" text; help text
  via `aria-describedby`; `required` + `aria-required`
- Test: unlabeled-field scan (`a11y_verify.py` JS_LABELS) + axe `label` on form pages
- Result: 0 unlabeled fields; placeholders are supplementary, never the only identifier
- Evidence: `verify_static.json` → `per_page["contact.html"].unlabeled = []`
- **Final status: VERIFIED FIXED**

## 8.3 — Missing autocomplete attributes on input fields
- Original: OPEN in L1, CLOSED in L2 · WCAG 1.3.5 (AA)
- Affected: `index.html` Create-Account, `contact.html`, `signin.html`, complaint forms
- Test: enumerate every non-button input and its `autocomplete` value
- Result: `name`, `email`, `tel`, `username`, `current-password` present on the correct fields;
  no inappropriate tokens assigned
- Evidence: `verify_static.json` → `per_page[<form page>].autocomplete`
- **Final status: ALREADY FIXED — VERIFIED**

## 8.4 — Insufficient colour contrast for text and UI components
- Original: OPEN · WCAG 1.4.3 (AA) / 1.4.11 (AA)
- Affected: hero heading, "Open an Account" button, ticker badges, accessibility toolbar,
  footer "Need help?", contact field borders
- Test: axe `color-contrast` (AA) across all 32 pages; pixel-sampled measurements of the
  flagged elements
- Result: **0 AA contrast violations**. The earlier "warning" on `smart_ODR.html` was a
  false positive — white text over `linear-gradient(135deg,#1a237e,#0d47a1)` measures
  **8.63:1 at the lightest gradient stop** (13.24:1 at the darkest), both above the 3:1
  large-text threshold; the tool could not resolve the gradient background.
  Contact field text colour was raised to meet 4.5:1.
- Evidence: `tests/evidence/axe_results.json` (0 violations), `axe_contrast.json`,
  `contrast.json`, `smart_odr_contrast.json`, screenshots
  `tests/evidence/smart_odr_step_heading_{1280,400}.png`
- **Final status: VERIFIED FIXED**

## 8.5 — Incomplete verification of text resize to 200%
- Original: OPEN · WCAG 1.4.4 (AA)
- Test: browser text-only enlargement to 200% on homepage, contact, products, login
- Result: no horizontal overflow, clipping or loss of content/functionality at any tested
  template
- Evidence: `verify_static.json` → `text_resize_200pct`
- Limitation: real OS/browser text-only zoom on a physical device was not exercised
- **Final status: VERIFIED FIXED** (browser-based)

## 8.6 — Text clipping under WCAG text-spacing overrides
- Original: OPEN in L1, CLOSED in L2 · WCAG 1.4.12 (AA)
- Test: injected 1.5 line-height, 0.12em letter-spacing, 0.16em word-spacing, 2em paragraph
  spacing; measured `scrollHeight > clientHeight` on text elements
- Result: no new clipping. Reported hits are `sr-only` helpers and `overflow:hidden`
  heading-line decorations (letter-spacing only, no vertical clipping), i.e. not text loss
- Evidence: `verify_static.json` → `text_spacing`
- **Final status: ALREADY FIXED — VERIFIED**

## 8.7 — Non-functional hamburger menu, keyboard navigation, hover content
- Original: OPEN · WCAG 1.4.10, 1.4.13, 2.1.1, 2.4.5
- Test: menu opened/closed by pointer and by keyboard (Enter, Space) at 375/640/893/894/895px;
  `aria-expanded` tracked; Escape closed it and returned focus; nav links reachable
- Result: opens and closes by pointer and keyboard at every width; `aria-expanded` flips
  false↔true; label updates; Escape closes and refocuses the toggle; all primary links present.
  Breakpoint confirmed between 895px (mobile toggle shown) and 960px (desktop row)
- Evidence: `tests/evidence/interaction.json` → `mobile_menu`, `keyboard_menu_open`
- **Final status: VERIFIED FIXED**

## 8.8 — Continuously auto-advancing carousel without pause control
- Original: OPEN · WCAG 2.2.2 (A)
- Test: observed hero slide transforms over 8 s; drove the ticker pause control and sampled
  motion before/pause/resume
- Result: hero slideshow is **static** (single slide, no transform change over 8 s) — no
  pause control required. The price ticker autoplays; its control toggles
  `aria-pressed false→true`, freezes the transform, and resume re-enables autoplay.
  `prefers-reduced-motion: reduce` starts the scrolling notices paused.
- Evidence: `tests/evidence/motion.json`
- **Final status: VERIFIED FIXED**

## 8.9 — Permanently hidden "Skip to main content" link
- Original: OPEN · WCAG 2.4.1 (A)
- Test: keyboard Tab on all 32 pages; measured position, size, outline; activated with Enter
- Result: skip link is the **first tab stop** on every page, becomes visible on focus
  (`top:10px; left:10px`, 189×43 px), carries a 3px `#0b4c8c` outline, and its target
  (`#main-content`) exists; Enter moves the hash to the main region
- Evidence: `tests/evidence/skiplink.json`, screenshot `skiplink_focused.png`
- **Final status: VERIFIED FIXED**

## 8.10 — Identical, non-descriptive page titles sitewide
- Original: OPEN in L1, CLOSED in L2 · WCAG 2.4.2 (A)
- Test: page-title inventory across all 32 pages
- Result: 32/32 unique, descriptive titles. (The duplicate pair `complaint.html` /
  `complaint_new.html` found during this audit was corrected — legacy page retitled
  "Complaint Form (Legacy)".)
- Evidence: `verify_static.json` → `per_page.*.title`, `FINAL_AUDIT/summary.json` → `titles`
- **Final status: ALREADY FIXED — VERIFIED** (one residual duplicate found and fixed)

## 8.11 — No visible focus indicator on custom buttons
- Original: OPEN · WCAG 2.4.7 (AA)
- Test: focused each control class and read the computed outline
- Result: 3px solid `rgb(11,76,140)` outline on skip link, buttons, links, inputs and
  custom controls; verified on real focus (not just stylesheet inspection)
- Evidence: `interaction.json` → `focus_rings`
- **Final status: VERIFIED FIXED**

## 8.12 — Accessible name does not contain the visible label text
- Original: OPEN · WCAG 2.5.3 (A)
- Affected: "Open Account", "Fund Transfer" (original report); "Pay now!",
  "Advisory – KYC Compliance" (prior run); plus controls found in this audit
- Changes: accessible names rewritten to begin with the visible text
  ("Open Account - start a new trading account", "Fund Transfer - transfer funds securely",
  "Pay now! - download the payment QR code PDF", "Advisory – KYC Compliance - download the
  KYC updation PDF"); this run additionally fixed `contact.html` "Send Message" and
  `signin.html` "Login".
- Test: computed visible text vs. accessible name across all pages; axe `label-in-name`
- Result: **0 violations** (icon-only controls with no visible text are correctly out of scope)
- Evidence: axe `label-in-name` = 0; per-page scan output in this report
- **Final status: VERIFIED FIXED**

## 8.13 — Interactive targets below minimum size
- Original: OPEN · WCAG 2.5.8 (AA) — 27 undersized targets (footer links, 1×1 px skip link)
- Test: rendered width/height of every interactive element across all 32 pages; axe `target-size`
- Result: skip link and footer links now meet 24×24. Six inline links inside a single
  paragraph on `contact.html` remain 18px tall but qualify for the **inline exception**
  (verified in-sentence: parent line-height 24.75px, adjacent text present). Accessibility
  contact links, the legacy submit button and the charter close buttons were raised to
  24px during this run.
- Evidence: `verify_static.json` → `per_page.*.undersized`; axe `target-size` = 0
- Limitation: physical touchscreen measurement not performed (no device available)
- **Final status: VERIFIED FIXED** (browser measurements; inline exceptions documented)

## 8.14 — Non-functional Hindi language toggle
- Original: OPEN in L1, CLOSED in L2 · WCAG 3.1.2 (AA)
- Test: drove the language control end to end
- Result: the old non-functional EN/HI toggle has been replaced by a Google Translate
  widget. Selecting **Hindi** changes the visible text (H1 → "मजबूत नींव स्थापित करना")
  and sets `<html lang="hi">` + `translated-ltr`; selecting **English** restores the
  English text and `<html lang="en">`. Keyboard operation confirmed.
- Evidence: `tests/evidence/language.json`, screenshot `language_hindi_index.png`
- Limitation: widget depends on Google Translate being reachable; verified locally where
  the widget script loaded successfully
- **Final status: ALREADY FIXED — VERIFIED**

## 8.15 — Missing input validation and error suggestions (Homepage + Contact)
- Original: OPEN · WCAG 3.3.1 (A) / 3.3.3 (AA) (4.1.3 also relevant)
- Test: submitted empty and malformed data to both forms in the local environment only
- Result:
  - Create-Account: empty submit → `aria-invalid="true"` on all three fields with
    `aria-describedby` wired to per-field error text; bad email → email flagged with a
    specific message; valid input → no `aria-invalid`, `#form-status` shows
    "Thank you! We will contact you shortly.", **no POST** issued (no backend contact).
  - Contact: empty submit → all three fields flagged, error summary
    "⚠️ Please fix the errors before submitting." exposed via `role="alert"`, focus moved to
    the first invalid field; malformed data → specific per-field messages. **No POST** issued.
- Evidence: `tests/evidence/interaction.json` → `create_account_*`, `contact_*`
- Limitation: the real `mail.php`/backend submission and reCAPTCHA were intentionally not
  triggered; server-side confirmation remains unverified
- **Final status: VERIFIED FIXED** (client-side); backend submission **NOT VERIFIED**

## 8.16 — Duplicate element IDs sitewide
- Original: OPEN · WCAG 4.1.1 (A) — note: 4.1.1 was **removed in WCAG 2.2**; retained here
  for historical traceability, with residual effects assessed under 4.1.2/1.3.1
- Test: duplicate-ID scan of the rendered DOM on all 32 pages
- Result: **0 duplicate IDs**; label/ARIA/anchor references resolve correctly
- Evidence: `verify_static.json` → `per_page.*.duplicate_ids = []`
- **Final status: VERIFIED FIXED**

## 8.17 — Broken ARIA states and JavaScript console errors
- Original: OPEN · WCAG 4.1.2 (A)
- Test: console + `pageerror` + failed-request capture on 8 templates with interaction
- Result:
  - Mobile toggle exposes `aria-expanded`/`aria-controls`, both tracking real state.
  - Chatbot iframe and Google Map/Translate frames carry descriptive titles.
  - **0 uncaught JavaScript exceptions** on every page tested.
  - Fixed during this run: the chat toggle was inert on 24 of 25 pages because
    `display()` bailed out when `.send__button` was absent; now the toggle works everywhere
    and its `aria-expanded`/label update correctly.
  - Residual console noise is environmental, not script defects: a 403 on the
    Google Translate `element.js` request (bot/rate limiting of `translate.google.com`) and
    a 403 on the third-party `webchat.botframework.com` embed — both external and
    pre-existing in HEAD. A YouTube embed on `news.html` refuses framing
    (`X-Frame-Options: sameorigin`), also pre-existing.
- Evidence: `interaction.json` → `console`; `verify_static.json` → `per_page.*.console_errors`
- **Final status: VERIFIED FIXED** (no script defects; external network noise documented)
