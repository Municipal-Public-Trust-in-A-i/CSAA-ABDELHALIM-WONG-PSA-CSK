#!/usr/bin/env python3
"""
Compare 801/802 motion-strike MASTER-AUTHORITY-LIST.json files against
CASE-LAW-AND-STATUTES cache. Writes gap-report-motion-strike.json under CASE-LAW-AND-STATUTES/.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent

PATHS_801_802 = [
    REPO / "801-MOTION-STRIKE-APR-22" / "PARSED" / "AUTHORITY-INDEX" / "MASTER-AUTHORITY-LIST.json",
    REPO / "802-MOTION-STRIKE-APR-22" / "PARSED" / "AUTHORITY-INDEX" / "MASTER-AUTHORITY-LIST.json",
]


def normalize_cal_cite(cite: str) -> str:
    t = re.sub(r"\s+", " ", cite.strip())
    t = re.sub(r"Cal\.\s*App\.\s*", "Cal. App. ", t, flags=re.I)
    return t


def parse_cal_citation(cite: str) -> dict | None:
    t = normalize_cal_cite(cite)
    m = re.match(
        r"^(\d+)\s+Cal\.\s*(?:App\.\s*)?((?:2d|3d|4th|5th|6th|7th))\s+(\d+)$",
        t,
        re.I,
    )
    if not m:
        return None
    vol, rep, page = m.group(1), m.group(2).lower(), m.group(3)
    is_app = bool(re.search(r"App\.", cite, re.I))
    return {
        "raw": t,
        "volume": vol,
        "reporter": rep,
        "first_page": page,
        "is_appellate": is_app,
    }


def statute_keys_for_citation(s: str) -> set[str]:
    """Filenames in statutes-cal/ to check (e.g. CCP-435.md)."""
    t = re.sub(r"\s+", " ", s.strip())
    out: set[str] = set()
    n = re.search(r"§\s*([0-9.]+[a-z]?)", t, re.I)
    if not n:
        return out
    sec = n.group(1)
    if re.search(r"C\.?C\.?P\.|Code of Civil Procedure", t, re.I):
        out.add(f"CCP-{sec}.md")
    if re.search(r"Civ\.?\s*Code", t, re.I):
        sub = re.search(r"§\s*([0-9.]+)(?:\(([a-z0-9]+)\))?", t, re.I)
        if sub:
            out.add(f"CIV-{sub.group(1)}.md")
            if sub.group(2):
                out.add(f"CIV-{sub.group(1)}-{sub.group(2)}.md")
    return out


def find_case_artifacts(meta: dict) -> list[str]:
    """PDFs/MDs under CASE-LAW-AND-STATUTES that match vol + first page (Demurrer naming)."""
    vol, page = meta["volume"], meta["first_page"]
    out: list[str] = []
    seen: set[str] = set()
    for sub in ("opinions-pdf", "cases-cal-supreme", "cases-cal-appellate"):
        base = ROOT / sub
        if not base.is_dir():
            continue
        for p in base.glob(f"**/*vol{vol}*p{page}*"):
            if p.is_file():
                r = str(p.relative_to(ROOT))
                if r not in seen:
                    seen.add(r)
                    out.append(r)
        for p in base.glob(f"**/*{vol}*Cal*{page}*"):
            if p.is_file() and p.suffix in (".pdf", ".md"):
                r = str(p.relative_to(ROOT))
                if r not in seen:
                    seen.add(r)
                    out.append(r)
    return out


def justia_url(meta: dict) -> str:
    v, p, r, app = (
        meta["volume"],
        meta["first_page"],
        meta["reporter"],
        meta["is_appellate"],
    )
    if not app and r in ("2d", "3d", "4th", "5th"):
        rseg = "2d" if r == "2d" else "3d" if r == "3d" else f"{r[0]}{r[1]}"
        if r == "2d":
            rseg = "2d"
        elif r == "3d":
            rseg = "3d"
        elif r == "4th":
            rseg = "4th"
        elif r == "5th":
            rseg = "5th"
        return f"https://law.justia.com/cases/california/supreme-court/{rseg}/{v}/{p}.html"
    if app and r in ("2d", "3d", "4th", "5th", "6th", "7th"):
        rseg = r if r in ("2d", "3d") else r
        return f"https://law.justia.com/cases/california/court-of-appeal/{rseg}/{v}/{p}.html"
    return ""


def main() -> int:
    all_cal: set[str] = set()
    all_fed: set[str] = set()
    all_stat: set[str] = set()
    for jp in PATHS_801_802:
        if not jp.is_file():
            print(f"Missing {jp}", file=sys.stderr)
            return 1
        data = json.loads(jp.read_text(encoding="utf-8"))
        for c in data.get("cases_california", []):
            all_cal.add(c)
        for c in data.get("cases_federal", []):
            all_fed.add(c)
        for c in data.get("statutes", []):
            all_stat.add(c)

    statute_files = {f.name for f in (ROOT / "statutes-cal").glob("*.md")}

    gaps_stat: list[dict] = []
    for s in sorted(all_stat):
        keys = statute_keys_for_citation(s)
        present = any(k in statute_files for k in keys)
        if not present:
            gaps_stat.append({"citation": s, "expected_files": sorted(keys)})

    case_rows: list[dict] = []
    for cite in sorted(all_cal):
        meta = parse_cal_citation(cite)
        if not meta:
            case_rows.append(
                {
                    "citation": cite,
                    "error": "parse_failed",
                    "justia_url": "",
                }
            )
            continue
        found = find_case_artifacts(meta)
        has_pdf = any(f.endswith(".pdf") for f in found)
        case_rows.append(
            {
                "citation": cite,
                "parsed": {k: v for k, v in meta.items() if k != "raw"},
                "cache_hits": found,
                "has_opinion_pdf": has_pdf,
                "justia_url": justia_url(meta),
                "needs_fetch": not has_pdf,
            }
        )

    fed_rows: list[dict] = []
    for cite in sorted(all_fed):
        m = re.search(r"(\d+)\s+U\.\s*S\.\s+(\d+)", cite, re.I)
        if not m:
            continue
        vol, pg = m.group(1), m.group(2)
        pdfs = list((ROOT / "opinions-pdf").glob(f"Demurrer-us-vol{vol}-p{pg}-*.pdf"))
        fed_rows.append(
            {
                "citation": cite,
                "has_opinion_pdf": bool(pdfs),
                "cache_hits": [str(p.relative_to(ROOT)) for p in pdfs[:3]],
            }
        )

    report = {
        "source_jsons": [str(p) for p in PATHS_801_802],
        "statutes_cited": sorted(all_stat),
        "statute_gaps": gaps_stat,
        "california_cases": case_rows,
        "federal_cases": fed_rows,
    }
    out_path = ROOT / "gap-report-motion-strike.json"
    out_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
