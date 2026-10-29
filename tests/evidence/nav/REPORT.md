# Navigation Menu Alignment Regression — Root Cause and Fix

**Reported symptom:** the primary navigation links split across two uneven rows
(“Home, Products, Contact, Complaints” on row 1; “About Us, Login, Quick Links,
KYC” on row 2) with inconsistent spacing and alignment.

**Status:** fixed and verified. No commit, push, or deploy was performed.

---

## 1. Root cause

Two rules in `css/accessibility-fixes.css` interacted to inflate the horizontal
menu beyond its container between the desktop breakpoint and ~1023px.

### Cause A — WCAG 1.4.12 text-spacing override applied to the menu

The text-spacing block is deliberately broad so it also survives a user-origin
override:

```css
p, li, td, th, label {
    line-height: 1.5 !important;
    letter-spacing: 0.12em !important;   /* 1.92px at 16px */
    word-spacing: 0.16em !important;     /* 2.56px at 16px */
}
```

`.uk-navbar-nav` is a `<ul>`, so every menu `<li>` matched. At the template's
16px menu font size that added ~1.92px tracking and ~2.56px word spacing to each
of the eight labels, widening the bar from **836px to 952px** — a 116px (14%)
increase. The desktop bar appears at `min-width: 960px` (uikit `.uk-visible@m`),
but the header container is narrower than 952px until ~1100px viewport, so the
links wrapped.

Measured, per-item widths at 1280px:

| Item | Width |
|------|-------|
| Home | 90 |
| Products | 113 |
| About Us | 114 |
| Contact | 103 |
| Login | 85 |
| Quick Links | 128 |
| KYC | 73 |
| Complaints | 130 |
| **total** | **836** |

### Cause B — `flex-wrap: wrap` on the menu

```css
header .uk-navbar-nav { flex-wrap: wrap; }
```

This rule (added for the 1.4.4 resize-text work) allowed the items to wrap
instead of overflowing, so the width overflow from Cause A became two unordered
rows rather than a scrollbar. Wrapping a horizontal menu reorders the visual
sequence relative to DOM order (WCAG 1.3.2 Meaningful Sequence / 2.4.3 Focus
Order).

### Evidence

| Width | Before | After |
|-------|--------|-------|
| 960px | 2 rows, `contentW 952 > navW 850`, logo/nav overlap | 1 row, `contentW 836 = navW 836`, no overlap |
| 1024px | 2 rows, `contentW 952 > navW 914` | 1 row, no overflow |
| 1100–1920px | 1 row | 1 row (unchanged) |

Both offending rules are present in `main` (pre-existing), so this is a
pre-existing regression surfaced by the earlier accessibility work, not
introduced by the audit commit.

---

## 2. The fix

### `css/accessibility-fixes.css`

1. Exempt navigation chrome from the prose text-spacing override (keeps 1.4.12
   support for flowing text):

```css
.uk-navbar-nav, .uk-navbar-nav li, .uk-navbar-nav li > a,
.uk-nav, .uk-nav li, .uk-nav li > a,
.uk-nav-sub, .uk-nav-sub li, .uk-nav-sub li > a {
    letter-spacing: normal !important;
    word-spacing: normal !important;
}
```

2. Keep the menu on one row so it cannot wrap into unordered rows:

```css
header .uk-navbar-nav { flex-wrap: nowrap; }
```

### `js/a11y-nav.js`

Added an extreme-text-enlargement fallback (WCAG 1.4.4). At very large text the
bar can exceed its container again; rather than clipping links or wrapping, the
bar collapses into the same accessible hamburger menu used at narrow viewports.
It measures `scrollWidth` vs `clientWidth`, is re-evaluated on `resize`, on the
site's own A+/A− control (via a `MutationObserver` on the root/body `style`
attribute, since that control fires no resize event), and after web-font load.
No effect at normal text sizes.

---

## 3. Viewports tested

`320, 375, 400, 640, 768, 894, 895, 959, 960, 1000, 1024, 1100, 1280, 1440, 1600, 1920` CSS px,
plus the 960–1023px band where the defect occurred, plus 200% browser zoom
(CSS 640px, 800px, 960px).

| Width | Layout | Rows | Clipped | Page overflow |
|-------|--------|------|---------|---------------|
| 320–959 | hamburger | — | no | no |
| 960–1920 | desktop, one row | 1 | no | no |

Result: **0 failures** across all 16 widths (script: `tests/audit/nav_layout_audit.py`).

Also verified at 960/1024/1100/1280px across 15 pages: 0 problems.

---

## 4. Accessibility preserved

| Check | Result |
|-------|--------|
| axe-core WCAG 2.0/2.1/2.2 A+AA+BP | 0 violations, 32/32 pages |
| Skip link (first tab stop, visible on focus, target exists) | 32/32 pages |
| Unique titles / duplicate IDs / missing alt | 32 unique / none / none |
| Mobile menu: pointer + Enter + Space; `aria-expanded` false↔true; Escape restores focus | verified |
| Hamburger opens when the bar collapses under text enlargement | verified (keyboard) |
| Dropdowns (About Us, Login, Quick Links, KYC): pointer hover and keyboard | verified |
| Ticker pause/resume + `aria-pressed` | verified |
| Hero slideshow static | verified |
| EN→HI→EN language switch | verified |
| Uncaught JS exceptions | 0 |

The 1.4.12 text-spacing support is retained for prose: forcing
`letter-spacing:0.12em`/`word-spacing:0.16em` on all text leaves the menu on one
row with no clipping (the nav exemption wins for author-origin overrides; a
user-origin override that outranks it is caught by the JS fallback).

---

## 5. Files changed

| File | Change |
|------|--------|
| `css/accessibility-fixes.css` | Exempt nav chrome from the prose text-spacing override; `flex-wrap: nowrap` on the menu |
| `js/a11y-nav.js` | Extreme-text-enlargement collapse fallback |
| `tests/audit/nav_layout_audit.py` | New regression test (16 widths, screenshots) |
| `tests/evidence/nav_layout.json` | Measured results |
| `tests/evidence/nav/*.png` (before_960.png, before_1024.png = defect; after_960.png, after_1024.png, after_1280.png, after_1440.png = fixed; mobile_375/768/894.png; collapsed_modal_1024.png) | Before/after desktop and mobile screenshots |

## 6. Remaining issues

- None outstanding for this regression.
- Unchanged, pre-existing and environmental: Google Translate `element.js` 403
  (rate-limited from the test sandbox), `webchat.botframework.com` 403, YouTube
  frame refusal, missing `media/kolintang.mp3`. None affect navigation.
