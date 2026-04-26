#!/usr/bin/env python3
"""
Build defense-only authority inventory from legal-authorities.json, cross-check MPA TOA,
and join DEMURRER-AUTHORITIES-CACHE-MANIFEST.json rows.

Outputs:
  DEFENSE/803-OPPOSITION-PACKET/Defense.Demurrer.Authority-Inventory.md
  DEFENSE/803-OPPOSITION-PACKET/Defense.Demurrer.Authority-Inventory.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Reuse cache script parsing (same citation keys as CAP manifest).
_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cache_demurrer_authorities import (  # noqa: E402
    apply_citation_fixes,
    cap_reporter_slug,
    drop_phantom_bockrath_212,
    federal_cap_slug,
    parse_cal_cites,
    parse_us_cites,
)

DEFAULT_DEFENSE_SLUGS = (
    "mpa-demurrer",
    "stmnt-demurrer",
    "ntc-demurrer",
    "rfjn-demurrer",
    "prop-order-demurrer",
)


def parse_mpa_table_of_authorities(mpa_md: Path) -> list[dict]:
    text = mpa_md.read_text(encoding="utf-8")
    start = text.find("TABLE OF AUTHORITIES")
    if start < 0:
        return []
    end = text.find("\nSTATUTES", start)
    if end < 0:
        end = text.find("STATUTES", start)
    block = text[start:end] if end > start else text[start:]
    lines = block.splitlines()
    cases: list[dict] = []
    current_name: str | None = None
    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or "PAGE(S)" in line or stripped == "CASES":
            continue
        cite_m = re.match(r"^\s+\((\d{4})\)\s+(.+)$", line)
        if cite_m and current_name:
            cases.append(
                {
                    "case_name": current_name,
                    "year": cite_m.group(1),
                    "reporter_line": cite_m.group(2).strip(),
                }
            )
            continue
        # Case lines often glue the caption to dot leaders without a space
        # (e.g. "Companies........................................10").
        name_m = re.match(r"^(.+?)\s*\.{5,}", line)
        if name_m:
            current_name = name_m.group(1).strip()
            continue
    return cases


def reporter_keys_from_toa_line(reporter_line: str) -> list[str]:
    """Return manifest-style citation_key strings for a TOA reporter line."""
    cal = set()
    for vol, rep, page, is_app in parse_cal_cites(reporter_line):
        cal.add((vol, rep, page, is_app))
    for vol, rep, page, is_app in apply_citation_fixes(reporter_line):
        cal.add((vol, rep, page, is_app))
    drop_phantom_bockrath_212(cal)
    keys = []
    for vol, rep, page, is_app in cal:
        slug = cap_reporter_slug(is_app, rep)
        keys.append(f"{vol} {slug} {page}".lower())
    for series, vol, page in parse_us_cites(reporter_line):
        slug = federal_cap_slug(series)
        keys.append(f"{vol} {slug} {page}".lower())
    return keys


def load_manifest_index(manifest_path: Path) -> dict[str, dict]:
    if not manifest_path.is_file():
        return {}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for row in data.get("rows", []):
        k = row.get("citation_key", "").lower().strip()
        if k:
            out[k] = row
    return out


def collect_from_json(
    authorities: list[dict],
    slug_filter: set[str],
) -> tuple[dict[str, list[dict]], set[str]]:
    """Normalized reporter keys -> list of hit dicts; also statute/code keys."""
    by_key: dict[str, list[dict]] = defaultdict(list)
    reporter_keys: set[str] = set()
    for h in authorities:
        if h.get("source_slug") not in slug_filter:
            continue
        slug = h.get("source_slug")
        mt = h.get("matched_text", "")
        ctx = h.get("context", "")
        combo = mt + " " + ctx
        atype = h.get("authority_type")
        if atype in ("california_reporter", "case_name_with_cite"):
            cal = set()
            for vol, rep, page, is_app in parse_cal_cites(combo):
                cal.add((vol, rep, page, is_app))
            for vol, rep, page, is_app in apply_citation_fixes(combo):
                cal.add((vol, rep, page, is_app))
            drop_phantom_bockrath_212(cal)
            for vol, rep, page, is_app in cal:
                cap_s = cap_reporter_slug(is_app, rep)
                key = f"{vol} {cap_s} {page}".lower()
                reporter_keys.add(key)
                by_key[key].append(
                    {
                        "source_slug": slug,
                        "authority_type": atype,
                        "matched_text": mt[:200],
                        "pdf_page": h.get("pdf_page"),
                    }
                )
        if atype in ("us_federal_reporter", "case_name_with_cite"):
            for series, vol, page in parse_us_cites(combo):
                cap_s = federal_cap_slug(series)
                key = f"{vol} {cap_s} {page}".lower()
                reporter_keys.add(key)
                by_key[key].append(
                    {
                        "source_slug": slug,
                        "authority_type": atype,
                        "matched_text": mt[:200],
                        "pdf_page": h.get("pdf_page"),
                    }
                )
        if atype not in ("california_reporter", "us_federal_reporter", "case_name_with_cite"):
            at = h.get("authority_type") or "unknown"
            st_key = f"non_reporter:{slug}:{at}:{mt[:160]}"
            by_key[st_key].append(
                {
                    "source_slug": slug,
                    "authority_type": h.get("authority_type"),
                    "matched_text": mt[:240],
                    "pdf_page": h.get("pdf_page"),
                }
            )
    return by_key, reporter_keys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--include-dec-toc",
        action="store_true",
        help="Also include dec-of-toc-demurrer slug",
    )
    args = ap.parse_args()

    slug_filter = set(DEFAULT_DEFENSE_SLUGS)
    if args.include_dec_toc:
        slug_filter.add("dec-of-toc-demurrer")

    auth_path = _REPO / "COURT-DEMURRER-DEFENSE" / "PARSED" / "legal-authorities.json"
    mpa_path = _REPO / "COURT-DEMURRER-DEFENSE" / "PARSED" / "text" / "mpa-demurrer.md"
    manifest_path = _REPO / "CASE-LAW-AND-STATUTES" / "DEMURRER-AUTHORITIES-CACHE-MANIFEST.json"
    out_dir = _REPO / "DEFENSE" / "803-OPPOSITION-PACKET"

    data = json.loads(auth_path.read_text(encoding="utf-8"))
    by_key, json_reporter_keys = collect_from_json(data.get("authorities", []), slug_filter)
    manifest_idx = load_manifest_index(manifest_path)

    toa = parse_mpa_table_of_authorities(mpa_path)
    toa_keys: set[str] = set()
    for row in toa:
        for k in reporter_keys_from_toa_line(row["reporter_line"]):
            toa_keys.add(k)

    toa_missing = sorted(toa_keys - json_reporter_keys)
    json_extra = sorted(json_reporter_keys - toa_keys)

    rows_out = []
    for key in sorted(k for k in by_key if not k.startswith("non_reporter:")):
        man = manifest_idx.get(key.lower(), {})
        rows_out.append(
            {
                "citation_key": key,
                "hit_slugs": sorted({h["source_slug"] for h in by_key[key]}),
                "hit_count": len(by_key[key]),
                "manifest_status": man.get("status", ""),
                "cache_pdf": man.get("pdf_rel_path", ""),
                "case_name_manifest": man.get("case_name", ""),
            }
        )

    non_rep = {k: v for k, v in by_key.items() if k.startswith("non_reporter:")}
    categories = defaultdict(list)
    for k, hits in non_rep.items():
        at = hits[0].get("authority_type", "unknown")
        categories[at].append(
            {
                "bucket_key": k,
                "hit_slugs": sorted({h["source_slug"] for h in hits}),
                "sample": hits[0].get("matched_text", ""),
            }
        )

    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "defense_slugs": sorted(slug_filter),
        "source_json": str(auth_path),
        "manifest_path": str(manifest_path),
        "mpa_toa_parsed_count": len(toa),
        "cross_check": {
            "toa_reporter_keys_missing_from_filtered_json": toa_missing,
            "filtered_json_reporter_keys_not_in_mpa_toa": json_extra,
        },
        "reporter_inventory": rows_out,
        "non_reporter_categories": {k: v for k, v in categories.items()},
        "mpa_table_of_authorities": toa,
    }

    out_json = out_dir / "Defense.Demurrer.Authority-Inventory.json"
    out_md = out_dir / "Defense.Demurrer.Authority-Inventory.md"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Defense demurrer: authority inventory (filtered slugs)",
        "",
        f"**Generated:** {payload['generated_utc']}",
        "",
        "## Scope",
        "",
        "Slugs: `" + "`, `".join(sorted(slug_filter)) + "`",
        "",
        "## MPA Table of Authorities (parsed)",
        "",
        "| Case (MPA TOA) | Reporter line | Manifest / cache |",
        "|----------------|---------------|------------------|",
    ]
    for row in toa:
        keys = reporter_keys_from_toa_line(row["reporter_line"])
        man_bits = []
        for k in keys:
            m = manifest_idx.get(k, {})
            st = m.get("status", "—")
            pdf = m.get("pdf_rel_path", "")
            if pdf:
                man_bits.append(f"`{k}`: {st} → `{pdf}`")
            elif m:
                man_bits.append(f"`{k}`: {st}")
            else:
                man_bits.append(f"`{k}`: (no manifest row yet)")
        lines.append(
            f"| {row['case_name']} | {row['reporter_line']} | {'; '.join(man_bits)} |"
        )

    lines += [
        "",
        "## Cross-check: TOA vs filtered JSON reporter keys",
        "",
        f"- **TOA keys missing from JSON:** {len(toa_missing)}",
 ]
    for x in toa_missing:
        lines.append(f"  - `{x}`")
    lines += [
        "",
        f"- **JSON reporter keys not listed in MPA TOA:** {len(json_extra)} (expected: cites only in other defense pleadings or normalization differences)",
    ]
    for x in json_extra[:40]:
        lines.append(f"  - `{x}`")
    if len(json_extra) > 40:
        lines.append(f"  - … and {len(json_extra) - 40} more (see JSON)")

    lines += [
        "",
        "## Reporter citations (deduped keys)",
        "",
        "| citation_key | hit_slugs | manifest | cache PDF |",
        "|--------------|-----------|----------|-----------|",
    ]
    for r in rows_out:
        lines.append(
            f"| `{r['citation_key']}` | {', '.join(r['hit_slugs'])} | {r['manifest_status'] or '—'} | {r['cache_pdf'] or '—'} |"
        )

    lines += [
        "",
        "## Non-reporter buckets (statutes, rules, case_name_with_cite, etc.)",
        "",
        "See `Defense.Demurrer.Authority-Inventory.json` under `non_reporter_categories`.",
        "",
        "## Other authorities (not in Case.law cache)",
        "",
        "- *Rosario v. Abdelhalim*, Court of Appeal Case No. A173827 (docket; add slip or reporter cite when fixed).",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_json}", file=sys.stderr)
    print(f"Wrote {out_md}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
