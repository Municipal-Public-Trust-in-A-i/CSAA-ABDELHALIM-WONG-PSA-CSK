#!/usr/bin/env python3
"""
Compare case citations in MPA .md vs by-document MPA-*.json; write VALIDATION.md
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_extract():
    spec = importlib.util.spec_from_file_location(
        "extract_authorities", ROOT / "extract_authorities.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        e = text.find("---", 3)
        if e != -1:
            return text[e + 3 :]
    return text


def norm_key(s: str) -> str:
    s = re.sub(r"\s+", " ", s.strip().lower())
    s = s.replace("cal. app.", "cal.app.")
    s = re.sub(r"cal\.\s+(\d)", r"cal.\1", s)
    return s


def all_cal_cites_from_text(text: str, ex) -> dict:
    s = strip_frontmatter(text)
    cases = {}
    for rx in ex.RE_CAL_PARTS:
        for m in rx.finditer(s):
            c = ex.norm_cal(m.group(1))
            if len(c) >= 6:
                cases[norm_key(c)] = c
    return cases


def main():
    ex = load_extract()
    if len(sys.argv) < 4:
        print(
            "Usage: validate_mpa_authorities.py <MPA.md> <MPA.json> <VALIDATION.md> [label]",
            file=sys.stderr,
        )
        sys.exit(1)
    md_path = Path(sys.argv[1])
    json_path = Path(sys.argv[2])
    out_path = Path(sys.argv[3])
    label = sys.argv[4] if len(sys.argv) > 4 else md_path.stem

    text = md_path.read_text(encoding="utf-8", errors="replace")
    data = json.loads(json_path.read_text(encoding="utf-8"))
    from_text = all_cal_cites_from_text(text, ex)
    idx = {norm_key(c): c for c in data.get("cases_california", [])}

    in_text_not_in_index = [
        from_text[k] for k in from_text if k not in idx
    ]
    in_index_not_in_text = [idx[k] for k in idx if k not in from_text]

    lines = [
        f"# Authority validation: `{label}`",
        "",
        f"- **Source text:** `{md_path.name}`",
        f"- **Index:** `{json_path.name}`",
        f"- **California cases in text (unique, normalized):** {len(from_text)}",
        f"- **California cases in JSON:** {len(idx)}",
        "",
    ]
    if not in_text_not_in_index and not in_index_not_in_text:
        lines.append(
            "**Result: PASS** — no mismatches after normalization (spacing in reporter)."
        )
    else:
        lines.append(
            "**Result: REVIEW** — see differences below (often `Cal. 3d` vs `Cal.3d`)."
        )
    lines.append("")
    if in_text_not_in_index:
        lines.append("## In TEXT but not in index JSON")
        for x in sorted(in_text_not_in_index, key=str.lower):
            lines.append(f"- {x}")
        lines.append("")
    if in_index_not_in_text:
        lines.append("## In index JSON but not found in TEXT (regex)")
        for x in sorted(in_index_not_in_text, key=str.lower):
            lines.append(f"- {x}")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
