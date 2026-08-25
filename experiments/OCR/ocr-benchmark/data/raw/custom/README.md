# Custom OCR Benchmark Dataset (current)

This is the finalized custom dataset for the OCR benchmark. It replaces the
previous source-pool / build-selection approach entirely, and (as of Phase 2)
follows a canonical identity contract.

## Counts (current)

- **Raw samples: 85** physical files (PDF / PNG / JPG) across 9 category
  folders.
- **Ground truth: 85 flat text files**, one per sample:
  `data/ground_truth/custom/<sample_id>.txt` — all manually reviewed;
  `ground_truth.status = verified` in
  `configs/custom_manifest_metadata.yaml`.
- **Manifest samples: 85** (`manifest.json`, generated from the canonical
  identity contract).

Each raw file contributes exactly one benchmark sample ("one benchmark
sample = one PDF page or one standalone image"). All currently shipped PDFs
are single-page extractions except one intentional document-level exception
(below).

> Historical: an earlier dataset generation had 55 physical files /
> 174 logical samples (multi-page PDFs expanded per page) and no ground
> truth. That generation is superseded; its manifest was regenerated.

## Canonical identity contract (FINAL)

For every Custom sample:

```
raw filename stem == GT filename stem == metadata key == manifest sample_id
```

- Matching is **exact and case-sensitive**
  (`Custom_English_scanned_002` stays exactly that).
- The builder **never** prepends an extra `custom_`
  (`custom_custom_english_born_digital_001_p001` remains exactly that),
  never slugifies, never case-folds.
- Duplicate identities are fatal build errors.
- Builder metadata-key mismatches are fatal errors, not warnings.

## Document-level exception

`6. Multi-column/custom_multi_column_004.pdf` is intentionally a
**document-level sample**: one manifest entry with `page: null`. It is not
split into `_pNNN` pages. Multi-page PDFs that are not declared
document-level are rejected by the builder instead of silently generating
new identities.

## Folders are organizational only

The subfolders under this directory exist for human browsing. They are not
used as the source of truth for any semantic label. The digital/scanned
classification rule is based exclusively on the literal sample ID token:
an ID containing `digital` is `*_born_digital`; otherwise it is
`*_scanned`. Mixed Arabic/English samples are valid first-class benchmark
samples and are never excluded.

## Ground truth convention

Flat layout: exactly one UTF-8 `.txt` per sample, named after the canonical
sample ID. No per-sample directories, no `meta.json`. See
`docs/annotation-guidelines.md` (§1) for the current official convention and
the transcription rules used by the verified GT.

## How the manifest is built and checked

- `scripts/build_custom_manifest.py` discovers every `.pdf/.png/.jpg/.jpeg`
  file, assigns the canonical ID (exact filename stem), layers in manual
  metadata from `configs/custom_manifest_metadata.yaml`, validates the
  digital/scanned + category/feature consistency contracts at the auditor
  level, and writes `manifest.json` atomically. It never modifies files in
  this directory; running it repeatedly reproduces a byte-identical manifest.
- `scripts/audit_custom_manifest.py` is a read-only audit of the full
  contract: identity chain (raw/GT/metadata/manifest), GT existence and
  integrity, digital/scanned rule, category↔feature and language↔category
  consistency, counts, and filesystem cross-check.

## Manual labeling workflow

1. Edit `configs/custom_manifest_metadata.yaml` entries keyed by canonical
   sample ID.
2. Re-run `python3 scripts/build_custom_manifest.py`.
3. Run `python3 scripts/audit_custom_manifest.py` — it must pass with zero
   errors.

## What not to do with this dataset

- Do not rename raw samples or GT files — they are the identity anchors.
- Do not add, remove, or replace samples outside a deliberate,
  separate dataset-curation step.
- Do not infer categories from folder names; the digital/scanned rule uses
  only the ID token.
- Do not treat extracted PDF text as ground truth.
- Do not auto-select or auto-balance evaluation subsets.
