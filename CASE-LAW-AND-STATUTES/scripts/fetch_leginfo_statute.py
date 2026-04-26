#!/usr/bin/env python3
"""
Download a California code section from leginfo and write CASE-LAW-AND-STATUTES/statutes-cal/{CODE}-{SEC}.md
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (compatible; local-legal-cache; +https://leginfo.legislature.ca.gov)"


def extract_section(html_text: str) -> str:
    m = re.search(
        r'<div id="single_law_section"[^>]*>(.*?)</div>\s*<input',
        html_text,
        re.S | re.I,
    )
    if not m:
        m = re.search(r'<div id="single_law_section"[^>]*>(.*)', html_text, re.S | re.I)
    if not m:
        return ""
    chunk = m.group(1)
    t = re.sub(r"<br\s*/?>", "\n", chunk, flags=re.I)
    t = re.sub(r"</p>", "\n\n", t, flags=re.I)
    t = re.sub(r"</h[0-6]+>", "\n", t, flags=re.I)
    t = re.sub(r"</div>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[\t\xa0 ]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("law_code", help="e.g. CCP")
    ap.add_argument("section", help="e.g. 435")
    ap.add_argument(
        "-o",
        "--out",
        type=str,
        default="",
        help="Output .md path (default: ../statutes-cal/{LAW}-{SEC}.md)",
    )
    from pathlib import Path

    args = ap.parse_args()
    here = Path(__file__).resolve().parents[1]
    url = f"https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode={args.law_code}&sectionNum={args.section}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read().decode("utf-8", "replace")
    body = extract_section(raw)
    if not body:
        print("Failed to extract section text", file=sys.stderr)
        return 1
    out = Path(args.out) if args.out else here / "statutes-cal" / f"{args.law_code}-{args.section}.md"
    text = f"Source: {url}\n\n## Text\n\n{body}\n"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"Wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
