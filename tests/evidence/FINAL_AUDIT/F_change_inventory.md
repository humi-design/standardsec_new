# Deliverable F — Change Inventory

All changes are in the working tree. **No commit, push, merge or deployment was performed.**
Existing user changes from the prior remediation were preserved; nothing was reset or reverted.

## Files modified in this audit run (on top of the prior 30-file change set)

| File | Change | Finding |
|------|--------|---------|
| `js/app.js` | `Chatbox.display()` no longer returns early when `.send__button`/input are absent; the toggle now binds and updates `aria-expanded`/label on every page | 8.17 |
| `css/accessibility-fixes.css` | Added `a.fab { position: static }` reset (fixes brand-icon stacking); form-field text colour for 4.5:1; 24px minimum for standalone text controls (tel/mailto links, legacy submit, charter close buttons) | 8.4, 8.13 |
| `contact.html` | `aria-label="Send Message"` (was "Send your message") to contain the visible label | 8.12 |
| `signin.html` | `aria-label`/`sr-only` updated to "Login - sign in to your account" | 8.12 |
| `news.html` | Chat message input given `<label>` + `aria-label` + `id`; send button `type="button"` | 8.2 |
| `complaint.html` | Retitled "Complaint Form (Legacy)"; added `lang`, viewport, skip link, `<main>`, form `aria-label`, autocomplete tokens | 8.10, 8.3 |
| `tests/audit/*.py`, `tests/evidence/*` | New audit harness and evidence (untracked) | — |

## Prior remediation change set (preserved, 30 files)
`404.html`, `Advisory.html`, `Commodities.html`, `Currency.html`, `Depository.html`,
`Equity.html`, `IPOs.html`, `Terms.html`, `about.html`, `accessibility-toolbar.html`,
`accessibility.html`, `botbot.html`, `careers.html`, `complaint_new.html`, `contact.html`,
`css/accessibility-fixes.css`, `customers.html`, `disclaimer.html`, `downloads.html`,
`history.html`, `index.html`, `invester_charter.html`, `js/app.js`, `management.html`,
`news.html`, `pay.html`, `privacy.html`, `procedures.html`, `products.html`, `signin.html`,
`single.html`, `smart_ODR.html`, `team.html`.

## Untracked additions
- `tests/audit/` — 8 audit scripts + vendored `axe.min.js`
- `tests/evidence/` — raw JSON results, screenshots, report extract, and this
  `FINAL_AUDIT/` package

## Confirmation
- `git status` shows 35 modified tracked files + 1 untracked `tests/` directory.
- No destructive Git command was used; no prior user change was discarded.
- No production configuration, credential or business data was altered.
