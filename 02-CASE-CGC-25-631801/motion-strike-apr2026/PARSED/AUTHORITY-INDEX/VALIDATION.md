# Authority validation (801 — CGC-25-631801)

Compares California reporter cites in the **MPA** against `by-document/MPA-CCP436.json` (regex + normalized spacing).

## MPA — full TEXT (`TEXT/MPA-CCP436.md`)

- **California cases in text (unique, normalized):** 10
- **California cases in JSON:** 10

**Result: PASS** — no mismatches after normalization (spacing in reporter).

## MPA — PART extract (`PART/MPA-CCP436.part.md`)

- **California cases in text (unique, normalized):** 10
- **California cases in JSON:** 10

**Result: PASS** — PART strip did not drop any MPA citations vs index.
