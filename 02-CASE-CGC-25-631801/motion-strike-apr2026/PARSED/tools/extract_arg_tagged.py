#!/usr/bin/env python3
"""Extract [HEADING], [CONCLUSORY], [FACT-ASSERTION] from cleaned .md for NTC/MPA."""
import re
import sys
from pathlib import Path

CONCLUSORY = re.compile(
    r"(?i)(not recoverable|as a matter of law|should be stricken|without merit|"
    r"absolutely privileged|collateral estoppel|collateral attack|"
    r"unsupported by|no basis|improper(ly)? seeks|fails to state|"
    r"entirety of the (FAC|First Amended)|barred by|irrelevant, false, or improper|"
    r"improper, or nonconforming|duplicitously|erroneous application|"
    r"legally (irrelevant|unsupportable)|plainly|cannot be cured)"
)

HEADING = re.compile(
    r"^(?P<h>"
    r"[IVX]{1,4}\.\s+[^\n]+|"
    r"[A-D]\.\s+[^\n]+|"
    r"\d{1,2}\.\s+The [^\n]+|"
    r"\d{1,2}\.\s+Plaintiff[’']s [^\n]+|"
    r"III\.\s+.+|IV\.\s+.+|V\.\s+.+"
    r")\s*$"
)


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_arg_tagged.py <file.md> [out.arg.md]", file=sys.stderr)
        sys.exit(1)
    p = Path(sys.argv[1])
    text = p.read_text(encoding="utf-8", errors="replace")
    if text.startswith("---"):
        e = text.find("---", 3)
        if e != -1:
            text = text[e + 3 :]
    lines = text.splitlines()
    out = [f"# Argument / conclusory extraction: `{p.name}`", ""]
    for i, line in enumerate(lines):
        t = line.strip()
        if not t or t == "---":
            continue
        hm = HEADING.match(t)
        if hm and len(t) < 200 and (t[0] in "IVX" or t[0] in "ABCD" or t[:2] in ("I.", "II", "III", "IV", "V.")):
            out.append(f"## [HEADING] {t}")
            out.append("")
            continue
        if CONCLUSORY.search(t) and len(t) > 40:
            out.append(f"- [CONCLUSORY] {t}")
            continue
        if re.search(
            r"(?i)FAC,?\s*(pg\.|p\.|at|¶|paragraph)", t
        ) and re.search(r"(Verdict|jury|defense verdict|Plaintiff lost|alleg)", t):
            out.append(f"- [FACT-ASSERTION] {t}")
            continue
    outp = Path(sys.argv[2]) if len(sys.argv) > 2 else p.with_suffix(".arg.md")
    outp.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(outp)


if __name__ == "__main__":
    main()
