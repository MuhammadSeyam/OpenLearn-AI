# OpenLearn AI — System Requirements & Deployment Profiles

**Companion document to:** OpenLearn AI Technical Specification v4.0
**Document type:** Hardware & Software Requirements Specification
**Scope:** Inferred from the v4.0 architecture (Hybrid AI, Provider Abstraction Layer, Modular Monolith, Docker Compose deployment)

> **How to read this document.** Every number below is tagged as one of three things:
> - **[FACT]** — stated explicitly in the v4.0 specification (e.g., NFRs, the Hardware Requirements by Mode table, the 7B≈6GB/14B≈12GB VRAM reference points).
> - **[ESTIMATE]** — a calculated engineering estimate derived from stated facts using standard, well-documented arithmetic (e.g., quantization byte-per-parameter ratios, per-container RAM footprints for named open-source software).
> - **[ASSUMPTION]** — a judgment call made because the spec does not constrain this value, clearly flagged so it can be revisited (e.g., how many students share a Research Server, how large a "large" knowledge base is).
>
> Nothing here is invented functionality — every requirement traces back to a named component in the v4.0 spec (FastAPI, Celery, PostgreSQL 16, ChromaDB, Redis, Neo4j/NetworkX, MinIO, Ollama, PaddleOCR, BGE-m3, bge-reranker-v2-m3, Next.js 16).

---

## 1. Introduction

OpenLearn AI is architected around a single, defining idea: **the Provider Abstraction Layer (PAL)** decouples every AI capability — reasoning, embedding, OCR, vision, speech, vector search, and ranking — from the service that implements it. Because of this, "OpenLearn AI's system requirements" is not a single number. The same codebase can run on a $0-GPU laptop that calls Claude and OpenAI over the network, or on a workstation with a 24GB GPU processing everything offline. The hardware floor is set entirely by *which providers are configured*, not by the application code itself.

This creates a genuine engineering question: **what do you actually need to buy or provision**, given that you've chosen a point on the local↔cloud spectrum? This document answers that question by walking the architecture — PAL interfaces, the eight system layers, the Modular Monolith backend, the multi-store database layer, and the Celery worker pool — and translating each into concrete CPU, GPU, RAM, storage, and network requirements.

Three architectural facts drive everything that follows:

1. **The system's own NFR-1 anchors the "reference" hardware target.** The spec calibrates its 3-second RAG latency target against "16GB RAM, 8GB VRAM GPU" — this is the spec's own definition of adequate local hardware, and it becomes the backbone of Profile D below.
2. **The spec gives two ground-truth VRAM data points**: a 7B model needs ≈6GB VRAM, a 14B model needs ≈12GB. Section 4 (GPU Analysis) extrapolates from these two real anchors rather than guessing.
3. **The spec explicitly separates Local / Hybrid / Cloud hardware tiers** (Section 23.3 of the spec) with its own RAM/GPU/storage minimums. Those numbers are treated as ground truth and expanded into full component-level breakdowns below, rather than re-derived from scratch.

Requirements differ by deployment mode for a simple reason: **VRAM and RAM are dominated by whichever AI models are resident in local memory.** A cloud-only deployment has no local model weights at all — its floor is set by a Next.js/FastAPI/PostgreSQL/Redis stack, which is lightweight. A fully local deployment must additionally hold an LLM (several GB), an embedding model, a reranker, and an OCR model in memory or VRAM simultaneously, plus run Neo4j and a vector index — which is why local hardware requirements are an order of magnitude higher than cloud requirements.

---

## 2. Deployment Profiles

Six profiles are defined, spanning the full range the v4.0 architecture supports. Profiles A–C map directly onto the spec's three named execution modes (Cloud, Hybrid, Local); Profiles D–F subdivide "Local" by hardware class, since "Local Mode" in the spec spans everything from a student laptop to a university server.

### Profile A — Cloud AI (API Only)

All seven PAL interfaces are bound to cloud providers (OpenAI, Anthropic/Claude, Gemini, OpenRouter, Groq, Together AI, Cohere, Google Vision, etc.). No model weights are ever loaded locally. This is the spec's **Cloud Mode** [FACT: Section 9.1, Section 23.3].

The local machine only needs to run the thin application layer: Next.js frontend, FastAPI backend, Celery worker (orchestration only — the actual OCR/embedding/generation calls are network round-trips), PostgreSQL, Redis, and MinIO. No Ollama, no ChromaDB model loading, no Neo4j is strictly required (NetworkX in-memory graph is sufficient at this scale).

| Component | Minimum | Recommended |
|---|---|---|
| CPU | 2 cores / 4 threads (Intel i3-1215U, AMD Ryzen 3 5300U, Apple M1) | 4 cores / 8 threads (Intel i5-1335U, Ryzen 5 7530U, Apple M2/M3) |
| GPU | None required | None required (integrated graphics is sufficient for the UI) |
| RAM | 4 GB **[FACT]** | 8 GB **[FACT]** |
| Storage | 5 GB **[FACT]** (Docker images, Postgres, logs, cached documents) | 15–20 GB SSD (headroom for uploaded PDFs and MinIO objects) **[ESTIMATE]** |
| OS | Windows 10/11, macOS 12+, Ubuntu 20.04+ | Windows 11, macOS 14+, Ubuntu 22.04/24.04 |
| Network | Broadband, persistent connection required **[FACT]** — every reasoning, embedding, OCR, and ranking call leaves the machine | 10+ Mbps, low-latency (<100ms to provider region) for acceptable RAG streaming |

**Why this is viable:** every AI-heavy stage in the Document Processing Pipeline and Knowledge Pipeline (Section 11–12 of the spec) routes through the PAL, which in Cloud Mode simply forwards to an API. The local machine never computes an embedding or runs an LLM forward pass — it only orchestrates HTTP/WebSocket calls. This is why Cloud Mode's floor (2GB RAM per the spec) is close to "any modern laptop or Chromebook-class device."

**Trade-off:** zero offline capability (violates NFR-7 by design — this is the explicit trade the spec allows), and every document chunk, prompt, and generated question is transmitted externally, subject to the Minimum Data Principle (Section 9.3 of the spec).

---

### Profile B — Hybrid AI (Recommended)

This is the spec's own **recommended default** [FACT: Section 9.1 — "Hybrid Mode (Recommended for most users)"]. The canonical configuration example in the spec (Section 8.2) is explicit: local reasoning via Ollama (Qwen2.5:7B) with cloud embeddings via OpenAI — but the more common "local-heavy" hybrid pattern the spec describes is the inverse: **local embeddings, local OCR, local reranker, cloud reasoning**, which is the pattern requested in this document's brief and is also fully supported by the PAL's per-interface configuration.

Under a local-embeddings / local-OCR / local-reranker / cloud-LLM configuration, VRAM demand drops dramatically because the largest model (the 7B+ reasoning model) is no longer resident locally — only the embedding model (BGE-m3, ~2.3GB in FP32 / ~600MB quantized), OCR model (PaddleOCR, a few hundred MB), and reranker (bge-reranker-v2-m3, ~1.1GB) need to fit in memory, and these can run comfortably on CPU.

| Component | Minimum | Recommended |
|---|---|---|
| CPU | 4 cores / 8 threads | 6–8 cores (Ryzen 5 7600, Intel Core Ultra 5 125H) — CPU-bound OCR/embedding throughput scales with cores |
| GPU | None (CPU inference of BGE-m3 + reranker is acceptable at this scale) | Optional 6GB+ VRAM (RTX 3050/4060) — cuts embedding/reranking latency roughly 5–10× **[ESTIMATE]** |
| RAM | 4 GB **[FACT]** | 8 GB **[FACT]** |
| Storage | 10 GB **[FACT]** | 25–30 GB SSD (local model weights + document corpus + vector index headroom) **[ESTIMATE]** |
| OS | Windows 10/11 + WSL2, macOS 12+, Ubuntu 20.04+ | Ubuntu 22.04/24.04, macOS 14+, Windows 11 + WSL2 |
| Network | Required, for the cloud reasoning provider **[FACT]** | Stable broadband; local components keep the system functional for ingestion even during brief outages |

**Why this is recommended:** it directly implements the Minimum Data Principle — the highest-risk data path (student prompts and full retrieved context going to an LLM) is the one component the spec's own risk register flags most (local LLM speed is a High/Medium risk), so keeping *that* on a fast cloud API while keeping document content processing (OCR, embedding, chunking, which never leave the machine) local gives the best privacy/quality/hardware balance. This also matches NFR-4 (50 concurrent users on 4GB RAM for hybrid mode) — a number that is only achievable because the heaviest compute (LLM inference) is offloaded to the cloud provider's infrastructure rather than the local server.

---

### Profile C — Local Small (Student Laptop)

Targets the spec's Local Mode **minimum** configuration [FACT: 8GB RAM floor], using the smallest viable model at every PAL interface: a quantized 1.5B–3B reasoning model (the spec's own risk-mitigation fallback names "Qwen 2.5 1.5B / Phi-3.5 Mini" for exactly this scenario), a compact embedding model, and lightweight OCR.

| Component | Minimum | Recommended | Ideal |
|---|---|---|---|
| CPU | 4-core (Intel i5-1135G7, Ryzen 5 5500U, Apple M1) | 6-core (Intel Core Ultra 5, Ryzen 5 7530U, Apple M2) | 8-core (Apple M3/M4, Ryzen 7 7735U) |
| GPU | Integrated graphics only (CPU inference, GGUF Q4) | Entry discrete: RTX 3050 6GB / RTX 4050 6GB | RTX 4060 8GB or Apple unified-memory GPU (M-series) |
| VRAM | 0 (CPU/RAM-only inference) | 6 GB | 8 GB |
| RAM | 8 GB **[FACT]** | 16 GB **[ESTIMATE — see §5]** | 32 GB |
| Storage | 20 GB **[FACT]** | 40 GB SSD (NVMe strongly preferred — OCR + embedding I/O is storage-latency sensitive) | 100 GB NVMe |
| OS | Windows 11, macOS 13+, Ubuntu 22.04 | same | same |
| Network | Optional (fully offline-capable) | Optional | Optional |

**Expected limitations [ASSUMPTION]:** on the Minimum tier, a 1.5B–3B GGUF model produces noticeably lower-quality concept extraction and question generation than the 7B default, directly triggering the spec's own documented risk ("Local LLM too slow / low quality" — Section 28.1). RAG latency will likely exceed the 3-second NFR-1 target on CPU-only inference (5–20 tokens/sec local generation is the spec's own stated range, and that range assumes some GPU acceleration). Concurrent use (more than one student session) is not realistic on this tier — it is single-user, single-session by design.

---

### Profile D — Local Standard

This is the direct hardware realization of the spec's **own reference configuration**: "16GB RAM, 8GB VRAM GPU" [FACT: Section 25.1, used to calibrate every NFR]. Everything in the eight-layer architecture runs locally: RAG, Knowledge Graph (NetworkX is sufficient at this scale — Neo4j is optional), Student Knowledge Model, Adaptive Engine, OCR, and Celery background workers, using the spec's own default model selections (Qwen2.5 7B, BGE-m3, PaddleOCR, bge-reranker-v2-m3).

| Component | Minimum | Recommended | Ideal |
|---|---|---|---|
| CPU | 6-core (Ryzen 5 5600, Intel i5-12400) | 8-core (Ryzen 7 7700, Intel Core Ultra 7 155H) | 8–12 core (Ryzen 7 7800X3D, Intel Core i7-14700K) |
| GPU | RTX 3060 12GB / RTX 4060 8GB | RTX 4060 Ti 16GB / RTX 4070 12GB | RTX 4070 Ti Super 16GB / RTX 5070 Ti 16GB |
| VRAM | 8 GB **[FACT — matches the spec's own reference point]** | 12 GB | 16 GB |
| RAM | 16 GB **[FACT]** | 32 GB | 32–64 GB |
| Storage | 30 GB **[ESTIMATE — see §6]** | 100 GB NVMe SSD | 500 GB+ NVMe SSD |
| OS | Ubuntu 22.04/24.04, Windows 11 + WSL2, macOS 14+ (Apple Silicon, via Ollama's Metal backend) | same | same |
| Network | Not required (offline-capable per NFR-7) | Optional, for occasional cloud fallback per the degradation strategy | Optional |

This is the tier at which the spec's NFR-1 (RAG < 3s), NFR-2 (10 MCQs < 30s), and NFR-3 (100-page PDF < 60s including OCR) are the *design targets*, not aspirational — 8GB VRAM is exactly enough to hold a Q4-quantized 7B reasoning model with room for KV-cache and context (§4 below).

---

### Profile E — Local Professional (Workstation)

Full platform, entirely local, with multiple simultaneous AI models resident (reasoning + embedding + OCR + reranker + optionally vision/speech), multiple concurrent Celery workers, Neo4j (not NetworkX) for the Knowledge Graph, and a workstation-class GPU that can hold a larger reasoning model (14B, or a 7B model at FP16 for better quality) without offloading.

| Component | Minimum | Recommended | Ideal |
|---|---|---|---|
| CPU | 12-core (Ryzen 9 7900, Intel Core i7-14700K) | 16-core (Ryzen 9 9950X, Intel Core Ultra 9 285K) | Threadripper 7960X / Xeon W-2400, 24+ cores |
| GPU | RTX 4070 Ti Super 16GB | RTX 4080 Super 16GB / RTX 5080 16GB | RTX 4090 24GB / RTX 5090 32GB |
| VRAM | 16 GB (7B–8B at FP16, or 14B at Q4) **[ESTIMATE — see §4]** | 16–24 GB (14B comfortably, headroom for reranker + vision model concurrently) | 24–32 GB (32B at Q4, or 14B at FP16 with large context) |
| RAM | 32 GB **[ESTIMATE]** | 64 GB | 64–128 GB |
| Storage | 250 GB NVMe SSD | 1 TB NVMe SSD | 2 TB+ NVMe SSD (RAID 0/1 for Postgres+Neo4j+vector index I/O) |
| OS | Ubuntu 24.04 LTS (best CUDA/driver support) | Ubuntu 24.04 LTS | Ubuntu 24.04 LTS |
| Network | Not required | Optional | Optional |

At this tier, running Neo4j alongside PostgreSQL, ChromaDB, Redis, MinIO, and a 14B-class Ollama model simultaneously is realistic without contention — this is the first profile where "multiple local AI models + multiple workers + concurrent processing" (as specified in the brief) stops being a resource-contention risk.

---

### Profile F — Research Server (University Deployment)

**[ASSUMPTION — explicitly flagged]:** the v4.0 spec does not define a multi-tenant or horizontally-scaled deployment; it targets a single-machine, single-student (or small classroom) Modular Monolith explicitly *because* microservices/cluster orchestration was judged out of scope for a graduation project (Section 18.1 of the spec: "a graduation project must be deployable on a single machine"). This profile is therefore an extrapolation, built by scaling the single-server architecture along the axes the spec does describe as scalable: NFR-4's "50 concurrent users on a single server" as a linear-scaling baseline, and the spec's own noted vector-search ceiling ("ChromaDB + HNSW provides sub-second retrieval up to ~100,000 vectors; beyond that, sharding or migration to Pinecone/Weaviate is needed" — Section 25.2).

| Component | Minimum (≈100 concurrent students) | Recommended (≈250 concurrent students) | Ideal (≈500+ concurrent students, multi-department) |
|---|---|---|---|
| CPU | Dual Xeon Silver 4410Y (24 cores) / EPYC 9124 | Dual Xeon Gold 6438M (64 cores) / EPYC 9354 | Dual EPYC 9554 (128 cores) |
| GPU | 1× A100 40GB or 2× RTX 4090 24GB (vLLM tensor-parallel serving) | 2× A100 80GB or 4× L40S 48GB | 4–8× A100/H100 80GB (multi-GPU vLLM cluster) |
| VRAM (total) | 40–48 GB | 160 GB | 320–640 GB |
| RAM | 128 GB | 256 GB | 512 GB–1 TB |
| Storage | 2 TB NVMe (OS/DB) + 10 TB HDD/SAN (document archive) | 4 TB NVMe + 30 TB SAN | 8 TB NVMe (all-flash array) + 100 TB+ SAN |
| Network | 1 Gbps internal, redundant WAN | 10 Gbps internal | 10–25 Gbps internal, redundant WAN with load balancer |
| OS | Ubuntu 24.04 LTS Server | Ubuntu 24.04 LTS Server | Ubuntu 24.04 LTS Server, containerized on Kubernetes or Docker Swarm |

**Key architectural change from Profiles A–E [ASSUMPTION]:** at this scale, the spec's own recommended single-instance stack needs three modifications the spec itself anticipates as escape hatches rather than requires: (1) swap ChromaDB embedded mode for a dedicated, shardable vector DB (spec names Pinecone/Weaviate/Qdrant as the horizontal-scaling path), (2) swap the single-process Ollama runtime for **vLLM** (named in the spec's own Technology Stack table as an alternative LLM runtime, specifically because it supports continuous batching and multi-GPU tensor parallelism, unlike Ollama), and (3) run multiple Celery worker replicas behind Redis, since the spec's Celery+Redis task-queue pattern scales horizontally by adding workers without any application-code changes — this is the one part of Profile F that follows directly and cleanly from the stated architecture.

---

## 3. Minimum / Recommended / Ideal Specifications — Consolidated

The tables above are the authoritative per-profile specs. Consolidated view:

| Profile | CPU (Rec.) | GPU (Rec.) | VRAM | RAM | Storage | OS |
|---|---|---|---|---|---|---|
| A — Cloud Only | Ryzen 5 7530U / i5-1335U | None | 0 | 8 GB | 15–20 GB | Any (Win/macOS/Linux) |
| B — Hybrid (Recommended) | Ryzen 5 7600 | Optional RTX 4060 | 0–6 GB | 8 GB | 25–30 GB | Any (Win/macOS/Linux) |
| C — Local Small | Ryzen 5 7530U / Apple M2 | RTX 3050/4050 6GB | 6 GB | 16 GB | 40 GB | Win 11 / macOS 13+ / Ubuntu 22.04 |
| D — Local Standard | Ryzen 7 7700 / Core Ultra 7 | RTX 4060 Ti 16GB / RTX 4070 | 12 GB | 32 GB | 100 GB | Ubuntu 22.04/24.04 |
| E — Local Professional | Ryzen 9 9950X | RTX 4080 Super / RTX 5080 | 16–24 GB | 64 GB | 1 TB | Ubuntu 24.04 |
| F — Research Server | Dual Xeon Gold / EPYC | 2–4× A100/L40S | 160 GB+ | 256 GB+ | 4 TB+ NVMe + SAN | Ubuntu 24.04 Server |

---

## 4. GPU Analysis

### 4.1 What actually consumes VRAM

Four PAL-interface model types can be VRAM-resident simultaneously in a fully local deployment: the **reasoning model** (largest, by far), the **embedding model** (BGE-m3, small), the **reranker** (bge-reranker-v2-m3, small, cross-encoder), and optionally a **vision model** (LLaVA/Qwen-VL, comparable in size to the reasoning model). OCR (PaddleOCR) and TTS/STT (Piper, Whisper) are lightweight and typically run on CPU without materially affecting the VRAM budget.

### 4.2 Reasoning-model VRAM by size and quantization

The spec provides two anchor points directly [FACT: Section 10.2]: **7B ≈ 6GB VRAM**, **14B ≈ 12GB VRAM**. This implies roughly 0.85GB of VRAM per billion parameters at the spec's assumed quantization level (consistent with 4-bit GGUF quantization — the format Ollama uses by default — plus typical KV-cache/context overhead). The table below extrapolates other common sizes using that same ratio for INT4/GGUF, and standard, well-established bytes-per-parameter ratios for INT8 (~1.1GB/B) and FP16 (~2.1GB/B) **[ESTIMATE, calibrated to the spec's own reference points]**:

| Model size | INT4 / GGUF (Q4_K_M) | INT8 | FP16 | Fits in 8GB? | Fits in 16GB? | Fits in 24GB? |
|---|---|---|---|---|---|---|
| 3B | ~2.5 GB | ~3.5 GB | ~6.5 GB | Yes (all levels) | Yes | Yes |
| 7B | **~6 GB [FACT]** | ~8.5 GB | ~15 GB | Q4 only, tight | Q4/INT8 | All |
| 8B | ~6.5 GB | ~9.5 GB | ~17 GB | Q4 only, tight | Q4/INT8 | All |
| 13B | ~11 GB | ~15 GB | ~27 GB | No | Q4 only | Q4/INT8 |
| 14B | **~12 GB [FACT]** | ~16 GB | ~29 GB | No | Q4 only, tight | Q4/INT8 |
| 32B | ~25 GB | ~36 GB | ~65 GB | No | No | No — needs 32GB+ or offload |
| 70B | ~42 GB | ~75 GB | ~145 GB | No | No | No — needs multi-GPU or API |

### 4.3 Which tier needs what

- **Fits entirely inside consumer VRAM (8GB):** 3B always; 7B only at Q4 with a short context window (this is exactly why the spec's own risk mitigation names the 1.5B–3B tier as the "too slow" fallback for constrained hardware).
- **Fits inside 16GB (Profile D/E entry):** 7B/8B comfortably at any quantization up to INT8; 14B at Q4 with headroom for the embedding + reranker models running alongside it — this is precisely the spec's own default configuration (Qwen2.5 7B) at its own reference hardware point.
- **Requires offloading (partial CPU/GPU split via llama.cpp/Ollama layer offload) or 24GB+:** 32B models on anything below a 4090/5090-class card. Expect a proportional drop in tokens/sec for every layer pushed to CPU.
- **Requires multi-GPU or an API, full stop:** 70B-class models. Even at Q4, 70B exceeds every single consumer GPU on the market (largest is 32GB on the RTX 5090). This is the hard line where Profile F's multi-GPU vLLM cluster — or simply routing to a cloud provider per the PAL's fallback chain — becomes the only realistic option.

### 4.4 Non-reasoning models (fixed, small overhead)

| Model | Purpose | Typical VRAM/RAM footprint |
|---|---|---|
| BAAI/bge-m3 (default embedding) | Multilingual embedding | ~2.3 GB FP32 / ~0.6 GB INT8 **[ESTIMATE]** |
| bge-reranker-v2-m3 (default reranker) | Cross-encoder re-ranking | ~2.2 GB FP32 / ~0.6 GB INT8 **[ESTIMATE]** |
| PaddleOCR v4 (default OCR) | Text extraction from scans | ~0.3–0.5 GB, CPU-friendly **[ESTIMATE]** |
| Whisper medium (default STT) | Speech-to-text | ~1.5 GB VRAM if GPU-accelerated, else CPU **[ESTIMATE, standard Whisper figures]** |
| Piper (default TTS) | Text-to-speech | <0.2 GB, CPU-only **[ESTIMATE]** |

On an 8GB card running the spec's default 7B model (~6GB) alongside embedding+reranker on CPU (the common configuration), roughly 1.5–2GB of VRAM headroom remains for context/KV-cache — workable but tight, which is exactly why Profile D's *recommended* tier moves to 12GB+.

---

## 5. RAM Analysis

RAM demand stacks additively across the OS, every containerized service, and (for local providers) model weights loaded outside VRAM or spilled from it. Figures below are **[ESTIMATE]**, based on standard, well-documented per-service footprints for the named open-source software in the spec's Technology Stack table.

| Component | Idle / Base | Under Load |
|---|---|---|
| Host OS (Linux) | 0.5–1 GB | 1–1.5 GB |
| Host OS (Windows 11 + WSL2 overhead) | 2–3 GB | 3–4 GB |
| FastAPI backend (Modular Monolith) | 0.3–0.5 GB | 0.8–1.5 GB (per worker process) |
| Next.js frontend (dev/SSR process, if self-hosted rather than static) | 0.3–0.5 GB | 0.5–1 GB |
| Redis (cache + Celery broker) | 0.05–0.1 GB | 0.3–1 GB (depends on queue depth and cache size) |
| PostgreSQL 16 | 0.3–0.5 GB (shared_buffers default) | 1–2 GB with a tuned config for this workload |
| Neo4j (Profile E/F only) | 1 GB (default JVM heap) | 2–4 GB for a mid-size prerequisite graph |
| ChromaDB (embedded mode) | 0.2 GB | 0.5–2 GB, scales with vector count (HNSW index is held in memory) |
| MinIO | 0.2 GB | 0.3–0.5 GB |
| Celery workers (Document + Embedding worker, per the spec's C4 diagram) | 0.3 GB each idle | 1–2 GB each during OCR/embedding batches |
| Ollama runtime overhead (excl. model weights, which are separately counted in §4) | 0.5 GB | 1 GB |
| Local reasoning model (non-VRAM RAM overlap for CPU inference or partial offload) | 0 (if fully on GPU) | up to full model size if running CPU-only (see §4.2 table) |
| OS file cache / buffers (headroom for document I/O) | — | 1–3 GB recommended headroom |

**Totals by profile [ESTIMATE, sum of the above]:**

| Profile | Estimated RAM floor | Matches spec's stated floor? |
|---|---|---|
| A — Cloud | ~2.5–3.5 GB | Spec states 4GB minimum **[FACT]** — consistent, spec adds margin |
| B — Hybrid | ~3.5–4.5 GB | Spec states 4GB minimum **[FACT]** — consistent, tight |
| C — Local Small (3B Q4 CPU) | ~7–8 GB | Spec states 8GB minimum **[FACT]** — consistent, no margin |
| D — Local Standard (7B on GPU) | ~10–13 GB with OS + all containers | Spec states 16GB **[FACT]** — matches, with comfortable margin for Neo4j/multi-tasking |
| E — Local Professional (14B + Neo4j + multiple workers) | ~20–28 GB | 32GB minimum recommended above — matches |
| F — Research Server (100+ concurrent sessions, connection pools, larger caches) | 80–120 GB | 128GB minimum recommended above — matches |

---

## 6. Storage Analysis

Storage is split between **application/infrastructure** (Docker images, databases, logs — grows slowly, roughly fixed) and **content** (uploaded documents, extracted text, embeddings, knowledge graph, model weights — grows with usage). Figures are **[ESTIMATE]**.

| Category | Minimum footprint | Recommended footprint | Heavy usage (100s of documents / many students) |
|---|---|---|---|
| Docker engine + images (all services in the spec's Docker Compose file: Nginx, Next.js, FastAPI, Celery, Postgres, Redis, MinIO, ChromaDB, Neo4j, Ollama) | 8–10 GB | 15 GB | 15–20 GB (rarely grows further — image layers are shared) |
| PostgreSQL data (users, materials metadata, SKM records, quiz attempts, exam sessions, review items) | 0.5 GB | 2 GB | 10–30 GB (thousands of quiz attempts / review items across users) |
| Neo4j graph data (concepts + relations, Profile E/F) | 0.2 GB | 1 GB | 5–10 GB (large multi-course prerequisite graphs) |
| Vector DB (ChromaDB — embeddings for all chunks) | 0.5 GB (~a few thousand chunks) | 3–5 GB | 20–40 GB (100k+ vectors — approaching the spec's own stated HNSW ceiling, §25.2) |
| Uploaded source documents (MinIO object storage) | 1 GB | 10 GB | 100+ GB (a university-scale document corpus) |
| Extracted text / OCR intermediate artifacts | 0.2 GB | 2 GB | 15–20 GB |
| Embedding cache (avoiding re-embedding unchanged chunks) | 0.1 GB | 1 GB | 5–10 GB |
| Logs (structlog JSON logs, Langfuse traces, Sentry local buffer) | 0.1 GB | 1 GB, with rotation | 5 GB with rotation policy |
| Backups (Postgres dumps + MinIO snapshot, 1 generation) | — (optional at minimum tier) | Equal to live DB+object size | 2–3× live size (retention window) |
| **Subtotal — infrastructure only** | **~10 GB** | **~20 GB** | **~30–40 GB** |
| **Subtotal — content-dependent** | **~2 GB** | **~17 GB** | **~150–200 GB+** |

Add AI model storage (Section 7 below) on top of these totals for local/hybrid deployments.

---

## 7. AI Model Storage

Model weights are downloaded once and cached on disk (typically under Ollama's model store or a HuggingFace cache directory for Sentence Transformers). Figures are **[ESTIMATE]**, using standard on-disk sizes for the named quantization formats.

| Model class | Example (from spec) | FP16 on-disk | INT8 on-disk | GGUF Q4 on-disk |
|---|---|---|---|---|
| Embedding model | BAAI/bge-m3 | ~2.2 GB | ~1.1 GB | N/A (rarely quantized this small) |
| Reranker | bge-reranker-v2-m3 | ~2.2 GB | ~1.1 GB | N/A |
| OCR model | PaddleOCR v4 | ~0.3–0.6 GB (already compact by design) | — | — |
| Small reasoning LLM | Qwen 2.5 1.5B / Phi-3.5 Mini | ~3 GB | ~1.6 GB | ~1 GB |
| Medium reasoning LLM (spec default) | **Qwen 2.5 7B** | ~15 GB | ~8 GB | **~4.5 GB** |
| Medium-large reasoning LLM | Qwen 2.5 14B | ~28 GB | ~15 GB | ~8.5 GB |
| Large reasoning LLM | Qwen 2.5 32B | ~65 GB | ~34 GB | ~19 GB |
| Very large reasoning LLM | Llama 3.1 70B-class | ~140 GB | ~75 GB | ~40 GB |
| Speech (STT) | Whisper medium | ~1.5 GB | — | — |
| Speech (TTS) | Piper (per voice) | ~60–100 MB | — | — |
| Vision model (optional) | Qwen-VL / LLaVA (7B-class) | ~15 GB | ~8 GB | ~4.5 GB |

**Trade-off summary:** GGUF Q4 quantization is roughly **3× smaller on disk and in VRAM** than FP16, at a well-documented, modest quality cost (typically a small drop in benchmark accuracy, more noticeable on structured-output/JSON-mode tasks — directly relevant to the spec's Knowledge Graph triple-extraction step, which depends on reliable JSON output). This is why the spec's own default (Qwen2.5 7B via Ollama, which defaults to Q4_K_M) is the pragmatic choice for Profiles C–D, while Profile E/F — with VRAM to spare — should prefer INT8 or FP16 for better extraction and generation fidelity.

---

## 8. Software Prerequisites

Directly enumerated from the spec's Technology Stack (Section 26) and Infrastructure sections:

| Category | Required | Notes |
|---|---|---|
| Containerization | Docker, Docker Compose | Spec's mandated one-command deployment mechanism (NFR-9) **[FACT]** |
| Backend runtime | Python 3.12 | FastAPI, SQLAlchemy 2, Pydantic v2, Celery **[FACT]** |
| Frontend runtime | Node.js (LTS, for Next.js 16 build) | **[ESTIMATE — implied by Next.js 16/React 19 requirement]** |
| Version control | Git | For deployment from the AGPL-3.0 repository **[FACT]** |
| Local LLM runtime | Ollama (default) — or vLLM / llama.cpp / LM Studio as alternatives named in the spec | Required only for Profiles B (partial)–F |
| GPU stack | NVIDIA Driver (550+) and CUDA 12.x | Required only if a local GPU-accelerated provider is configured |
| Databases | PostgreSQL 16, Redis, Neo4j (Profile E/F) or NetworkX (bundled Python lib, Profiles A–D) | **[FACT]** |
| Vector store | ChromaDB (embedded, default) or Qdrant/FAISS as alternatives | **[FACT]** |
| Object storage | MinIO | **[FACT]** |
| Reverse proxy | Nginx (default) or Traefik | **[FACT]** |
| Build tools | gcc/build-essential (Linux), Xcode CLT (macOS) — needed for some Python ML package wheels (e.g., pyBKT, py-irt native extensions) | **[ESTIMATE]** |
| GPU libraries (local only) | cuDNN, cuBLAS (bundled with Ollama/vLLM builds) | **[ESTIMATE]** |
| CPU instruction support | AVX2 (baseline for efficient GGUF/llama.cpp inference); AVX-512 improves throughput where available | **[ESTIMATE — standard llama.cpp/GGML requirement]** |
| Linux packages | libssl, libpq-dev (Postgres client libs), ffmpeg (Whisper audio preprocessing) | **[ESTIMATE]** |

---

## 9. Operating System Support

| OS | Suitability | Notes |
|---|---|---|
| **Ubuntu 24.04 LTS** | **Best** | Best NVIDIA driver/CUDA support, native Docker performance (no VM layer), the spec's own risk register treats Linux+WSL2 as the reference environment |
| **Ubuntu 22.04 LTS** | Excellent | Still fully supported; slightly older kernel/driver baseline |
| **Debian 12** | Very good | Nearly identical to Ubuntu for this workload; less pre-packaged NVIDIA tooling |
| **Fedora (latest)** | Good | Newer kernel can mean bleeding-edge driver issues with Ollama/CUDA; less commonly tested in the Ollama/vLLM ecosystems |
| **Windows 11 (native)** | Limited | Docker Desktop works but adds a virtualization layer; native GPU passthrough to containers is unreliable — **WSL2 is the spec's own documented risk mitigation** for Windows [FACT: Section 28.1] |
| **Windows 11 + WSL2** | Good | Recommended path for Windows users; near-native Docker/GPU performance once configured; this is the spec's explicit fallback for "Docker deployment fails on Windows" |
| **macOS 14+ (Apple Silicon)** | Good, with caveats | Ollama supports Metal acceleration well for local LLM inference; Docker Desktop for Mac has known overhead; NVIDIA-specific tooling (CUDA) is not applicable — Apple Silicon uses unified memory instead of discrete VRAM, which somewhat changes the VRAM math in Section 4 (shared with system RAM) |

**Recommendation:** Ubuntu 24.04 LTS (bare metal or as the WSL2 distro) for any Profile D–F deployment; Windows/macOS are fully viable for Profiles A–C where GPU acceleration is optional or absent.

---

## 10. Docker Resource Allocation

Recommended `docker-compose` resource limits per profile, following the spec's own service-profile pattern (`--profile local|hybrid|cloud`):

| Profile | CPUs (Docker limit) | RAM (Docker limit) | Swap | Disk (Docker root) | GPU passthrough | Notable volumes |
|---|---|---|---|---|---|---|
| A — Cloud | 2 | 4 GB | 2 GB | 20 GB | None | postgres_data, redis_data, minio_data |
| B — Hybrid | 4 | 6 GB | 2 GB | 30 GB | Optional (`--gpus` for embedding/reranker containers) | + chroma_data |
| C — Local Small | 4 | 12 GB | 4 GB | 50 GB | Optional (`--gpus all` if discrete GPU present) | + ollama_models (small model only) |
| D — Local Standard | 6 | 24 GB | 8 GB | 120 GB | Required (`--gpus all`, NVIDIA Container Toolkit) | + ollama_models (7B) |
| E — Local Professional | 12 | 48 GB | 16 GB | 1 TB | Required, dedicated GPU(s) | + neo4j_data, ollama_models (14B+) |
| F — Research Server | 32+ (per node) | 128 GB+ (per node) | 32 GB+ | 4 TB+ (NVMe, per node) | Required, multi-GPU with NVIDIA Container Toolkit + `CUDA_VISIBLE_DEVICES` partitioning per service | Kubernetes PVCs / NFS-backed volumes for shared state |

**[ASSUMPTION]** for Profile F: multi-node orchestration (Kubernetes or Docker Swarm rather than a single `docker-compose up`) is not specified by the v4.0 document, which is explicitly single-machine by design — this row represents the natural extension path, not a documented requirement.

---

## 11. Performance Expectations

These restate and extend the spec's own Non-Functional Requirements (Section 25.1); anything beyond the six NFRs is marked as an estimate.

| Metric | Profile A/B (Cloud reasoning) | Profile D (Local, reference hardware) | Profile E/F (Local, high-end) |
|---|---|---|---|
| Document ingestion (100-page PDF, text-native) | 10–20 s **[ESTIMATE]** | <60 s including OCR **[FACT: NFR-3]** | 20–30 s **[ESTIMATE]** |
| OCR speed (scanned page, PaddleOCR) | N/A (cloud OCR, network-bound) | ~1–3 s/page on CPU **[ESTIMATE]** | ~0.3–0.5 s/page on GPU **[ESTIMATE]** |
| Embedding speed (BGE-m3, batch of chunks) | N/A if cloud embeddings used (API-bound) | ~20–50 chunks/s on CPU **[ESTIMATE]** | ~100–300 chunks/s on GPU **[ESTIMATE]** |
| Indexing (ChromaDB HNSW insert) | Sub-second up to 100k vectors **[FACT: Section 25.2]**, applies to all profiles once vectors exist locally | same | same, until sharding needed beyond 100k |
| RAG end-to-end latency | <3 s target, cloud generation is typically fast (50–100+ tok/s) **[FACT: Section 10.2]**, network round-trip adds ~0.2–1 s | <3 s target **[FACT: NFR-1]**, achievable at reference hardware with streaming | <3 s comfortably, often <1.5 s with GPU-accelerated reranking |
| Chat token generation | 50–100+ tok/s (cloud) **[FACT]** | 5–20 tok/s (local, GPU-assisted) **[FACT: Section 10.2]** | 20–40 tok/s (better GPU, same model) **[ESTIMATE]** |
| 10 MCQ generation | <30 s **[FACT: NFR-2]**, easily met via cloud API | <30 s target, tight on CPU-only inference | <30 s comfortably |
| Concurrent users, single server | N/A (stateless per-request cloud calls scale independently) | 50 concurrent users on 4GB RAM **[FACT: NFR-4, stated for Hybrid Mode]** | 100+ concurrent, hardware-dependent **[ESTIMATE, Profile F]** |
| Background (Celery) throughput | Bound by cloud API rate limits | 1–2 documents/minute per worker (OCR-bound) **[ESTIMATE]** | 4–8 documents/minute with multiple GPU-backed workers **[ESTIMATE]** |

These are engineering estimates, not benchmark results — actual throughput depends heavily on document complexity (scanned vs. text-native, Arabic vs. Latin script density affecting OCR time), context length, and specific hardware/driver versions.

---

## 12. Scalability Matrix

| Deployment class | Maps to Profile | Concurrent users | Local AI models | Typical use case |
|---|---|---|---|---|
| Student Laptop | C (Local Small) | 1 | 1.5B–3B LLM, small embed/OCR | Individual student, offline study |
| Gaming Laptop | C→D boundary | 1–2 | 7B LLM (Q4), full local stack | Individual student wanting full local privacy |
| Desktop | D (Local Standard) | 1–5 (shared family/lab machine) | 7B LLM, full local stack incl. Neo4j optional | Power user, small study group |
| Workstation | E (Local Professional) | 5–15 | 14B–32B LLM, all PAL interfaces local incl. vision | Advanced user, small research lab |
| Single GPU Server | E→F boundary | 15–50 | 14B–32B via vLLM, single high-VRAM GPU | Small department pilot deployment |
| Multi-GPU Server | F (Research Server, min–rec) | 50–250 | 32B–70B via vLLM tensor parallelism | University department |
| Cloud VM (A/B hybrid) | A or B, hosted centrally | Scales with instance count (stateless) | None (all cloud) or embedding-only | Institution without local GPU budget, using managed cloud AI APIs |
| University Server | F (Research Server, ideal) | 250–500+ | Multiple concurrent 70B-class models, multi-tenant | Full university/multi-department rollout |

---

## 13. Cost Estimation

**Important pricing caveat:** as of mid-2026, both GPU and DRAM markets are experiencing a significant, AI-driven supply shortage. Consumer DDR5 RAM prices have roughly quadrupled since late 2025 (a 32GB DDR5-6000 kit that cost ~$80–100 in mid-2025 was running ~$400–470 by July 2026), and GPU prices — especially cards with 16GB+ VRAM — have risen 15–75%+ above MSRP depending on model and availability, with some flagship cards trading 2–3× their launch price. **The figures below reflect this elevated 2026 market and should be treated as a snapshot, not a stable baseline** — they will likely fall once DRAM/GDDR supply normalizes (analysts cited in current market coverage do not expect meaningful relief before 2027–2028).

| Profile | Hardware budget (USD, mid-2026 pricing) | What you're paying for |
|---|---|---|
| A — Cloud AI | **$300–800** (any capable laptop/mini-PC) + ongoing API costs (usage-based, not a one-time hardware cost) | No GPU, minimal RAM — cost is dominated by API usage, not hardware |
| B — Hybrid (Recommended) | **$600–1,200** (mid-range laptop/desktop, optional entry GPU) + modest ongoing API costs for the cloud-routed reasoning calls | Best cost/capability ratio — avoids the current GPU/VRAM price spike almost entirely |
| C — Local Small | **$700–1,400** (used/budget laptop + entry discrete GPU, or Apple M-series with 16GB unified memory) | Consumer laptop-class hardware; RAM/GPU inflation has the largest relative impact here |
| D — Local Standard | **$1,800–3,200** (desktop with RTX 4060 Ti/4070-class GPU, 32GB DDR5) | GPU (~$700–1,100 at current inflated pricing) and RAM (~$400+ for 32GB) are now the two largest line items — notably higher than pre-2026 estimates for equivalent capability |
| E — Local Professional | **$3,500–7,500+** (workstation-class CPU, RTX 4080 Super/5080-class GPU or better, 64GB RAM, NVMe RAID) | GPU alone can be $1,200–3,000+ at current market pricing depending on model/tier chosen |
| F — Research Server | **$40,000–250,000+** depending on tier (single A100 node at the low end to a multi-GPU H100 cluster at the high end) | Datacenter GPUs (A100/H100/L40S), server-grade RAM/CPU, and enterprise storage are priced on a different curve than consumer parts and are less exposed to the consumer DRAM/GPU shortage, but not immune to it |

**Value-for-money read:** Profile B (Hybrid) is the strongest value position specifically *because* of the 2026 hardware market — it sidesteps the GPU/RAM shortage almost entirely by keeping the expensive component (the reasoning LLM) on someone else's hardware, while still keeping document content processing local for privacy. Profile D, which the spec designs its own performance targets around, is currently the most cost-inflated tier relative to historical pricing, since it requires exactly the two components (16GB+ VRAM GPU, 32GB RAM) most affected by the current shortage.

---

## 14. Decision Matrix

| Profile | Difficulty | Cost | Performance | Offline Capability | Privacy | Recommended User | Maintenance | Power Consumption | Upgrade Path | Overall Recommendation |
|---|---|---|---|---|---|---|---|---|---|---|
| **A — Cloud AI** | Low | $ | High (fast cloud inference) | None | Low (all data leaves device) | Resource-constrained students, shared/lab computers | Low | ~15–30W (no local AI compute) | → B (add local components incrementally) | Good for zero-hardware-budget access; accept the privacy trade explicitly |
| **B — Hybrid** | Medium | $$ | High | Partial (ingestion works offline; chat needs network) | Medium-High (documents stay local, prompts go to cloud) | **Most users — this is the spec's own recommended default** | Medium | ~30–80W (embedding/OCR under load) | → D (add GPU, shift reasoning local) | **Best overall balance; start here unless privacy or connectivity is a hard constraint** |
| **C — Local Small** | Medium-High | $$ | Low-Medium (small model quality/speed trade-off) | Full | High | Students needing full offline privacy on existing/budget hardware | Medium (self-hosted stack) | ~30–65W | → D (upgrade GPU/RAM) | Solid for privacy-first students who accept reduced AI quality |
| **D — Local Standard** | High | $$$ | Medium-High (meets the spec's own NFR targets) | Full | High | Privacy-focused individual users with a GPU budget | Medium-High | ~150–250W under load (discrete GPU) | → E (bigger GPU, add Neo4j) | Matches the spec's design center — recommended if full local operation is a firm requirement |
| **E — Local Professional** | High | $$$$ | High | Full | High | Power users, small labs, thesis/demo environments needing headroom | High | ~300–450W under load | → F (multi-GPU, dedicated server) | Best for development, demos, and privacy-critical small-team use |
| **F — Research Server** | Very High | $$$$$ | Very High (multi-user, large models) | Full (self-hosted) | High (institution-controlled) | Universities, institutional pilots | Very High (dedicated ops/SRE effort) | 1–8+ kW depending on GPU count | Horizontal (add nodes) | Only justified once concurrent-user counts exceed what a single workstation (Profile E) can serve — not part of the spec's stated graduation-project scope |

---

*This document extrapolates hardware/software requirements from OpenLearn AI Technical Specification v4.0. Facts marked [FACT] are drawn directly from the spec; figures marked [ESTIMATE] are engineering calculations from stated facts using standard, industry-documented ratios (quantization arithmetic, known per-service memory footprints); figures marked [ASSUMPTION] extend beyond what the spec defines and are flagged for review, particularly Profile F, which represents a scale-out beyond the spec's explicitly single-machine design scope.*
