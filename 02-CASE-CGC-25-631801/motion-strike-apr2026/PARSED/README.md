# PARSED output — CGC-25-631801 (Apr 22 motion to strike)

**Scope:** Only PDFs in [801-MOTION-STRIKE-APR-22/](../) (this motion packet). Plaintiff opposition briefs are **not** stored here; see `801-DEFENSE-COURT/DRAFT/court-pdfs/` elsewhere in the repo if needed.

## Contents

| Path | Description |
|------|-------------|
| `TEXT/` | `pdftotext -layout` **.txt**, **.raw.txt**, cleaned **.md** (YAML frontmatter), **.json** metadata |
| `PART/` | Lean **.part.md** — POS and repeated running headers stripped (theory work) |
| `AUTHORITY-INDEX/by-document/` | Per-PDF case/statute extraction (`.md` + `.json`) |
| `AUTHORITY-INDEX/MASTER-AUTHORITY-LIST.*` | Deduped merge (**4** defense PDFs). `MASTER-AUTHORITY-LIST.md` = defense-only. |
| `AUTHORITY-INDEX/VALIDATION.md` | MPA citation check (TEXT vs PART vs index) |
| `DEFENSE-LEGAL-SPINE-631801.md` | Consolidated **defense** theory, relief, argument map, rebuttal hooks |
| `ARG/` | Tagged **[CONCLUSORY]** / **[HEADING]** for **NTC** + **MPA** |
| `BREAKDOWN/` | One sheet per defense PDF |
| `tools/` | `clean_pleading_text.py`, `extract_authorities.py`, `merge_master_authority.py`, `extract_arg_tagged.py`, `build_part.py`, `validate_mpa_authorities.py` |

## Source PDFs in this folder

| File | Slug |
|------|------|
| `NTC - CCP436.pdf` | `NTC-CCP436` |
| `MPAs - CCP436.pdf` | `MPA-CCP436` |
| `RFJN  - CCP436.pdf` | `RFJN-CCP436` |
| `Prop Order - CCP436.pdf` | `PROP-ORDER-CCP436` |

## Cross-case

[SIDE-BY-SIDE/](../../SIDE-BY-SIDE/) (801 vs 802; links to spines and `PART/` where useful).
