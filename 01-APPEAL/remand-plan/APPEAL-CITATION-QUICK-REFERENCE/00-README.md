# Appeal Citation Quick Reference

**Purpose:** One-page-per-citation extract for the appellate judge. Each page shows the exact record excerpt cited in the Appellant's Opening Brief and Supplemental Memorandum, with a citation header stamp at the top for easy cross-reference.

**Source:** Citations extracted from 01-Appellants-Opening-Brief, 05-APPELLANTS-SUPPLEMENTAL-MEMORANDUM, and appeal source .tex files. No original PDFs are modified.

**Output:**
- `extracted-pages/` - One PDF per unique citation, with citation header stamp
- `COMBINED-CITATION-QUICK-REFERENCE.pdf` - Single PDF (51 pages after regeneration; count rises by one when augmented jury CT pinpoints are filled and extracts are re-run)
- `CITATION-INDEX.md` - Table mapping citation to file and combined PDF page number

**Current status:** Citation manifest uses certified **CT** for clerk materials; augmented jury materials are wired through `source/ct-augmented-jury-pinpoints.tex`. While those `\def` values remain `TBD`, the quick-reference combined PDF omits the jury-note page. After you set certified volume, page, and lines, run the two Python scripts below to add the CT extract. Legacy motion-exhibit pagination is not used for active extraction (`citation_source_map.json` keeps `JURY-QUESTIONS_legacy_motion_exhibit_pdf` only for old manifests).

**To regenerate:**
```bash
cd <workspace-root>
python3 Appeal-MASTER/scripts/build_citation_manifest.py
python3 Appeal-MASTER/scripts/extract_citation_pages.py
```
