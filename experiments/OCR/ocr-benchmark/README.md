OpenLearn-AI OCR Benchmark

Purpose
-------
Evaluate candidate OCR/document-understanding engines and select a
practical default for the OpenLearn-AI ingestion pipeline.

Current objective
-----------------
Finish OCR/model evaluation and freeze a working default.

Future context
--------------
The selected component will eventually participate in a broader pipeline
including native document parsing, quality-based routing, unified document
representation, embeddings, vector/graph retrieval, and citations.

Those components are NOT implemented by this benchmark yet.

Datasets
--------
MISRAJ       → text/OCR accuracy
BCE          → layout/structure
Custom       → OpenLearn-specific difficult cases
              with verified GT used for quantitative evaluation

Candidate families
------------------
Specialized document parsers:
    PaddleOCR-VL
    MinerU2.5-Pro
    Baseer

General VLM:
    Qwen2.5-VL
    Qwen3-VL

Native parser:
    Docling

Important:
-----------
Candidates are evaluated empirically.
No model is assumed to be the winner.

Benchmark principles
--------------------
- evidence over assumptions
- minimal necessary methodology
- reproducibility
- no fabricated ground truth
- preserve raw outputs
- dataset-specific evaluation
- no unnecessary infrastructure
- do not build the future ingestion pipeline here

Current status
--------------
Dataset inspection complete enough to establish dataset roles.
Benchmark implementation is now beginning.
