**OpenLearn AI Open-Source Ecosystem Research Report (as of early August 2026)**

This report synthesizes exhaustive multi-hop web research across GitHub, arXiv, Papers with Code, Hugging Face, awesome lists, research labs, blogs, benchmarks, and community discussions. Research prioritized free/open-source (or permissively licensed) projects suitable for an ambitious adaptive learning platform emphasizing local/self-hosted deployment, multilingual (including Arabic) support, document understanding, RAG/GraphRAG, student modeling, AI tutors, and production readiness. Iterations followed references recursively (e.g., from Docling/MinerU/Marker comparisons to Surya, PDF-Extract-Kit, GraphRAG variants, FSRS, agent frameworks, and self-hosting PaaS).

**Key caveats**: Stars, licenses, and activity change rapidly; verify latest GitHub/PyPI/HF cards. “Production readiness” is assessed from benchmarks, Docker support, community signals, and reported use. Arabic support is noted where explicitly tested or claimed (strongest in PaddleOCR/Surya/BGE-M3 family). Many projects are CPU-viable with optional GPU acceleration.

### 1. Executive Summary
The open-source landscape in 2026 is mature enough to build a high-quality, self-hosted adaptive learning platform without proprietary lock-in. Core strengths exist in:
- Document ingestion (Docling, MinerU, Marker/Surya, PaddleOCR).
- RAG/GraphRAG (LlamaIndex + LangChain/LangGraph, Microsoft GraphRAG, LightRAG, Graphiti).
- Local LLM serving (Ollama for simplicity, vLLM/llama.cpp for scale).
- Vector/hybrid search (Qdrant, Weaviate, pgvector, Chroma, Milvus).
- Adaptive/educational foundations (OATutor, OpenTutor, pyBKT/EduCDM, FSRS, Anki ecosystem).
- Self-hosting (Coolify, Dokploy, CapRover).

**Recommended core stack for OpenLearn AI (MVP → production)**:
- Ingestion: Docling (MIT, broad formats, RAG-friendly) or MinerU (high fidelity, especially Chinese/complex) + PaddleOCR/Surya for OCR/multilingual.
- Chunking/Embeddings: LlamaIndex hierarchical/semantic + BGE-M3 (or Arabic-tuned variants) / Qwen3-Embedding / nomic-embed.
- Storage/Retrieval: Qdrant or Weaviate (hybrid) + optional Neo4j/FalkorDB via Graphiti or LightRAG.
- Orchestration/Agents: LangGraph (stateful) + CrewAI (role-based tutors) or LlamaIndex workflows.
- Student modeling/Adaptive: pyBKT + FSRS + custom knowledge graphs.
- Inference: Ollama (dev/local) → vLLM (production multi-user).
- Auth/Deploy: Keycloak + Coolify/Dokploy on Docker/K8s.
- Frontend/Mobile: Next.js/React + React Native or Flutter; UI libs like shadcn/ui.
- Evaluation: RAGAS, custom educational metrics, Evidently for drift.

**Gaps**: Mature, production-grade open-source student modeling beyond BKT/DKT is thinner than commercial ITS; Arabic educational datasets and specialized adaptive algorithms need more community work; full end-to-end open LMS with deep AI tutors is emerging but fragmented (OATutor, OpenTutor, LearnHouse, LAMB).

**Risks**: License variations (some RAIL/AGPL/custom), GPU costs for high-volume indexing/OCR, evaluation of educational efficacy (beyond retrieval metrics), data privacy for student models.

**Roadmap suggestion**: Phase 1 (ingestion + basic RAG tutor), Phase 2 (GraphRAG + adaptive scheduling + quiz/flashcards), Phase 3 (multi-agent, analytics, mobile, collaboration), Phase 4 (self-improving student models + open ecosystem).

### 2. Category-by-Category Highlights
(High-value projects only; full evaluation criteria applied where data available. “Must Use / Evaluate / Optional / Not Recommended” relative to OpenLearn AI goals.)

**1–4. PDF Processing / OCR / Document Layout / Markdown Extraction**  
- **Docling** (IBM/LF AI & Data): MIT. Parses PDF/Office/HTML/images → structured Markdown/JSON/DocTags with layout, tables (TableFormer), reading order, OCR. Excellent CPU performance and RAG readiness. High stars/activity. Local/Docker. Arabic via OCR backends. **Must Use**. Fits: Document → structured knowledge pipeline.  
- **MinerU** (OpenDataLab/Shanghai AI Lab): High-fidelity (formulas, complex tables, 84+ languages). Evolving license (more permissive). Strong on academic/scanned. GPU preferred for speed. **Evaluate / Must Use** for fidelity.  
- **Marker** (Datalab) + **Surya OCR 2**: Fast, accurate layout/OCR/tables/reading order (90+ languages, Arabic ~72.7% on internal multilingual). Marker 2 strong throughput. License notes on weights (OpenRAIL-M variants). **Evaluate**.  
- **PaddleOCR** (incl. PP-OCRv5 / PaddleOCR-VL): Apache-2.0. 100+/109 languages (excellent Arabic/Chinese). Layout, tables, formulas. Lightweight. **Must Use** for multilingual/OCR.  
- Others: Unstructured, PyMuPDF/pymupdf4llm (fast digital), Nougat (academic), olmOCR, PDF-Extract-Kit, HURIDOCS VGT (high accuracy claims).  
Architecture fit: PDF/Image → OCR/Layout → Markdown/JSON → Chunking.

**5. Chunking**  
LlamaIndex (hierarchical, semantic, Auto-Merging), LangChain (recursive, semantic), Chonkie, Docling splitters, late-chunking research patterns. **Must Use** LlamaIndex primitives. Fits post-extraction.

**6. Embeddings**  
- BGE-M3 (BAAI/FlagEmbedding): Multilingual (100+), dense+sparse+multi-vector, 8k context, MIT. Arabic-tuned variants exist (e.g., pruned arabic-english-bge-m3). **Must Use**.  
- Qwen3-Embedding family, nomic-embed-text-v2-moe, embeddinggemma, multilingual-e5, mDenseOn/mLateOn, sentence-transformers ecosystem. Local, open weights. Arabic support strong in BGE/Paddle/Qwen families.  
Fits: Chunk → Embedding → Vector store.

**7–8. Vector Databases / Hybrid Search**  
Qdrant (Rust, Apache-2.0, excellent filters/hybrid, self-host), Weaviate (hybrid native), Chroma (dev/embedded), Milvus, pgvector (Postgres), FAISS, OpenSearch/Elasticsearch (BM25+vector). Hybrid via RRF/fusion in LlamaIndex/LangChain. **Must Use** Qdrant or Weaviate + BM25. Fits retrieval layer.

**9–11. RAG Frameworks / GraphRAG / Knowledge Graph**  
- LlamaIndex (retrieval specialist), LangChain + LangGraph (orchestration/agents). **Must Use**.  
- Microsoft GraphRAG (MIT, community detection/summaries; expensive indexing).  
- LightRAG (cheaper dual-level).  
- Graphiti (Zep; temporal knowledge graphs, Apache-2.0, Neo4j/FalkorDB; agent memory).  
- Cognee, flexible-graphrag, unstructured2graph, Neo4j GraphRAG toolkit, Vector Graph RAG (Milvus-only multi-hop).  
**Evaluate** Graphiti/LightRAG for student knowledge graphs and multi-hop tutoring. Fits: Vector/Graph index → Tutor Agent.

**12–14. Student Modeling / Adaptive Learning / Recommendation**  
- OATutor (UC Berkeley CAHL; open adaptive tutoring, BKT, A/B testing). **Must Use / Evaluate**.  
- OpenTutor, LearnBuddy, PersonalLearningPro/EduAI, LAMB (learning assistants + LTI/Moodle).  
- pyBKT, EduCDM, DKT variants (PyTorch). FSRS for scheduling.  
Knowledge-graph-based personalization via Graphiti + embeddings. Emerging multi-agent adaptive systems. Fits core adaptive engine.

**15–17. Quiz Generation / Flashcards / Spaced Repetition**  
Anki (FSRS default), FSRS algorithm implementations, openflashcards (FSRS + TTS, self-hosted), Mnemosyne, AI generation via LLMs + RAG. OpenTutor/OATutor include quiz/flashcard generation. **Must Use** FSRS + Anki ecosystem or self-hosted FSRS. Fits practice layer.

**18–19. AI Agents / Workflow Engines**  
LangGraph (stateful graphs; production), CrewAI (role-based crews for tutors), AutoGen/AG2 (conversational), LlamaIndex Workflows, Pydantic AI. **Must Use** LangGraph + CrewAI for multi-agent tutors (researcher, explainer, assessor). Fits orchestration.

**20–25. Backend / Frontend / UI / Mobile / Auth / AuthZ**  
Backend: FastAPI, Django, NestJS. Frontend: Next.js/React, Vue, Svelte; shadcn/ui, Radix. Mobile: React Native, Flutter, Capacitor. Auth: Keycloak, Authentik, Ory, Supabase Auth (self-hostable). Authorization: Casbin, OPA/Gatekeeper. Fits full-stack.

**26–29. Deployment / Self-Hosting / Docker / K8s**  
Coolify (feature-rich, multi-server, Apache-2.0), Dokploy (lightweight Compose), CapRover (mature Swarm), Dokku. Docker Compose everywhere; K8s via standard operators. **Must Use** Coolify or Dokploy.

**30–34. Monitoring / Logging / Evaluation / Observability / Analytics**  
Prometheus + Grafana, Loki, OpenTelemetry, LangSmith/LangFuse (self-host options), RAGAS/DeepEval for RAG, Evidently/WhyLabs for drift, Learning Locker (xAPI). Fits ops layer.

**35–39. Open Source LMS / AI Education / Notes / Whiteboard / Collaboration**  
LearnHouse, ClassroomIO, Moodle (LTI), Open edX; LAMB, Open TutorAI; Obsidian/Logseq/AppFlowy (notes); Excalidraw, tldraw (whiteboard); Yjs/CRDT or Liveblocks alternatives for collab. Fits platform shell.

**40–46. Search / Browser Automation / Local LLM / GPU Inference / Speech / Image / Video**  
Meilisearch/Typesense; Playwright/Selenium; Ollama (easiest), llama.cpp (portable/quantized), vLLM (throughput), SGLang, TGI, TensorRT-LLM. STT: Whisper; TTS: Piper/Coqui. Image: Stable Diffusion/ComfyUI; Video: ffmpeg + open models. **Must Use** Ollama → vLLM progression.

**47–48. Datasets / Benchmarks**  
Educational: various ITS/BKT datasets, EdNet, ASSISTments; OCR: DocLayNet, etc.; QA: HotpotQA, MuSiQue, educational QA; Arabic: specific MIRACL/Arabic RAG leaderboards. Benchmarks: olmOCR-bench, GraphRAG-Bench, MTEB, RAGAS, educational mastery metrics. Monitor for Arabic educational corpora.

**49–50. Development Productivity / Hidden Gems**  
OpenCode/Claude Code alternatives, Cursor-like open tools, agentic coding (Aider, Continue). Hidden gems: Graphiti (temporal), flexible-graphrag, Chunky (RAG prep toolkit), HURIDOCS layout models, compact Arabic embeddings, FSRS pure implementations, OpenTutor (block-based adaptive).

### 3. Architecture Mapping (Example Pipeline)
```
User Upload (PDF/Image/Notes)
    ↓
PDF/OCR/Layout (Docling / MinerU / PaddleOCR + Surya)
    ↓
Markdown / Structured Doc (DoclingDocument)
    ↓
Chunking (LlamaIndex hierarchical/semantic + late chunking)
    ↓
Embeddings (BGE-M3 / Arabic variant) + Optional KG Extraction
    ↓
Vector DB (Qdrant hybrid) + Graph Store (Graphiti / LightRAG / Neo4j)
    ↓
Hybrid / GraphRAG Retrieval
    ↓
Student Model (pyBKT + knowledge graph state + FSRS)
    ↓
Multi-Agent Tutor (LangGraph + CrewAI: Explainer / Quizzer / Adapter)
    ↓
Quiz/Flashcard Generation + Spaced Practice
    ↓
Analytics / Dashboard + Adaptive Path Update
```
Backend (FastAPI) + Frontend (Next.js) + Auth (Keycloak) + Deploy (Coolify/Docker) + Inference (vLLM/Ollama). Mobile clients consume APIs. Collaboration via CRDTs or real-time layers.

### 4–6. Comparison Tables, Stack Recommendations & Best Combinations
**PDF Pipeline Comparison (qualitative from 2025–2026 benchmarks)**: Docling (best balance/speed/CPU/MIT), MinerU (fidelity/complex), Marker/Surya (speed/multilingual), PaddleOCR (languages/Arabic).  
**RAG**: LlamaIndex (retrieval) + LangGraph (agents).  
**Local LLM**: Ollama (start) → vLLM (scale).  
**Self-host**: Coolify (features) or Dokploy (lightweight).  

**Best combinations**:
- Privacy-first local: Docling + BGE-M3 + Qdrant + Ollama + FSRS + OpenTutor-inspired UI.
- High-fidelity multilingual: MinerU/PaddleOCR + Graphiti + vLLM + Coolify.
- Adaptive research: OATutor + pyBKT + GraphRAG + LangGraph.

### 7–9. Missing Components, Risks, Roadmap
**Missing**: Unified open educational knowledge graphs with mastery tracking; large high-quality Arabic adaptive datasets; standardized open evaluation for tutor efficacy (beyond RAG metrics); seamless offline-first mobile with full local LLM.  
**Risks**: Indexing cost/time for GraphRAG; model license restrictions; student data privacy/compliance; evaluation gaps leading to ineffective adaptation; community fragmentation.  
**Roadmap**:
1. Ingestion + basic RAG tutor (1–2 months).
2. Hybrid/GraphRAG + quiz/flashcards/FSRS (next).
3. Student models + multi-agent + analytics.
4. Full LMS features, mobile, collaboration, open ecosystem contributions.
5. Continuous eval + Arabic specialization + self-improving agents.

### 10–11. Top Repositories & Hidden Gems (Representative)
**Top (by impact/stars/activity relevance)**: Docling, MinerU, PaddleOCR, Surya/Marker, LlamaIndex, LangChain/LangGraph, Microsoft GraphRAG, LightRAG, Graphiti, Qdrant, BGE-M3/FlagEmbedding, Ollama, vLLM, llama.cpp, Coolify, OATutor, Anki/FSRS, CrewAI, Keycloak, etc. (full ranked list exceeds space; prioritize the “Must Use” above).  

**Hidden gems**: Graphiti (temporal agent memory), flexible-graphrag, Chunky, OpenTutor, HURIDOCS layout, compact Arabic BGE variants, pure FSRS libs, Vector Graph RAG (Milvus multi-hop without separate graph DB), LAMB, various EduCDM tools.

### 12. Future Technologies to Monitor
Late-interaction/multi-vector embeddings, diffusion-based OCR (e.g., MinerU-Diffusion), compact domain-adapted extractors (Meno-Lite style), bi-temporal/agent-native KGs, psychometric + LLM hybrid student models, on-device multimodal tutors, open educational foundation models, standardized xAPI/Caliper + AI event schemas.

### 13. References
Primary sources include arXiv papers (Docling, MinerU), GitHub repos (linked via searches), benchmark posts (olmOCR-bench, GraphRAG-Bench), comparison blogs (2025–2026), Hugging Face model cards, and community discussions. Specific citations appear inline from tool results (e.g., [web:0] Docling arXiv, [web:15] GraphRAG tools, [web:31] OATutor, [web:60] local LLM comparison, [web:70] Surya 2, [web:74] Coolify comparisons, etc.). Always re-verify live repositories for latest stars, licenses, and commits.

This mapping provides a solid foundation to accelerate OpenLearn AI. Prioritize Docling/PaddleOCR + LlamaIndex/LangGraph + Qdrant + Ollama/vLLM + FSRS/OATutor foundations for fastest high-quality progress. Further targeted deep dives (e.g., exact Arabic benchmarks or specific category stars) can refine any section.
