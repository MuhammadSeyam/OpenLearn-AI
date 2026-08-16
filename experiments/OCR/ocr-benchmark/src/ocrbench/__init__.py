"""ocrbench — OpenLearn AI OCR benchmark package.

Foundation stage: structure and documentation only.
- core/ will hold engine-independent evaluation logic (metrics, dataset loading,
  text normalization). Nothing implemented yet.
- adapters/ will hold per-engine wrappers implementing a shared BaseOCREngine
  interface (see ../OCR_BENCHMARKING_HANDBOOK.md Phase 2). Nothing implemented yet.

Rule (handbook Phase 2): core/ must never import anything engine-specific, and
engine-specific quirks must never live outside adapters/.
"""
