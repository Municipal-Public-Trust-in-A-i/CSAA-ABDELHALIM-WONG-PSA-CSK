# Clerk packets — April 24, 2026 (ex parte)

Two consolidated PDFs for Room 103 filing, one per case. Each packet separates **FILED** (register) papers from **LODGED** (courtesy / proposed-order) papers with a full-page section divider.

| Output | Case |
|--------|------|
| `CLERK-PACKET-801-CGC-25-631801.pdf` | CGC-25-631801 (Dept. 301) |
| `CLERK-PACKET-802-CGC-25-631802.pdf` | CGC-25-631802 (Dept. 302) |

**Regenerate:** from `APRIL-24-2026/clerk-packets/`, run `python3 build_clerk_packets.py` (optional: `--parts` to write cover/section/tab divider PDFs under `parts/`).

---

## Print settings

- **Paper:** US Letter (8.5 x 11 in).
- **Scaling:** 100% (no “fit to page” shrink).
- **Sides:** Single-sided.
- **Color:** Black and white is fine unless a document requires color.
- **Binding:** Three-hole punch along the left margin is optional; the clerk may re-bind or scan.

---

## Clerk window script (short)

> “Good morning. Two cases, two packets. **Please file-stamp the FILED section first** — everything after the full-page **‘--- FILED ---’** divider through the last document before the full-page **‘--- LODGED — DO NOT FILE-STAMP ---’** divider.  
> **Then the LODGED stack:** proposed orders need **endorsement** treatment per your usual CRC 3.1312 practice — **not** ordinary register file stamps on those orders or on the reply lodgings. The **early-lodging cover (801 only)** and **late-lodgment cover (802)** explain chambers courtesy; **please do not file-stamp** the lodged reply PDFs behind those covers. Thank you.”

---

## Rule-basis table (by packet section)

### CGC-25-631801 — FILED

| Document (tab) | Basis (short) |
|----------------|---------------|
| Notice of Filing — Decl. & proposed order (May 15) | CRC 3.1345(a)(5) |
| Consolidated POS-050 — Apr 22 service | CRC 3.1204(b) (ex parte notice proof) |
| POS-050 — Apr 24 filing-service | CCP 1010.6; CRC 2.251 |

### CGC-25-631801 — LODGED

| Document (tab) | Basis (short) |
|----------------|---------------|
| [Proposed] order staying MTS | CRC 3.1312 |
| Early-lodging cover (801 Reply + objections) | LRSF 2.7(B); formal reply filing Apr 29 under CCP 1005(b) |
| Reply (May 6) + Evid. objections (801) | Chambers courtesy (LRSF 2.7(B)); objections CRC 3.1354 with Reply |

### CGC-25-631802 — FILED

| Document (tab) | Basis (short) |
|----------------|---------------|
| Notice of Filing — separate statement (May 18) | CRC 3.1345 |
| Notice of Re-Presentation — SAC support | Clerk register correction / re-presentation |
| Evidentiary objections — O’Connell (802) | CRC 3.1354 (with Reply lodged same day) |
| Consolidated POS-050 — Apr 22 service | CRC 3.1204(b) |
| POS-050 — Apr 24 filing-service | CCP 1010.6; CRC 2.251 |
| POS-050 — Apr 24 reply-service | CCP 1010.6; CRC 2.251 |
| POS-050 — Apr 24 supplemental-service | CCP 1010.6; CRC 2.251 |

### CGC-25-631802 — LODGED

| Document (tab) | Basis (short) |
|----------------|---------------|
| [Proposed] order staying MTS | CRC 3.1312 |
| Late-lodgment cover — Reply (802) | CCP 1005(b); CRC 3.1300(d) |
| Reply ISO MFL-SAC — Apr 30 (802) | Lodged with cover; service proofs in FILED section |

---

## Source for the 801 early-lodging cover

- Markdown: `APRIL-24-2026/src/18-EARLY-LODGING-COVER-801-REPLY.md`
- PDF: `APRIL-24-2026/pdf/18-EARLY-LODGING-COVER-801-REPLY-COURT-READY.pdf`  
- Build: `python3 tex/build_apr24_pdfs.py 18-EARLY-LODGING-COVER-801-REPLY`

---

## What is *not* in these packets

Chambers-only or later-file items (oral outlines, bench briefs, blank Notice of Ruling templates, duplicate separate statement, duplicate POS, pre-dated Apr 29 POS for 801, clerk patch) stay in the judge binders or are filed separately per your filing plan.
