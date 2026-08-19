# Decision Log

Short context/decision records for the benchmark (ADR-style; the repo-level ADR
directory `docs/architecture/ADR/` is reserved for whole-project decisions).

## 0001 — Benchmark foundation scope (2026-08-16)

- **Context:** Week 2 of the 44-week plan; the OCR benchmark needs a
  reproducible home. The repo already contains 4 ad-hoc sample documents and an
  exploratory PaddleOCR notebook with hardcoded absolute paths.
- **Decision:**
  1. Benchmark lives at `experiments/OCR/ocr-benchmark/` following the OCR
     Benchmarking Handbook Phase 2 layout (adapter/core separation, raw vs.
     ground-truth vs. processed data).
  2. Sample documents are **copied** into `data/raw/custom/`, not moved —
     original paths under `experiments/OCR/benchmarks/` remain valid so the
     existing notebook and any external references keep working. Copies
     verified byte-identical (SHA-256 in `docs/provenance.md`).
  3. Foundation stage contains **structure, configuration, and documentation
     only** — no metrics, no adapters, no ground truth, no scores. Those are
     separate tasks so each lands reviewably.
  4. Manifest uses the roadmap golden-set schema (doc_id, path, lang, type,
     scan_quality, has_table, has_formula, has_figure, expected_word_count,
     tricky_regions) plus optional provenance fields; `null` is used wherever
     a value cannot be honestly established yet.
  5. Dependency environment: `uv`-managed, runtime deps empty at this stage;
     OCR engines each get their own pinned environment later (handbook
     Phase 0). PaddleOCR is NOT a dependency of this package — the existing
     exploratory notebook keeps its own environment.
- **Consequences:** two copies of 4 sample files exist temporarily (~1.8 MB
  duplication) — acceptable until the originals are retired deliberately.
  Untangling "which copy is canonical" is solved by pointing at this
  benchmark's manifest as the single source of truth for dataset metadata.
