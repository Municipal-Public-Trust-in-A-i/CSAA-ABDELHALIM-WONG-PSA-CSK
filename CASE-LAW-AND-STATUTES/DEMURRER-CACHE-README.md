# Demurrer defense authorities (PDF cache)

California and federal **reporter citations** taken from `COURT-DEMURRER-DEFENSE/PARSED/legal-authorities.json` are cached here as **single-opinion PDFs** under `opinions-pdf/`, filename prefix `Demurrer-`.

## Curated PDFs (`COURT-DEMURRER-DEFENSE/auth`)

Justia downloads maintained with the demurrer defense packet live under:

`COURT-DEMURRER-DEFENSE/auth/`

**In-tree mirror (by court):** the same PDFs are also stored under:

- `opinions-pdf/curated-demurrer-auth/california-supreme/`
- `opinions-pdf/curated-demurrer-auth/california-court-of-appeal/`

See `INDEX.md` section **9a** for the exact filenames. After updating `auth/`, copy into both `curated-demurrer-auth/…` and the `Demurrer-*.pdf` names below.

When refreshing the cache, **prefer copying from `auth/`** into `opinions-pdf/` so the repo matches your working copies:

| File in `auth/` | Typical `opinions-pdf/` name |
|-----------------|------------------------------|
| `2017-a147236.pdf` | `Demurrer-cal-app-5th-vol14-p841-Mahan-v-Charles-W-Chan-Ins-Agency-Justia.pdf` |
| `2017-g052460.pdf` | `Demurrer-cal-app-5th-vol15-p462-FEV-v-City-of-Anaheim-Justia.pdf` |
| `Bockrath v. Aldrich Chemical Co. (1999) __ __ Supreme Court of California Decisions __ California Case Law __ California Law __ U.S. Law __ Justia.pdf` | `Demurrer-cal-4th-vol21-p71-Bockrath-v-Aldrich-Chemical-Co.pdf` |
| `2018-d072298.pdf` | `Demurrer-ca4d1-d072298-2018-Estate-of-Norman-Casserley-Auth.pdf` |

`2018-d072298.pdf` is **not** *Estate of Casserley* (1941) 42 Cal.App.2d 794. It is *Estate of Norman Casserley* (Court of Appeal, Fourth Dist., Div. One, docket D072298, filed 4/27/18, certified for publication). Keep it separate from the 1941 reporter cite.

## Source (not FindLaw)

Downloads use the **Harvard Case.law** open corpus (`static.case.law`), the same stack as `scripts/fetch-listed-opinions.py`: reporter volume PDF plus JSON metadata to extract the correct page span.

**FindLaw** is not scraped automatically. Each row in `DEMURRER-AUTHORITIES-CACHE-MANIFEST.json` includes a `findlaw_search_url` (Google search biased toward FindLaw, courts.ca.gov, and Justia) for manual browser retrieval when needed.

## Justia (California opinions)

California case law hub: [law.justia.com/cases/california/](https://law.justia.com/cases/california/). Courts of Appeal by year: [law.justia.com/cases/california/court-of-appeal/](https://law.justia.com/cases/california/court-of-appeal/) (pick a year, then scroll or in-page search for the case name).

**Important:** `https://law.justia.com/search?...` was observed to redirect to a **Justia account login**. For manual research, prefer the **year index** pages above (no login) or a **direct opinion URL** when you know the Court of Appeal docket number.

**URL pattern (verified on 2026-04-14):** published Court of Appeal opinions are often at:

`https://law.justia.com/cases/california/court-of-appeal/{YEAR}/{docket}.html`

where `{docket}` is the neutral docket in lowercase (examples below).

| Citation | Case | Justia opinion page |
|----------|------|---------------------|
| 14 Cal.App.5th 841 | *Mahan v. Charles W. Chan Ins. Agency, Inc.* | [a147236.html (2017)](https://law.justia.com/cases/california/court-of-appeal/2017/a147236.html) |
| 15 Cal.App.5th 462 | *F.E.V. v. City of Anaheim* | [g052460.html (2017)](https://law.justia.com/cases/california/court-of-appeal/2017/g052460.html) |

Each of those pages includes **Opinion** and **Download PDF** links for a full-text copy outside Case.law.

**Direct PDF on `cases.justia.com` (for scripting):** after opening **Download PDF** in a browser once, the PDF often loads from:

`https://cases.justia.com/california/court-of-appeal/{YEAR}-{docket}.pdf`

Examples verified in this repo: `2017-a147236.pdf` (*Mahan*), `2017-g052460.pdf` (*F.E.V.*). Query string `?ts=...` may appear in the tab URL but is usually optional for download.

**Older reporters (example):** `https://law.justia.com/cases/california/court-of-appeal/2d/42/794.html` serves an opinion whose **metadata** aligns with modern Cal. App. 2d volume numbering; it is **not** a reliable shortcut for historical 1941 opinions such as *Estate of Casserley* (42 Cal.App.2d 794). For pre-digital volumes, use the year listing (for example [1941](https://law.justia.com/cases/california/court-of-appeal/1941/)), official court PDFs, or Google Scholar. A browser spot-check of the 1941 index did not surface *Casserley* on the first index page; pagination or non-Justia sources may be required.

## Manifest

| File | Purpose |
|------|---------|
| `DEMURRER-AUTHORITIES-CACHE-MANIFEST.json` | Per-citation status, Case.law JSON and volume URLs, optional search URL, relative PDF path |

`status_counts` in the manifest summarizes the last run (for example `skipped_existing_demurrer_pdf`, `not_found`).

## Refresh

```bash
cd CASE-LAW-AND-STATUTES/scripts
# Re-parse demurrer PDFs if inputs changed:
# (from repo root) python3 COURT-DEMURRER-DEFENSE/parse_demurrer_defense_pdfs.py
# python3 COURT-DEMURRER-DEFENSE/extract_legal_authorities.py

python3 cache_demurrer_authorities.py
```

After a manifest run, re-apply curated Justia PDFs from the defense packet if needed: copy from `COURT-DEMURRER-DEFENSE/auth/` into (1) `opinions-pdf/curated-demurrer-auth/california-supreme/` and `…/california-court-of-appeal/` using the **9a** filenames in `INDEX.md`, and (2) the `Demurrer-*.pdf` names in the table above.

Optional: `python3 cache_demurrer_authorities.py --json /path/to/legal-authorities.json`

Volume PDFs are cached under `CASE-LAW-AND-STATUTES/.cache/cap-volumes/` to avoid re-downloading full reporter books.

## Not in Case.law (manual follow-up)

These citations from the demurrer extract did not resolve to a Case.law case JSON (`404`). Use the manifest `findlaw_search_url`, **Justia** links in the section above, or official court sites:

| Citation (approx.) | Notes |
|---------------------|--------|
| 21 Cal.4th 71 | *Bockrath v. Aldrich Chemical*; phantom `212` / `2122` was OCR noise. Cache script normalizes to **21** Cal.4th 71 for Case.law. |
| 42 Cal.App.2d 794 | *Estate of Casserley* (1941); very old volume; Justia vol/page URL may not map to this opinion (see Justia section). |
| 14 Cal.App.5th 841 | *Mahan*; [Justia a147236](https://law.justia.com/cases/california/court-of-appeal/2017/a147236.html); local PDF via [`2017-a147236.pdf` on cases.justia.com](https://cases.justia.com/california/court-of-appeal/2017-a147236.pdf) |
| 15 Cal.App.5th 462 | *F.E.V.*; [Justia g052460](https://law.justia.com/cases/california/court-of-appeal/2017/g052460.html); local PDF via [cases.justia.com 2017-g052460.pdf](https://cases.justia.com/california/court-of-appeal/2017-g052460.pdf) |
| 705 F.2d 1143 | *Associated Press v. U.S. Dist. Court* (9th Cir. 1983); CAP and some indexes use **705 F.2d 1141** for the same decision. Full text and PDF tab on [CourtListener 8927010](https://www.courtlistener.com/opinion/8927010/associated-press-v-united-states-district-court-for-central-district-of/) (volume index: `/c/f2d/705/?page=10`). Automated `curl` to CourtListener opinion or PDF URLs may hit WAF; use a browser for PDF export if needed. |

## Statutes

Statutory cites in the demurrer (CCP, Civ. Code, etc.) are **not** exported as PDF here. Many are already under `statutes-cal/` from other workflows. California codes on [leginfo.legislature.ca.gov](https://leginfo.legislature.ca.gov) are HTML; this cache focuses on **opinion PDFs**.
