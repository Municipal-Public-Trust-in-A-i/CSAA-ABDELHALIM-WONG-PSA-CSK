#!/usr/bin/env python3
"""
Clean pdftotext -layout output: strip line numbers, form-feed page markers, join hyphen line breaks.
"""
import json
import re
import subprocess
import sys
from pathlib import Path


def pdf_page_count(pdf_path: str) -> int:
    try:
        out = subprocess.check_output(
            ["pdfinfo", pdf_path], text=True, stderr=subprocess.DEVNULL
        )
        for line in out.splitlines():
            if line.strip().lower().startswith("pages:"):
                return int(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return 0


def clean_layout_text(raw: str) -> str:
    # Normalize form feeds to page breaks
    text = raw.replace("\f", "\n\n---\n\n")
    lines = text.splitlines()
    out_lines = []
    for line in lines:
        s = line.rstrip()
        if not s.strip():
            if out_lines and out_lines[-1] != "":
                out_lines.append("")
            continue
        # Page header/footer repeats (e.g. MEMORANDUM OF POINTS... alone)
        if re.match(
            r"^[\s/]*$", s
        ) or s.strip() in (
            "///",
        ):
            continue
        if re.match(r"^\s*\d{1,3}\s*$", s):
            # Standalone line number
            continue
        # " 2" "     text" - line number with 2+ spaces then content
        m = re.match(r"^\s*\d{1,2}\s{2,}(.+)$", s)
        if m:
            out_lines.append(m.group(1).rstrip())
            continue
        # " 1          I. INTRODUCTION" - number + one+ space + content starting non-space
        m = re.match(r"^\s*\d{1,2}\s+(\S.+\S.*|\S.*)$", s)
        if m and not re.match(r"^\d+\s*$", m.group(1)):
            out_lines.append(m.group(1).rstrip())
            continue
        m = re.match(r"^\s*\d{1,2}\s+(\S.*)$", s)
        if m:
            g = m.group(1)
            if len(g.strip()) > 0:
                out_lines.append(g.rstrip())
            continue
        # Continuation / non-numbered line (e.g. indented address block)
        out_lines.append(s)

    # Join broken hyphenation at line ends
    text = "\n".join(out_lines)
    # Join word- hyphens
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Collapse 3+ newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main():
    if len(sys.argv) < 4:
        print(
            "Usage: clean_pleading_text.py <layout.txt> <out.md> <metadata.json> <pdf> [frontmatter key=value ...]",
            file=sys.stderr,
        )
        sys.exit(1)
    layout_path = Path(sys.argv[1])
    out_md = Path(sys.argv[2])
    meta_path = Path(sys.argv[3])
    pdf = sys.argv[4]
    extra = {}
    for kv in sys.argv[5:]:
        if "=" in kv:
            k, v = kv.split("=", 1)
            extra[k] = v

    raw = layout_path.read_text(encoding="utf-8", errors="replace")
    body = clean_layout_text(raw)
    pages = pdf_page_count(pdf) if Path(pdf).exists() else 0

    fm = {
        "source_pdf": pdf,
        "page_count": pages,
        "extracted": "pdftotext -layout + clean_pleading_text.py",
    }
    fm.update(extra)
    # YAML front matter (safe)
    ylines = ["---"]
    for k, v in sorted(fm.items(), key=lambda x: x[0]):
        ylines.append(f"{k}: {v}")
    ylines.append("---")
    out_md.write_text(
        "\n".join(ylines) + "\n\n" + body, encoding="utf-8"
    )
    meta_path.write_text(json.dumps(fm, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
