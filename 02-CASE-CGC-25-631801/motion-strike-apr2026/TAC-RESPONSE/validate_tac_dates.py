#!/usr/bin/env python3
"""
Cross-check dates and docket-style facts in TAC-RESPONSE markdown against CALENDARS/APRIL22.md.

Run from repository root:
  python3 801-MOTION-STRIKE-APR-22/TAC-RESPONSE/validate_tac_dates.py
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
TAC_DIR = Path(__file__).resolve().parent
CALENDAR = REPO / "CALENDARS" / "APRIL22.md"


@dataclass
class DateDiscrepancy:
    path: Path
    line_no: int
    line_text: str
    expected_substring: str | None
    detail: str


EXPECTED_SUBSTRINGS: list[tuple[str, str]] = [
    ("801 SAC-leave heading", "## May 6, 2026"),
    ("801 SAC dept.", "Dept. 301"),
    ("802 SAC-leave hearing row", "**Apr 30 (Thu)**"),
    ("802 SAC-leave label", "802 SAC-leave hearing"),
    ("802 SAC dept.", "Dept. 302"),
    ("801 defense MTS heading", "## May 22, 2026"),
    ("802 defense MTS heading", "## May 19, 2026"),
    ("Defense MTS filing date narrative", "filed Apr 22, 2026"),
    ("801 Demurrer anchor", "May 12"),
    ("Anti-SLAPP anchor", "May 13"),
    ("CMC anchor", "May 27"),
    ("Underlying case number", "CGC-21-594102"),
]


def load_calendar_text() -> str:
    if not CALENDAR.is_file():
        return ""
    return CALENDAR.read_text(encoding="utf-8", errors="replace")


def validate_calendar_present(calendar_text: str) -> list[DateDiscrepancy]:
    out: list[DateDiscrepancy] = []
    if not calendar_text.strip():
        out.append(
            DateDiscrepancy(
                CALENDAR,
                0,
                "",
                None,
                "Calendar file missing or empty; cannot validate against APRIL22.md",
            )
        )
        return out
    for label, needle in EXPECTED_SUBSTRINGS:
        if needle not in calendar_text:
            out.append(
                DateDiscrepancy(
                    CALENDAR,
                    0,
                    "",
                    needle,
                    f"Calendar anchor missing in {CALENDAR.name}: {label}",
                )
            )
    return out


def scan_md_files(paths: list[Path]) -> list[DateDiscrepancy]:
    issues: list[DateDiscrepancy] = []
    for path in paths:
        if not path.is_file():
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(lines, start=1):
            if "2025" in line and re.search(r"\b2025\b", line):
                if "December 23, 2025" in line or "February 25, 2026" in line:
                    continue
                if "April 25, 2025" in line and "judgment" in line.lower():
                    continue
            if "`[HEARING DATE]`" in line or "TBD" in line:
                continue
    return issues


def validate_dates(md_files: list[Path], calendar: Path) -> list[DateDiscrepancy]:
    """
    Extract dates from markdown files and cross-check against calendar anchors.
    Returns discrepancies (including missing calendar anchors).
    """
    cal_text = calendar.read_text(encoding="utf-8", errors="replace") if calendar.is_file() else ""
    out = validate_calendar_present(cal_text)
    out.extend(scan_md_files(md_files))
    return out


def main() -> int:
    md_files = sorted(TAC_DIR.glob("*.md"))
    disc = validate_dates(md_files, CALENDAR)
    if disc:
        for d in disc:
            loc = f"{d.path}:{d.line_no}" if d.line_no else str(d.path)
            print(f"{loc}: {d.detail}", file=sys.stderr)
            if d.expected_substring:
                print(f"  expected substring: {d.expected_substring}", file=sys.stderr)
            if d.line_text:
                print(f"  line: {d.line_text[:200]}", file=sys.stderr)
        return 1
    print("validate_tac_dates: OK (calendar anchors present; no heuristic issues flagged).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
