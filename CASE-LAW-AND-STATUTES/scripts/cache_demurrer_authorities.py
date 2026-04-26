#!/usr/bin/env python3
"""
Build a local PDF cache for California and federal reporter citations found in
COURT-DEMURRER-DEFENSE/PARSED/legal-authorities.json.

Source: Harvard Case.law static volumes (same as fetch-listed-opinions.py), not FindLaw.
Optional FindLaw search URL is recorded in the manifest for manual browser retrieval.

Usage:
  python3 cache_demurrer_authorities.py
  python3 cache_demurrer_authorities.py --json /path/to/legal-authorities.json
  python3 cache_demurrer_authorities.py --slugs mpa-demurrer,stmnt-demurrer,ntc-demurrer,rfjn-demurrer,prop-order-demurrer
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pypdf

UA = "Mozilla/5.0 (compatible; case-law-research; +https://case.law/about)"
CAP_BASE = "https://static.case.law"

def apply_citation_fixes(t: str) -> list[tuple[str, str, str, bool]]:
    """Extra cites when OCR merges digits (e.g. 2122 Cal.4th 71 next to Bockrath -> 21 Cal.4th 71)."""
    fixes: list[tuple[str, str, str, bool]] = []
    if "Bockrath" in t and "Cal.4th" in t and "71" in t:
        fixes.append(("21", "4th", "71", False))
    return fixes


def drop_phantom_bockrath_212(cal: set[tuple[str, str, str, bool]]) -> None:
    """Remove spurious 212 Cal.4th 71 triple if 21 Cal.4th 71 is present (OCR bleed)."""
    has_correct = ("21", "4th", "71", False) in cal
    phantom = ("212", "4th", "71", False)
    if has_correct and phantom in cal:
        cal.discard(phantom)


@dataclass
class ManifestRow:
    citation_key: str
    cap_reporter: str
    volume: str
    first_page: str
    case_json: str
    case_name: str
    pdf_rel_path: str
    source_url_json: str
    source_url_volume_pdf: str
    findlaw_search_url: str
    status: str
    detail: str


def fetch(url: str, dest: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)


def load_cap_meta(reporter: str, vol: str, case_json: str) -> dict:
    url = f"{CAP_BASE}/{reporter}/{vol}/cases/{case_json}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def ensure_volume_pdf(cache_dir: str, reporter: str, vol: str) -> str:
    name = f"{reporter.replace('/', '-')}-{vol}.pdf"
    path = os.path.join(cache_dir, name)
    if os.path.isfile(path) and os.path.getsize(path) > 100_000:
        return path
    url = f"{CAP_BASE}/{reporter}/{vol}.pdf"
    print(f"  volume PDF {url}", file=sys.stderr)
    fetch(url, path)
    return path


def extract_pages(src_pdf: str, dest_pdf: str, first_order: int, last_order: int) -> None:
    reader = pypdf.PdfReader(src_pdf)
    n = len(reader.pages)
    lo, hi = first_order, last_order
    if lo < 1 or hi < lo or hi > n:
        raise ValueError(f"bad page span {lo}-{hi} (pdf has {n} pages)")
    writer = pypdf.PdfWriter()
    for idx in range(lo - 1, hi):
        writer.add_page(reader.pages[idx])
    with open(dest_pdf, "wb") as f:
        writer.write(f)


def slugify_cap_name(s: str) -> str:
    s = re.sub(r"[^\w\s\-]", "", s, flags=re.UNICODE)
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s[:180] if len(s) > 180 else s


def findlaw_search_query(citation_key: str, case_name: str = "") -> str:
    from urllib.parse import quote_plus

    base = case_name.strip() if case_name else citation_key
    return "https://www.google.com/search?q=" + quote_plus(
        f"{base} site:findlaw.com OR site:courts.ca.gov OR site:justia.com"
    )


def parse_cal_cites(text: str) -> list[tuple[str, str, str, bool]]:
    """
    Return list of (volume, reporter_token, first_page, is_app).
    reporter_token is 2d|3d|4th|5th.
    """
    t = text.replace("\n", " ")
    out: list[tuple[str, str, str, bool]] = []
    for m in re.finditer(
        r"(?:\(\d{4}\)\s*)?(\d+)\s+Cal\.(App\.)?\s*([2345]th|[23]d)\s+(\d+)",
        t,
        re.I,
    ):
        vol, app_dot, rep, page = m.group(1), m.group(2), m.group(3).lower(), m.group(4)
        is_app = bool(app_dot)
        if int(vol) > 999:
            continue
        out.append((vol, rep, page, is_app))
    return out


def cap_reporter_slug(is_app: bool, rep: str) -> str:
    if is_app:
        return f"cal-app-{rep}"
    return f"cal-{rep}"


def parse_us_cites(text: str) -> list[tuple[str, str, str]]:
    """Return (series, volume, first_page) for U.S., F.3d, F.2d."""
    t = text.replace("\n", " ")
    out = []
    for m in re.finditer(
        r"(\d+)\s+U\.\s*S\.\s+(\d+)",
        t,
        re.I,
    ):
        out.append(("us", m.group(1), m.group(2)))
    for m in re.finditer(r"(\d+)\s+F\.3d\s+(\d+)", t, re.I):
        out.append(("f3d", m.group(1), m.group(2)))
    for m in re.finditer(r"(\d+)\s+F\.2d\s+(\d+)", t, re.I):
        out.append(("f2d", m.group(1), m.group(2)))
    return out


def federal_cap_slug(series: str) -> str:
    return {"us": "us", "f3d": "f3d", "f2d": "f2d"}[series]


def try_load_case_json(reporter: str, vol: str, page: str) -> dict | None:
    case_json = f"{int(page):04d}-01.json"
    url = f"{CAP_BASE}/{reporter}/{vol}/cases/{case_json}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def process_one_cap(
    reporter: str,
    vol: str,
    page: str,
    out_dir: Path,
    cache_dir: Path,
    manifest_rows: list[ManifestRow],
) -> None:
    key = f"{vol} {reporter} {page}"
    case_json = f"{int(page):04d}-01.json"
    meta = try_load_case_json(reporter, vol, page)
    if meta is None:
        manifest_rows.append(
            ManifestRow(
                citation_key=key,
                cap_reporter=reporter,
                volume=vol,
                first_page=page,
                case_json=case_json,
                case_name="",
                pdf_rel_path="",
                source_url_json=f"{CAP_BASE}/{reporter}/{vol}/cases/{case_json}",
                source_url_volume_pdf=f"{CAP_BASE}/{reporter}/{vol}.pdf",
                findlaw_search_url=findlaw_search_query(key),
                status="not_found",
                detail="404 on case JSON (try alternate pagination or not in CAP)",
            )
        )
        return

    name = meta.get("name_abbreviation") or meta.get("name") or "Unknown"
    lo = int(meta["first_page_order"])
    hi = int(meta["last_page_order"])
    short = slugify_cap_name(name)
    fname = f"Demurrer-{reporter}-vol{vol}-p{page}-{short}.pdf"
    dest = out_dir / fname
    json_url = f"{CAP_BASE}/{reporter}/{vol}/cases/{case_json}"

    try:
        vol_path = ensure_volume_pdf(str(cache_dir), reporter, vol)
        extract_pages(vol_path, str(dest), lo, hi)
        st = "ok"
        detail = f"pages {lo}-{hi} from volume PDF"
    except Exception as exc:
        st = "error"
        detail = str(exc)[:500]

    manifest_rows.append(
        ManifestRow(
            citation_key=key,
            cap_reporter=reporter,
            volume=vol,
            first_page=page,
            case_json=case_json,
            case_name=name,
            pdf_rel_path=str(dest.relative_to(out_dir.parent)) if dest.is_file() else "",
            source_url_json=json_url,
            source_url_volume_pdf=f"{CAP_BASE}/{reporter}/{vol}.pdf",
            findlaw_search_url=findlaw_search_query(key, name),
            status=st,
            detail=detail,
        )
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Path to legal-authorities.json",
    )
    ap.add_argument(
        "--slugs",
        type=str,
        default="",
        help=(
            "Comma-separated source_slug values to include (e.g. mpa-demurrer,stmnt-demurrer). "
            "Empty means all authorities in JSON."
        ),
    )
    ap.add_argument(
        "--out-manifest",
        type=Path,
        default=None,
        help=(
            "Write manifest JSON here (default: CASE-LAW-AND-STATUTES/DEMURRER-AUTHORITIES-CACHE-MANIFEST.json). "
            "Use when caching from a different legal-authorities.json so the default demurrer manifest is not overwritten."
        ),
    )
    args = ap.parse_args()
    slug_filter: set[str] | None = None
    if args.slugs.strip():
        slug_filter = {s.strip() for s in args.slugs.split(",") if s.strip()}

    root = Path(__file__).resolve().parents[1]
    auth_path = args.json or (
        root.parent
        / "COURT-DEMURRER-DEFENSE"
        / "PARSED"
        / "legal-authorities.json"
    )
    if not auth_path.is_file():
        print(f"Missing {auth_path}", file=sys.stderr)
        return 1

    data = json.loads(auth_path.read_text(encoding="utf-8"))
    cal_triples: set[tuple[str, str, str, bool]] = set()
    us_triples: set[tuple[str, str, str]] = set()

    for h in data.get("authorities", []):
        if slug_filter is not None and h.get("source_slug") not in slug_filter:
            continue
        mt = h.get("matched_text", "")
        ctx = h.get("context", "")
        if h.get("authority_type") in ("california_reporter", "case_name_with_cite"):
            blob = mt + " " + ctx
            for vol, rep, page, is_app in parse_cal_cites(blob):
                cal_triples.add((vol, rep, page, is_app))
            for vol, rep, page, is_app in apply_citation_fixes(blob):
                cal_triples.add((vol, rep, page, is_app))
        if h.get("authority_type") in ("us_federal_reporter", "case_name_with_cite"):
            blob = mt + " " + ctx
            for series, vol, page in parse_us_cites(blob):
                if series == "us" and int(vol) == 556 and int(page) >= 800:
                    continue
                us_triples.add((series, vol, page))

    drop_phantom_bockrath_212(cal_triples)

    out_pdf = root / "opinions-pdf"
    cache_dir = root / ".cache" / "cap-volumes"
    out_pdf.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    rows: list[ManifestRow] = []

    done_cap: set[tuple[str, str, str]] = set()

    for vol, rep, page, is_app in sorted(cal_triples, key=lambda x: (x[3], x[1], int(x[0]), int(x[2]))):
        slug = cap_reporter_slug(is_app, rep)
        key3 = (slug, vol, page)
        if key3 in done_cap:
            continue
        done_cap.add(key3)
        existing = list(out_pdf.glob(f"Demurrer-{slug}-vol{vol}-p{page}-*.pdf"))
        if existing and existing[0].stat().st_size > 1000:
            rows.append(
                ManifestRow(
                    citation_key=f"{vol} {slug} {page}",
                    cap_reporter=slug,
                    volume=vol,
                    first_page=page,
                    case_json=f"{int(page):04d}-01.json",
                    case_name="(skipped; Demurrer PDF already present)",
                    pdf_rel_path=f"opinions-pdf/{existing[0].name}",
                    source_url_json="",
                    source_url_volume_pdf="",
                    findlaw_search_url="",
                    status="skipped_existing_demurrer_pdf",
                    detail=existing[0].name,
                )
            )
            continue
        process_one_cap(slug, vol, page, out_pdf, cache_dir, rows)

    for series, vol, page in sorted(us_triples, key=lambda x: (x[0], int(x[1]), int(x[2]))):
        slug = federal_cap_slug(series)
        key3 = (slug, vol, page)
        if key3 in done_cap:
            continue
        done_cap.add(key3)
        existing = list(out_pdf.glob(f"Demurrer-{slug}-vol{vol}-p{page}-*.pdf"))
        if existing and existing[0].stat().st_size > 1000:
            rows.append(
                ManifestRow(
                    citation_key=f"{vol} {slug} {page}",
                    cap_reporter=slug,
                    volume=vol,
                    first_page=page,
                    case_json=f"{int(page):04d}-01.json",
                    case_name="(skipped; Demurrer PDF already present)",
                    pdf_rel_path=f"opinions-pdf/{existing[0].name}",
                    source_url_json="",
                    source_url_volume_pdf="",
                    findlaw_search_url="",
                    status="skipped_existing_demurrer_pdf",
                    detail=existing[0].name,
                )
            )
            continue
        process_one_cap(slug, vol, page, out_pdf, cache_dir, rows)

    from collections import Counter

    status_counts = Counter(r.status for r in rows)
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_api": "Harvard Case.law static.case.law (open corpus)",
        "input_authorities_json": str(auth_path),
        "status_counts": dict(status_counts),
        "note": (
            "PDFs are single-opinion extracts from Case.law reporter volumes. "
            "findlaw_search_url is a Google search helper (FindLaw / court sites), not auto-scraped. "
            "For official court PDFs, use courts.ca.gov and Court of Appeal portals when available."
        ),
        "rows": [asdict(r) for r in rows],
    }
    out_manifest = args.out_manifest if args.out_manifest is not None else (root / "DEMURRER-AUTHORITIES-CACHE-MANIFEST.json")
    out_manifest.parent.mkdir(parents=True, exist_ok=True)
    out_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_manifest}", file=sys.stderr)
    print(f"status_counts={dict(status_counts)} total_rows={len(rows)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
