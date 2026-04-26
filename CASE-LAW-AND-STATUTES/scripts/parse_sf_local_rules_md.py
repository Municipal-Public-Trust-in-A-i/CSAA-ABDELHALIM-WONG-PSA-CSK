#!/usr/bin/env python3
"""
Extract San Francisco Superior Court Uniform Local Rules from PDF to Markdown:
table of contents, anchored sections, and light cross-links (CRC title index, CCP leginfo, LRSF anchors).

Requires: pdftotext (poppler)

Usage:
  python3 parse_sf_local_rules_md.py
  python3 parse_sf_local_rules_md.py --pdf /path/to/SF-Local-Rules-effective-2026-01-01.pdf
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = ROOT / "rules-of-court" / "sf-superior" / "SF-Local-Rules-effective-2026-01-01.pdf"
OUT_MD = ROOT / "rules-of-court" / "sf-superior" / "SF-Local-Rules-effective-2026-01-01.md"

# CRC rule number -> Judicial Council title index slug (first segment of rule number)
_CRC_TITLE_SLUG: dict[int, str] = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
    10: "ten",
}


def slug_lrsf(num: str) -> str:
    """8.2A -> lrsf-8-2a (normalize case)."""
    n = num.strip().upper()
    return "lrsf-" + re.sub(r"[^0-9A-Z]+", "-", n, flags=re.I).strip("-").lower()


def pdftotext(pdf: Path) -> str:
    r = subprocess.run(
        ["pdftotext", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
        errors="replace",
    )
    return r.stdout


def strip_running_headers(text: str) -> str:
    """Remove repeated page headers (do not strip the following 'Rule N' line — it is real content)."""
    t = text.replace("\r\n", "\n")
    t = re.sub(
        r"\n*Local Rules of Court\n+San Francisco Superior Court\n+",
        "\n\n",
        t,
        flags=re.IGNORECASE,
    )
    t = re.sub(
        r"\n*Local Rules of Court\n+San Francisco Superior Court\n+Appendix A\n+",
        "\n\n",
        t,
        flags=re.IGNORECASE,
    )
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t


@dataclass
class Subsection:
    num: str
    title: str
    lines: list[str] = field(default_factory=list)


@dataclass
class MajorRule:
    num: int
    chapter_title: str
    leading_lines: list[str] = field(default_factory=list)
    subsections: list[Subsection] = field(default_factory=list)


def parse_structure(lines: list[str]) -> tuple[list[MajorRule], list[str], list[str]]:
    """
    Returns (major_rules, appendix_a_lines, index_lines).
    Parsing starts at first 'Rule 1' line after TOC.
    """
    # Find body start: first standalone "Rule 1"
    start = 0
    for i, line in enumerate(lines):
        if line.strip() == "Rule 1":
            start = i
            break
    body = lines[start:]

    major_re = re.compile(r"^Rule (\d+)\s*$")
    chapter_re = re.compile(r"^(\d{1,2})\s+([A-Z].+)$")
    sub_re = re.compile(r"^(\d+\.\d+[A-Za-z]?)\s+(.*)$")

    rules: list[MajorRule] = []
    current_major: MajorRule | None = None
    current_sub: Subsection | None = None
    phase = "rules"  # rules | appendix | index
    appendix_buf: list[str] = []
    index_buf: list[str] = []

    def flush_sub() -> None:
        nonlocal current_sub
        if current_sub is not None and current_major is not None:
            current_major.subsections.append(current_sub)
        current_sub = None

    for raw in body:
        line = raw.rstrip()
        stripped = line.strip()

        if phase == "rules":
            if stripped == "APPENDIX A" or stripped.startswith("APPENDIX A "):
                flush_sub()
                current_major = None
                phase = "appendix"
                appendix_buf.append(line)
                continue

            m = major_re.match(stripped)
            if m:
                flush_sub()
                n = int(m.group(1))
                if not rules or rules[-1].num != n:
                    current_major = MajorRule(num=n, chapter_title="")
                    rules.append(current_major)
                else:
                    current_major = rules[-1]
                current_sub = None
                continue

            m = chapter_re.match(stripped)
            if m and current_major is not None and m.group(1) == str(current_major.num):
                # e.g. "8 Civil Law and Motion..."
                current_major.chapter_title = m.group(2).strip()
                continue

            # Chapter line without leading rule number (e.g. "Ex Parte Applications (CRC …)" for Rule 9)
            if (
                current_major is not None
                and current_sub is None
                and not current_major.chapter_title
                and stripped
                and re.match(r"^[A-Z]", stripped)
                and not major_re.match(stripped)
                and not sub_re.match(stripped)
            ):
                current_major.chapter_title = stripped
                continue

            m = sub_re.match(stripped)
            if m:
                num, rest = m.group(1), m.group(2).strip()
                # Wrapped body line like "5.0 applies to any settlement …" is not a new subsection
                if rest and rest[0].islower():
                    if current_sub is not None:
                        current_sub.lines.append(line)
                    elif current_major is not None:
                        current_major.leading_lines.append(line)
                    continue
                flush_sub()
                current_sub = Subsection(num=num, title=rest, lines=[])
                continue

            if current_sub is not None:
                current_sub.lines.append(line)
            elif current_major is not None and stripped:
                if not current_major.subsections and current_major.chapter_title:
                    current_major.leading_lines.append(line)
            continue

        if phase == "appendix":
            if stripped == "INDEX":
                phase = "index"
                index_buf.append(line)
                continue
            appendix_buf.append(line)
            continue

        if phase == "index":
            index_buf.append(line)

    flush_sub()

    for mr in rules:
        lead = mr.leading_lines
        if lead and mr.subsections:
            mr.subsections[0].lines[:0] = lead
            mr.leading_lines = []
        elif lead:
            mr.subsections.insert(0, Subsection(num=f"{mr.num}.0", title="(preamble)", lines=list(lead)))
            mr.leading_lines = []

    return rules, appendix_buf, index_buf


def collect_lrsf_ids(rules: list[MajorRule]) -> set[str]:
    s: set[str] = set()
    for mr in rules:
        for sub in mr.subsections:
            s.add(sub.num)
    return s


def linkify_ccp(text: str) -> str:
    def one_section(m: re.Match[str]) -> str:
        sec = re.sub(r"\s+", "", m.group(1))
        url = (
            "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?"
            f"lawCode=CCP&sectionNum={sec}"
        )
        return f"[CCP § {m.group(1).strip()}]({url})"

    return re.sub(r"\bCCP\s*§\s*([\d.()a-zA-Z]+)", one_section, text)


def linkify_crc(text: str) -> str:
    """Link CRC cites to the Judicial Council title index (first rule number segment)."""

    def one_crc(m: re.Match[str]) -> str:
        label = m.group(0)
        first = m.group(1)
        try:
            title = int(first.split(".")[0])
        except ValueError:
            return label
        slug = _CRC_TITLE_SLUG.get(title)
        if not slug:
            return label
        url = f"https://courts.ca.gov/cms/rules/index/{slug}"
        return f"[{label}]({url})"

    # e.g. CRC 3.720, CRC 3.1200-3.1207, CRC 1.6
    return re.sub(
        r"\bCRC\s+((?:\d+\.)*\d+[A-Za-z]?(?:\([^)]*\))?(?:\s*[-–]\s*(?:\d+\.)*\d+[A-Za-z]?(?:\([^)]*\))?)?)\b",
        one_crc,
        text,
        flags=re.IGNORECASE,
    )


def linkify_lrsf(text: str, known: set[str]) -> str:
    """Link 'rule 8.2', 'Rule 8.2', 'rules 8.2' to #lrsf-8-2 when that subsection exists."""

    def repl(m: re.Match[str]) -> str:
        num = m.group(1)
        if num in known:
            return f"[{m.group(0)}](#{slug_lrsf(num)})"
        return m.group(0)

    return re.sub(
        r"(?i)\brules?\s+(\d+\.\d+[A-Za-z]?)\b",
        repl,
        text,
    )


def linkify_lrsf_bare_numbers(text: str, known: set[str]) -> str:
    """Link bare '8.2' when preceded by LRSF or local rule."""
    # Avoid dates and money: conservative — only after LRSF or 'Local Rule'
    def repl(m: re.Match[str]) -> str:
        num = m.group(2)
        if num in known:
            return f"{m.group(1)}[{num}](#{slug_lrsf(num)})"
        return m.group(0)

    return re.sub(
        r"(?i)(LRSF|Local Rules?)\s+(\d+\.\d+[A-Za-z]?)\b",
        repl,
        text,
    )


def format_body(text: str, known: set[str]) -> str:
    t = text
    t = linkify_ccp(t)
    t = linkify_crc(t)
    t = linkify_lrsf_bare_numbers(t, known)
    t = linkify_lrsf(t, known)
    return t


def rules_to_markdown(rules: list[MajorRule], known: set[str]) -> str:
    parts: list[str] = []
    parts.append("## Rules (body)\n")
    for mr in rules:
        anchor = f"rule-{mr.num}"
        title = mr.chapter_title or f"Rule {mr.num}"
        parts.append(f'\n<a id="{anchor}"></a>\n\n### Rule {mr.num} — {title}\n')
        for sub in mr.subsections:
            sid = slug_lrsf(sub.num)
            head = f'<a id="{sid}"></a>\n\n#### {sub.num} {sub.title}\n\n'
            body = "\n".join(sub.lines).strip()
            body = format_body(body, known)
            parts.append(head + body + "\n")
    return "".join(parts)


def appendix_to_markdown(lines: list[str]) -> str:
    body = "\n".join(lines).strip()
    return f'<a id="appendix-a"></a>\n\n## Appendix A\n\n```\n{body}\n```\n'


def index_to_markdown(lines: list[str]) -> str:
    body = "\n".join(lines).strip()
    return f'<a id="index"></a>\n\n## Index\n\n```\n{body}\n```\n'


def build_toc(rules: list[MajorRule]) -> str:
    rows: list[str] = []
    rows.append("| Rule | Chapter | Jump |")
    rows.append("| ---: | --- | --- |")
    for mr in rules:
        anchor = f"rule-{mr.num}"
        title = mr.chapter_title or "—"
        rows.append(f"| {mr.num} | {title} | [§](#{anchor}) |")
        for sub in mr.subsections:
            sid = slug_lrsf(sub.num)
            short = (sub.title[:60] + "…") if len(sub.title) > 60 else sub.title
            rows.append(f"| | {sub.num} {short} | [{sub.num}](#{sid}) |")
    return "\n".join(rows) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    ap.add_argument("-o", "--output", type=Path, default=OUT_MD)
    args = ap.parse_args()

    if not args.pdf.is_file():
        print(f"Missing PDF: {args.pdf}", file=sys.stderr)
        return 1

    raw = pdftotext(args.pdf)
    cleaned = strip_running_headers(raw)
    lines = cleaned.splitlines()

    rules, appendix_lines, index_lines = parse_structure(lines)
    known = collect_lrsf_ids(rules)

    toc = build_toc(rules)
    body_md = rules_to_markdown(rules, known)
    app_md = appendix_to_markdown(appendix_lines) if appendix_lines else ""
    idx_md = index_to_markdown(index_lines) if index_lines else ""

    header = f"""---
source_pdf: {args.pdf.name}
parsed_by: parse_sf_local_rules_md.py
court: Superior Court of California, County of San Francisco
title: Uniform Local Rules of Court (LRSF)
---

# San Francisco Uniform Local Rules of Court (indexed)

Official PDF: `{args.pdf.name}`

Cross-references in this file:

- **CRC** … → link to the Judicial Council [California Rules of Court](https://courts.ca.gov/rules-forms/rules-court) title index matching the rule’s title number.
- **CCP §** … → link to [California Legislative Information](https://leginfo.legislature.ca.gov) for that Code of Civil Procedure section.
- **LRSF / local rule** subsection numbers → in-document anchors `#lrsf-…` when that subsection was detected in the PDF.

> **Caveat:** `pdftotext` extraction can mis-wrap lines; verify critical text against the PDF before filing.

## Master index (rules and subsections)

{toc}

"""

    out = header + body_md + "\n" + app_md + "\n" + idx_md
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(out, encoding="utf-8")
    print(f"Wrote {args.output} ({len(rules)} major rules, {len(known)} subsections)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
