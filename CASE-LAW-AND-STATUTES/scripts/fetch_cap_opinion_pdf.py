#!/usr/bin/env python3
"""
Fetch a single California opinion as PDF from Harvard static.case.law
(reuses Case.law volume + page order extraction like cache_demurrer_authorities.py).

Usage:
  python3 fetch_cap_opinion_pdf.py --reporter cal-4th --vol 11 --page 274 \\
    --out-basename Motion-Strike-cal-4th-vol11-p274
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pypdf

UA = "Mozilla/5.0 (compatible; case-law-research; +https://case.law/about)"
CAP_BASE = "https://static.case.law"


def fetch(url: str, dest: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)


def try_load_case_json(reporter: str, vol: str, page: str) -> dict | None:
    case_json = f"{int(page):04d}-01.json"
    url = f"{CAP_BASE}/{reporter}/{vol}/cases/{case_json}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def ensure_volume_pdf(cache_dir: Path, reporter: str, vol: str) -> Path:
    name = f"{reporter.replace('/', '-')}-{vol}.pdf"
    path = cache_dir / name
    if path.is_file() and path.stat().st_size > 100_000:
        return path
    url = f"{CAP_BASE}/{reporter}/{vol}.pdf"
    print(f"  downloading volume {url}", file=sys.stderr)
    fetch(url, str(path))
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


def slugify_name(s: str) -> str:
    s = re.sub(r"[^\w\s\-]", "", s, flags=re.UNICODE)
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s[:160] if len(s) > 160 else s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reporter", required=True, help="e.g. cal-4th, cal-app-5th")
    ap.add_argument("--vol", required=True)
    ap.add_argument("--page", required=True, help="first page in reporter")
    ap.add_argument(
        "--prefix",
        default="Motion-Strike",
        help="output filename prefix (default Motion-Strike)",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="default: CASE-LAW-AND-STATUTES/opinions-pdf",
    )
    args = ap.parse_args()
    here = Path(__file__).resolve().parents[1]
    out_dir = args.out_dir or (here / "opinions-pdf")
    cache_dir = here / ".cache" / "cap-volumes"
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    meta = try_load_case_json(args.reporter, args.vol, args.page)
    if meta is None:
        print("Case JSON not found on Case.law", file=sys.stderr)
        return 1
    name = meta.get("name_abbreviation") or meta.get("name") or "Unknown"
    lo = int(meta["first_page_order"])
    hi = int(meta["last_page_order"])
    short = slugify_name(name)
    fname = f"{args.prefix}-{args.reporter}-vol{args.vol}-p{args.page}-{short}.pdf"
    dest = out_dir / fname
    if dest.is_file() and dest.stat().st_size > 1000:
        print(f"Exists {dest}", file=sys.stderr)
        return 0
    vol_path = ensure_volume_pdf(cache_dir, args.reporter, args.vol)
    extract_pages(str(vol_path), str(dest), lo, hi)
    print(f"Wrote {dest}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
