#!/usr/bin/env python3
"""Download California opinions: supreme archive PDFs + CAP reporter slices (static.case.law)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request

import pypdf

UA = "Mozilla/5.0 (compatible; case-law-research; +https://case.law/about)"
CAP_BASE = "https://static.case.law"
ARCHIVE = "https://www4.courts.ca.gov/opinions/archive"

# (slug, outfile, method, payload)
# CAP payload: (reporter_slug, volume, json_path under cases/) e.g. ("cal-4th", "41", "1232-01.json")
JOBS: list[tuple[str, str, str, dict | str]] = [
    (
        "Action-Apartment-Assn-v-City-of-Santa-Monica-41-Cal-4th-1232",
        "Action-Apartment-Assn-v-City-of-Santa-Monica-41-Cal-4th-1232.pdf",
        "cap",
        {"reporter": "cal-4th", "vol": "41", "case_json": "1232-01.json"},
    ),
    (
        "Aubry-v-Tri-City-Hospital-Dist-2-Cal-4th-962",
        "Aubry-v-Tri-City-Hospital-Dist-2-Cal-4th-962.pdf",
        "cap",
        {"reporter": "cal-4th", "vol": "2", "case_json": "0962-01.json"},
    ),
    (
        "Baral-v-Schnitt-1-Cal-5th-376",
        "Baral-v-Schnitt-1-Cal-5th-376.pdf",
        "archive",
        "S225090.PDF",
    ),
    (
        "Blank-v-Kirwan-39-Cal-3d-311",
        "Blank-v-Kirwan-39-Cal-3d-311.pdf",
        "cap",
        {"reporter": "cal-3d", "vol": "39", "case_json": "0311-01.json"},
    ),
    (
        "Cansino-v-Bank-of-America-224-Cal-App-4th-1462",
        "Cansino-v-Bank-of-America-224-Cal-App-4th-1462.pdf",
        "cap",
        {"reporter": "cal-app-4th", "vol": "224", "case_json": "1462-01.json"},
    ),
    (
        "City-of-Cotati-v-Cashman-29-Cal-4th-69",
        "City-of-Cotati-v-Cashman-29-Cal-4th-69.pdf",
        "cap",
        {"reporter": "cal-4th", "vol": "29", "case_json": "0069-01.json"},
    ),
    (
        "City-of-Stockton-v-Superior-Court-42-Cal-4th-730",
        "City-of-Stockton-v-Superior-Court-42-Cal-4th-730.pdf",
        "cap",
        {"reporter": "cal-4th", "vol": "42", "case_json": "0730-01.json"},
    ),
    (
        "Engalla-v-Permanente-Medical-Group-15-Cal-4th-951",
        "Engalla-v-Permanente-Medical-Group-15-Cal-4th-951.pdf",
        "cap",
        {"reporter": "cal-4th", "vol": "15", "case_json": "0951-01.json"},
    ),
    (
        "Alliance-Mortgage-Co-v-Rothwell-10-Cal-4th-1226",
        "Alliance-Mortgage-Co-v-Rothwell-10-Cal-4th-1226.pdf",
        "cap",
        {"reporter": "cal-4th", "vol": "10", "case_json": "1226-01.json"},
    ),
    (
        "Egan-v-Mutual-of-Omaha-Ins-Co-24-Cal-3d-809",
        "Egan-v-Mutual-of-Omaha-Ins-Co-24-Cal-3d-809.pdf",
        "cap",
        {"reporter": "cal-3d", "vol": "24", "case_json": "0809-01.json"},
    ),
    (
        "Moradi-Shalal-v-Firemans-Fund-Ins-Companies-46-Cal-3d-287",
        "Moradi-Shalal-v-Firemans-Fund-Ins-Companies-46-Cal-3d-287.pdf",
        "cap",
        {"reporter": "cal-3d", "vol": "46", "case_json": "0287-01.json"},
    ),
    (
        "Fox-v-Ethicon-Endo-Surgery-35-Cal-4th-797",
        "Fox-v-Ethicon-Endo-Surgery-35-Cal-4th-797.pdf",
        "cap",
        {"reporter": "cal-4th", "vol": "35", "case_json": "0797-01.json"},
    ),
    (
        "Korea-Supply-Co-v-Lockheed-Martin-29-Cal-4th-1134",
        "Korea-Supply-Co-v-Lockheed-Martin-29-Cal-4th-1134.pdf",
        "cap",
        {"reporter": "cal-4th", "vol": "29", "case_json": "1134-01.json"},
    ),
    (
        "Kwikset-Corp-v-Superior-Court-51-Cal-4th-310",
        "Kwikset-Corp-v-Superior-Court-51-Cal-4th-310.pdf",
        "cap",
        {"reporter": "cal-4th", "vol": "51", "case_json": "0310-01.json"},
    ),
    (
        "Lazar-v-Superior-Court-12-Cal-4th-631",
        "Lazar-v-Superior-Court-12-Cal-4th-631.pdf",
        "cap",
        {"reporter": "cal-4th", "vol": "12", "case_json": "0631-01.json"},
    ),
    (
        "Neu-Visions-Sports-v-Soren-86-Cal-App-4th-303",
        "Neu-Visions-Sports-v-Soren-86-Cal-App-4th-303.pdf",
        "cap",
        {"reporter": "cal-app-4th", "vol": "86", "case_json": "0303-01.json"},
    ),
    (
        "Park-v-Board-of-Trustees-CSU-2-Cal-5th-1057",
        "Park-v-Board-of-Trustees-CSU-2-Cal-5th-1057.pdf",
        "archive",
        "S229728.PDF",
    ),
]


def fetch(url: str, dest: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
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
    print(f"  downloading volume {url}", file=sys.stderr)
    fetch(url, path)
    return path


def extract_pages(src_pdf: str, dest_pdf: str, first_order: int, last_order: int) -> None:
    """first_order and last_order are 1-based inclusive page numbers in the reporter PDF."""
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


def snippet_from_pdf(path: str, max_chars: int = 400) -> str:
    try:
        out = subprocess.check_output(
            ["pdftotext", "-l", "1", path, "-"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8", errors="replace")[:max_chars]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "opinions-pdf")
    os.makedirs(out_dir, exist_ok=True)
    cache_dir = os.path.join(root, ".cache", "cap-volumes")
    os.makedirs(cache_dir, exist_ok=True)

    for slug, filename, method, payload in JOBS:
        dest = os.path.join(out_dir, filename)
        print(f"== {slug}", file=sys.stderr)
        if method == "archive":
            assert isinstance(payload, str)
            url = f"{ARCHIVE}/{payload}"
            print(f"  archive {url}", file=sys.stderr)
            fetch(url, dest)
        elif method == "cap":
            assert isinstance(payload, dict)
            meta = load_cap_meta(
                payload["reporter"], payload["vol"], payload["case_json"]
            )
            name = meta.get("name_abbreviation") or meta.get("name") or ""
            lo = int(meta["first_page_order"])
            hi = int(meta["last_page_order"])
            print(f"  CAP {name} pages {lo}-{hi} in vol {payload['reporter']} {payload['vol']}", file=sys.stderr)
            vol_path = ensure_volume_pdf(cache_dir, payload["reporter"], payload["vol"])
            extract_pages(vol_path, dest, lo, hi)
        else:
            raise ValueError(method)

        snip = snippet_from_pdf(dest)
        print(f"  wrote {dest} ({os.path.getsize(dest)} bytes)", file=sys.stderr)
        if snip:
            line = snip.replace("\n", " ")[:200]
            print(f"  text head: {line!r}", file=sys.stderr)

    print("done", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
