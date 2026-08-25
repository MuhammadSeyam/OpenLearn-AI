# Provenance Record

Provenance for documents in `data/raw/custom/`. Required by the repo's dataset
rules (every dataset subfolder documents source/license/use) and by handbook
Phase 4 (record source, version, date for everything used in the benchmark).

**Coverage status:** the four records below are **HISTORICAL** provenance
entries from the original 4-document pilot. They cover **4 of the 85 current
samples at most** — and even that mapping is only partially established
(see lineage evidence below). **Provenance for the remaining samples has NOT
been backfilled; no claim of complete 85/85 provenance coverage is made.**

**Policy:** `provenance_status` remains `UNKNOWN` until a human records
evidence of rights (permission, open license, or ownership). UNKNOWN means
*unknown*, not "permitted". Documents with UNKNOWN status may be used for
internal benchmark research only, never redistributed, and must be replaced
before any public release of this dataset.

**Known lineage evidence (from Phase 1 SHA-256 matching):**
- `custom_figures_diagrams_001.png` (SHA-256 `f7e66c44…c903f7e7`) is
  byte-identical to historical record OL-C-002 (`slides/2.png`) → OL-C-002's
  provenance entry applies to this current sample.
- `Custom_English_scanned_002.jpg` (SHA-256 `46a6b222…b71d1c2c7`) was
  byte-identical to the former `custom_noisy_low_quality_001.jpg` of the
  superseded dataset generation (same image reused across two old
  categories); its origin remains UNKNOWN.

---

## HISTORICAL — OL-C-001 — `slides/1.png`

- **SHA-256:** `d14c72b9758d949bc07e702ee4b5d1426e25f36e59d079e1a13c08bd4a785546`
- **Size:** 180,479 bytes
- **How obtained:** already present in repo at `experiments/OCR/benchmarks/1.png`
  before this scaffold (first appears with the OCR experiments; author/date of
  original addition not recorded in git history — predates benchmark work).
- **Content:** born-digital English presentation slide (bullet list).
- **Rights status:** **UNKNOWN** — original creator and license unidentified.
- **Current-sample mapping:** not established.

## HISTORICAL — OL-C-002 — `slides/2.png`

- **SHA-256:** `f7e66c449c1e52470df515fb35f454524856a2b032ca74eff0612835c903f7e7`
- **Size:** 256,473 bytes
- **How obtained:** already present in repo at `experiments/OCR/benchmarks/2.png`
  (same as OL-C-001). Never used in any committed notebook run so far.
- **Content:** born-digital English slide with a labeled neuron diagram.
- **Rights status:** **UNKNOWN**.
- **Current-sample mapping:** byte-identical to
  `9. Figures-diagrams/custom_figures_diagrams_001.png` (confirmed Phase 1).

## HISTORICAL — OL-C-003 — `scanned/ar.png`

- **SHA-256:** `408f776d60bb5edbd326b495d6f67699f5a52b4853aeebf3b4f3e6ca4d9092fe`
- **Size:** 137,929 bytes
- **How obtained:** already present in repo at `experiments/OCR/benchmarks/ar.png`
  (same as OL-C-001).
- **Content:** scanned Arabic page with diacritics (textbook-style), RTL.
- **Rights status:** **UNKNOWN** — the underlying work may be a copyrighted
  textbook page; needs identification before any external use.
- **Current-sample mapping:** not established.

## HISTORICAL — OL-C-004 — `lectures_digital/Data+Structre+lect1.pdf`

- **SHA-256:** `1b327444c97d207c4bb934cc1d486002b1e89b3bad0c896c274cbbeeae9510de`
- **Size:** 1,213,766 bytes (24 pages, 720x540pt, PowerPoint export — pdfinfo)
- **How obtained:** already present in repo at
  `experiments/OCR/benchmarks/Data+Structre+lect1.pdf` (same as OL-C-001).
- **Content:** "Data Structures" lecture 1, Kafrelsheikh University faculty
  material attributed on the cover page to Dr. Basma M. Hassan, academic year
  2024/2025. PDF metadata Author field reads "MOBA Loved Family" (likely the
  re-uploader, not the author).
- **Rights status:** **UNKNOWN** — identifiable author and institution on the
  cover page. **Action item:** request the lecturer's permission (or replace
  the document) before treating this file as anything other than internal
  research. Hosting a named lecturer's material in a public repo is an
  unresolved risk flagged to the team.
- **Current-sample mapping:** not established (the original multi-page PDF no
  longer exists; it was superseded by per-page extracts whose provenance is
  inherited only if byte-level lineage is proven).

---

## Backlog

- Backfill provenance for the remaining ~81 current samples (source, license,
  date) or explicitly mark them UNKNOWN per policy.
- Establish byte-level lineage (SHA-256) between the historical pilot files
  and current page-level extracts where possible.

## Change log

- 2026-08-16 — Record created with the four pilot documents (copies of the
  pre-existing `experiments/OCR/benchmarks/` samples; originals preserved).
- Phase 3 — Records marked HISTORICAL (cover ≤4/85 samples). Lineage evidence
  documented. No fabricated provenance added; backfill tracked in Backlog.
