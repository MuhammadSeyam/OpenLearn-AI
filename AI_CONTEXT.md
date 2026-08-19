# AI_CONTEXT.md — OpenLearn AI

Companion document for AI assistants and new contributors. Read this file first; it summarizes the entire repository so you can become productive without reading every document. Facts are sourced from the repository. Anything uncertain is marked **Unknown**.

> **One-line summary:** OpenLearn AI is a spec-first, pre-alpha, open-source (AGPL-3.0) Arabic-first adaptive learning platform — no working product yet, but an unusually rigorous documentation and planning corpus.

---

## 1. Project Overview

OpenLearn AI turns study material (PDFs, slides, notes, scans) into an adaptive learning loop rather than a static chat window. It ingests documents, builds a knowledge graph of concepts and prerequisites, tracks per-concept student mastery, and uses that model to recommend what to study next and when to review it (spaced repetition) before it is forgotten.

Positioning (from `README.md`):

| | Chat-with-PDF tools | Closed adaptive platforms | OpenLearn AI |
|---|---|---|---|
| Tracks per-concept mastery | ✗ | ✓ | ✓ |
| Prerequisite-aware study paths | ✗ | Partial | ✓ |
| Spaced repetition scheduling | ✗ | Sometimes | ✓ |
| Runs fully offline | ✗ | ✗ | ✓ |
| Open source | ✗ | ✗ | ✓ (AGPL-3.0) |
| Arabic-first multilingual support | ✗ | ✗ | ✓ |

**Core philosophy:** every AI-facing component (LLM reasoning, embeddings, OCR, vector storage) sits behind a **Provider Abstraction Layer (PAL)** so the same codebase can run fully offline, fully on managed cloud APIs, or any mix — a configuration choice, not a fork.

**Why it exists:** existing chat-with-your-PDF tools remember nothing between sessions; closed adaptive platforms (institution-priced) exclude individual students in underserved language markets. The project targets those students.

**Target outcome (from `planning/Roadmap/MASTER_ROADMAP.md`):** a graduation-defense product (v1.0, June 2027) engineered "startup-grade," deployable post-graduation without re-architecture.

---

## 2. Architecture (documented design; not yet implemented)

Content pipeline (from `README.md` and `docs/design/OpenLearn_AI_v4_Technical_Specification.md`):

```
ingestion → knowledge base → knowledge graph → student model → learner profile
    → adaptive engine → generation → analytics   (with feedback loops)
```

- **Modular monolith** (single FastAPI process; services communicate via interface calls, NOT microservices — see ADR, which does not exist yet).
- **Provider Abstraction Layer (PAL):** all AI calls (reasoning/embedding/OCR/speech/vision/ranking/vectorDB) go through swappable provider interfaces. Nothing calls a vendor SDK directly inside a service.
- **C4 target:** Browser → Next.js 16 → FastAPI (9 modules) → PAL → PostgreSQL 16 + ChromaDB + Redis + MinIO + Neo4j; Celery Doc/Embed workers for async jobs.
- **Three deployment modes** (same codebase, config presets): **Local** (fully on-device, 16GB RAM, GPU recommended), **Hybrid** (local core + cloud augmentation, 8GB RAM; recommended), **Cloud** (fully managed APIs, 4GB RAM).
- **Documented default model stack** (Tech Spec §10.3): Qwen2.5 7B via Ollama (reasoning), BGE-M3 (embeddings), PaddleOCR v4 (OCR), bge-reranker-v2-m3 (reranking), ChromaDB (vector store), Piper (TTS), Whisper medium (STT).
- **Adaptive engine (Tech Spec §16):** fuses Student Knowledge Model (SKM, per-concept mastery) + Cognitive/Skill Profile (CSP) + Knowledge Graph (prerequisites); 4-step decision (candidate generation → prerequisite check → priority scoring → recommendation). SM-2 spaced repetition + CAT (Computer-Adaptive Testing) exam simulator. Mastery starts heuristic, upgrades to Bayesian Knowledge Tracing (BKT) as data accumulates.
- **Multi-store DB (Tech Spec §21):** entities include USER, CSP, MATERIAL, CONCEPT, SKM_RECORD, REVIEW_ITEM, QUESTION (with BKT fields).
- **Key API endpoints (Tech Spec §22):** `/materials/upload`, `/chat/session`, WS `/ws/chat/{id}`, `/exams/start`, `/recommendations/today`, `/knowledge-graph/{id}`. Roles: Student, Teacher, Admin, Guest, Contributor.
- **Documented stack (Tech Spec §26 / roadmap):** Next.js 16, React 19, TypeScript 5 strict, Tailwind CSS 4 + shadcn/ui, Zustand + TanStack Query; FastAPI / Python 3.12, Pydantic v2, structlog; PostgreSQL 16, Qdrant, Neo4j, Redis, MinIO, ChromaDB; LiteLLM gateway; PaddleOCR; BGE-M3; Celery + Redis; Docker + k3s; GitHub Actions; Grafana/Prometheus/Loki/Sentry.

> Note: Qdrant (roadmap) vs ChromaDB (Tech Spec §10.3 defaults) appear in different documents. The roadmap's fallback F-1 is Qdrant→pgvector. This discrepancy is unresolved; treat it as **Unknown** which is canonical.

---

## 3. Current Status

**Pre-alpha. Spec-first by design.** Documentation and planning are deliberately ahead of implementation (README: "this is a deliberate spec-first approach, not neglect"). Expected frequent breaking changes until v1.0.

What exists vs. what is empty (refreshed 2026-08-16 foundation cleanup — see `docs/repository-foundation-audit.md`):

| Area | Status |
|---|---|
| `docs/design/` | Substantive: v4 Technical Specification (1,377 lines), System Requirements (402 lines), User Requirements Guide (202 lines), DeveloperGuide (updated to match real layout) |
| `planning/Roadmap/` | Substantive: 44-WEEK-EXECUTION-PLAN.md (schedule authority), MASTER_ROADMAP.md (strategy), ROADMAP_GUIDE_AR.md (companion) |
| `planning/` sprints | Sprint-01.md (retrospective from git history), Sprint-02.md (live scope) — previously empty |
| `docs/ai-reports/` | **Moved** to `docs/research/raw/ai-reports/` (non-authoritative raw research) |
| `docs/research/` | README index + OCR.md flowchart; former empty stubs deleted; raw/ archive |
| `backend/` | FastAPI skeleton (`app/main.py` hello-world + 1 smoke test); deps curated (fastapi, uvicorn + dev pins) |
| `frontend/` | Next.js 16 + React 19 + Tailwind 4 + shadcn scaffold; design-system preview page; no RTL/i18n yet |
| `experiments/` | OCR benchmark (`ocr-benchmark/`: pinned uv project, 4-doc pilot dataset w/ manifest + provenance, package skeleton), PaddleOCR notebook (paths fixed), HTML prototypes |
| `infra/` | docker-compose.dev.yml (backend + postgres 16), backend Dockerfile |
| `.github/` | CI workflow (backend lint+pytest; frontend lint+typecheck+build), CODEOWNERS, PR template |
| `docs/adr/` | ADR-0001..0004 (monolith, doc authority, OCR benchmark, vector-store deferral) |

**CI, tests and lint exist and pass** (backend: ruff + pytest, verified in clean venv; frontend: lint/typecheck/build in CI — this workstation has no Node). Empty placeholder files were filled or deleted in the 2026-08-16 cleanup.

---

## 4. Important Files & Paths

### Real, substantive files
- `README.md` — project overview, capabilities, deployment modes, doc map, dev status.
- `docs/design/OpenLearn_AI_v4_Technical_Specification.md` — system source of truth (30 sections / 5 parts).
- `docs/design/DeveloperGuide.md` — contributor conventions, repo layout rules, coding standards, git workflow, ADR format, PR checklist, §19 suggested improvements.
- `docs/design/OpenLearn_AI_System_Requirements_and_Deployment_Profiles.md` — hardware profiles A–F, tagged `[FACT]`/`[ESTIMATE]`/`[ASSUMPTION]`; notes mid-2026 GPU/DRAM shortage.
- `docs/design/OpenLearn_AI_User_System_Requirements_Guide.md` — user-facing install guide (3 editions).
- `planning/Roadmap/MASTER_ROADMAP.md` — SSOT roadmap (see §8).
- `planning/Roadmap/ROADMAP_GUIDE_AR.md` — Arabic companion guide for student readers.
- `planning/team-roles/TEAM_HANDBOOK_v1.1.md` — values, pods, processes, 20 working agreements.
- `docs/ai-reports/*` — OSS ecosystem research (best-in-class tool recommendations, incl. Studyield as reference architecture).
- `docs/research/OCR.md` — document→OCR→Docling→chunking→KG→vector-DB pipeline flowchart.
- `backend/app/main.py` — FastAPI hello-world stub (7 lines).
- `experiments/prototypes/Prototype.html` (3,268 lines) — advanced Arabic RTL UI prototype: Tailwind CDN, Chart.js, SVG knowledge graph with typed edges (prerequisite/is-a/part-of), dark mode, flashcards, forgetting-curve chart, heatmap.
- `experiments/prototypes/OpenLearn_AI_Prototype.html` (915 lines) — earlier "lamp in the library" design-token prototype.
- `experiments/OCR/paddle-test/GPU-version-test.ipynb` — PaddleOCR English + Arabic experiment (with `arabic_reshaper.reshape()` + `bidi.algorithm.get_display` post-processing pattern).
- `experiments/OCR/benchmarks/` — sample images (`1.png`, `2.png`, `ar.png`) + `Data+Structre+lect1.pdf` (data-structures lecture slides).
- `presentations/demo/OpenLearn_AI_Presentation (1).html` — demo slide deck.
- `scripts/setup_project_structure.sh` — the skeleton generator that created the empty scaffolding.
- `LICENSE` — AGPL-3.0.

### Empty files & broken references — RESOLVED (2026-08-16 foundation cleanup)
Formerly-empty files were filled (architecture SystemArchitecture/DataFlow, root CHANGELOG/CONTRIBUTING/CODE_OF_CONDUCT, Sprint-01/02) or deleted (empty research/design stubs, mode docs). README links repaired to real paths; ADRs live at `docs/adr/`. Point-in-time record: `docs/repository-foundation-audit.md`.

### Known defects — RESOLVED or tracked
- `backend/requirements.txt` (formerly a UTF-16 pip-freeze with Windows deps; earlier re-encoded, then curated 2026-08-16 to `fastapi==0.138.1` + `uvicorn==0.49.0` only).
- `requirements-dev.txt` `httpx2` — investigated: **not a typo**; starlette 1.6 TestClient requires the httpx2 package line. Now pinned `httpx2==2.10.0`.
- OCR notebook absolute `/run/media/...` paths — fixed to repo-relative; notebook outputs retain historical logs.
- Remaining human decisions: OL-C-004 PDF rights (see benchmark `docs/provenance.md`); vector-store choice (ADR-0004, due W4); roadmap capacity re-baseline.

---

## 5. Technologies

### Documented/planned (not implemented)
- **Backend:** FastAPI (Python 3.12), Pydantic v2, Celery + Redis, structlog, SQLAlchemy/Alembic (implied by `migrations/`; not confirmed). LiteLLM gateway for provider routing.
- **Frontend:** Next.js 16 (App Router), React 19, TypeScript 5 strict, Tailwind CSS 4 + shadcn/ui, Zustand (local state), TanStack Query (server state).
- **Data:** PostgreSQL 16 (primary), Qdrant (vector), Neo4j (knowledge graph), ChromaDB (dev vector store), MinIO (object storage), Redis (cache/queue).
- **AI:** Ollama + Qwen2.5 7B, BGE-M3 embeddings, bge-reranker-v2-m3, PaddleOCR (Arabic), Piper TTS, Whisper medium. Research candidates: MinerU, Marker 2, Docling, Surya, Qari-OCR, Baseer.
- **ML modeling:** pyBKT (v1 mastery, DKT later), FSRS (spaced repetition scheduler).
- **Infra:** Docker, k3s/Kubernetes, Nginx, GitHub Actions, Grafana + Prometheus + Loki + Sentry.

### Actually present in repo
- Python 3.12 (backend stub + OCR notebook), FastAPI, Jupyter, PaddleOCR 3.0.3, PaddlePaddle GPU 3.0.0, plain HTML/CSS/JS prototypes.

---

## 6. Workflows & Conventions

Codified in `docs/design/DeveloperGuide.md`. **Documented but not yet enforced by tooling** (no pre-commit, no CI).

- **Repo philosophy:** separation by concern — code, docs, research, planning, experiments are deliberately kept apart. Nothing under `experiments/` may be imported by `backend/`, `frontend/`, or `services/`. Research ≠ decisions (ADRs are decisions). Experiments are disposable; code is never moved from `experiments/` into production — it is reimplemented to standards.
- **Git workflow (documented):** trunk-based + short-lived branches `feature/|bugfix/|hotfix/|release/<scope>-...`; squash-merge PRs into `develop`; Conventional Commits (`feat|fix|docs|refactor|test|chore|perf|build|ci`); commit-msg hook. **Currently only `main` exists; no CI, no branch protection.**
- **Python standards:** Python 3.12; `black` + `ruff` + `mypy`; mandatory type hints; Pydantic v2 models at all service/API boundaries; no bare `except:`; `structlog` logging. FastAPI: thin handlers, explicit `response_model`, long ops → Celery (never sync in handlers).
- **Service layout:** each `services/*` module = `interface.py` (contract) + `service.py` (impl) + `models.py` (Pydantic) + `repository.py` (data access) + tests. Services depend only on each other's interfaces; AI provider calls only via PAL.
- **Frontend standards:** TS strict, no implicit `any`; function components with typed props; TanStack Query for server state, Zustand for local UI (never mixed); feature code under `features/<feature>/`.
- **Naming:** Python `snake_case` files/functions/vars, `PascalCase` classes; TS `camelCase` functions/vars, `PascalCase` components/types, filenames match component names; directories `kebab-case` everywhere.
- **Docs standards:** never duplicate content — link instead; Tech Spec changes only on system-design changes; every ADR linked from `SystemArchitecture.md`.
- **ADRs:** `docs/architecture/ADR/NNNN-short-title.md`, numbered, with Status/Context/Decision/Consequences/Alternatives Considered. None exist yet.
- **Datasets rules:** nothing > a few MB or sensitive committed; each dataset subfolder needs a README with source/license/use.
- **Dev workflow:** idea → discussion → research → architecture → implementation → testing → docs → review → merge. Docs-first.
- **Planned CI (roadmap, not built):** 7 PR stages (lint, unit, integration, build, docs check, license scan, coverage), staging auto-deploy, tag→prod manual approval. Coverage targets: 80% (auth/course/ingestion, W8), 40% (W20), 60% (W38). RAG CI evals from W17; load test (50 concurrent, P95<2s) W39; OWASP+Semgrep+pen test W40.

---

## 7. Key Design Decisions & Research Positions

The "why" is documented in research + ai-reports; formal ADRs are pending (none exist yet).

- **Modular monolith over microservices** — simpler ops, hard interface boundaries.
- **Provider Abstraction Layer** — provider-agnostic; local/cloud/hybrid by config. LiteLLM as the gateway.
- **OCR:** PaddleOCR primary (strong Arabic support + Arabic post-processing via arabic_reshaper/bidi); research shortlist PaddleOCR / Surya / Qari-OCR (WER 0.160 on Arabic diacritics) / Baseer (WER 0.25); layout parsing via Docling (default) / MinerU (fallback); Marker license (GPL+RAIL-M) flagged as risk.
- **Embeddings:** BGE-M3 default; bge-reranker-v2-m3 reranking.
- **RAG:** LlamaIndex/LangChain/Haystack consolidated; LightRAG (~1/6000th GraphRAG indexing cost) candidate; LazyGraphRAG noted.
- **Vector DB:** Qdrant default (roadmap) / ChromaDB dev default (spec) / pgvector for Postgres-centric fallback; Weaviate hybrid noted.
- **Student modeling:** heuristic mastery first, pyBKT (Bayesian Knowledge Tracing) as data accumulates, DKT later; FSRS for scheduling.
- **Quiz/adaptivity:** build quiz generation in-house (research finding); CAT-style exam simulation; OATutor/OpenTutor as references.
- **Arabic-first:** Arabic OCR is a documented top risk and a differentiator; KITAB-Bench cited for Arabic OCR evaluation.
- **License:** AGPL-3.0 chosen for open source; acknowledged to constrain commercial adoption.
- **Hidden-gem references:** Studyield (FastAPI+Next.js+pgvector+multi-agent+MCP reference architecture), Graphiti, OpenTutor, flexible-graphrag, Chunky, HURIDOCS.

---

## 8. Roadmap Summary (SSOT: `planning/Roadmap/MASTER_ROADMAP.md`)

- **Horizon:** 44 weeks, 3 Aug 2026 → 6 Jun 2027. Version 1.0, approved 2026-08-03. Status: pre-kickoff (project is at the very start; ~2 weeks before/at W1).
- **Team:** 9 engineers / 4 pods — A Backend (2), B AI/ML (3), C Frontend (2), D DevOps+QA+Eval (2) + rotating TPM/Firefighter/Docs Owner. **1,820 usable hours** (pessimistic, ~60% productivity multiplier for university workload).
- **Delivery confidence:** ~70% for v1.0 by W44 — "honest for a student team building an AI product in 10 months."
- **Critical date:** **W16 (21 Nov 2026) = v0.4 Thin MVP** — pre-loaded PDF, no auth, single chat box, answer with citations. If it ships, the plan absorbs almost any problem; if not, everything slips.
- **Phases:** P0 Pre-Flight (W1–4, v0.1 + CI + 5 ADRs) → P1 Foundations (W5–8, v0.2 auth/courses/upload) → P2 AI Pipeline (W9–20, v0.4 Thin MVP W16 + v0.5 Tier 1 Freeze W20) → P3 Knowledge & Cognition (W21–30, v0.7 + Tier 2 Freeze) → P4 Adaptation & Analytics (W31–38, v0.9 + Feature Freeze) → P5 Hardening (W39–42, v1.0-rc + Code Freeze) → P6 Graduation (W43–44, v1.0).
- **5 quality gates:** v0.4 Thin MVP (W16), Tier 1 Architecture Freeze (W20), Tier 2 Architecture Freeze (W30), Feature Freeze (W38), Code Freeze (W42).
- **Milestones:** 15 integration (IM), 15 testing (TM), 16 documentation (DM), 8 demo-data (DDM), 13 graduation-prep (GPM) milestones; 4 weeks critical-path slack (W38–44 have zero).
- **Version timeline:** v0.1 (W6, 12 Sep 2026) → v1.0 (W44, 5 Jun 2027, graduation).
- **Interface contracts:** 10, frozen progressively at W8/W20/W30.
- **Key risks (of 32; score = L×I, ≥12 red):** R-01 OCR (16), R-02 RAG (16), R-16/R-17 exam crunch (16/12), R-18 MVP slip (15), R-03 adaptive engine (12), R-07 LLM provider (12), R-20 Feature Freeze (12), R-21 dropout (12), R-22 Pod B overload (12). R-12 Pod D bus-factor structurally reduced 16→8.
- **6 contingency playbooks (PB-01..06)** and **7 scoped fallbacks (F-1..F-7):** Qdrant→pgvector, Neo4j→JSONB, BGE-M3→OpenAI embeddings, cost→4o-mini/DeepSeek/GLM-4-flash, Celery→Inngest, PaddleOCR→Google Document AI, ML→rule-based. Invoked independently, never as a full-stack swap.
- **Out-of-scope (15 signed items):** mobile app, multi-tenant, SSO/SAML, real-time collaboration, proctoring, etc.
- **Graduation prep:** 30-min presentation arc (8 segments), demo data (3 courses × 5–10 PDFs, 5 seeded students, 20 quizzes, 5 known-good questions), 4 dry-runs.
- **Note:** `TEAM_HANDBOOK_v1.1.md` differs slightly from the roadmap on team structure (fixed TPM, docs folded into pod leads, no standing firefighter). The handbook itself declares the roadmap the SSOT on contradiction.

---

## 9. Constraints & Considerations

- **No budget:** the project is built by undergrad students with no funding. Cost-sensitive choices dominate (self-hosted open models, free tiers, fallback to cheap models). AI-cost reports in `docs/ai-reports/` and the SaaS blueprint analyze monthly cost ($0 free-tier scenario documented).
- **University calendar:** productivity haircut, exam-crunch buffers, graduation deadline drives the plan.
- **Hardware reality:** mid-2026 GPU/DRAM shortage noted in requirements doc (32GB DDR5 ≈ $400–470). Deployment profiles assume modest hardware (Local mode 16GB RAM + GPU recommended).
- **Licensing:** AGPL-3.0 — open but commercially restrictive (acknowledged tradeoff).
- **Language focus:** Arabic OCR + RTL UX are differentiators and top risks.
- **Team bus-factor:** Pod D (DevOps/QA) is 2 people; flagged as structural risk.
- **No budget for compute at scale** → everything must fit free tiers during development; production cost depends on the chosen deployment profile.

---

## 10. Current Repository Snapshot

> **Refresh note (2026-08-16):** the snapshot below predates the frontend
> scaffold, CI, and the foundation cleanup; it is retained for history. The
> tables in §3/§4 above are the current state, and
> `docs/repository-foundation-audit.md` is the authoritative point-in-time
> record of the cleanup. Gaps #3 (CI), #4 (broken references), #5 (empty
> stubs), #6 (requirements corruption), #9 (.gitignore), #12 (sprints) and
> #13 (empty governance docs) are resolved; #2 (ADRs) is resolved for
> foundation decisions (0001–0004); the rest remain open and tracked in
> `planning/Sprint-02.md`.

**State at last commit (`a638548`, 5 Aug 2026; clean working tree; 47 tracked files on `main`):** the project is at the very beginning of its 44-week plan. Everything about the *implementation* surface is still scaffolding created by `scripts/setup_project_structure.sh`; the value in the repo today is the documentation, roadmap, research, and UI prototypes.

**Unfinished work / open gaps discovered:**
1. **No product code:** `backend/` is a hello-world stub; `frontend/`, all 9 `services/`, `models/`, `infrastructure/`, `datasets/`, `.github/` are empty. The W16 Thin MVP has not started.
2. **No ADRs** — 5 are due at W4 per the roadmap.
3. **No CI/CD** — roadmap specifies GitHub Actions in detail; `.github/workflows/` is empty.
4. **Broken doc references:** README/DeveloperGuide link to `docs/project/*`, root `ROADMAP.md`, and `docs/architecture/*.md` files that are absent or 0-byte. Either the paths or the content need fixing.
5. **17+ empty 0-byte stub files** across `docs/architecture/`, `docs/design/`, `docs/research/`, `planning/`, and root.
6. **`backend/requirements.txt` is corrupt** for pip use (UTF-16LE/CRLF pip-freeze dump) — needs regeneration as UTF-8, split into the intended `requirements/` layout.
7. **No tooling configs:** no `pyproject.toml`, `package.json`, `tsconfig.json`, lint configs, or pre-commit hooks — despite DeveloperGuide specifying them.
8. **No tests** anywhere; `backend/tests/` empty.
9. **`.gitignore` incomplete** relative to DeveloperGuide promises (no `node_modules/`, `.next/`, `.env`, model weights).
10. **Discrepancy:** Qdrant (roadmap) vs ChromaDB (Tech Spec) as the vector store default — **Unknown** which wins.
11. **`docs/api/` and `docs/architecture/ADR/` are empty**, though the API reference and ADR program are part of the roadmap's doc gates.
12. **`planning/Sprint-01.md` / `Sprint-02.md` empty** — sprint planning hasn't been written despite W1–W8 planning docs.
13. **`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `CHANGELOG.md` are empty** placeholders (README links to them).

**Most productive next steps for a contributor** (per README + roadmap): implement a single `services/*` module against its documented interface (following the `interface.py`/`service.py`/`models.py`/`repository.py` layout), review/propose an ADR, or improve Arabic OCR/embedding research. Do NOT open large unscoped PRs — module boundaries are intentional and the repository is spec-first.
