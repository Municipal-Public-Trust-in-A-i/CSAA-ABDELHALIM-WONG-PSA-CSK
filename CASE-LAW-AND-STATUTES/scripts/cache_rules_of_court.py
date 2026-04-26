#!/usr/bin/env python3
"""
Download California Rules of Court (Judicial Council PDFs by title/appendix)
and San Francisco Superior Court local rules into CASE-LAW-AND-STATUTES/rules-of-court/.

Usage:
  python3 cache_rules_of_court.py
  python3 cache_rules_of_court.py --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "Mozilla/5.0 (compatible; rules-of-court-cache; +https://courts.ca.gov)"

# Index: https://courts.ca.gov/rules-forms/rules-court
CRC_BASE = "https://courts.ca.gov/system/files?file="

# (relative path under rules-of-court/, query file= value after CRC_BASE)
CRC_ARTIFACTS: list[tuple[str, str]] = [
    ("statewide-crc/roc-title-1.pdf", "file/roc-title-1.pdf"),
    ("statewide-crc/roc-title-2.pdf", "file/roc-title-2.pdf"),
    ("statewide-crc/roc-title-3.pdf", "file/roc-title-3_0.pdf"),
    ("statewide-crc/roc-title-4.pdf", "file/roc-title-4.pdf"),
    ("statewide-crc/roc-title-5.pdf", "file/roc-title-5.pdf"),
    ("statewide-crc/roc-title-6.pdf", "rules-court/roc-title-6.pdf"),
    ("statewide-crc/roc-title-7.pdf", "file/roc-title-7.pdf"),
    ("statewide-crc/roc-title-8.pdf", "file/roc-title-8_0.pdf"),
    ("statewide-crc/roc-title-9.pdf", "file/roc-title-9.pdf"),
    ("statewide-crc/roc-title-10.pdf", "file/roc-title-10.pdf"),
    ("statewide-crc/roc-standards-judicial-administration.pdf", "file/roc-standards-judicial-administration.pdf"),
    ("statewide-crc/roc-ethics-standards-neutral-arbitrators.pdf", "rules-court/roc-ethics-standards-neutral-arbitrators.pdf"),
    ("statewide-crc/roc-appendix-a-forms-list.pdf", "rules-court/appendix.pdf"),
    ("statewide-crc/roc-appendix-b.pdf", "rules-court/appendix_b.pdf"),
    ("statewide-crc/roc-appendix-c.pdf", "rules-court/roc-appendix-c.pdf"),
    ("statewide-crc/roc-appendix-d.pdf", "rules-court/roc-appendix-d.pdf"),
    ("statewide-crc/roc-appendix-e.pdf", "rules-court/roc-appendix-e.pdf"),
    ("statewide-crc/roc-appendix-f.pdf", "rules-court/roc-appendix-f.pdf"),
    ("statewide-crc/roc-appendix-g.pdf", "rules-court/roc-appendix-g.pdf"),
    ("statewide-crc/roc-appendix-h.pdf", "rules-court/roc-appendix-h.pdf"),
    ("statewide-crc/roc-appendix-i-covid-emergency.pdf", "rules-court/roc-appendix-i.pdf"),
    ("statewide-crc/rules-conversion-table-new-to-old.pdf", "rules-court/rules_conversion_table_06_06_06__2_.pdf"),
    ("statewide-crc/rules-conversion-table-old-to-new.pdf", "rules-court/rules_conversion_table_reverse_060606.pdf"),
    ("statewide-crc/ca-code-of-judicial-ethics.pdf", "rules-court/ca_code_judicial_ethics.pdf"),
]

SF_LOCAL_RULES = (
    "sf-superior/SF-Local-Rules-effective-2026-01-01.pdf",
    "https://sf.courts.ca.gov/system/files/local-rules/final-proposed-changes-lrsf-effective-january-1-2026_0.pdf",
)


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Print URLs only")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    out_root = root / "rules-of-court"
    fetched_at = datetime.now(timezone.utc).isoformat()
    manifest: dict = {
        "fetched_at_utc": fetched_at,
        "source_index": "https://courts.ca.gov/rules-forms/rules-court",
        "sf_local_rules_page": "https://sf.courts.ca.gov/general-information/san-francisco-local-rules-court",
        "artifacts": [],
    }

    rows: list[dict] = []

    for rel, file_param in CRC_ARTIFACTS:
        url = CRC_BASE + urllib.parse.quote(file_param, safe="/")
        dest = out_root / rel
        if args.dry_run:
            print(url, "->", dest, file=sys.stderr)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"GET {url}", file=sys.stderr)
        try:
            data = fetch_bytes(url)
        except urllib.error.HTTPError as e:
            print(f"FAIL {rel}: HTTP {e.code}", file=sys.stderr)
            rows.append(
                {
                    "path": rel,
                    "url": url,
                    "status": "error",
                    "detail": f"HTTP {e.code}",
                }
            )
            continue
        if len(data) < 500 or not data.startswith(b"%PDF"):
            print(f"WARN {rel}: not a PDF or too small ({len(data)} bytes)", file=sys.stderr)
            rows.append({"path": rel, "url": url, "status": "error", "detail": "invalid or empty PDF"})
            continue
        dest.write_bytes(data)
        h = sha256_bytes(data)
        rows.append(
            {
                "path": rel,
                "url": url,
                "bytes": len(data),
                "sha256": h,
                "status": "ok",
            }
        )
        print(f"  -> {len(data)} bytes sha256={h[:16]}...", file=sys.stderr)

    if not args.dry_run:
        rel, url = SF_LOCAL_RULES
        dest = out_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"GET {url}", file=sys.stderr)
        try:
            data = fetch_bytes(url)
        except urllib.error.HTTPError as e:
            rows.append({"path": rel, "url": url, "status": "error", "detail": f"HTTP {e.code}"})
        else:
            if len(data) < 500 or not data.startswith(b"%PDF"):
                rows.append({"path": rel, "url": url, "status": "error", "detail": "invalid or empty PDF"})
            else:
                dest.write_bytes(data)
                h = sha256_bytes(data)
                rows.append({"path": rel, "url": url, "bytes": len(data), "sha256": h, "status": "ok"})
                print(f"  -> {len(data)} bytes sha256={h[:16]}...", file=sys.stderr)

    manifest["artifacts"] = rows
    if not args.dry_run:
        man_path = out_root / "RULES-OF-COURT-CACHE-MANIFEST.json"
        man_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {man_path}", file=sys.stderr)

    errors = [r for r in rows if r.get("status") != "ok"]
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
