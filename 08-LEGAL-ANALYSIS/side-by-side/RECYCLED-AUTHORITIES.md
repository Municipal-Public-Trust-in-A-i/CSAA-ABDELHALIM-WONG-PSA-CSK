# Recycled vs new — motion-to-strike citations vs `801-DEFENSE-COURT` corpus

> **Corpus used:** all `801-DEFENSE-COURT/AUTHORITY-INDEX/by-document/*.json` files with a **`"cases"`** array (demurrer, anti-SLAPP, etc.), **case-normalized** (spacing-insensitive, lowercased for matching).  
> **Motion-strike** sets: **801** = `MASTER-AUTHORITY-LIST-DEFENSE-ONLY` (4 defense PDFs); **802** = full `802` `MASTER-AUTHORITY-LIST.json`.

## Recycled — also appeared in prior defense **801** by-document list

| Case (normalized) | In 801 MTD strike | In 802 MTD strike |
|-------------------|-------------------|-------------------|
| 1 Cal.3d 467 | ✓ | (not in 802 MPA set — 802 is insurer fraud) |
| 49 Cal.App.3d 917 | ✓ | ✓ |
| 58 Cal.App.2d 878 | ✓ | ✓ |
| 71 Cal.App.4th 268 | ✓ | ✓ |
| 146 Cal.App.3d 470 | ✓ | ✓ (reporter spacing differs in text: `Cal. App. 3d`) |
| 15 Cal.App.5th 462/463 | **463** (801) / **462** (802) | see **pincite** check on **F.E.V. v. City of Anaheim** in **original** PDFs |
| 227 Cal.App.4th 813 | ✓ | ✓ |
| 265 Cal.App.2d 82 | ✓ | ✓ |

**Interpretation:** the **estoppel** / **collateral attack** / **insurer standing** **cluster** **recycles** from **demurrer/anti-SLAPP** work on the same **core** *Rosario* / **PSA** / **CSAA** file.

## New in motion-to-strike (not in the demurrer **by-document** set sampled)

**801 (examples):** *Coyne* **35** Cal.2d 257; *Ribas* **38 Cal.3d 355; *F.E.V.* 15 Cal.App.5th **463**; **98 U.S. 61** *Throckmorton* (federal) — *Throckmorton* may be **rare** in the **short** 801 `MASTER` excerpt but appears in **MPA-CCP436**.

**802 (examples):** *Trope* 11 Cal.4th 274; *Food Pro* 169 Cal.App.4th 976; *Stewart* 17 Cal.App.4th 468; *Angelica* 28 Cal.3d 908; *Today’s IV* 83 Cal. App. 5th 1137; *McNeal* 80 Cal.App.5th 841; **Civ. Code §§ 3294 / 1021** themes; **12 Cal.4th 631**; **96 Cal.App.4th 1017**; **Chandler* line **59 Cal.2d 618** (in **decl** / TOC extraction).

**Note:** **C.C.P. § 430.70** appears in **RFJN**; **Evid. §§ 452/453** — also in **RJN** in **other** matters — so **RJN** is **procedural** **recycle**, not a “new” legal theory.

## Conclusory / rhetorical **recycle**

Both MPAs use the same **RPG**-style phrasing: “**not recoverable as a matter of law**,” “**absolutely privileged**,” “**collateral attack** on a **valid** judgment,” “**duplicitous**” fee disclaimers — parallel to [801-vs-802-CONCLUSORY-STATEMENTS.md](./801-vs-802-CONCLUSORY-STATEMENTS.md).

## Script (repro)

Run from repository root (adjust paths if needed):

```text
# Intersection: see implementation used in session (Python json+norm_cite) comparing
# motion-strike MASTER JSONs vs 801-DEFENSE-COURT/AUTHORITY-INDEX/by-document/*.json
```

**Manual follow-up:** merge **OCR/typo** line **35** vs **36** Cal.2d for *Coyne* in **802 MPA** PDF.
