# Provenance Record

One entry per document in `data/raw/custom/`. Required by the repo's dataset
rules (`docs/design/DeveloperGuide.md`: every dataset subfolder documents
source/license/use) and by handbook Phase 4 (record source, version, date for
everything used in the benchmark).

**Policy:** `provenance_status` is `UNKNOWN` until a human records evidence of
rights (permission, open license, or ownership). UNKNOWN means *unknown*, not
"permitted". Documents with UNKNOWN status may be used for internal benchmark
research only, never redistributed, and must be replaced before any public
release of this dataset.

---

## OL-C-001 — `slides/1.png`

- **SHA-256:** `d14c72b9758d949bc07e702ee4b5d1426e25f36e59d079e1a13c08bd4a785546`
- **Size:** 180,479 bytes
- **How obtained:** already present in repo at `experiments/OCR/benchmarks/1.png`
  before this scaffold (first appears with the OCR experiments; author/date of
  original addition not recorded in git history — predates benchmark work).
- **Content:** born-digital English presentation slide (bullet list).
- **Rights status:** **UNKNOWN** — original creator and license unidentified.

## OL-C-002 — `slides/2.png`

- **SHA-256:** `f7e66c449c1e52470df515fb35f454524856a2b032ca74eff0612835c903f7e7`
- **Size:** 256,473 bytes
- **How obtained:** already present in repo at `experiments/OCR/benchmarks/2.png`
  (same as OL-C-001). Never used in any committed notebook run so far.
- **Content:** born-digital English slide with a labeled neuron diagram.
- **Rights status:** **UNKNOWN**.

## OL-C-003 — `scanned/ar.png`

- **SHA-256:** `408f776d60bb5edbd326b495d6f67699f5a52b4853aeebf3b4f3e6ca4d9092fe`
- **Size:** 137,929 bytes
- **How obtained:** already present in repo at `experiments/OCR/benchmarks/ar.png`
  (same as OL-C-001).
- **Content:** scanned Arabic page with diacritics (textbook-style), RTL.
- **Rights status:** **UNKNOWN** — the underlying work may be a copyrighted
  textbook page; needs identification before any external use.

## OL-C-004 — `lectures_digital/Data+Structre+lect1.pdf`

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

---

## Change log

- 2026-08-16 — Record created with the four pilot documents (copies of the
  pre-existing `experiments/OCR/benchmarks/` samples; originals preserved).
