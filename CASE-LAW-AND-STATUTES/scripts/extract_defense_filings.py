#!/usr/bin/env python3
"""
Extract text and structured metadata from DEFENSE-FILINGS-PDF for CGC-25-631801 and
631802. Writes DEFENSE-FILINGS/ at repository root with extractions, analysis companions,
per-day memos, and index files.

Usage:
  python3 extract_defense_filings.py
  python3 extract_defense_filings.py --pdf-dir /path/to/DEFENSE-FILINGS-PDF --out /path/to/DEFENSE-FILINGS
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Reuse citation parsers
_SCRIPTS = Path(__file__).resolve().parent
_WORKSPACE = _SCRIPTS.parents[2]  # repo root
sys.path.insert(0, str(_SCRIPTS))
from cache_demurrer_authorities import (  # noqa: E402
    apply_citation_fixes,
    cap_reporter_slug,
    drop_phantom_bockrath_212,
    federal_cap_slug,
    parse_cal_cites,
    parse_us_cites,
)

DEFAULT_PDF_DIR = _WORKSPACE / "DEFENSE-FILINGS-PDF"
DEFAULT_OUT = _WORKSPACE / "DEFENSE-FILINGS"

MONTHS_MAP = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

CASE_RE = re.compile(r"CGC-25-63180([12])", re.I)
# E-filing and signature dates
DATE_PATTERNS = [
    re.compile(
        r"Electronically\s+(?:FILED|Filed|filed)\s+[^\n]*?(\d{1,2})/(\d{1,2})/(\d{4})",
        re.I,
    ),
    re.compile(
        r"(?:\bFiled|FILED)\s*(?:on|:)?\s*(\d{1,2})/(\d{1,2})/(\d{4})",
    ),
    re.compile(r"\bDated\s*:?\s*(\d{1,2})/(\d{1,2})/(\d{4})", re.I),
    re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})"),
]
# California codes and rules (broad)
STATUTE_RES = [
    re.compile(
        r"(?:\bCCP\b|Code\s+Civ\.\s*Proc\.|Civ\.\s*Code|"
        r"Evid\.\s*Code|Bus\.\s*&\s*Prof\.\s*Code|"
        r"Gov(?:'|)t\.?\s*Code|Pen\.\s*Code)\s*§\s*[\d.]+(?:\([a-zA-Z0-9]+\))*",
        re.I,
    ),
    re.compile(
        r"California\s+Const\.?\s*,?\s*art\.\s*[IVX\d]+,?\s*§\s*[\d.]+", re.I
    ),
    re.compile(
        r"U\.\s*S\.\s*Const\.\s*,?\s*amend\.?\s*[IVX\d]+", re.I
    ),
    re.compile(
        r"Cal\.\s*Rules?\s+of\s+Court,?\s*rule\s*[\d.]+", re.I
    ),
]


def _run(cmd: list[str]) -> str:
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {cmd!r} stderr={r.stderr!r}")
    return r.stdout or ""


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_page_count(path: Path) -> int:
    out = _run(["pdfinfo", str(path)])
    for line in out.splitlines():
        if line.strip().lower().startswith("pages:"):
            return int(line.split()[-1].strip())
    return 0


def pdftotext_range(path: Path, f: int, l: int, layout: bool) -> str:
    args = (
        ["pdftotext", "-layout", "-f", str(f), "-l", str(l), str(path), "-"]
        if layout
        else ["pdftotext", "-f", str(f), "-l", str(l), str(path), "-"]
    )
    return _run(args)


def pdftotext_full(path: Path, layout: bool) -> str:
    args = ["pdftotext"] + (["-layout"] if layout else []) + [str(path), "-"]
    return _run(args)


def clean_text(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"\n{4,}", "\n\n\n", s)
    s = re.sub(r"[ \t]+\n", "\n", s)
    return s.strip() + "\n" if s.strip() else ""


def normalize_stem(name: str) -> str:
    s = re.sub(r"^\(\d+\)\s+", "", name)
    s = s.replace("  ", " ")
    return s.rsplit(".", 1)[0] if "." in s else s


def classify_filename(filename: str) -> tuple[str, str | None, bool]:
    """
    Returns: (pleading_type_slug, motion_family, is_procedural_chaff)
    """
    base = filename.rsplit(".", 1)[0]
    n = base.lower()
    n_unprefixed = re.sub(r"^\(\d+\)\s+", "", n).strip()
    is_chaff = "consent to electronic" in n or n.startswith("stipulation tolling")
    motion: str | None
    if "anti-slapp" in n or "anti slapp" in n:
        motion = "Anti-SLAPP"
    elif "ccp436" in n or "ccp-436" in n or re.search(
        r"\bccp\s*\.?\s*436\b", n
    ):
        motion = "CCP436"
    elif "demurrer" in n:
        motion = "Demurrer"
    elif "sac" in n or "leave to file" in n:
        motion = "MFL-SAC"
    else:
        motion = None
    if n_unprefixed.startswith("ntc") or " ntc" in f" {n_unprefixed}":
        return "notice", motion, is_chaff
    if n_unprefixed.startswith("mpa") or n_unprefixed.startswith("mpas"):
        return "mpa", motion, is_chaff
    if "dec of toc" in n or "dec of toc" in n.replace(" ", ""):
        return "dec-toc", motion, is_chaff
    if "rfjn" in n or "rjn" in n:
        return "rfjn", motion, is_chaff
    if "prop order" in n or "proposed order" in n:
        return "prop-order", motion, is_chaff
    if "stmnt" in n or "statement" in n:
        return "stmnt", motion, is_chaff
    if "opposition" in n:
        return "opposition", motion, is_chaff
    if "m&c" in n or "m & c" in n:
        return "mc-letter", motion, is_chaff
    if "stipulation" in n:
        return "stipulation", motion, is_chaff
    if "consent" in n:
        return "consent", motion, is_chaff
    return "other", motion, is_chaff


def case_from_text(text: str) -> str | None:
    m = CASE_RE.search(text)
    if not m:
        return None
    return f"CGC-25-63180{m.group(1)}"


def case_from_filename(name: str) -> str | None:
    n = name.lower()
    if "631801" in n:
        return "CGC-25-631801"
    if "631802" in n:
        return "CGC-25-631802"
    if "abdelhalim" in n:
        return "CGC-25-631801"
    if "csaa" in n:
        return "CGC-25-631802"
    return None


def parse_filing_date(text: str) -> str | None:
    """Return YYYY-MM-DD. Prefer e-file stamp in header, else last Dated: Month, YYYY in body."""
    best: tuple[int, str] | None = None
    head = text[:20000] if len(text) > 20000 else text
    dpat = re.compile(
        r"\bDated\s*:\s*"
        r"(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+"
        r"(\d{1,2}),\s*(\d{4})",
        re.I,
    )
    for i, pat in enumerate(DATE_PATTERNS):
        for m in pat.finditer(head):
            mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if 1 <= mo <= 12 and 1 <= d <= 31 and 2000 <= y <= 2100:
                key = f"{y:04d}-{mo:02d}-{d:02d}"
                pri = (0 if "Electronic" in m.group(0) else 1) * 10 + i
                if i == 3 and m.start() < 4000:
                    pri += 25
                if best is None or pri < best[0]:
                    best = (pri, key)
    # Signature "Dated: April 1, 2026" in last portion only (long MPAs include historical dates)
    last_dated_key: str | None = None
    tail = text[-12000:] if len(text) > 12000 else text
    for m in dpat.finditer(tail):
        mon = MONTHS_MAP.get(m.group(1).lower())
        day = int(m.group(2))
        y = int(m.group(3))
        if mon and 1 <= day <= 31 and 2000 <= y <= 2100:
            last_dated_key = f"{y:04d}-{mon:02d}-{day:02d}"
    if not last_dated_key and len(text) > 50000:
        for m in dpat.finditer(text):
            mon = MONTHS_MAP.get(m.group(1).lower())
            day = int(m.group(2))
            y = int(m.group(3))
            if mon and 1 <= day <= 31 and 2000 <= y <= 2100:
                last_dated_key = f"{y:04d}-{mon:02d}-{day:02d}"
    if last_dated_key and (best is None or best[0] > 5):
        best = (5, last_dated_key)
    return best[1] if best else None


def collect_statute_cites(text: str) -> list[str]:
    out: set[str] = set()
    for rx in STATUTE_RES:
        for m in rx.finditer(text):
            out.add(m.group(0)[:200].strip())
    return sorted(out)


def collect_reporter_cites(text: str) -> list[str]:
    t = text.replace("\n", " ")
    keys: set[str] = set()
    cal: set[tuple[str, str, str, bool]] = set()
    for v, r, p, is_app in parse_cal_cites(t):
        cal.add((v, r, p, is_app))
    for v, r, p, is_app in apply_citation_fixes(t):
        cal.add((v, r, p, is_app))
    drop_phantom_bockrath_212(cal)
    for v, r, p, is_app in cal:
        keys.add(f"{v} {cap_reporter_slug(is_app, r)} {p}")
    for series, v, p in parse_us_cites(t):
        keys.add(f"{v} {federal_cap_slug(series)} {p}")
    return sorted(keys)


def parse_toa_block(text: str) -> list[dict[str, str]]:
    start = text.upper().find("TABLE OF AUTHORITIES")
    if start < 0:
        return []
    end = text.find("STATEMENT OF", start)
    if end < 0:
        end = text.find("INTRODUCTION", start)
    if end < 0 or end < start:
        end = min(len(text), start + 20000)
    block = text[start:end]
    cases: list[dict[str, str]] = []
    current_name: str | None = None
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped or "PAGE" in line.upper() and "PAGE(S)" in line.upper():
            if "PAGE" in line and "AUTHORITY" in block[:500]:
                pass
        cite_m = re.match(r"^\s*\((\d{4})\)\s+(.+)$", line)
        if cite_m and current_name:
            cases.append(
                {
                    "case_name": current_name,
                    "year": cite_m.group(1),
                    "reporter_line": cite_m.group(2).strip(),
                }
            )
            continue
        name_m = re.match(r"^(.+?)\s*\.{5,}", line)
        if name_m:
            current_name = name_m.group(1).strip()
            continue
    return cases


def extract_heading_skeleton(text: str, max_n: int = 40) -> list[str]:
    lines = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if re.match(
            r"^([IVX]{1,6}|[1-9]\d?|[A-Z])\s*[\).]\s+.{4,80}$", s, re.I
        ):
            lines.append(s[:200])
        if len(lines) >= max_n:
            break
    return lines


def guess_role(pleading: str) -> str:
    if pleading in ("opposition",):
        return "opposing"
    if pleading in ("notice", "mpa", "dec-toc", "rfjn", "prop-order", "stmnt"):
        return "moving"
    if pleading in ("stipulation", "consent", "mc-letter"):
        return "procedural"
    return "supporting"


def theory_blurb(text: str, max_para: int = 3) -> list[str]:
    t = text
    for marker in (
        "INTRODUCTION",
        "INTRO",
        "ARGUMENT",
        "STATEMENT OF",
    ):
        idx = t.upper().find("\n" + marker)
        if idx < 0:
            idx = t.upper().find(marker)
        if idx >= 0:
            t = t[idx: idx + 8000]
            break
    paras = [p.strip() for p in re.split(r"\n\n+", t) if len(p.strip()) > 50]
    return paras[:max_para]


def requested_relief_snips(text: str) -> list[str]:
    t = text.upper()
    for key in (
        "RELIEF REQUESTED",
        "PRAYER",
        "WHEREFORE",
        "CONCLUSION",
        "REQUESTED RELIEF",
    ):
        i = t.find(key)
        if i >= 0:
            snip = text[i : i + 2500]
            out = re.findall(r"[^\n]{20,200}", snip)
            return [x.strip() for x in out[:8]]
    return []


@dataclass
class DocRec:
    source_pdf: Path
    stem: str
    normalized_stem: str
    case_number: str
    pleading: str
    motion_family: str | None
    is_chaff: bool
    filing_date: str | None
    output_dir: Path
    sha256: str
    page_count: int
    text_flow: str = ""
    text_layout: str = ""
    authorities: dict[str, Any] = field(default_factory=dict)
    fdate_inferred: bool = False


@dataclass
class PendingDoc:
    source_pdf: Path
    stem: str
    norm: str
    pleading: str
    motion: str | None
    is_chaff: bool
    case: str
    flow: str
    layout: str
    fdate: str | None
    sha: str
    npages: int
    auth: dict[str, Any]
    fdate_inferred: bool = False


def build_authority_index_entry(text: str) -> dict[str, Any]:
    st = collect_statute_cites(text)
    rep = collect_reporter_cites(text)
    toa = parse_toa_block(text)
    return {
        "statutes_and_codes": st,
        "reporter_cites_normalized": rep,
        "toa_case_rows": toa,
    }


def build_analysis_md(
    rec: DocRec,
    cross_refs: list[str],
) -> str:
    title = rec.stem
    t = rec.text_flow
    role = guess_role(rec.pleading)
    auth = rec.authorities
    lines: list[str] = [
        f"# Analysis: {title}",
        "",
        "## Document header",
        "",
        f"- **Case**: {rec.case_number}",
        f"- **Filing date** (best parse): {rec.filing_date or 'undated'}",
        f"- **Filing date inferred from same case and motion bundle**: {rec.fdate_inferred}",
        f"- **Pleading type**: {rec.pleading}",
        f"- **Motion family** (if any): {rec.motion_family or 'n/a'}",
        f"- **Role (heuristic)**: {role}",
        f"- **Procedural chaff (limited analysis)**: {rec.is_chaff}",
        "",
    ]
    if rec.is_chaff:
        lines.extend(
            [
                "## Note",
                "",
                "Procedural filing; no substantive motion analysis in this companion.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.append("## Principal theory (heuristic, first section excerpts)")
    lines.append("")
    for p in theory_blurb(t):
        lines.append(f"- {p[:700]}{'...' if len(p) > 700 else ''}")
    lines.append("")
    lines.append("## Position and requested relief (snippets)")
    lines.append("")
    for s in requested_relief_snips(t) or ["(not auto-detected)"]:
        lines.append(f"- {s[:500]}")
    lines.append("")
    lines.append("## Objections and structure (skeleton from headings)")
    lines.append("")
    for h in extract_heading_skeleton(t):
        lines.append(f"- {h}")
    if len(extract_heading_skeleton(t)) == 0:
        lines.append("- (no numbered headings auto-detected)")
    lines.append("")
    lines.append("## Legal authority")
    lines.append("")
    lines.append("### Table of authorities (parsed rows, if any)")
    lines.append("")
    if auth.get("toa_case_rows"):
        for row in auth["toa_case_rows"][:30]:
            lines.append(
                f"- {row.get('case_name', '')} ({row.get('year', '')}): {row.get('reporter_line', '')}"
            )
    else:
        lines.append("- (no TOA block detected)")
    lines.append("")
    lines.append("### Statutes, codes, rules (regex pass)")
    lines.append("")
    for c in (auth.get("statutes_and_codes") or [])[:50]:
        lines.append(f"- {c}")
    if not auth.get("statutes_and_codes"):
        lines.append("- (none or none detected)")
    lines.append("")
    lines.append("### Reporter cites (normalized keys)")
    lines.append("")
    for c in (auth.get("reporter_cites_normalized") or [])[:60]:
        lines.append(f"- `{c}`")
    if not auth.get("reporter_cites_normalized"):
        lines.append("- (none or none detected)")
    lines.append("")
    lines.append("## Specific claims (factual assertions, sample sentences)")
    lines.append("")
    sents = re.split(
        r"(?<=[.!?])\s+",
        re.sub(r"\s+", " ", t[:15000]),
    )
    key = re.compile(
        r"\b(Plaintiff|Defendant|alleges|alleged|contends|asserts|is entitled|must)\b",
        re.I,
    )
    out_s = [s for s in sents if key.search(s) and 40 < len(s) < 500][:15]
    for s in out_s:
        lines.append(f"- {s}")
    if not out_s:
        lines.append("- (no sample sentences auto-selected)")
    lines.append("")
    lines.append("## Cross-references (same case, same filing date, same motion family)")
    lines.append("")
    for x in cross_refs:
        lines.append(f"- {x}")
    if not cross_refs:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)


def discover_pdfs(pdf_dir: Path) -> list[Path]:
    return sorted(
        p for p in pdf_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"
    )


def infer_missing_filing_dates(pendings: list[PendingDoc]) -> None:
    """If a document has no parseable date, use the mode date for same case + motion family."""
    from collections import Counter

    groups: dict[tuple[str, str], list[PendingDoc]] = defaultdict(list)
    for p in pendings:
        if p.case != "UNKNOWN" and p.motion:
            groups[(p.case, p.motion)].append(p)
    for _key, g in groups.items():
        dated = [x.fdate for x in g if x.fdate]
        if not dated:
            continue
        mode_date, _c = Counter(dated).most_common(1)[0]
        for x in g:
            if x.fdate is None:
                x.fdate = mode_date
                x.fdate_inferred = True


def align_outlier_bundle_dates(pendings: list[PendingDoc], max_days: int = 21) -> None:
    """
    When one filing in a motion bundle has a date far from the bundle mode (e.g. long
    combined PDF picking up an exhibit date), replace it with the mode date.
    """
    from collections import Counter
    from datetime import datetime

    def _d(s: str):
        return datetime.strptime(s, "%Y-%m-%d").date()

    groups: dict[tuple[str, str], list[PendingDoc]] = defaultdict(list)
    for p in pendings:
        if p.case != "UNKNOWN" and p.motion:
            groups[(p.case, p.motion)].append(p)
    for _key, g in groups.items():
        dated = [x.fdate for x in g if x.fdate]
        if len(dated) < 2:
            continue
        ref_s = max(dated)
        try:
            ref = _d(ref_s)
        except ValueError:
            continue
        for x in g:
            if not x.fdate:
                continue
            try:
                cur = _d(x.fdate)
            except ValueError:
                continue
            if abs((cur - ref).days) > max_days:
                x.fdate = ref_s
                x.fdate_inferred = True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--pdf-dir",
        type=Path,
        default=DEFAULT_PDF_DIR,
        help="Directory containing defense PDFs",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output root (DEFENSE-FILINGS)",
    )
    args = ap.parse_args()
    pdf_dir: Path = args.pdf_dir
    out_root: Path = args.out
    if not pdf_dir.is_dir():
        print(f"ERROR: not a directory: {pdf_dir}", file=sys.stderr)
        return 1

    for sub in (
        "CGC-25-631801",
        "CGC-25-631802",
        "CGC-25-631801/by-date",
        "CGC-25-631802/by-date",
        "_index",
    ):
        (out_root / sub).mkdir(parents=True, exist_ok=True)

    pdfs = discover_pdfs(pdf_dir)
    undated_or_case: list[dict[str, str]] = []
    pair_check: dict[tuple[str, str], list[str]] = defaultdict(list)
    pendings: list[PendingDoc] = []
    for pdf in pdfs:
        stem = pdf.name
        norm = normalize_stem(stem)
        pleading, motion, is_chaff = classify_filename(stem)
        p1 = pdftotext_range(pdf, 1, 1, layout=False)
        case = case_from_text(p1) or case_from_filename(stem) or case_from_text(
            pdftotext_full(pdf, False)[:20000]
        )
        if not case:
            undated_or_case.append(
                {
                    "file": stem,
                    "reason": "case number not found in page-1 or filename",
                }
            )
            case = "UNKNOWN"
        else:
            pair_check[(case, norm)].append(stem)

        flow = clean_text(pdftotext_full(pdf, False))
        layout = clean_text(pdftotext_full(pdf, True))
        fdate = parse_filing_date(flow) or parse_filing_date(layout) or None
        sha = file_sha256(pdf)
        npages = pdf_page_count(pdf) or 1
        auth = build_authority_index_entry(flow)
        pendings.append(
            PendingDoc(
                source_pdf=pdf,
                stem=stem,
                norm=norm,
                pleading=pleading,
                motion=motion,
                is_chaff=is_chaff,
                case=case,
                flow=flow,
                layout=layout,
                fdate=fdate,
                sha=sha,
                npages=npages,
                auth=auth,
            )
        )

    align_outlier_bundle_dates(pendings)
    infer_missing_filing_dates(pendings)

    records: list[DocRec] = []
    for p in pendings:
        stem = p.stem
        norm = p.norm
        pleading = p.pleading
        motion = p.motion
        is_chaff = p.is_chaff
        case = p.case
        flow = p.flow
        layout = p.layout
        fdate = p.fdate
        date_key = fdate or "undated"
        raw_slug = f"{pleading}-{motion or 'na'}-{norm or stem}"
        base_slug = re.sub(
            r"[^a-z0-9._-]+",
            "-",
            raw_slug.lower(),
        ).strip("-")
        folder = f"{date_key}__{pleading}__{base_slug[:80]}"
        out_dir = out_root / case if case != "UNKNOWN" else out_root / "_index" / "UNKNOWN-CASE"
        if case == "UNKNOWN":
            out_dir.mkdir(parents=True, exist_ok=True)
        final_dir = out_dir / folder
        n = 2
        while final_dir.is_dir():
            final_dir = out_dir / f"{folder}-{n}"
            n += 1
        final_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p.source_pdf, final_dir / "source.pdf")
        (final_dir / "extraction.md").write_text(
            f"# {stem}\n\n## Full text (pdftotext, flow)\n\n{flow}\n\n"
            f"## Layout (pdftotext -layout) excerpt, first 4000 chars\n\n"
            f"```\n{layout[:4000]}\n```\n",
            encoding="utf-8",
        )
        meta = {
            "original_filename": stem,
            "normalized_stem": norm,
            "case_number": case,
            "filing_date": fdate,
            "filing_date_inferred_from_motion_bundle": p.fdate_inferred,
            "pleading_type": pleading,
            "motion_family": motion,
            "is_procedural_chaff": is_chaff,
            "role_guess": guess_role(pleading),
            "sha256": p.sha,
            "page_count": p.npages,
            "output_relpath": str(
                final_dir.relative_to(out_root) if case != "UNKNOWN" else final_dir
            ),
        }
        (final_dir / "metadata.json").write_text(
            json.dumps(meta, indent=2) + "\n", encoding="utf-8"
        )
        records.append(
            DocRec(
                source_pdf=p.source_pdf,
                stem=stem,
                normalized_stem=norm,
                case_number=case,
                pleading=pleading,
                motion_family=motion,
                is_chaff=is_chaff,
                filing_date=fdate,
                output_dir=final_dir,
                sha256=p.sha,
                page_count=p.npages,
                text_flow=flow,
                text_layout=layout,
                authorities=p.auth,
                fdate_inferred=p.fdate_inferred,
            )
        )

    # cross-refs
    by_key: dict[tuple[str, str | None, str | None], list[DocRec]] = defaultdict(
        list
    )
    for r in records:
        if r.case_number == "UNKNOWN":
            continue
        by_key[(r.case_number, r.filing_date, r.motion_family)].append(r)

    for r in records:
        sibs = [
            x.output_dir.name
            for x in by_key.get(
                (r.case_number, r.filing_date, r.motion_family), []
            )
            if x.source_pdf != r.source_pdf
        ]
        cross = [f"Sibling folder: `{s}`" for s in sibs]
        (r.output_dir / "analysis.md").write_text(
            build_analysis_md(r, cross), encoding="utf-8"
        )

    # Duplicates: same (case, normalized_stem) with >1 file
    dup_lines: list[str] = []
    for (case, nstem), files in pair_check.items():
        if case == "UNKNOWN":
            continue
        if len(files) > 1:
            dup_lines.append(
                f"- **{case}** / `{nstem}`: {len(files)} files: {', '.join(files)}"
            )

    unresolved: list[str] = []
    for u in undated_or_case:
        unresolved.append(
            f"- {u.get('file', '?')}: {u.get('reason', 'unknown')}"
        )
    if dup_lines:
        unresolved.append("")
        unresolved.append("## Same case + normalized filename stem (check duplicates)")
        unresolved.extend(dup_lines)

    if unresolved:
        (out_root / "_index" / "UNRESOLVED.md").write_text(
            "# Unresolved or attention items\n\n" + "\n".join(unresolved) + "\n",
            encoding="utf-8",
        )

    purpose_map = {
        "notice": "Notice of motion; sets briefing and hearing schedule.",
        "mpa": "Memorandum of points and authorities; substantive law and argument for the motion.",
        "dec-toc": "Declaration re table of contents for MPA; procedural certificate.",
        "rfjn": "Request for judicial notice; materials for the court to consider.",
        "prop-order": "Proposed order for court signature if the motion is granted.",
        "stmnt": "Separate statement of facts; often required for demurrer practice.",
        "opposition": "Opposition to a plaintiff or third-party motion; defensive response on the merits and procedure.",
        "mc-letter": "Meet-and-confer correspondence; Proposition 1 compliance or other conferral record.",
        "stipulation": "Stipulation between parties, often scheduling or response deadlines.",
        "consent": "Consent to electronic service or service configuration.",
    }

    def day_analysis_lines(
        case: str, fdate: str, group: list[DocRec], day_dir: Path
    ) -> str:
        lines: list[str] = [
            f"# Filings for {case} on {fdate}",
            "",
            "Summary: defense filings processed from PDF; dates are best-effort from the face of the document.",
            "Each `analysis.md` in the listed folder contains principal theory, position, authorities, and cross-refs to same-day siblings in the same motion family.",
            "",
        ]
        for r in sorted(group, key=lambda x: (x.pleading, x.stem)):
            purpose = purpose_map.get(r.pleading, "Case filing.")
            dep: list[str] = []
            if r.pleading == "opposition" and r.motion_family == "MFL-SAC":
                dep.append(
                    "Responds to plaintiff's motion for leave to file a further amended pleading (SAC), if that motion is pending in this case."
                )
            if r.pleading == "mpa":
                dep.append(
                    "Typically read with the notice of motion and supporting papers filed the same day."
                )
            if r.pleading in ("dec-toc", "rfjn", "prop-order", "stmnt"):
                dep.append(
                    "Supporting papers for the related motion in the same motion family, same day."
                )
            if r.pleading == "notice":
                dep.append(
                    "Lead paper for a motion; memorandum and other papers usually follow the same day."
                )
            rel_ana = os.path.relpath(
                r.output_dir / "analysis.md", day_dir
            )
            rel_ext = os.path.relpath(
                r.output_dir / "extraction.md", day_dir
            )
            rel_folder = os.path.relpath(r.output_dir, day_dir)
            lines.append(f"## {r.stem}")
            lines.append("")
            lines.append(
                f"- **Type**: {r.pleading} | **Family**: {r.motion_family or 'n/a'} | **Procedural chaff**: {r.is_chaff}"
            )
            lines.append(f"- **Purpose (brief)**: {purpose}")
            if dep:
                lines.append(
                    f"- **Dependencies (heuristic)**: {'; '.join(dep)}"
                )
            lines.append(f"- **Folder**: [`{r.output_dir.name}`]({rel_folder}/)")
            if r.is_chaff:
                lines.append(
                    f"- **Companion metadata**: [metadata.json]({rel_folder}/metadata.json) (no full `analysis` body for procedural chaff.)"
                )
            else:
                lines.append(
                    f"- **Analysis**: [analysis.md]({rel_ana})"
                )
            lines.append(f"- **Extraction**: [extraction.md]({rel_ext})")
            # Inline principal authority summary for the day file
            if not r.is_chaff:
                auth = r.authorities
                st = (auth.get("statutes_and_codes") or [])[:8]
                rep = (auth.get("reporter_cites_normalized") or [])[:8]
                if st:
                    lines.append(
                        f"- **Statutes or codes (sample)**: {', '.join(st)}"
                    )
                if rep:
                    lines.append(
                        f"- **Reporter keys (sample)**: {', '.join(rep)}"
                    )
            lines.append("")
        return "\n".join(lines) + "\n"

    for case in ("CGC-25-631801", "CGC-25-631802"):
        by_date: dict[str, list[DocRec]] = defaultdict(list)
        for r in records:
            if r.case_number != case:
                continue
            by_date[r.filing_date or "undated"].append(r)
        for fdate, group in sorted(by_date.items(), key=lambda x: x[0]):
            dd = fdate if re.match(r"^\d{4}-\d{2}-\d{2}$", fdate) else "undated"
            day_dir = out_root / case / "by-date" / dd
            day_dir.mkdir(parents=True, exist_ok=True)
            (day_dir / "DAY-ANALYSIS.md").write_text(
                day_analysis_lines(case, fdate, group, day_dir),
                encoding="utf-8",
            )

    # MASTER-INDEX
    m_lines = [
        "# Master index: defense filings extractions",
        "",
        "| Case | Filing date | Pleading | Family | Chaff | Folder (under DEFENSE-FILINGS) |",
        "|------|------------|----------|--------|-------|--------------------------------|",
    ]
    for r in sorted(
        records, key=lambda x: (x.case_number, x.filing_date or "9999", x.stem)
    ):
        rel = r.output_dir.relative_to(out_root)
        m_lines.append(
            f"| {r.case_number} | {r.filing_date or 'undated'} | {r.pleading} | "
            f"{r.motion_family or 'n/a'} | {r.is_chaff} | `{rel}` |"
        )
    (out_root / "_index" / "MASTER-INDEX.md").write_text(
        "\n".join(m_lines) + "\n", encoding="utf-8"
    )

    # AUTHORITIES-INDEX: union of statutes and reporter keys with back-refs
    by_stat: dict[str, list[str]] = defaultdict(list)
    by_rep: dict[str, list[str]] = defaultdict(list)
    for r in records:
        if r.is_chaff or r.case_number == "UNKNOWN":
            continue
        rel = r.output_dir.relative_to(out_root)
        tag = f"{rel}"
        for s in r.authorities.get("statutes_and_codes") or []:
            by_stat[s].append(tag)
        for k in r.authorities.get("reporter_cites_normalized") or []:
            by_rep[k].append(tag)

    a_lines = [
        "# Authorities index (regex extraction, union across substantive filings)",
        "",
        "Back-refs are paths under `DEFENSE-FILINGS/` relative to that folder.",
        "",
        "## Statutes, rules, and codes (deduplicated)",
        "",
    ]
    for s in sorted(by_stat):
        a_lines.append(f"- **{s}**  ")
        a_lines.append(f"  - {', '.join(sorted(set(by_stat[s])))}")
        a_lines.append("")
    a_lines.append("## Normalized reporter keys")
    a_lines.append("")
    for k in sorted(by_rep):
        a_lines.append(f"- `{k}`  ")
        a_lines.append(f"  - {', '.join(sorted(set(by_rep[k])))}")
        a_lines.append("")
    (out_root / "_index" / "AUTHORITIES-INDEX.md").write_text(
        "\n".join(a_lines) + "\n", encoding="utf-8"
    )

    print(
        f"Wrote {len(records)} documents under {out_root}", file=sys.stderr
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
