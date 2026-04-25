# April 14, 2026: clerk counter filing (master checklist)

**Purpose:** One place to see what must be **finished**, **printed**, and **handed to the civil filing window** (San Francisco Superior Court), plus immediate follow-up (ex parte routing, proof of service, courtesy copies).

**Primary case:** **Rosario v. CSAA Insurance Exchange**, **CGC-25-631802**.

**Print and file three separate packets (three collated stacks):**

| # | Packet | Role |
|---|--------|------|
| **1** | **Leave + proposed SAC** | Motion for leave to file Second Amended Complaint, memorandum, declaration, RJN, proposed order, **proposed SAC**, bench brief, exhibit appendix. |
| **2** | **Ex parte + Anti-SLAPP opposition** | Oversized-memorandum ex parte; shorten-time ex parte; Anti-SLAPP opposition volume containing the principal memorandum, separate rebuttal memorandum, and supporting declaration; evidentiary objections; **same** exhibit appendix as Packet 1. |
| **3** | **Opposition to demurrer (standalone)** | Full demurrer opposition on its own: memorandum, declaration (**Proposed SAC** as Exhibit A), proposed order, proof of service (optional notice/RJN). **Same operative theory and Exhibit Appendix labeling** as Packets 1 and 2 (see **802/07** checklist); the **Exhibit Appendix PDF** is filed with Packets 1 and 2, not required inside the default RD collate unless the clerk directs. |

**Filing-ready vs clerk-packet PDFs (802 island build):** `build_all_pdfs.sh` produces clean consolidated PDFs for submission (`802-PLAINTIFF-MOTION-LEAVE-PROPOSED-SAC-CONSOLIDATED.pdf`, `803-PLAINTIFF-ANTI-SLAPP-OPPOSITION-FULL-CONSOLIDATED.pdf`, `RD-PLAINTIFF-DEMURRER-OPPOSITION-CONSOLIDATED.pdf`). It also emits `*-CLERK-PACKET.pdf` variants under the build `OUT/` folders: same documents in the same order, each preceded by a one-page non-pleading clerk routing sheet. Prefer **filing-ready** PDFs for EFSP uploads unless the clerk asks for the routing version. Segment map: [`RESPONSE-MASTER-801-802/802/RESPONSE-PACKET-HUB/CLERK-PACKET-ROUTING-GROUPING-MAP.md`](RESPONSE-MASTER-801-802/802/RESPONSE-PACKET-HUB/CLERK-PACKET-ROUTING-GROUPING-MAP.md).

**Target date:** Tuesday, **April 14, 2026** (confirm the court is open: [SF Superior holidays](https://sf.courts.ca.gov/general-info/holidays)).

**Deeper detail:** Exhibit appendix policy, full rebuild commands, Section 10 information table, and extended timelines live in [`DEFENSE/APR-14-COURT/INSTRUCT.FILING.md`](DEFENSE/APR-14-COURT/INSTRUCT.FILING.md). **Shared operative theory** (gravamen, denial letter as evidence, later proceedings as context, **790.03** disclaimer, SAC additions) is duplicated verbatim in the three lead memoranda: [`DEFENSE/802/02-MEMORANDUM-OF-POINTS-AND-AUTHORITIES.md`](DEFENSE/802/02-MEMORANDUM-OF-POINTS-AND-AUTHORITIES.md), [`DEFENSE/803-OPPOSITION-PACKET/803-02-OPPOSITION-TO-ANTI-SLAPP-AND-DEMURRER-V2.md`](DEFENSE/803-OPPOSITION-PACKET/803-02-OPPOSITION-TO-ANTI-SLAPP-AND-DEMURRER-V2.md), [`RESPONSE-DEMURRER/01-PLAINTIFFS-MEMORANDUM-OPPOSITION-TO-DEMURRER.md`](RESPONSE-DEMURRER/01-PLAINTIFFS-MEMORANDUM-OPPOSITION-TO-DEMURRER.md); canonical checklist: [`DEFENSE/802/07-SAC-EXHIBIT-AND-CITATION-CHECKLIST.md`](DEFENSE/802/07-SAC-EXHIBIT-AND-CITATION-CHECKLIST.md).

**Disclaimer:** This is a workflow checklist from your litigation repo. It is **not** legal advice. Clerk practice, fees, mandatory e-filing, and local rules change; **the court’s posted materials and clerk instructions control**.

---

## Three packets: files to print (paths and links)

Use these **repository-relative** links in your editor or on GitHub after push (`blob/main/` + same path). **Authoritative build outputs** are under `DEFENSE/802/OUT/`, `DEFENSE/803-OPPOSITION-PACKET/OUT/`, and `RESPONSE-DEMURRER/OUT/`. Filing-day copies of the 802/803 consolidates may also exist under `DEFENSE/APR-14-COURT/`.

### Packet 1: leave + SAC + bench brief + appendix

| Print this PDF | Path (clickable in repo) |
|----------------|--------------------------|
| **Primary build output** | [`802-PLAINTIFF-MOTION-LEAVE-PROPOSED-SAC-CONSOLIDATED.pdf`](DEFENSE/802/OUT/802-PLAINTIFF-MOTION-LEAVE-PROPOSED-SAC-CONSOLIDATED.pdf) |
| **Filing copy (if present)** | [`802-PLAINTIFF-MOTION-LEAVE-PROPOSED-SAC-CONSOLIDATED.pdf`](DEFENSE/APR-14-COURT/802-PLAINTIFF-MOTION-LEAVE-PROPOSED-SAC-CONSOLIDATED.pdf) |

**Source markdown / build:** `DEFENSE/802/` motion set; rebuild via `DEFENSE/802/court-pdfs/` scripts (see `INSTRUCT.FILING.md` Section 7).

### Packet 2: oversized ex parte + shorten-time ex parte + Anti-SLAPP opposition + objections + appendix

| Print this PDF | Path (clickable in repo) |
|----------------|--------------------------|
| **Primary build output** | [`803-PLAINTIFF-ANTI-SLAPP-OPPOSITION-FULL-CONSOLIDATED.pdf`](DEFENSE/803-OPPOSITION-PACKET/OUT/803-PLAINTIFF-ANTI-SLAPP-OPPOSITION-FULL-CONSOLIDATED.pdf) |
| **Filing copy (same merge, APR-14 folder name)** | [`803-CONSOLIDATED-FULL-OPPOSITION-PACKET.pdf`](DEFENSE/APR-14-COURT/803-CONSOLIDATED-FULL-OPPOSITION-PACKET.pdf) |

**Source markdown / build notes:** the 803 build now produces a principal Anti-SLAPP memorandum, a separate rebuttal memorandum, and a declaration, then merges those into `803-02-OPPOSITION-PACKET-COMBINED.pdf` before the final packet merge. Rebuild via `RESPONSE-MASTER-801-802/802/build/803-opposition/court-pdfs/` or the canonical island `build_all_pdfs.sh`.

**Archived singles if the clerk requires split uploads:** under [`DEFENSE/APR-14-COURT/_archive-individuals-and-partial-merges/`](DEFENSE/APR-14-COURT/_archive-individuals-and-partial-merges/) (for example [`803-01-EX-PARTE-APPLICATION.pdf`](DEFENSE/APR-14-COURT/_archive-individuals-and-partial-merges/803-01-EX-PARTE-APPLICATION.pdf), [`803-02-OPPOSITION-PACKET-COMBINED.pdf`](DEFENSE/APR-14-COURT/_archive-individuals-and-partial-merges/803-02-OPPOSITION-PACKET-COMBINED.pdf), [`803-03-EVIDENTIARY-OBJECTIONS.pdf`](DEFENSE/APR-14-COURT/_archive-individuals-and-partial-merges/803-03-EVIDENTIARY-OBJECTIONS.pdf)).

### Packet 3: opposition to demurrer only (standalone)

**Option A (one print job):** print one merged PDF end to end. Prefer **[`RD-DEMURRER-OPPOSITION-PACKET-CORE.pdf`](RESPONSE-DEMURRER/OUT/RD-DEMURRER-OPPOSITION-PACKET-CORE.pdf)** (memorandum, declaration, proposed order, proof of service only) when optional notice and RJN are not in this stack. Use **[`RD-PLAINTIFF-DEMURRER-OPPOSITION-CONSOLIDATED.pdf`](RESPONSE-DEMURRER/OUT/RD-PLAINTIFF-DEMURRER-OPPOSITION-CONSOLIDATED.pdf)** for a full merge including optional notice and RJN, or for internal review.

| Print this PDF | Path (clickable in repo) |
|----------------|--------------------------|
| **CORE consolidated** (default single stack) | [`RD-DEMURRER-OPPOSITION-PACKET-CORE.pdf`](RESPONSE-DEMURRER/OUT/RD-DEMURRER-OPPOSITION-PACKET-CORE.pdf) |
| **Full consolidated** (optional 06/07 included) | [`RD-PLAINTIFF-DEMURRER-OPPOSITION-CONSOLIDATED.pdf`](RESPONSE-DEMURRER/OUT/RD-PLAINTIFF-DEMURRER-OPPOSITION-CONSOLIDATED.pdf) |

**Option B (separate lead documents, typical for clerk / EFSP):** print each file in this order, then collate.

| # | Document | Path (clickable in repo) |
|---|----------|--------------------------|
| 1 | Memorandum in opposition to demurrer | [`RD-01-MEMORANDUM-OPPOSITION-DEMURRER.pdf`](RESPONSE-DEMURRER/OUT/RD-01-MEMORANDUM-OPPOSITION-DEMURRER.pdf) |
| 2 | Declaration in support | [`RD-04-DECLARATION-DEMURRER.pdf`](RESPONSE-DEMURRER/OUT/RD-04-DECLARATION-DEMURRER.pdf) |
| 3 | Proposed order | [`RD-05-PROPOSED-ORDER-DEMURRER.pdf`](RESPONSE-DEMURRER/OUT/RD-05-PROPOSED-ORDER-DEMURRER.pdf) |
| 4 | Proof of service | [`RD-08-PROOF-OF-SERVICE.pdf`](RESPONSE-DEMURRER/OUT/RD-08-PROOF-OF-SERVICE.pdf) |

**Optional (only if filed):**

| Document | Path (clickable in repo) |
|----------|--------------------------|
| Notice of filing | [`RD-06-NOTICE-FILING-OPTIONAL.pdf`](RESPONSE-DEMURRER/OUT/RD-06-NOTICE-FILING-OPTIONAL.pdf) |
| Request for judicial notice | [`RD-07-REQUEST-JUDICIAL-NOTICE-OPTIONAL.pdf`](RESPONSE-DEMURRER/OUT/RD-07-REQUEST-JUDICIAL-NOTICE-OPTIONAL.pdf) |

**Rebuild Packet 3 PDFs:** `cd RESPONSE-DEMURRER/court-pdfs && python3 build_response_demurrer_pdfs.py`

**Cross-check:** [`RESPONSE-DEMURRER/09-FILING-CHECKLIST-DEMURRER-OPPOSITION.md`](RESPONSE-DEMURRER/09-FILING-CHECKLIST-DEMURRER-OPPOSITION.md)

---

## 0. Before you rely on walk-in filing (mandatory e-filing check)

- [ ] Confirm on [Civil Clerk’s Office](https://sf.courts.ca.gov/divisions/civil-division/civil-clerks-office) and current local rules whether **CGC-25-631802** may be **walk-in filed** at **Room 103** for these document types, or must go through the **approved e-filing provider** (and any **in pro per** exceptions).
- [ ] If the clerk redirects you to e-filing, complete that step and keep **confirmation numbers** before or instead of the window steps below.

---

## 1. What to complete before you print (all three packets)

### Packet 1: leave + SAC

| Task | Done |
|------|------|
| PDF current: prefer [`DEFENSE/802/OUT/802-PLAINTIFF-MOTION-LEAVE-PROPOSED-SAC-CONSOLIDATED.pdf`](DEFENSE/802/OUT/802-PLAINTIFF-MOTION-LEAVE-PROPOSED-SAC-CONSOLIDATED.pdf) or filing copy [`DEFENSE/APR-14-COURT/802-PLAINTIFF-MOTION-LEAVE-PROPOSED-SAC-CONSOLIDATED.pdf`](DEFENSE/APR-14-COURT/802-PLAINTIFF-MOTION-LEAVE-PROPOSED-SAC-CONSOLIDATED.pdf) | [ ] |
| Open PDF; scroll to **last page**; confirm **no** accidental blank or truncated end | [ ] |
| **Caption** and case number **CGC-25-631802** on first pages | [ ] |
| Hearing / reservation lines: if rules require **real** dates (not `[TBD]`), update `DEFENSE/802/court-pdfs/build_802_court_pdfs.py`, rebuild, re-copy | [ ] |
| If exhibit manifest changed: run `build_802_exhibit_appendix.py` before 802 merges (`INSTRUCT.FILING.md` Section 7) | [ ] |

**Packet 1 contains (in order):** notice, memorandum, declaration, RJN, proposed order, **proposed SAC**, **shared exhibit appendix**, then the **master final bench brief** appended once at the end. The current island merge no longer inserts `802-12` as a separate segment in this consolidated packet.

### Packet 2: oversized ex parte + shorten-time ex parte + Anti-SLAPP opposition + objections + appendix

| Task | Done |
|------|------|
| PDF current: [`DEFENSE/803-OPPOSITION-PACKET/OUT/803-PLAINTIFF-ANTI-SLAPP-OPPOSITION-FULL-CONSOLIDATED.pdf`](DEFENSE/803-OPPOSITION-PACKET/OUT/803-PLAINTIFF-ANTI-SLAPP-OPPOSITION-FULL-CONSOLIDATED.pdf) or [`DEFENSE/APR-14-COURT/803-CONSOLIDATED-FULL-OPPOSITION-PACKET.pdf`](DEFENSE/APR-14-COURT/803-CONSOLIDATED-FULL-OPPOSITION-PACKET.pdf) | [ ] |
| Open PDF; scroll to **last page**; confirm **no** accidental blank or truncated end | [ ] |
| **Caption** and case number **CGC-25-631802** on first pages | [ ] |
| **Ex parte** block complete: relief, good cause, meet-and-confer, notice to opponent, proposed order (Section 5) | [ ] |
| Hearing / reservation: update `DEFENSE/803-OPPOSITION-PACKET/court-pdfs/build_803_court_pdfs.py` if needed | [ ] |

**Packet 2 contains (in order):** oversized-memorandum ex parte; shorten-time ex parte; combined Anti-SLAPP opposition packet containing the principal memorandum, separate rebuttal memorandum, and supporting declaration; evidentiary objections; **same** exhibit appendix as Packet 1.

### Packet 3: standalone demurrer opposition

| Task | Done |
|------|------|
| PDFs current: [`RD-DEMURRER-OPPOSITION-PACKET-CORE.pdf`](RESPONSE-DEMURRER/OUT/RD-DEMURRER-OPPOSITION-PACKET-CORE.pdf) (subset without optional notice/RJN) or [`RD-PLAINTIFF-DEMURRER-OPPOSITION-CONSOLIDATED.pdf`](RESPONSE-DEMURRER/OUT/RD-PLAINTIFF-DEMURRER-OPPOSITION-CONSOLIDATED.pdf) (current filing-ready merge with `803-00`, `803-01`, then RD-01 through RD-08) **or** separate RD-01, RD-04, RD-05, RD-08 (and optional RD-06, RD-07) | [ ] |
| Spot-check last page of each printed PDF | [ ] |
| **CGC-25-631802** on captions; hearing date / department match **current** notice and calendar | [ ] |
| Meet-and-confer (declaration) matches memorandum Section II.B | [ ] |
| CRC **3.1113** length / word count / TOC pinpoints addressed per [`09-FILING-CHECKLIST-DEMURRER-OPPOSITION.md`](RESPONSE-DEMURRER/09-FILING-CHECKLIST-DEMURRER-OPPOSITION.md) | [ ] |

### Strategic order at the clerk window (register logic)

**Recommended handoff order:**

1. **Packet 1** first (**leave + proposed SAC**) so the amendment hits the register before oppositions.
2. **Packet 2** second (**oversized ex parte + shorten-time ex parte + Anti-SLAPP opposition**).
3. **Packet 3** third (**standalone demurrer opposition**).

Ask the clerk whether these are **one** transaction, **three** fee events, or must be **split** for data entry.

---

## 2. Print and bind (three stacks at clerk counter)

| Task | Done |
|------|------|
| Print **Packet 1** full collated set(s) from [`802-PLAINTIFF-MOTION-LEAVE-PROPOSED-SAC-CONSOLIDATED.pdf`](DEFENSE/802/OUT/802-PLAINTIFF-MOTION-LEAVE-PROPOSED-SAC-CONSOLIDATED.pdf) (or APR-14-COURT copy) | [ ] |
| Print **Packet 2** full collated set(s) from [`803-PLAINTIFF-ANTI-SLAPP-OPPOSITION-FULL-CONSOLIDATED.pdf`](DEFENSE/803-OPPOSITION-PACKET/OUT/803-PLAINTIFF-ANTI-SLAPP-OPPOSITION-FULL-CONSOLIDATED.pdf) (or [`803-CONSOLIDATED-FULL-OPPOSITION-PACKET.pdf`](DEFENSE/APR-14-COURT/803-CONSOLIDATED-FULL-OPPOSITION-PACKET.pdf) if that legacy copy is still current) | [ ] |
| Print **Packet 3** from [`RD-DEMURRER-OPPOSITION-PACKET-CORE.pdf`](RESPONSE-DEMURRER/OUT/RD-DEMURRER-OPPOSITION-PACKET-CORE.pdf) or [`RD-PLAINTIFF-DEMURRER-OPPOSITION-CONSOLIDATED.pdf`](RESPONSE-DEMURRER/OUT/RD-PLAINTIFF-DEMURRER-OPPOSITION-CONSOLIDATED.pdf) **or** collate RD-01, RD-04, RD-05, RD-08 (plus optional RD-06, RD-07) | [ ] |
| **Binding:** staple or binder clip **per packet** (three separate physical volumes) | [ ] |
| **Copy count:** often **two** full sets per packet (or **one original + copies** per clerk); ask at window | [ ] |
| Optional **tabs** flat enough for scanning | [ ] |
| **Courtesy** sets for department / judge if required | [ ] |

---

## 3. What to bring to the courthouse (bag checklist)

- [ ] **Packet 1** printed set(s) (leave + SAC)
- [ ] **Packet 2** printed set(s) (oversized ex parte + shorten-time ex parte + Anti-SLAPP opposition)
- [ ] **Packet 3** printed set(s) (standalone demurrer opposition)
- [ ] Photo ID
- [ ] **Payment** for filing fees (verify morning-of on official fee schedule)
- [ ] **Proof of service** forms for **each** filing event the clerk identifies (often **completed after** stamping)
- [ ] Self-addressed stamped envelopes **only if** clerk offers mail-back conformed copies
- [ ] Phone or laptop with all **three** PDFs offline; **USB** backup
- [ ] Notepad for receipt numbers, clerk names, routing instructions

---

## 4. Where and when (civil clerk window)

| Item | Detail |
|------|--------|
| Building | Civic Center Courthouse, **400 McAllister Street**, San Francisco, CA **94102** |
| Civil filings | **Room 103** (confirm window on arrival) |
| Civil clerk phone (per court site) | **(415) 551-3808** |
| General | **(415) 551-4000** |
| Typical hours | **8:30 a.m. to 4:00 p.m.**; **closed noon to 1:00 p.m.** lunch |

**Tip:** Arrive **well before noon** or plan for **after 1:00 p.m.** with time to finish before 4:00 p.m. Allow extra time for **security** screening.

---

## 5. At the clerk window: short script and order

**When called:**

1. State case: **Rosario v. CSAA Insurance Exchange**, **CGC-25-631802**.
2. Say: “I am filing **three** submissions today. **First**, plaintiff’s **motion for leave to file a second amended complaint** with the **proposed second amended complaint** and related papers (**Packet 1**). **Second**, plaintiff’s **oversized-memorandum ex parte**, **shorten-time ex parte**, and **opposition to defendant’s special motion to strike (Anti-SLAPP)**, including the **rebuttal memorandum**, **declaration**, and **evidentiary objections** (**Packet 2**). **Third**, plaintiff’s **separate opposition to defendant’s demurrer** with **declaration**, **proposed order**, and **proof of service** (**Packet 3**).”
3. Hand **Packet 1**, then **Packet 2**, then **Packet 3**; ask **one vs multiple** filing events and fees.
4. **Pay**; keep **all receipts**; note register identifiers.
5. Obtain **file-stamped** copies (same day vs mail-back).
6. Ask **ex parte** routing; whether **any** paper must be **e-filed** as well.
7. Confirm **proof of service** timing for **each** packet or combined event.

**Ex parte extra questions at Room 103** (write answers down):

- How is the **first document in Packet 2** coded; **separate fee** from the rest of that volume?
- May Packet 2 stay **one** PDF or must you **split** (use [`_archive-individuals-and-partial-merges/`](DEFENSE/APR-14-COURT/_archive-individuals-and-partial-merges/) or `DEFENSE/803-OPPOSITION-PACKET/OUT/`)?
- **Who** hears civil **ex parte**; **phone**, **room**, **hours**.
- **When** must POS on ex parte be **filed** relative to department ex parte.
- How many **stamped** copies for **department** ex parte.

**Important:** Clerk filing **does not** by itself calendar ex parte. Plan **department or presiding** steps per current local rules.

---

## 6. Before you leave the building

- [ ] Photograph or scan **receipts** and **stamped first pages** for **each** filing event
- [ ] Complete **proof of service** and **serve** as soon as you have conformed copies
- [ ] File POS if your procedure requires it after service
- [ ] Deliver **courtesy copies** if required

---

## 7. If the clerk rejects a combined PDF

| Problem | Action |
|---------|--------|
| Packet 2 combined PDF not accepted | Split using [`DEFENSE/APR-14-COURT/_archive-individuals-and-partial-merges/`](DEFENSE/APR-14-COURT/_archive-individuals-and-partial-merges/) or singles under [`DEFENSE/803-OPPOSITION-PACKET/OUT/`](DEFENSE/803-OPPOSITION-PACKET/OUT/). Keep **Packet 1, then Packet 2 parts, then Packet 3** in sensible order. |
| Packet 3 consolidated not accepted | File [`RD-01`](RESPONSE-DEMURRER/OUT/RD-01-MEMORANDUM-OPPOSITION-DEMURRER.pdf), [`RD-04`](RESPONSE-DEMURRER/OUT/RD-04-DECLARATION-DEMURRER.pdf), [`RD-05`](RESPONSE-DEMURRER/OUT/RD-05-PROPOSED-ORDER-DEMURRER.pdf), [`RD-08`](RESPONSE-DEMURRER/OUT/RD-08-PROOF-OF-SERVICE.pdf) as separate PDFs. |
| Mandatory e-filing only | Use approved EFSP; keep confirmation numbers. |
| Wrong fee | Obtain correct payment; return same day before close if possible. |

---

## 8. Related case: CGC-25-631801 (leave + SAC only, different inventory)

If you also file **Rosario v. Abdelhalim** under **CGC-25-631801**, that track uses **`DEFENSE/801/`** builds, not the 802/803 packets above. See:

- [`DEFENSE/801/APR-14-2026-FILING/FILE-THESE-PDFS-ONLY/README.md`](DEFENSE/801/APR-14-2026-FILING/FILE-THESE-PDFS-ONLY/README.md)
- [`DEFENSE/801/APR-14-2026-FILING/FILING-INVENTORY.md`](DEFENSE/801/APR-14-2026-FILING/FILING-INVENTORY.md)

**Do not mix case numbers** on captions or proofs.

---

## 9. Same-day final tick (walk out the door)

- [ ] Court open; no emergency closure
- [ ] All **three** PDF stacks spot-checked end-to-end
- [ ] **Three** separate bound packets ready (not one merged printout unless clerk agrees)
- [ ] **CGC-25-631802** on visible captions
- [ ] Ex parte and hearing blanks resolved **or** follow-up noted with clerk
- [ ] Fees and payment method ready
- [ ] Plan for POS, service, and courtesy copies recorded
