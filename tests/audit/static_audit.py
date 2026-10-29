#!/usr/bin/env python3
"""Static markup audit across all HTML pages: titles, duplicate IDs, alt text,
labels, iframe titles, heading outline. Outputs JSON evidence."""
import json, os, re, sys
from html.parser import HTMLParser
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "tests", "evidence", "static_audit.json")


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.imgs = []
        self.iframes = []
        self.headings = []
        self.labels = []
        self.inputs = []
        self.title = None
        self._in_title = False
        self._cur_h = None
        self._hbuf = ""
        self.html_lang = None
        self._stack = []
        self._label_depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.html_lang = a.get("lang")
        if tag == "label":
            self._label_depth += 1
        if "id" in a and a["id"]:
            self.ids.append(a["id"])
        if tag == "title":
            self._in_title = True
            self._hbuf = ""
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._cur_h = tag
            self._hbuf = ""
        if tag == "img":
            self.imgs.append({"src": a.get("src"), "alt": a.get("alt"),
                              "aria-label": a.get("aria-label"),
                              "role": a.get("role"), "id": a.get("id")})
        if tag == "iframe":
            self.iframes.append({"src": a.get("src"), "title": a.get("title")})
        if tag == "label":
            self.labels.append({"for": a.get("for"), "text": ""})
        if tag in ("input", "select", "textarea"):
            self.inputs.append({
                "tag": tag, "type": a.get("type", ""), "id": a.get("id"),
                "name": a.get("name"), "placeholder": a.get("placeholder"),
                "aria-label": a.get("aria-label"),
                "aria-labelledby": a.get("aria-labelledby"),
                "autocomplete": a.get("autocomplete"), "required": a.get("required"),
                "aria-required": a.get("aria-required"),
                "aria-invalid": a.get("aria-invalid"),
                "aria-describedby": a.get("aria-describedby"),
                "implicit_label": self._label_depth > 0,
            })

    def handle_endtag(self, tag):
        if tag == "label" and self._label_depth > 0:
            self._label_depth -= 1
        if tag == "title" and self._in_title:
            self._in_title = False
            self.title = self._hbuf.strip()
        if tag == self._cur_h:
            self.headings.append({"level": tag, "text": re.sub(r"\s+", " ", self._hbuf).strip()})
            self._cur_h = None

    def handle_data(self, data):
        if self._in_title:
            self._hbuf += data
        if self._cur_h:
            self._hbuf += data
        if self.labels and self._cur_h is None:
            pass


def audit_file(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    p = P()
    p.feed(raw)
    idc = Counter(p.ids)
    dups = {k: v for k, v in idc.items() if v > 1}
    label_fors = {l["for"] for l in p.labels if l["for"]}
    unlabeled = []
    for inp in p.inputs:
        if inp["type"] in ("hidden", "submit", "button", "reset", "image"):
            continue
        has = bool(inp.get("aria-label") or inp.get("aria-labelledby")
                   or inp.get("id") in label_fors or inp.get("implicit_label"))
        if not has:
            unlabeled.append(inp)
    return {
        "file": os.path.basename(path),
        "title": p.title,
        "html_lang": p.html_lang,
        "duplicate_ids": dups,
        "img_total": len(p.imgs),
        "img_missing_alt": [i for i in p.imgs if i.get("alt") is None and not i.get("aria-label") and i.get("role") != "presentation"],
        "iframes": p.iframes,
        "iframes_untitled": [f for f in p.iframes if not (f.get("title") or "").strip()],
        "headings": p.headings,
        "heading_sequence": [h["level"] for h in p.headings],
        "h1_count": sum(1 for h in p.headings if h["level"] == "h1"),
        "unlabeled_inputs": unlabeled,
        "inputs": p.inputs,
    }


def main():
    files = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
    results = [audit_file(os.path.join(ROOT, f)) for f in files]
    titles = Counter(r["title"] for r in results)
    dup_titles = {t: c for t, c in titles.items() if c > 1}
    summary = {
        "pages": len(results),
        "pages_with_duplicate_ids": [r["file"] for r in results if r["duplicate_ids"]],
        "pages_with_duplicate_titles": [r["file"] for r in results if r["title"] in dup_titles],
        "duplicate_title_values": dup_titles,
        "pages_missing_title": [r["file"] for r in results if not r["title"]],
        "pages_with_unlabeled_inputs": [r["file"] for r in results if r["unlabeled_inputs"]],
        "pages_with_untitled_iframes": [r["file"] for r in results if r["iframes_untitled"]],
        "pages_with_missing_alt": [r["file"] for r in results if r["img_missing_alt"]],
        "pages_h1_not_one": [{"file": r["file"], "h1": r["h1_count"]} for r in results if r["h1_count"] != 1],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"summary": summary, "pages": results}, open(OUT, "w"), indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
