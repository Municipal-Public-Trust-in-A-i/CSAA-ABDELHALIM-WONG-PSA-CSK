# Authority validation (802 — CGC-25-631802)

Compares California reporter cites in the **MPA** against `by-document/MPA2-CCP436.json` (regex + normalized spacing).

## MPA — full TEXT (`TEXT/MPA2-CCP436.md`)

- **California cases in text (unique, normalized):** 17
- **California cases in JSON:** 17

**Result: PASS** — no mismatches after normalization (spacing in reporter).

## MPA — PART extract (`PART/MPA2-CCP436.part.md`)

- **California cases in text (unique, normalized):** 17
- **California cases in JSON:** 17

**Result: PASS** — PART strip did not drop any MPA citations vs index.
