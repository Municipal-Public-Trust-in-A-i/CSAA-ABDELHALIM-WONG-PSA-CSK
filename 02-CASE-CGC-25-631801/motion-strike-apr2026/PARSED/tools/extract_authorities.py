#!/usr/bin/env python3
"""
Extract legal authorities from cleaned .md pleading text.
Outputs by-document .md and .json; caller merges masters.
"""
import json
import re
import sys
from pathlib import Path
from collections import OrderedDict

# California Reports — split patterns to avoid catastrophic backtracking
RE_CAL_PARTS = [
    re.compile(
        r"\b(\d{1,3}Cal\.\s*(?:App\.\s*)?(?:2d|3d|4th|5th|6th|7th)\s+\d{1,4})\b"
    ),
    re.compile(
        r"\b(\d{1,3}\s*Cal\.\s*(?:App\.\s*)?(?:2d|3d|4th|5th|6th|7th|d)\s+\d{1,4})\b"
    ),
    re.compile(
        r"\b(\d{1,3}\s+Cal\.\s+(?:App\.\s+)?(?:2d|3d|4th|5th|6th|7th)\s+\d{1,4})\b"
    ),
]
# Normalize bad matches
RE_FED = re.compile(
    r"\b(\d{1,4}\s+F\.\d?d(?:\s+Supp\.)?(?:\s+2d)?\s+\d{1,4})\b|"
    r"\b(\d{1,4}\s+U\.\s*S\.\s+\d{1,4})\b|"
    r"\b(\d{1,4}\s+F\.\s+Supp\.\s+2d\s+\d{1,4})\b"
)
RE_STAT = re.compile(
    r"(C\.C\.P\.\s*§\s*[\d.()a-zA-Z]+|"
    r"C\.\s*C\.P\.\s*§\s*[\d.()a-zA-Z]+|"
    r"Code of Civil Procedure\s*§\s*[\d.()a-zA-Z]+|"
    r"Cal\.\s*Civ\.\s*Code\s*§\s*[\d.()a-zA-Z]+|"
    r"Civ\.\s*Code\s*§\s*[\d.()a-zA-Z]+|"
    r"Cal\.\s*Civ\.\s*Code\s*§\s*[\d.()a-zA-Z]+|"
    r"Evid\.\s*Code\s*§\s*[\d.()a-zA-Z]+|"
    r"Ins\.\s*Code\s*§\s*[\d.()a-zA-Z]+|"
    r"Bus\.\s*&\s*Prof\.\s*Code\s*§\s*[\d.()a-zA-Z]+|"
    r"Gov\.\s*Code\s*§\s*[\d.()a-zA-Z]+|"
    r"Pen\.\s*Code\s*§\s*[\d.()a-zA-Z]+|"
    r"Cal\.\s*Const\.\s*,\s*art\.\s*[IVX\d]+|"
    r"U\.\s*S\.\s*Const\.\s*,\s*amend\.\s*[IVX\d]+)"
)
RE_CRC = re.compile(
    r"\b(Cal\.\s*Rules?\s*of\s*Court,?\s*rule\s*[\d.()a-zA-Z]+|Rule\s*of\s*Court\s*[\d.()]+|CRC\s*rule\s*[\d.()a-zA-Z]+)\b",
    re.I,
)
RE_CACI = re.compile(
    r"\b(CACI(?:\s+No\.?)?\s*[\d.()a-zA-Z-]+|"
    r"Witkin[,\s]+[^.\n]+(?:\([^)]+\))?)"
)


def norm_cal(s: str) -> str:
    s = re.sub(r"\s+", " ", s.strip())
    return s


def stat_key(m: str) -> str:
    t = m.upper().replace(" ", "-")
    t = re.sub(r"[^A-Z0-9§.-]+", "-", t)
    t = re.sub(r"-+", "-", t)
    return t[:120]


def extract_from_text(text: str) -> dict:
    cases = OrderedDict()
    for rx in RE_CAL_PARTS:
        for m in rx.finditer(text):
            c = norm_cal(m.group(1))
            if len(c) < 6:
                continue
            cases[c] = True
    feds = OrderedDict()
    for m in RE_FED.finditer(text):
        for g in m.groups():
            if g:
                feds[norm_cal(g)] = True
    stats = OrderedDict()
    for m in RE_STAT.finditer(text):
        raw = m.group(1) if m.lastindex else m.group(0)
        # Trim line-ending noise only (do not strip ')' that closes § 3294(a) etc.)
        raw = re.sub(
            r"(C\.C\.P\.\s*§\s*436)\)\s*$", r"\1", raw
        )  # "§ 436)" from PDF
        raw = re.sub(
            r"(C\.C\.P\.\s*§\s*435)\)\s*$", r"\1", raw
        )
        raw = raw.rstrip(" .;")
        if "provides" in raw.lower() and "47(b)" in raw:
            raw = raw.split("provides", 1)[0].rstrip(" .;")
        raw = raw.strip()
        if raw:
            stats[raw] = True
    crcs = OrderedDict()
    for m in RE_CRC.finditer(text):
        s = m.group(0).strip()
        if "CRC" in s and "View" in s:  # PDF UI artifact
            continue
        crcs[s] = True
    secondary = OrderedDict()
    for m in RE_CACI.finditer(text):
        secondary[m.group(0).strip()[:200]] = True

    return {
        "cases_california": list(cases.keys()),
        "cases_federal": list(feds.keys()),
        "statutes": list(stats.keys()),
        "rules_court": list(crcs.keys()),
        "secondary": list(secondary.keys()),
    }


def render_md(pdf_name: str, data: dict) -> str:
    lines = [f"# Authorities: `{pdf_name}`", ""]
    lines.append(f"- California cases ({len(data['cases_california'])}):")
    for c in data["cases_california"]:
        lines.append(f"  - {c}")
    lines.append("")
    if data["cases_federal"]:
        lines.append(f"- Federal cases ({len(data['cases_federal'])}):")
        for c in data["cases_federal"]:
            lines.append(f"  - {c}")
        lines.append("")
    lines.append(f"- Statute strings ({len(data['statutes'])}):")
    for s in data["statutes"]:
        lines.append(f"  - `{stat_key(s)}` — {s}")
    lines.append("")
    if data["rules_court"]:
        lines.append(f"- Court rules ({len(data['rules_court'])}):")
        for r in data["rules_court"]:
            lines.append(f"  - {r}")
        lines.append("")
    if data["secondary"]:
        lines.append(f"- Secondary / CACI / treatise ({len(data['secondary'])}):")
        for r in data["secondary"]:
            lines.append(f"  - {r}")
        lines.append("")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: extract_authorities.py <input.md> <out_base> <source_pdf_name>", file=sys.stderr)
        sys.exit(1)
    md_path = Path(sys.argv[1])
    out_base = Path(sys.argv[2])
    pdf_name = sys.argv[3] if len(sys.argv) > 3 else md_path.name
    text = md_path.read_text(encoding="utf-8", errors="replace")
    # Strip YAML frontmatter
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3 :]
    data = extract_from_text(text)
    out_base = out_base.with_suffix("")
    (out_base.parent / (out_base.name + ".md")).write_text(
        render_md(pdf_name, data), encoding="utf-8"
    )
    (out_base.parent / (out_base.name + ".json")).write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
