# Deliverable G — Remaining Actions

| # | Defect / missing verification | Page / component | Why unresolved | Next step | Blocker type |
|---|------------------------------|------------------|----------------|-----------|--------------|
| 1 | Live screen-reader pass not performed | Whole site (shared nav, forms, chat, ticker, language widget) | No screen reader (NVDA/JAWS/VoiceOver) available in this Linux sandbox | Run NVDA on Windows or VoiceOver on macOS/iOS against the key templates; verify heading/landmark nav, form labels, error announcements, menu state, ticker state, language switch | Environment |
| 2 | Real form submission not verified | `contact.html` (mail.php + reCAPTCHA), Create-Account | Triggering a real submission would send client mail / trip production reCAPTCHA | Test on a staging endpoint with a disposable mailbox and a test reCAPTCHA key | Environment / client |
| 3 | Physical touchscreen target measurement not performed | Footer/inline links, all controls | No touchscreen device attached | Measure with a physical device or device-emulation touch events; confirm 24×24 or spacing | Environment |
| 4 | Native OS text-only zoom not exercised | Whole site | Only browser text-size enlargement was available | Repeat at 200% OS/browser text-only zoom on a physical machine | Environment |
| 5 | Third-party embed failures | Google Translate `element.js` (403), `webchat.botframework.com` (403), YouTube `news.html` (`X-Frame-Options`) | External services rate-limit/refuse requests from this sandbox; not code defects | Re-verify from a normal client network; if YouTube framing must work, switch to the `/embed/` URL | External / code (optional) |
| 6 | Missing local media asset | `news.html` → `media/kolintang.mp3` (404) | Asset absent from repository (pre-existing) | Restore the asset or remove the reference | Code / content |
| 7 | Non-functional hero video reference | `history.html` references `img/monee-slideshow-image3` (absent) | Pre-existing missing asset | Restore asset or remove reference | Content |

None of items 1–4 blocks the accessibility fixes themselves; they are verification gaps
that require a different environment or client-side staging access.
