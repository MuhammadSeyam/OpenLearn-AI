# Custom Raw Dataset (`data/raw/custom/`)

Untouched original documents for the OpenLearn AI OCR benchmark. **Never edit,
re-export, or write generated files here** (handbook Phase 2 rule: `data/raw/` is
read-only by convention).

## Contents

Pilot batch of 4 documents, copied byte-identical from
[`experiments/OCR/benchmarks/`](../../../../benchmarks/) on 2026-08-16 (originals
preserved there; see `docs/provenance.md` for checksums):

| doc_id    | file                                   | lang | type                | origin                     |
|-----------|----------------------------------------|------|---------------------|----------------------------|
| OL-C-001  | `slides/1.png`                         | en   | slide (digital)     | pre-existing repo sample   |
| OL-C-002  | `slides/2.png`                         | en   | slide + figure      | pre-existing repo sample   |
| OL-C-003  | `scanned/ar.png`                       | ar   | scanned page        | pre-existing repo sample   |
| OL-C-004  | `lectures_digital/Data+Structre+lect1.pdf` | en | lecture PDF (24pp) | pre-existing repo sample   |

Authoritative metadata: [`manifest.json`](manifest.json) (roadmap-compatible schema).

## Source / License / Use

- **Source:** all four files pre-date this benchmark scaffold; their original
  provenance (who created them, under what terms) is **UNKNOWN**.
- **License:** **UNKNOWN** — no redistribution rights are granted or assumed.
  Treat as internal-research-only until each entry's `provenance_status` in the
  manifest is resolved (see `docs/provenance.md`).
- **Use:** internal OCR benchmark evaluation for the OpenLearn AI graduation
  project only. Not for redistribution, and must be removed/replaced before any
  public dataset release if rights cannot be confirmed.
