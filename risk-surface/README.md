# RISK-SURFACE (settlement breakouts)

**April 2026 restructure** of the quantified exposure model in the archival source [`../RISK.SURFACE.md`](../RISK.SURFACE.md). That file is unchanged; this folder adds per-case isolation, per-party rollups, CSAA-only settlement demand drafts (802), and a non-redundant master index.

## Reading order

1. **[MASTER-CONSOLIDATED.md](MASTER-CONSOLIDATED.md)** — spine: matrices, cross-walk, totals, links (no duplicate long narrative).
2. **Per proceeding** — [`per-case/`](per-case/) (Appeal, 801, 802, Retrial).
3. **Per defendant** — [`per-party/_grouped/`](per-party/_grouped/) and [`per-party/_individuals/`](per-party/_individuals/).
4. **CSAA-only demand (CGC-25-631802)** — [`settlement-demand-CSAA/`](settlement-demand-CSAA/) (three tone tiers).

## Canonical dollar figures (anti double-count)

| Topic | Canonical file |
|--------|----------------|
| 802 compensatory, punitive ratios, UCL, CSAA total | [per-case/FRAUD-UCL-802-CGC-25-631802.md](per-case/FRAUD-UCL-802-CGC-25-631802.md) |
| 801 ancillary per-defendant | [per-case/EQUITY-801-CGC-25-631801.md](per-case/EQUITY-801-CGC-25-631801.md) |
| Retrial PI line items + Abdelhalim punitive | [per-case/RETRIAL-CGC-21-594102.md](per-case/RETRIAL-CGC-21-594102.md) |
| Appeal: $0 direct; derivative totals | [per-case/APPEAL-A173827.md](per-case/APPEAL-A173827.md) — derivative **references** retrial canonical |

Other documents link here instead of restating tables.

### Verification (no duplicate canonical tables)

| Check | Status |
|-------|--------|
| 802 compensatory / punitive / UCL / CSAA 5:1 totals | Single table block in `per-case/FRAUD-UCL-802-CGC-25-631802.md` only |
| 801 ancillary per-defendant | Single matrix in `per-case/EQUITY-801-CGC-25-631801.md` only |
| Retrial PI lines + punitive + combined totals | Single file `per-case/RETRIAL-CGC-21-594102.md` only |
| Appeal derivative dollars | **No table** — `per-case/APPEAL-A173827.md` links to retrial anchors only |
| CSAA demand drafts | Anchor figures only; full grids linked to 802 per-case file |
| Master index | Rollup tables preserved once here + in archival `RISK.SURFACE.md` |

## Directory map

```
RISK-SURFACE/
  README.md
  MASTER-CONSOLIDATED.md
  settlement-demand-CSAA/
  per-case/
  per-party/
    _grouped/
    _individuals/
```

---

*Not legal advice. Figures and law citations trace to `RISK.SURFACE.md`.*

---

## Document metadata

| Field | Value |
|-------|-------|
| Created | 2026-07-10 |
| Last updated | 2026-04-24 |
| Last author | soltrinox |
| Version | `d40ae05` (rev 1) |
| Repository | GITHUB-PAGE |

*Auto-generated from git history. Re-run `scripts/audit_strategic_docs.py --apply` to refresh.*
