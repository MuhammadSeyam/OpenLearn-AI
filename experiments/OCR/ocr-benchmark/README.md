# ocr-benchmark — OpenLearn AI OCR Benchmark

Evaluation harness for choosing the default OCR engine for OpenLearn AI's
Arabic-first ingestion pipeline. Methodology authority:
[`../OCR_BENCHMARKING_HANDBOOK.md`](../OCR_BENCHMARKING_HANDBOOK.md) (Phase 0–8).

The benchmark's deliverable is **not a leaderboard** — it is an evidence-backed
recommendation ("use engine X because A, B, C; fallback Y for case Z; reject W
because license/accuracy/maintenance"), evaluating Arabic, English, and
mixed-language educational documents on more than raw character accuracy
(reading order, Markdown quality, tables, formulas, speed, VRAM, license).

## Current scope (foundation stage, 2026-08-16)

**Structure, configuration, and documentation only.** In place:

- Dataset pilot: 4 documents under `data/raw/custom/` with a roadmap-compatible
  `manifest.json` and per-document provenance records (`docs/provenance.md`).
- Package skeleton `src/ocrbench/` (`core/` + `adapters/`, empty by design).
- Pinned, dependency-free `uv` project (`pyproject.toml` + `uv.lock`).

## What is NOT implemented yet (deliberately)

- ❌ Metrics (CER/WER/normalization) — next task (handbook Phase 1/5)
- ❌ OCR engine adapters — after engine screening (Phase 3/8)
- ❌ Ground truth — dedicated annotation task after the annotation guideline
  exists; `data/ground_truth/custom/` is **empty by design**, nothing fabricated
- ❌ Experiment runner / reports — Phase 7/8
- ❌ Public datasets (KITAB-Bench etc.) — later, after license verification

## Dataset layout

```
data/
├── raw/custom/            # untouched originals (read-only). NEVER edit.
│   ├── manifest.json      # authoritative document metadata (schema below)
│   ├── slides/  scanned/  lectures_digital/
├── ground_truth/custom/   # hand-verified transcriptions (empty until annotation)
└── processed/             # generated (page images, metadata.csv) — gitignored
```

## Provenance policy

Every document's rights status is **UNKNOWN until proven otherwise**
(`docs/provenance.md`). UNKNOWN ≠ permitted: internal benchmark research only,
no redistribution, replacement required before any public dataset release.
`data/raw/` is never mutated in place; generated files go to `data/processed/`.

## Manifest schema (roadmap golden-set compatible)

Per document (`data/raw/custom/manifest.json`):

| field                | meaning                                                        |
|----------------------|----------------------------------------------------------------|
| `doc_id`             | stable id (`OL-C-###` = OpenLearn custom)                      |
| `path`               | path relative to `data/raw/custom/`                            |
| `lang`               | `en` / `ar` / `mixed`                                          |
| `type`               | document type (slide, scanned_page, lecture_slides_pdf, ...)   |
| `scan_quality`       | `digital` / `high` / `medium` / `low` / `unknown`              |
| `has_table`          | bool or null (null = not yet inspected at page level)          |
| `has_formula`        | bool or null                                                   |
| `has_figure`         | bool or null                                                   |
| `expected_word_count`| null until ground truth exists (never estimated from OCR output)|
| `tricky_regions`     | list of strings; empty = none observed yet                     |
| `provenance_status`  | `UNKNOWN` until rights are evidenced                           |

## Environment / reproducibility

```bash
cd experiments/OCR/ocr-benchmark
uv sync          # creates .venv from the pinned uv.lock (no runtime deps yet)
uv run pytest    # package unit tests (none yet — added with metrics task)
```

Runtime dependencies are intentionally empty at this stage. Metric libraries
(`jiwer`, `rapidfuzz`) and OCR engines arrive in later tasks — each OCR engine
gets its **own pinned environment** (handbook Phase 0: per-engine isolation,
framework-bundled CUDA, no global CUDA toolkit). The exploratory PaddleOCR
notebook (`../paddle-test/`) keeps its separate environment and is **not** the
benchmark execution mechanism — it remains an exploration record.

## Evolution (later tasks)

1. Metrics task: `core/text_normalize.py` (Arabic/Latin normalization rules) +
   `core/metrics.py` (raw & normalized CER, WER) + unit tests.
2. Annotation task: guideline → hand-verified ground truth pilot (~6 pages) →
   fill `expected_word_count`, confirm layout flags, page-level PDF inspection.
3. Engine screening (handbook Phase 3): feasibility + smoke tests → survivor
   list → adapters for survivors only.
4. Experiment runner: YAML-configured runs → `results/` (gitignored,
   regenerable) → comparison reports.
5. Grow dataset toward the roadmap's 20-PDF golden set (priority gaps: mixed
   Arabic/English, tables, formulas, low-quality scans).
