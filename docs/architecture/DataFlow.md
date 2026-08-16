# Data Flow

> Authority note: the authoritative pipeline design is the
> [Technical Specification](../design/OpenLearn_AI_v4_Technical_Specification.md).
> This page tracks the one data flow currently under active engineering:
> document ingestion for OCR evaluation.

## Ingestion pipeline (design; first stage under evaluation)

```
Document (PDF / image / scan)
   │
   ├─ has embedded text? ── yes ──→ text extraction (parsing stage, later)
   │                                  │
   └─ scanned / image ────→ OCR engine          ← CURRENT FOCUS
                             │
                             ▼
                     Structured text (Markdown target)
                             │
                             ▼
                    Chunking + metadata
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
      Knowledge graph (later)      Embeddings → vector search (later)
```

(Original sketch: [`docs/research/OCR.md`](../research/OCR.md).)

## What exists today

- `experiments/OCR/ocr-benchmark/` — the evaluation harness for the OCR stage:
  4-document pilot dataset with provenance, roadmap-compatible manifest,
  pinned environment. Metrics, ground truth, and engine adapters are the next
  tasks (sequencing per ADR-0003: ground truth → metrics → one engine →
  validate harness → more engines).
- `experiments/OCR/paddle-test/` — exploratory PaddleOCR notebook
  (English/Arabic/PDF smoke evidence). Not part of the product pipeline.

## Data boundary rules

- Nothing under `experiments/` is imported by `backend/` or `frontend/`.
- Benchmark data (`ocr-benchmark/data/`) is evaluation-only. Demo data for the
  v0.4 MVP will live separately (`tests/data/demo_pdf/` per the execution
  plan); production ingestion data will live in the platform's storage. These
  three must never mix without an explicit ADR.
