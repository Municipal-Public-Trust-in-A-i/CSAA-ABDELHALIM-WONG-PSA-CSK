#!/usr/bin/env python3
"""
Produce lean PART/*.part.md from TEXT/*.md: drop POS, repeated headers, excess page breaks.
"""
import re
import sys
from pathlib import Path

REPEAT_HEADER_PATTERNS = [
    r"^MEMORANDUM OF POINTS AND AUTHORITIES IN SUPPORT OF MOTION TO STRIKE PLEADING\s*$",
    r"^NOTICE OF MOTION AND MOTION TO STRIKE PLEADING\s*$",
    r"^REQUEST FOR JUDICIAL NOTICE IN SUPPORT OF MOTION TO STRIKE PLEADING\s*$",
    r"^DECLARATION OF TYLER J\. O'CONNELL IN SUPPORT OF MOTION TO STRIKE PLEADING\s*$",
    r"^\[PROPOSED\] ORDER\s*$",
]
REPEAT_COMPILED = [re.compile(p, re.I) for p in REPEAT_HEADER_PATTERNS]

# Truncate very long declarations (slug contains DEC-TOC)
DEC_MAX_LINES = 450


def strip_frontmatter(s: str) -> str:
    if s.startswith("---"):
        end = s.find("---", 3)
        if end != -1:
            return s[end + 3 :].lstrip()
    return s


def to_part_markdown(body: str, slug: str) -> str:
    t = strip_frontmatter(body)
    # Cut at proof of service
    m = re.search(
        r"(?im)^\s*PROOF OF SERVICE\s*$", t
    ) or re.search(
        r"(?im)^\s*I declare under penalty of perjury under the laws of the State of California that the foregoing is true and correct\.\s*$",
        t,
    )
    if m:
        t = t[: m.start()].rstrip()
    # Drop line-equals "Franciscus Dylan Rosario" caption blocks before POS if still there
    t = re.sub(
        r"\n\s*Franciscus Dylan Rosario v\.[^\n]+\n\s*San Francisco County Superior Court Case No\.: CGC-[^\n]+\n",
        "\n",
        t,
        flags=re.I,
    )
    lines = t.splitlines()
    out = []
    prev_blank = False
    for line in lines:
        if any(rx.match(line.rstrip() or "") for rx in REPEAT_COMPILED):
            continue
        if re.match(r"^[\s/]*$", line) and line.strip() in ("", "/"):
            continue
        s = line.rstrip()
        if s.strip() == "///":
            continue
        if not s.strip():
            if not prev_blank:
                out.append("")
                prev_blank = True
            continue
        prev_blank = False
        out.append(s)
    text = "\n".join(out)
    # Collapse duplicate horizontal rules
    text = re.sub(r"(\n---\n){2,}", "\n---\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip() + "\n"

    if "DEC-TOC" in slug or ("DEC" in slug and "TOC" in slug):
        ls = text.splitlines()
        if len(ls) > DEC_MAX_LINES:
            head = "\n".join(ls[:DEC_MAX_LINES])
            text = (
                f"> Truncated to first {DEC_MAX_LINES} body lines; full text in `TEXT/{slug.split('.')[0]}.md`.\n\n"
                + head
                + f"\n\n[… {len(ls) - DEC_MAX_LINES} lines omitted …]\n"
            )

    meta = f"<!-- part_extract: {slug} — no POS, repeated running headers removed -->\n\n"
    return meta + text


def main():
    if len(sys.argv) < 2:
        print("Usage: build_part.py <TEXT/foo.md> [out.part.md]", file=sys.stderr)
        sys.exit(1)
    src = Path(sys.argv[1])
    slug = src.stem
    dst = (
        Path(sys.argv[2])
        if len(sys.argv) > 2
        else src.parent.parent / "PART" / f"{slug}.part.md"
    )
    body = src.read_text(encoding="utf-8", errors="replace")
    out = to_part_markdown(body, slug)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    print(dst)


if __name__ == "__main__":
    main()
