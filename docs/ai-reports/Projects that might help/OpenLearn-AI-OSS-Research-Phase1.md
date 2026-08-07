# OpenLearn AI — Open-Source Ecosystem Research: Phase 1

**Scope:** This is Phase 1 of the full 50-category audit — the eight categories that gate your next build milestones: PDF Processing, OCR (incl. Arabic), Chunking, Embeddings, Vector Databases, RAG/GraphRAG, Quiz & Flashcard Generation, and Student Modeling/Adaptive Learning. Every entry below is backed by a live web search run in July–August 2026, not recalled from memory. Run the full 50-category sweep (agents, backend/frontend, deployment, monitoring, LMS, etc.) through Claude's **Research** mode for the complete picture — it's built for that scale.

---

## 1. Executive Summary

The ingestion → retrieval → tutoring pipeline that OpenLearn AI needs can be built almost entirely from mature, permissively-licensed open source in 2026. The honest headline: **you don't need to build a document pipeline, an embedding model, a vector store, or a knowledge-tracing algorithm from scratch — all four have production-grade OSS options today.** The real engineering work is gluing them together for Arabic-first, RTL, adaptive-learning UX, which is exactly where OpenLearn AI's differentiation lives.

A genuine hidden gem surfaced this round: **[Studyield](https://github.com/studyield/studyield)** is an open-source, self-hosted AI learning platform (FastAPI + Next.js + pgvector + custom multi-agent orchestrator + MCP server) that already ships exam-cloning, knowledge graphs, teach-back evaluation, and course-scoped RAG in 12 languages — it is close enough to OpenLearn AI's own spec that it's worth reading as a reference architecture (and possibly forking pieces of) rather than reinventing independently.

Top-line recommendation per pipeline stage:

| Stage | Recommended default | Why |
|---|---|---|
| PDF → structured text | **Docling** (enterprise RAG fit) or **Marker** (general-purpose) | Both free, both integrate natively with LlamaIndex/LangChain; Docling preserves semantic hierarchy for downstream chunking |
| OCR (incl. Arabic) | **PaddleOCR-VL** for general multilingual; **Qari-OCR** or **Baseer** for Arabic-specific/diacritics-heavy text | PaddleOCR handles 100+ languages incl. Arabic at production speed; Qari-OCR/Baseer are open-source Arabic SOTA on WER/CER |
| Chunking | **Recursive/semantic chunking via LlamaIndex or Chonkie**, escalate to **late chunking (Jina-style)** for long-context material | Best cost/accuracy default; late chunking is worth it once you're indexing full lecture PDFs, not FAQ snippets |
| Embeddings | **BGE-M3** | 100+ languages, dense+sparse+multi-vector (ColBERT-style) in one model, self-hostable, strong Arabic coverage |
| Vector DB | **Qdrant** (speed/self-host) or **pgvector** (if you want one database for everything) | Qdrant is the fastest open-source option to self-host; pgvector is the simplest if your backend is already Postgres |
| RAG orchestration | **LlamaIndex** or **Haystack** | Both are RAG-first (vs. LangChain's broader-but-heavier scope) |
| GraphRAG | **LightRAG** | ~1/6000th the indexing cost of Microsoft GraphRAG with comparable multi-hop quality; incremental updates without full re-index |
| Quiz/Flashcard generation | Build in-house on top of your RAG layer; **pyBKT** for mastery modeling underneath | No single OSS "quiz generator library" dominates — this is genuinely a build, not a buy, category |
| Spaced repetition | **FSRS algorithm** (open-source scheduler, MIT-licensed, used by modern Anki) | Outperforms SM-2; drop-in scheduling logic |
| Student modeling / adaptive learning | **pyBKT** (Bayesian Knowledge Tracing) to start; **Deep Knowledge Tracing (DKT)** implementations once you have real interaction data | pyBKT is the most accessible, well-documented, actively-maintained open implementation |

---

## 2. Category-by-Category Findings

### 2.1 PDF Processing

The 2026 landscape has matured from "bad vs. less bad" into genuinely good, differentiated tools.

| Project | License | Best for | Notes |
|---|---|---|---|
| **[Docling](https://github.com/DS4SD/docling)** (IBM Research) | MIT | Enterprise RAG pipelines | Outputs a structured `DoclingDocument` preserving semantic hierarchy, not just text. Handles PDF, DOCX, PPTX, XLSX, HTML, images, audio, LaTeX. First-class LlamaIndex/LangChain integration. Ships a companion **Granite-Docling-258M** vision-language model (Apache 2.0, ~0.35s/page on A100) for one-shot conversion incl. OCR/layout/tables/equations. <cite index="3-1">Best for enterprise document processing, structured extraction, teams already in the LlamaIndex/LangChain ecosystem</cite> |
| **[Marker](https://github.com/datalab-to/marker)** (Datalab) | Code: GPL-3.0; weights: modified OpenRAIL-M (free for research/personal/startups <$2M) | General-purpose, one-tool-for-everything | <cite index="4-1">Supports PDF, image, PPTX, DOCX, XLSX, HTML, and EPUB; formats tables, forms, equations, inline math, links, and code</cite>. Optional `--use_llm` flag layers an LLM on top for messy layouts. Scores ~76.1 on olmOCR-Bench. |
| **[MinerU](https://github.com/opendatalab/MinerU)** (OpenDataLab / Shanghai AI Lab) | Custom "MinerU Open Source License" (Apache 2.0-based, recently relaxed for commercial use) | CJK-heavy documents, complex academic layouts | <cite index="4-1">Pairs a processing pipeline with a vision-language model (MinerU2.5-Pro), targeting high-resolution parsing of complex layouts including cross-page tables and charts</cite>. Most GitHub stars in the category. |
| **PyMuPDF4LLM / pdf-craft** | AGPL/MIT variants | Quick digital-PDF extraction / book-length works | Lightweight, no ML overhead — good fallback for clean, text-layer PDFs (a large share of course material) |

**Architecture placement:** `Raw PDF/DOCX/PPTX upload → Docling or Marker → structured Markdown/JSON with preserved headings/tables → Chunking stage`

**Recommendation:** Run **Docling** as the default parser (LlamaIndex-native, MIT license, no licensing friction at scale), with **MinerU** as a fallback for scanned/complex Arabic textbook layouts where structure detection is trickier.

---

### 2.2 OCR (Arabic-Priority)

This is the category where OpenLearn AI's Arabic-first requirement matters most, and it's also the one with the most active 2025–2026 research activity.

**General-purpose multilingual OCR (covers Arabic as one of 100+ languages):**

| Project | License | Notes |
|---|---|---|
| **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** / PaddleOCR-VL | Apache 2.0 | <cite index="12-1">Toolbox from the PaddlePaddle ecosystem (Baidu), used to extract text from images/PDFs into structured, usable data</cite>. <cite index="9-1">PP-OCRv4 handles Chinese, Japanese, Korean, and Arabic scripts with accuracy Tesseract can't match</cite>. <cite index="11-1">The newer PaddleOCR-VL-1.5 (Jan 2026) pushes accuracy to 94.5% on OmniDocBench v1.5</cite>, and processes roughly 120 pages/min on an RTX 3090 vs. Tesseract's ~25 pages/min CPU-bound. Requires GPU for best throughput; heavier PaddlePaddle framework dependency. |
| **Surya OCR** | Code GPL-3.0; weights OpenRAIL-M variant | Strong layout analysis, reading-order detection for research-paper-style multi-column documents; lighter weight (650M params) than full VLM OCR |
| **Tesseract 5** | Apache 2.0 | Battle-tested, CPU-only, weakest on complex Arabic layouts/diacritics but zero-dependency and universally available as a fallback |

**Arabic-specialized OCR (the real gems for OpenLearn AI):**

| Project | License | What it does | Why it matters |
|---|---|---|---|
| **[Qari-OCR](https://huggingface.co/papers/2506.02295)** | Open (Qwen2-VL-2B derivative) | <cite index="16-1">Vision-language model derived from Qwen2-VL-2B-Instruct, iteratively fine-tuned for Arabic; QARI v0.2 sets a new open-source SOTA with WER 0.160, CER 0.061, BLEU 0.737 on diacritically-rich texts</cite>. | Handles **tashkeel (diacritics)** — the single hardest part of Arabic OCR for course material with vowel marks |
| **[Baseer](https://huggingface.co/papers/2509.18174)** | Open | <cite index="17-1">Vision-language model fine-tuned specifically for Arabic document OCR using a decoder-only strategy, achieving WER 0.25 and outperforming existing open-source and commercial solutions</cite>. Ships with **Misraj-DocOCR**, an expert-verified Arabic OCR benchmark. | Best current open Arabic document-to-Markdown OCR; a second model of the same name (`AbdoTarek/Baseer-OCR-V1.0`) specializes in Arabic legal documents with structured JSON output |
| **[AtlasOCR](https://huggingface.co/blog/imomayiz/atlasocr)** | Open | <cite index="18-1">First open-source Darija (Moroccan Arabic dialect) OCR model, a 3B-parameter fine-tuned VLM; generalizes well to standard Arabic on KITAB-Bench</cite> | Useful if you ever support dialectal Arabic content, not just Modern Standard Arabic |
| **[Arabic-Nougat](https://github.com/mohamedalirashad/arabic-nougat)** | Open | <cite index="22-1">Suite of OCR models extracting structured Markdown from Arabic book pages, extending Meta's Nougat architecture with an Arabic-optimized tokenizer and 8192-token context</cite> | Purpose-built for **book-length Arabic academic material** — directly relevant to textbook ingestion |
| **KITAB-Bench** | Benchmark, not a model | <cite index="18-1">Large-scale, multi-domain benchmark for Arabic OCR and document understanding covering 8,800+ samples across printed/handwritten text, tables, charts, and complex layouts</cite> | Use this to evaluate whichever Arabic OCR model you ship, rather than trusting vendor claims |

**Architecture placement:** `Scanned PDF/image → OCR (PaddleOCR-VL for general docs, Qari-OCR/Baseer for diacritic-heavy or legal Arabic text) → plain text or structured JSON → merges into the Docling/Marker pipeline output → Chunking`

**Recommendation:** Don't pick one Arabic OCR model — route by document type. Printed textbook Arabic with diacritics → Qari-OCR. Handwritten student work → the `Arabic-English-handwritten-OCR-v3` Qwen2.5-VL fine-tune. General mixed-language documents → PaddleOCR-VL. Benchmark all three against a KITAB-Bench sample before committing.

---

### 2.3 Chunking

| Strategy | When it wins | Tooling |
|---|---|---|
| Recursive/fixed-size (400–512 tokens, 10–20% overlap) | Uniform short-paragraph prose — FAQs, product docs | LangChain `RecursiveCharacterTextSplitter`, LlamaIndex node parsers |
| Semantic chunking (embedding-based cluster boundaries) | Long-form prose where topic boundaries matter more than markup — <cite index="26-1">research papers, transcripts, books</cite> | `Chonkie`, LlamaIndex `SemanticSplitterNodeParser` |
| Late chunking | Long documents where you want each chunk's embedding to carry full-document context | <cite index="27-1">Instead of chunking first and embedding each chunk independently, late chunking embeds the entire document first using a long-context model, then splits the resulting token embeddings into chunks — each chunk's embedding carries long-range semantic signals independent short-chunk embeddings miss</cite>. Introduced by Jina AI (arXiv 2409.04701); usable locally via `transformers` with a long-context embedding model like `jina-embeddings-v3`. |
| Clause-level | Legal/regulatory-style text | Custom regex/rule-based splitters keyed to document structure |

Benchmarks vary meaningfully: <cite index="25-1">NVIDIA's 2024 test of seven chunking strategies across five datasets found page-level chunking won with 0.648 accuracy and the lowest variance, while Chroma Research found semantic chunking methods varied recall by up to 9%</cite>. **Takeaway: chunking strategy is a per-corpus decision, not a universal one** — worth A/B testing against your actual Arabic course-material corpus rather than trusting generic benchmarks.

**Recommendation for OpenLearn AI:** Start with LlamaIndex's semantic/recursive splitters (fast to ship), and graduate specific content types (long PDFs of full courses) to late chunking with a BGE-M3 or Jina-v3 long-context embedder once retrieval quality on those documents becomes the bottleneck.

---

### 2.4 Embeddings (Multilingual / Arabic)

| Model | License | Languages | Notes |
|---|---|---|---|
| **[BGE-M3](https://huggingface.co/BAAI/bge-m3)** | MIT | <cite index="31-1">100+ languages, common semantic space enabling both multilingual retrieval within a language and cross-lingual retrieval between languages</cite> | <cite index="31-1">Multi-granularity: processes inputs from short sentences to long documents up to 8192 tokens</cite>. Ships dense + sparse (SPLADE-like) + multi-vector (ColBERT-like) retrieval in one model — genuinely useful for hybrid search without stitching three separate systems together. Current open-weight multilingual leader per most 2026 roundups. |
| **Qwen3-Embedding** | Apache 2.0 | Multilingual, instruction-aware | <cite index="32-1">Flexible dimensionality from 256 to 2048; the 8B version is available cheaply via OpenRouter</cite> — a good option if you want to trade off storage cost vs. quality per collection |
| **Nomic Embed v2** | Apache 2.0 | Multilingual | <cite index="32-1">Mixture-of-Experts architecture, works well with long documents</cite> |
| **GATE (General Arabic Text Embedding)** | Open (research) | Arabic-specific | Purpose-built for Arabic semantic textual similarity using Matryoshka representation learning — worth evaluating against BGE-M3 specifically on Arabic-only retrieval tasks (per <cite index="16-1">Qari-OCR's related-work list</cite>) |
| **LaBSE** | Apache 2.0 | 109 languages incl. Arabic | Language-agnostic BERT sentence embeddings trained on translation ranking — a solid, older, very safe fallback |

**Recommendation:** **BGE-M3** as the default embedding backbone across OpenLearn AI (Arabic + English + technical terms mixed in the same document, which is exactly your stated content pattern). Its native hybrid (dense+sparse) mode also removes the need to bolt on BM25 separately for keyword-exact matches (important for Arabic technical/legal terminology that dense embeddings alone sometimes blur).

---

### 2.5 Vector Databases

| DB | Self-host? | Best for | Notes |
|---|---|---|---|
| **Qdrant** | Yes (Rust, Apache 2.0) | Speed + filtering at small-to-mid scale | <cite index="38-1">10-25% faster than Weaviate or Milvus on common workloads; p99 latency at 10M vectors ~12ms vs. Weaviate's ~16ms and Milvus's ~18ms</cite>. <cite index="40-1">Best free tier, native sparse (SPLADE, miniCOIL) and ColBERT multi-vector support</cite> — pairs naturally with BGE-M3's hybrid output. |
| **pgvector** | Yes (Postgres extension) | Teams that want one database for documents + metadata + vectors | <cite index="42-1">Gives SQL filtering, joins, and transactional consistency between documents and embeddings in the same database you already operate</cite>. <cite index="37-1">Recommended pick for general use under a few million vectors</cite>. |
| **Weaviate** | Yes | Built-in hybrid search + auto-vectorization modules | <cite index="40-1">Hybrid search (vector + BM25 + metadata filters) with strong docs and modular embeddings</cite> |
| **Milvus** | Yes | Billion-scale corpora | <cite index="43-1">Built for billion-scale similarity search with multiple index types and multi-modal support, but more resource-intensive to operate</cite> — overkill for OpenLearn AI's likely near-term scale |
| **Chroma** | Yes (embedded) | Prototyping | <cite index="40-1">Best for prototyping and MVPs; now has an object-storage backend and collection forking for lightweight production use</cite> |

**Recommendation:** Start with **pgvector** if your backend is already Postgres (simplifies ops for a student-facing app with relational data like enrollments, grades, and progress alongside the vector index). Graduate to **Qdrant** once retrieval latency or filtered-search complexity (e.g., "only search within this student's enrolled courses") becomes a bottleneck — Qdrant's payload filtering is purpose-built for exactly that access pattern.

---

### 2.6 RAG Frameworks & GraphRAG

**Standard RAG orchestration:**

| Framework | Best for |
|---|---|
| **LlamaIndex** | Data indexing/retrieval-first workflows; deep Docling integration |
| **Haystack** | Purpose-built RAG pipelines, strong evaluation tooling |
| **LangChain** | Broadest ecosystem/integrations but heavier abstraction if all you need is RAG |

**GraphRAG (for knowledge-graph-backed tutoring, cross-topic reasoning):**

| Project | License | Cost profile | Notes |
|---|---|---|---|
| **[LightRAG](https://github.com/HKUDS/LightRAG)** (HKUDS, EMNLP 2025) | Apache 2.0 | Very low — <cite index="50-1">roughly 1/6000th the cost of Microsoft's original GraphRAG pipeline</cite> | <cite index="46-1">Uses a dual-layer graph-plus-vector index that updates incrementally instead of requiring a full re-index, at roughly the same indexing cost as embedding the text alone</cite>. <cite index="49-1">10k+ GitHub stars, active community, but less production-hardened than Microsoft's version — hardening is on you</cite>. |
| **Microsoft GraphRAG** | MIT | High — <cite index="46-1">indexing a single dataset could historically run to $33,000 in LLM calls</cite> | <cite index="49-1">The reference implementation; does community detection (Leiden) over the extracted graph with hierarchical summaries; strong for "what are the major themes across this corpus" sensemaking queries</cite>. Its newer **LazyGraphRAG** mode defers summarization to query time and is far cheaper. |
| **Cognee** | Apache 2.0 | Moderate | <cite index="49-1">Modular memory engine — pipelines, tasks, and DAGs you compose to ingest, normalize, and query; supports multiple graph stores (Kuzu, Neo4j, FalkorDB)</cite> |
| **Graphiti** | Apache 2.0 | Moderate | <cite index="49-1">Temporal knowledge graphs — every edge has a validity interval, so it correctly handles facts that change over time</cite>. Built for agent memory, but the temporal-edge idea maps well onto **student mastery decay over time**, which is directly relevant to adaptive learning. |
| **nano-graphrag** | MIT | Very low | A ~1,100-line lightweight reimplementation of Microsoft GraphRAG's mechanics — good for understanding/hacking the algorithm rather than production use |

**Recommendation:** **LightRAG** for OpenLearn AI's knowledge graph layer — it's the only option here that's both cheap enough to re-index frequently (as students upload new material) and mature enough to trust for a v1. Reserve Microsoft GraphRAG evaluation for later if you need its stronger global-sensemaking queries (e.g., "summarize everything this student has studied on thermodynamics").

**Architecture placement (full pipeline so far):**

```
PDF/Image upload
   ↓
OCR (PaddleOCR-VL / Qari-OCR / Baseer, if scanned)
   ↓
Docling / Marker (structure extraction → Markdown/JSON)
   ↓
Chunking (recursive → semantic → late chunking for long docs)
   ↓
BGE-M3 embeddings (dense + sparse)
   ↓
pgvector / Qdrant (vector store) ←→ LightRAG (knowledge graph)
   ↓
LlamaIndex/Haystack retrieval layer
   ↓
Tutor Agent / Quiz Generator / Flashcard Generator
```

---

### 2.7 Quiz Generation & Flashcards

This category is more fragmented — there is no dominant single open-source library the way there is for embeddings or vector DBs. Most serious tools are commercial SaaS (Quizgecko, StudyGlen, Laxu AI) that layer AI generation on top of Anki/Quizlet. The open-source options are mostly project-scale rather than library-scale:

- **[Studyield](https://github.com/studyield/studyield)** — the standout: <cite index="95-1">an open-source, self-hosted AI learning platform combining exam-clone generation, multi-agent problem-solving (Analysis, Solver, and Verifier agents), auto-extracted knowledge graphs, and teach-back evaluation with traditional study tools like flashcards, quizzes, and notes</cite>. Stack: FastAPI, Next.js, pgvector, Celery, custom (no-LangChain) multi-agent orchestrator, MCP server, golden evals in CI. This is close enough to your own spec that it's worth studying its architecture directly, or forking components (its exam-cloning and teach-back evaluation modules in particular).
- **Anki (core app)** — <cite index="58-1">free, open-source, largest add-on ecosystem</cite>, but no built-in AI generation — the review engine (FSRS-based scheduling) is what you'd want to borrow, not the whole app.
- Generic `quiz-generator` GitHub-topic projects — mostly small CLI tools (`pdf-to-quiz`, LLM-wrapper scripts). Useful as implementation reference, not as dependencies.

**Recommendation:** Build quiz/flashcard generation as a thin LLM-prompted layer on top of your own RAG + knowledge-graph stack (this is genuinely the right call — it's mostly prompt engineering plus structured-output parsing, not a hard algorithmic problem), and adopt the **FSRS scheduling algorithm** (open-source, MIT-licensed, the modern replacement for SM-2 that current Anki uses) for review-interval logic rather than writing your own spaced-repetition scheduler.

---

### 2.8 Student Modeling & Adaptive Learning

| Project | License | What it is |
|---|---|---|
| **[pyBKT](https://github.com/CAHLR/pyBKT)** (UC Berkeley) | BSD-3-Clause | <cite index="66-1">Python implementation of Bayesian Knowledge Tracing and extensions, estimating student cognitive mastery from problem-solving sequences</cite>. <cite index="66-1">Provides fitted probabilities for learning, forgetting, and per-resource transition rates; includes methods for fetching online educational datasets</cite>. The most accessible, well-documented, actively-cited open BKT implementation — the natural starting point for OpenLearn AI's student-model component. |
| **Deep Knowledge Tracing (DKT)** implementations, e.g. [mmkhajah/dkt](https://github.com/mmkhajah/dkt) | MIT/Apache variants | <cite index="64-1">An LSTM-based recurrent neural network model designed to predict student performance</cite>, trained on interaction logs (student, skill, correct/incorrect). More powerful than BKT once you have enough real interaction data (thousands of student-question pairs), but a cold-start problem for a young platform. |
| **OATutor** (learning-sciences project, cited in the StanBKT paper) | Open | <cite index="63-1">An open-source adaptive tutoring system and curated content library for learning sciences research</cite> — a genuine reference implementation of a full adaptive-tutoring stack, worth reading even if you don't reuse code directly. |
| **FSRS** | MIT | Not knowledge tracing per se, but the review-scheduling half of "adaptive learning" — pairs naturally with pyBKT's mastery estimates to decide *when* to re-test a concept, not just *what* to test next. |

**Recommendation:** Ship **pyBKT** for v1 mastery estimation (per-skill "known/not known" probabilities feeding your adaptive-path logic) — it needs far less data than DKT to be useful and is trivially interpretable, which matters for a student-facing dashboard that needs to explain *why* it's recommending a topic. Revisit DKT once you're logging enough real interaction data (order of magnitude: tens of thousands of graded attempts) to train it without overfitting.

---

## 3. Risks & Gaps Worth Flagging

- **License friction:** Marker's code is GPL-3.0 (copyleft) and its model weights are OpenRAIL-M with a $2M revenue/funding cap — fine for an academic open-source project today, but worth tracking if OpenLearn AI ever seeks funding or commercial partners. Docling (MIT) avoids this entirely.
- **Arabic OCR is still a moving target:** Qari-OCR, Baseer, and AtlasOCR are all 2025-vintage research releases, not battle-tested production libraries — budget time for evaluation/fine-tuning rather than assuming drop-in accuracy, and validate against KITAB-Bench yourself.
- **GraphRAG cost discipline matters:** even LightRAG's cheap indexing can add up if every student upload triggers a full graph re-extraction — batch/debounce ingestion rather than indexing per-upload.
- **No off-the-shelf "quiz generator" library exists.** This is real engineering work for your team, not a library-integration task — plan time for it accordingly, and look hard at Studyield's implementation before starting from zero.
- **Cold-start problem for student modeling:** pyBKT and DKT both need interaction history to be useful; your v1 adaptive-path logic will need a content-difficulty-based fallback (e.g., simple rule-based sequencing) until you've accumulated enough real student data.

---

## 4. References (Phase 1 sources)

- Docling / Marker / MinerU comparisons: [jimmysong.io](https://jimmysong.io/blog/pdf-to-markdown-open-source-deep-dive/), [themenonlab.blog](https://themenonlab.blog/blog/best-open-source-pdf-to-markdown-tools-2026), [marktechpost.com](https://www.marktechpost.com/2026/07/04/structured-pdf-to-json-a-guide-to-open-source-extraction-models-in-2026/), [pdfmux.com](https://pdfmux.com/blog/pdfmux-vs-pymupdf-vs-marker-vs-docling/)
- OCR / Arabic OCR: [unstract.com](https://unstract.com/blog/best-opensource-ocr-tools/), [imagetotable.ai](https://imagetotable.ai/blog/best-open-source-ocr-tools-2026), [koncile.ai](https://www.koncile.ai/en/ressources/paddleocr-analyse-avantages-alternatives-open-source), Qari-OCR paper (huggingface.co/papers/2506.02295), Baseer paper (huggingface.co/papers/2509.18174), AtlasOCR (huggingface.co/blog/imomayiz/atlasocr), Arabic-Nougat (github.com/mohamedalirashad/arabic-nougat)
- Chunking: [futureagi.com](https://futureagi.com/blog/advanced-chunking-techniques-for-rag/), [firecrawl.dev](https://www.firecrawl.dev/blog/best-chunking-strategies-rag), [atlan.com](https://atlan.com/know/chunking-strategies-rag/)
- Embeddings: [bentoml.com](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models), [webscraft.org](https://webscraft.org/blog/embeddingmodeli-dlya-rag-u-2026-yak-obrati-porivnyannya-provayderiv?lang=en)
- Vector DBs: [datacamp.com](https://www.datacamp.com/blog/the-top-5-vector-databases), [digitalapplied.com](https://www.digitalapplied.com/blog/vector-databases-for-ai-agents-pinecone-qdrant-2026), [firecrawl.dev](https://www.firecrawl.dev/blog/best-vector-databases), [encore.dev](https://encore.dev/articles/best-vector-databases)
- GraphRAG: [medium.com/@tongbing00](https://medium.com/@tongbing00/graphrag-in-2026-what-to-use-when-to-use-it-and-what-to-watch-out-for-a1fa1c283023), [cruxdigits.nl](https://cruxdigits.nl/blog/rag-vs-graphrag-2026/), [typegraph.ai](https://typegraph.ai/blog/best-open-source-graph-rag-tools), [eliteaiadvantage.com](https://eliteaiadvantage.com/blog/build-graphrag-lightrag-cheaper-microsoft)
- Quiz/Flashcards: [studyglen.com](https://studyglen.com/guides/best-ai-flashcard-generator), Studyield (github.com/studyield/studyield)
- Student modeling: pyBKT (github.com/CAHLR/pyBKT), DKT implementations (github.com/mmkhajah/dkt), StanBKT paper (arxiv.org/pdf/2605.23048)

---

## 5. Next Steps

- **Option A (parallel track):** Kick off Claude's Research mode with the full 50-category brief for the exhaustive sweep (agents, backend/frontend frameworks, deployment/DevOps, monitoring, LMS platforms, note-taking/whiteboard, browser automation, speech, datasets/benchmarks, etc.)
- Want me to go deeper on any single category above right now (e.g., pull Studyield's actual repo structure, or benchmark Qari-OCR vs. Baseer vs. PaddleOCR-VL against a sample of your own Arabic course PDFs)? Say the word and I'll do it in this same chat.
