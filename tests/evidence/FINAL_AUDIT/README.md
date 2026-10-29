# Final WCAG 2.2 Audit Package — Standard Securities

Deliverables produced by the independent verification run (see `../report/` for the
original PDF-derived report text and `../report_matrix.json` for the extracted 56-criterion
matrix).

| File | Deliverable |
|------|-------------|
| `A_executive_summary.md` | A — Executive summary and verdict |
| `B_finding_tracker.md` | B — 17-finding closure tracker (8.1–8.17) |
|  `C_criteria_matrix.md` | C — Complete 56-criterion matrix with final status |
| `D_page_matrix.md` | D — Page-by-page test matrix (32 pages) |
| `E_test_execution_report.md` | E — Test execution report |
| `F_change_inventory.md` | F — Change inventory |
| `G_remaining_actions.md` | G — Remaining actions and blockers |
| `summary.json`, `criteria_final.json`, `page_matrix.json` | Machine-readable backing data |

Raw evidence (JSON + screenshots) lives one level up in `tests/evidence/`:
`axe_results.json`, `verify_static.json`, `skiplink.json`, `interaction.json`,
`motion.json`, `language.json`, `contrast.json`, `smart_odr_contrast.json`,
`smart_odr_step_heading_*.png`, `language_hindi_index.png`, `skiplink_focused.png`.

## Reproducing
```bash
cd /workspace/project/standardsec_new
python -m http.server 12000 &        # serve the site
python tests/audit/axe_scan.py
python tests/audit/a11y_verify.py
python tests/audit/skiplink_audit.py
python tests/audit/interaction_audit.py
python tests/audit/motion_audit.py
python tests/audit/language_audit.py
python tests/audit/smartodr_contrast.py
```

## Verdict
**FIXES APPLIED BUT PARTIALLY UNVERIFIED** — see `A_executive_summary.md`.
