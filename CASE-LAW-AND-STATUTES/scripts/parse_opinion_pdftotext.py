#!/usr/bin/env python3
"""
Run pdftotext on opinion PDFs and write .raw.txt + .md (full text) alongside.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "pattern",
        nargs="?",
        default="Motion-Strike-*.pdf",
        help="Glob under opinions-pdf (default: Motion-Strike-*.pdf)",
    )
    args = ap.parse_args()
    pdf_dir = ROOT / "opinions-pdf"
    files = sorted(pdf_dir.glob(args.pattern))
    if not files:
        print(f"No files matching {args.pattern}", file=sys.stderr)
        return 1
    for pdf in files:
        raw = pdf.with_suffix(".raw.txt")
        md = pdf.with_suffix(".md")
        subprocess.run(
            ["pdftotext", "-layout", str(pdf), str(raw)],
            check=True,
        )
        body = raw.read_text(encoding="utf-8", errors="replace")
        title = pdf.stem.replace("-", " ")
        md.write_text(
            f"---\n"
            f"source_pdf: {pdf.name}\n"
            f"title: {title}\n"
            f"---\n\n"
            f"## Full text (pdftotext -layout)\n\n"
            f"```\n{body.rstrip()}\n```\n",
            encoding="utf-8",
        )
        print(f"Wrote {raw.name} and {md.name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
