# Legal authorities (case law, statutes, rules)

This site mirrors a local copy of California case law materials, statutory extracts, and court rules used in briefing and analysis. **Prefer the PDF** when both a reporter-style PDF and a Markdown extract exist; use **Markdown** when no PDF is present or for quick reading; use **external** (Justia, leginfo, courts.ca.gov) when the authority is cited on the site but not yet cached locally.

**Master index:** [CASE-LAW-AND-STATUTES/INDEX.md](CASE-LAW-AND-STATUTES/INDEX.md) (tables of cases, statutes, opinion PDFs, and coverage reports).

## Folder layout (under `CASE-LAW-AND-STATUTES/`)

| Folder | Contents |
|--------|----------|
| [opinions-pdf/](CASE-LAW-AND-STATUTES/opinions-pdf/) | Opinion PDFs (including Demurrer / motion-strike / equity batches). Some entries include paired `.md` / `.raw.txt` extractions. |
| [cases-cal-supreme/](CASE-LAW-AND-STATUTES/cases-cal-supreme/) | California Supreme Court: narrative `.md` (often with source URLs in the file). |
| [cases-cal-appellate/](CASE-LAW-AND-STATUTES/cases-cal-appellate/) | Court of Appeal: narrative `.md`. |
| [statutes-cal/](CASE-LAW-AND-STATUTES/statutes-cal/) | Code sections pulled from [leginfo.legislature.ca.gov](https://leginfo.legislature.ca.gov) (source URL in each file). |
| [standards/](CASE-LAW-AND-STATUTES/standards/) | California Rules of Court excerpts (e.g. CRC 8.204). |
| [rules-of-court/](CASE-LAW-AND-STATUTES/rules-of-court/) | Statewide CRC PDFs, SF local rules (PDF + MD where applicable). |
| [DEFENSE-PLEADINGS-COVERAGE-REPORT.md](CASE-LAW-AND-STATUTES/DEFENSE-PLEADINGS-COVERAGE-REPORT.md) | Machine inventory vs. pleading citations (defense packet). |

**Not mirrored here:** the `scripts/` directory from the main repo (fetch / validation utilities) is omitted from this published tree; scripts remain in the repository under `CASE-LAW-AND-STATUTES/scripts/` for maintainers.

## GitHub / size

- The mirror is large (~multi‑GB) because it includes full opinion PDFs. The largest single file checked in this worktree is under **100 MB** (GitHub’s hard per-file limit is 100 MB for normal git; use **Git LFS** only if a future PDF exceeds that).

## Gaps and external fallbacks

Authorities cited on [README.md](README.md), [MERITS.md](MERITS.md), or [EXTRINSIC-FRAUD-THREADING-THE-NEEDLE-801-AND-802.md](EXTRINSIC-FRAUD-THREADING-THE-NEEDLE-801-AND-802.md) that **may not** have a local PDF in `opinions-pdf/` include (non-exhaustive):

| Authority | Typical fallback |
|-----------|------------------|
| *Soukup v. Law Offices of Herbert Hafif* (2006) 39 Cal.4th 260 | [Justia (39 Cal.4th 260)](https://law.justia.com/cases/california/supreme-court/4th/39/260.html) |
| *Stansfield v. Starkey* (1990) 220 Cal.App.3d 59 | [Justia (3d 220, p. 59)](https://law.justia.com/cases/california/court-of-appeal/3d/220/59.html) |
| *D'Amico v. Board of Medical Examiners* (1974) 11 Cal.3d 1 | [Justia (11 Cal.3d 1)](https://law.justia.com/cases/california/supreme-court/3d/11/1.html) |
| *Committee on Children’s Television, Inc. v. General Foods Corp.* (1983) 35 Cal.3d 197 | [Justia (35 Cal.3d 197)](https://law.justia.com/cases/california/supreme-court/3d/35/197.html) |
| *Caldwell v. Taylor* (1933) 218 Cal. 471 | Reporter volume—use a neutral database or the official reported opinion source; not bundled as a stand-alone PDF in this mirror. |
| *Pico v. Cohn* (1891) 91 Cal. 129 | Same; use neutral database. |
| *Blanton v. Womancare, Inc.* (1985) 38 Cal.3d 396 | [Justia (38 Cal.3d 396)](https://law.justia.com/cases/california/supreme-court/3d/38/396.html) |
| *Smith v. Superior Court* (1992) 10 Cal.App.4th 1033 | [Justia (10 Cal.App.4th 1033)](https://law.justia.com/cases/california/court-of-appeal/4th/10/1033.html) (verify division if needed) |
| *In re Marriage of Rosevear* (1998) 65 Cal.App.4th 673 | [Justia (65 Cal.App.4th 673)](https://law.justia.com/cases/california/court-of-appeal/4th/65/673.html) |
| Title **10** Cal. Code of Regs. § **2695.7** (insurance claims) | **Regulatory** text: use the **California Department of Insurance** compilation or your preferred official source; not duplicated as a standalone file in this mirror. |
| “Additional cases … not yet pulled” in INDEX | See [INDEX.md § 6–7](CASE-LAW-AND-STATUTES/INDEX.md) and Justia URL patterns there. |

Many additional cases **are** available locally—search `opinions-pdf/` by party name or citation string in the filename.

## Statutes added for this site (meet-and-confer / merits cites)

These were fetched into `statutes-cal/` to support inline links where the code section is quoted in the merits materials:

- [CCP § 2015.5](CASE-LAW-AND-STATUTES/statutes-cal/CCP-2015.5.md) (verifying pleadings)
- [CCP § 430.41](CASE-LAW-AND-STATUTES/statutes-cal/CCP-430.41.md) · [CCP § 435.5](CASE-LAW-AND-STATUTES/statutes-cal/CCP-435.5.md) (meet and confer)
- [B&amp;P § 6128](CASE-LAW-AND-STATUTES/statutes-cal/BPC-6128.md) (attorney deceit)
- [Civ. Code § 2338](CASE-LAW-AND-STATUTES/statutes-cal/CIV-2338.md) · [Civ. Code § 1573](CASE-LAW-AND-STATUTES/statutes-cal/CIV-1573.md) (ratification / constructive fraud touchstones as cited)

Canonical copies of the same files also exist under the repository root `CASE-LAW-AND-STATUTES/statutes-cal/` (outside `GITHUB-PAGE/`) for non-site workflows.

---
*This page is navigation only, not legal advice.*
