"""Render the WCAG 2.2 remediation report to PDF.

Source:  tests/evidence/FINAL_AUDIT/report.html
Output:  tests/evidence/FINAL_AUDIT/Standard_Securities_WCAG22_Remediation_Report.pdf

Chromium's print-to-PDF is used so no extra PDF toolchain is required beyond the
Playwright dependency the audit scripts already use.

Usage:  python tests/audit/make_report_pdf.py
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "tests" / "evidence" / "FINAL_AUDIT" / "report.html"
OUT = ROOT / "tests" / "evidence" / "FINAL_AUDIT" / "Standard_Securities_WCAG22_Remediation_Report.pdf"

MARGIN = {"top": "9mm", "bottom": "10mm", "left": "9mm", "right": "9mm"}


def main() -> int:
    if not SRC.exists():
        print(f"source not found: {SRC}", file=sys.stderr)
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page()
        page.goto(SRC.as_uri(), wait_until="load")
        page.wait_for_timeout(800)
        page.pdf(
            path=str(OUT),
            format="A4",
            print_background=True,
            margin=MARGIN,
        )
        browser.close()

    pages = OUT.read_bytes().count(b"/Type /Page") + OUT.read_bytes().count(b"/Type/Page")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
