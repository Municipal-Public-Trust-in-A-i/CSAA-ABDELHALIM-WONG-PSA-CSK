#!/usr/bin/env python3
"""Merge by-document authority .json files into MASTER-AUTHORITY-LIST.{md,json}."""
import json
import sys
from pathlib import Path
from collections import OrderedDict


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def merge_docs(dir_path: Path, basenames: list[str], label: str) -> dict:
    merged_cases = OrderedDict()
    merged_fed = OrderedDict()
    merged_stat = OrderedDict()
    merged_rules = OrderedDict()
    merged_sec = OrderedDict()
    by_doc = {}
    for base in basenames:
        p = dir_path / f"{base}.json"
        if not p.exists():
            continue
        d = load_json(p)
        by_doc[base] = d
        for c in d.get("cases_california", []):
            merged_cases[c] = True
        for c in d.get("cases_federal", []):
            merged_fed[c] = True
        for c in d.get("statutes", []):
            merged_stat[c] = True
        for c in d.get("rules_court", []):
            merged_rules[c] = True
        for c in d.get("secondary", []):
            merged_sec[c] = True
    return {
        "label": label,
        "sources": basenames,
        "cases_california": sorted(merged_cases.keys(), key=str.lower),
        "cases_federal": sorted(merged_fed.keys(), key=str.lower),
        "statutes": sorted(merged_stat.keys(), key=str.lower),
        "rules_court": sorted(merged_rules.keys(), key=str.lower),
        "secondary": sorted(merged_sec.keys(), key=str.lower),
        "by_document": by_doc,
    }


def write_md(out: Path, data: dict) -> None:
    lines = [
        f"# Master authority list — {data['label']}",
        "",
        f"**Sources merged:** {', '.join(data['sources'])}",
        "",
        f"## California cases ({len(data['cases_california'])})",
        "",
    ]
    for c in data["cases_california"]:
        lines.append(f"- {c}")
    lines.append("")
    if data["cases_federal"]:
        lines.append(f"## Federal cases ({len(data['cases_federal'])})")
        lines.append("")
        for c in data["cases_federal"]:
            lines.append(f"- {c}")
        lines.append("")
    lines.append(f"## Statutes / codes ({len(data['statutes'])})")
    lines.append("")
    for c in data["statutes"]:
        lines.append(f"- {c}")
    lines.append("")
    if data["rules_court"]:
        lines.append("## Court rules")
        lines.append("")
        for c in data["rules_court"]:
            lines.append(f"- {c}")
        lines.append("")
    if data["secondary"]:
        lines.append("## Secondary / CACI / treatise")
        lines.append("")
        for c in data["secondary"]:
            lines.append(f"- {c}")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


def main():
    if len(sys.argv) < 2:
        print("Usage: merge_master_authority.py <AUTHORITY-INDEX_dir> <def_basename>...", file=sys.stderr)
        sys.exit(1)
    adir = Path(sys.argv[1])
    basenames = sys.argv[2:]
    label = adir.parent.name  # 801-.../PARSED -> we pass full path
    # argv[1] is like .../801-MOTION-STRIKE-APR-22/PARSED/AUTHORITY-INDEX
    data = merge_docs(adir / "by-document", basenames, adir.parent.parent.name)
    (adir / "MASTER-AUTHORITY-LIST.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )
    write_md(adir / "MASTER-AUTHORITY-LIST.md", data)


if __name__ == "__main__":
    main()
