# FRIDAY-PACKAGE-ANTISLAPP — What To File Today (Apr 24, 2026)

Strategic goal: change the outcome of the **May 12, 2026 anti-SLAPP hearings** (Case 801 Dept 301; Case 802 Dept 302) by (A) locking in a categorical exemption (§ 425.17(c) / *Flatley*) via supplemental authority, and (B) unlocking a narrow slice of prong-two discovery via a § 425.16(g) motion heard on shortened time.

## Artifacts produced

```
FRIDAY-PACKAGE-ANTISLAPP/
  build_antislapp_package.py        # pdflatex build script
  CITATION-VALIDATION-42517C-FLATLEY.md
  README.md                         # (this file)
  801/
    src/
      PREAMBLE.tex
      CAPTION-801.tex
      SIGBLOCK.tex
      NOTICE-LODGING-SUPPL-AUTH-42517C-FLATLEY-801.tex       # Track A
      MOTION-42516g-COMBINED-801.tex                          # Track B (notice+MPA+decl+Exh.A/B+order)
      EX-PARTE-OST-42516g-801.tex                             # Track B companion OST
      EXHIBIT-A-APR24-DEFENSE-EMAIL.tex                       # Exhibit re Apr. 24, 2026 e-mail
      CAPTION-801-SUPP-APR27.tex / SIGBLOCK-APR27.tex
      SUPPL-DECL-ROSARIO-APR27-MEET-CONFER-801.tex         # M&C record + Exhibit A
    court-pdfs/
      NOTICE-LODGING-SUPPL-AUTH-42517C-FLATLEY-801.pdf
      MOTION-42516g-COMBINED-801.pdf
      EX-PARTE-OST-42516g-801.pdf
      EXHIBIT-A-APR24-DEFENSE-EMAIL.pdf   (from ../EMAILS/ by default, or typeset)
      SUPPL-DECL-ROSARIO-APR27-MEET-CONFER-801.pdf
  802/
    src/   (parallel; same supplemental + 802-SUPP caption)
    court-pdfs/
      NOTICE-LODGING-SUPPL-AUTH-42517C-FLATLEY-802.pdf
      MOTION-42516g-COMBINED-802.pdf
      EX-PARTE-OST-42516g-802.pdf
      EXHIBIT-A-APR24-DEFENSE-EMAIL.pdf   (from ../EMAILS/ by default, or typeset)
      SUPPL-DECL-ROSARIO-APR27-MEET-CONFER-802.pdf
  ../EMAILS/   (Gmail print-to-PDF; see ../EMAILS/README.md)
```

**Supplemental declarations (Apr. 27, 2026 e-filing / service):** Filing and POS-050: [`../FILING-INSTRUCTIONS-APR27-SUPPLEMENTAL.md`](../FILING-INSTRUCTIONS-APR27-SUPPLEMENTAL.md). Validation: [`../VALIDATION-CHECKLIST-SUPP-APR27.md`](../VALIDATION-CHECKLIST-SUPP-APR27.md). By default, `build_antislapp_package.py` **stages** Exhibit A from [`../EMAILS/*.pdf`](../EMAILS/README.md) into `EXHIBIT-A-APR24-DEFENSE-EMAIL.pdf`, then builds the Supplemental (which `\includepdf`s it). Use `--exhibit typeset` to build Exhibit A from `EXHIBIT-A-APR24-DEFENSE-EMAIL.tex` instead.

Rebuild anytime with:

```bash
cd APRIL-24-2026/FRIDAY-PACKAGE-ANTISLAPP
python3 build_antislapp_package.py            # both cases
python3 build_antislapp_package.py --case 801 # one case
```

## What to file today (Friday, Apr 24, 2026)

**Filing venue:** Room 103 (pro per / fee-waiver, LRSF 2.11 / CRC 2.253(a)(3)). One clerk trip per case, or combined if the clerk accepts both.

### Case 801 (CGC-25-631801, Dept 301, Hon. Van Aken)

Filing order at the counter:

1. **Track A — FILED stack:**
   - `801/court-pdfs/NOTICE-LODGING-SUPPL-AUTH-42517C-FLATLEY-801.pdf` (file-stamp; index on register)
2. **Track B — FILED stack:**
   - `801/court-pdfs/MOTION-42516g-COMBINED-801.pdf` (file-stamp the notice / MPA / declaration; **lodge** the [Proposed] Order at the end for endorsement only — not a file stamp)
   - `801/court-pdfs/EX-PARTE-OST-42516g-801.pdf` (file-stamp the ex parte application and the supporting declaration; **lodge** the [Proposed] Order at the end; hand to ex parte clerk for the Monday Apr 27, 11:00 a.m. ex parte calendar per LRSF 9)
3. **Proof of service:** one consolidated POS-050 per case, covering Tracks A + B; add to `official-pos050/` alongside existing Apr 24 POS forms.

### Case 802 (CGC-25-631802, Dept 302, Hon. Quinn)

Filing order at the counter:

1. **Track A — FILED stack:**
   - `802/court-pdfs/NOTICE-LODGING-SUPPL-AUTH-42517C-FLATLEY-802.pdf`
2. **Track B — FILED stack:**
   - `802/court-pdfs/MOTION-42516g-COMBINED-802.pdf`
   - `802/court-pdfs/EX-PARTE-OST-42516g-802.pdf` (for Dept 302 ex parte calendar Mon Apr 27, 11:00 a.m.)
3. **Proof of service:** one consolidated POS-050 per case.

### Service on defense (before filing)

Per CRC 3.1203, 24-hour written notice of the ex parte OST applications must have been served by **10:00 a.m. Thursday Apr 23, 2026**. If that notice was not given:

- Either (a) present today at 11:00 a.m. AM and argue good cause why 24-hour notice could not be given and the application should still be heard (CRC 3.1204(b)), **or** (b) serve the 24-hour notice now and reset the ex parte to Monday Apr 27, 11:00 a.m.

The ex parte applications as drafted recite Apr 23, 2026 service. Amend the recitation in the Declaration of Plaintiff (para. 6 in the OST TEX for each case) if service was actually made later, re-build, and re-file.

### Courtesy copies (LRSF 2.7(B))

- Deliver courtesy binder-packet copies to:
  - **Dept 301** (Hon. Van Aken) — Case 801 Track A + B + OST
  - **Dept 302** (Hon. Quinn) — Case 802 Track A + B + OST
- Bookmark each PDF in the chambers packet at Notice, MPA, Declaration, Exhibit A, Exhibit B, Proposed Order (matches the internal section structure of `MOTION-42516g-COMBINED-*`).

## Stay-compliance checklist (do NOT skip)

- [ ] No RFP or deposition notice has been served on defense.
- [ ] Exhibit A (RFPs) and Exhibit B (depo notice) within the combined motion are clearly labeled "conditional; not served."
- [ ] The only discovery-related paper filed today is the § 425.16(g) **motion itself** + its OST companion — neither is "discovery" for stay purposes.
- [ ] If OST is granted on Apr 27 and the Motion is heard on Apr 30 / May 1 and granted, then (and only then) serve RFPs and depo notice.

## Risk posture and fallbacks

- **Defense counter-move:** If defense opposes the OST as an end-run around the stay, rely on paragraph 8 of the OST Declaration (no discovery served, motion itself is not discovery) and on *Lafayette Morehouse* (narrowly tailored discovery satisfies good cause even during the stay).
- **If OST is denied:** The § 425.16(g) Motion is already filed on regular notice. It will simply be heard later; Track A still stands alone as supplemental authority for May 12.
- **If Track A is challenged as "late-filed":** CRC 3.1113(j) / 3.1306(c) allow lodging of supplemental authority any time before the hearing. No amendment to the pleading is made.
- **Amendment-to-defeat (Simmons/Salma) concern:** Neither Track A nor Track B amends any pleading. The § 425.17(c) exemption is invoked on the existing FAC.

## Validation

- Citations validated in `CITATION-VALIDATION-42517C-FLATLEY.md`.
- Build: clean pdflatex compile of all 6 TEX sources, 3 PDFs per case (~250 KiB each).
- Recommended: run `APRIL-24-2026/scan-reports/scan_pdfs.py` over `801/court-pdfs/*.pdf` and `802/court-pdfs/*.pdf` as a smoke test before printing.

## One-line filing summary

> **801:** File Notice of Lodging + § 425.16(g) Motion + ex parte OST; lodge both Proposed Orders. Run the OST through Dept 301 ex parte Monday 4/27 11:00 a.m.  **802:** Same, Dept 302. No discovery served until OST ruling. Track A is ripe for May 12 either way.
