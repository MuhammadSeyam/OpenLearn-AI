
# Developer Guide

Internal reference for contributors working on OpenLearn AI. This document describes how the repository is organized, how development work should flow through it, and what conventions keep it maintainable as the team and codebase grow. It assumes familiarity with the [README](../../README.md) and the [Technical Specification](OpenLearn_AI_v4_Technical_Specification.md) — this guide does not repeat either.

This document is not user-facing. It exists for the people writing code, reviewing pull requests, and making architectural decisions in this repository over the life of the project.

---

## 1. Purpose of this Guide

Repositories degrade when conventions live only in people's heads. Six months in, with multiple contributors touching different services, undocumented assumptions become the main source of friction: where does a new file go, which branch do I fork from, does this decision need to be written down anywhere.

This guide is the answer to those questions. It should be updated whenever a convention changes — if you find yourself explaining something in a PR review that isn't written here, that's a signal to add it.

---

## 2. Repository Philosophy

The repository is organized around one principle: **separation by concern, not by convenience.** Code, documentation, research, planning, and experimentation are deliberately kept apart because they have different audiences, different lifecycles, and different quality bars.

- **Services are isolated** (`services/`) because the system is designed as a modular monolith with hard interface boundaries between domains (ingestion, RAG, knowledge graph, student model, etc.). Isolating them in the folder structure enforces the same discipline in the codebase that the architecture requires — a contributor working on `ocr` should not need to understand the internals of `adaptive-engine`, only its interface.
- **Documentation is separated from code** (`docs/`) because documentation has a different review cadence and different authors than code. Architecture and research documents often precede implementation by weeks; keeping them out of `backend/` and `frontend/` avoids coupling doc changes to code PRs.
- **Research is separated from architecture** because research is exploratory and can be wrong, outdated, or superseded — it should never be mistaken for a decision that has been made. Architecture documents and ADRs represent decisions; `docs/research/` represents the evidence and reasoning that led to them.
- **Experiments are separated from production code** because prototypes are disposable by design. Nothing under `experiments/` should ever be imported by `backend/`, `frontend/`, or `services/`.
- **Planning is separated from documentation** because sprint plans and meeting notes are time-bound and operational, not a lasting reference — they should never be required reading to understand the system.

This structure is meant to scale by addition, not reorganization: new services, new docs, new experiments all have an obvious home. If something doesn't have an obvious home, that's a sign the top-level structure needs to change — see [Section 19](#19-suggested-repository-improvements) before improvising.

---

## 3. Repository Architecture

### `backend/`
**Purpose:** The FastAPI application — API gateway, route handlers, and the composition point where service modules are wired together via dependency injection.
**Belongs here:** Route definitions, request/response models, auth middleware, the Celery worker entrypoints, database migrations (`migrations/`), and backend-specific tests (`tests/`).
**Does not belong here:** Business logic for a specific domain (ingestion, RAG, adaptive engine, etc.) — that lives in `services/`. `backend/` calls services; it does not implement them.
**Example:** `backend/app/main.py` wires the FastAPI app and includes routers; a router calls `services/rag`'s interface rather than implementing retrieval logic inline.

### `frontend/`
**Purpose:** The Next.js application.
**Belongs here:** Pages/routes (`app/`), reusable UI (`components/`), feature-scoped modules (`features/`), and hooks (`hooks/`).
**Does not belong here:** API logic beyond thin fetch/query wrappers. The frontend is a consumer of the backend API, not a place to duplicate backend logic.
**Example:** A new dashboard view goes under `features/analytics/`, not directly into `app/` as a monolithic page.

### `services/`
**Purpose:** Independently defined domain modules (`ingestion`, `ocr`, `embeddings`, `rag`, `knowledge-graph`, `student-model`, `adaptive-engine`, `generation`, `analytics`). See [Section 8](#8-services-architecture) for details.
**Belongs here:** Domain logic, the service's own interface definition, and unit tests scoped to that service.
**Does not belong here:** Cross-service orchestration (that's `backend/`) or direct provider/vendor SDK calls (those go through the Provider Abstraction Layer, not directly inside a service).

### `models/`
**Purpose:** Configuration for AI models, prompt templates, and locally-hosted model assets. See [Section 9](#9-models-directory).

### `datasets/`
**Purpose:** Sample data, evaluation sets, and benchmark data used for testing and research. See [Section 10](#10-datasets).

### `experiments/`
**Purpose:** Notebooks, prototypes, and benchmark scripts that have not been promoted to production code. See [Section 11](#11-experiments).

### `infrastructure/`
**Purpose:** Deployment and operations — Docker, Kubernetes manifests, Nginx configuration, monitoring setup, and operational scripts.
**Belongs here:** Anything needed to run the system, not anything needed to build a feature.
**Does not belong here:** Application code of any kind.

### `docs/`
**Purpose:** All durable documentation — project docs, architecture, research, and API reference. See [Section 7](#7-documentation-standards).

### `planning/`
**Purpose:** Sprint plans, meeting minutes, weekly reports, task tracking, team roles. See [Section 12](#12-planning).

### `presentations/`
**Purpose:** Slide decks and demo materials for proposal, midterm, and final presentations. Not referenced by any other part of the repository — purely archival/output artifacts.

### `assets/`
**Purpose:** Logo, diagrams, and screenshots referenced by the README and documentation. Diagrams that are also maintained as Mermaid source should live alongside their source in `docs/architecture/`, with only exported images here.

### `scripts/`
**Purpose:** One-off or repeatable repository-level scripts (e.g., `setup_project_structure.sh`). Anything specific to a service belongs inside that service's own directory, not here.

---

## 4. Development Workflow

Every non-trivial change should move through the following stages. Trivial changes (typo fixes, small doc edits) can skip directly to implementation and review.

1. **Idea** — Raised as a GitHub issue or discussed in a planning session. Vague ideas stay in `planning/`; well-formed ones become issues.
2. **Discussion** — Open questions are discussed on the issue or in a meeting; outcomes are captured in `planning/meeting-minutes/`.
3. **Research** — If the idea requires evaluating an approach, model, or algorithm, this happens in `docs/research/` (or `experiments/` for hands-on evaluation) before any implementation begins.
4. **Architecture** — If the change affects module boundaries, data flow, or a technology choice, it is documented as an ADR (Section 13) before code is written.
5. **Implementation** — Code is written in the relevant `backend/`, `frontend/`, or `services/*` directory, on a feature branch.
6. **Testing** — Unit tests accompany the implementation in the same PR. No feature is considered done without tests.
7. **Documentation** — Relevant docs (architecture, API, or README) are updated in the same PR, not deferred.
8. **Review** — Opened as a pull request against `develop` following the PR checklist (Section 15).
9. **Merge** — Squash-merged once approved and CI passes.

Skipping research or architecture for a change that clearly needs it is the single most common way this kind of project accumulates technical debt — treat steps 3–4 as mandatory for anything touching system design.

---

## 5. Git Workflow

### Branches

| Branch | Purpose | Lifetime |
|---|---|---|
| `main` | Always deployable. Only release-tagged, tested code. | Permanent |
| `develop` | Integration branch for ongoing work. | Permanent |
| `feature/<scope>-<short-description>` | New functionality. Branched from `develop`. | Until merged |
| `bugfix/<scope>-<short-description>` | Non-urgent fixes. Branched from `develop`. | Until merged |
| `hotfix/<scope>-<short-description>` | Urgent production fixes. Branched from `main`. | Until merged |
| `release/<version>` | Stabilization before a tagged release. Branched from `develop`. | Until released |

`<scope>` should match a repository area where practical: `backend`, `frontend`, `rag`, `ocr`, `docs`, `infra`, etc.

Examples:
```
feature/rag-hybrid-search-weighting
bugfix/ocr-arabic-diacritics
hotfix/backend-auth-token-expiry
release/v0.3.0
```

### Merge Strategy

- Feature/bugfix branches merge into `develop` via squash merge, keeping history linear and readable.
- `develop` merges into `main` only through a `release/*` branch, tagged with a version number.
- Hotfixes merge into both `main` and `develop` to avoid regressions being reintroduced.
- No direct commits to `main` or `develop`. All changes go through a pull request, including from maintainers.

---

## 6. Coding Standards

### General Principles

- Prefer explicit code over clever code. This project has a long expected lifetime and will be read far more often than written.
- Every module-level public function and class has a docstring stating purpose, parameters, and return value.
- No service or backend module calls an AI provider (OpenAI, Ollama, etc.) directly — always through the Provider Abstraction Layer interface for that capability.
- Business logic is never placed in route handlers or React components; both are thin — logic lives in services or hooks.

### Python (backend, services)

- Python 3.12, formatted with `black`, linted with `ruff`.
- Type hints are mandatory on all function signatures. `mypy` runs in CI.
- Pydantic v2 models for all data crossing a service or API boundary.
- Module layout within a service follows: `interface.py` (abstract contract), `service.py` (implementation), `models.py` (Pydantic domain models), `repository.py` (data access, if applicable).
- No bare `except:` clauses; exceptions are caught specifically and logged via `structlog`.

### FastAPI

- Route handlers only parse input, call a service, and return output — no business logic inline.
- All endpoints have explicit `response_model` declarations.
- Long-running operations are dispatched to Celery, never executed synchronously in a request handler.

### React / Frontend

- TypeScript strict mode enabled; no implicit `any`.
- Components are function components with typed props; no class components.
- Server state (API data) goes through TanStack Query; local UI state through Zustand or component state — never mixed.
- Feature-specific components live under `features/<feature-name>/`, not `components/`, unless genuinely reusable across features.

### Naming Conventions

- Python: `snake_case` for files, functions, variables; `PascalCase` for classes.
- TypeScript/React: `camelCase` for functions/variables, `PascalCase` for components and types, files matching component names (`StudentDashboard.tsx`).
- Directories: `kebab-case` throughout the repository (matches existing `services/adaptive-engine`, `services/knowledge-graph`).

### Formatting

- Enforced via pre-commit hooks: `black` and `ruff` for Python, `prettier` and `eslint` for TypeScript.
- CI fails on formatting or lint violations — do not rely on manual review to catch these.

---

## 7. Documentation Standards

| Document | Audience | Purpose |
|---|---|---|
| `README.md` | External visitors and new contributors | First impression, high-level orientation, entry point to everything else |
| `docs/project/DeveloperGuide.md` (this document) | Internal team | How to work in this repository day to day |
| `docs/project/OpenLearn_AI_v4_Technical_Specification.md` | Internal team, academic reviewers | Full system design — the source of truth for *what* the system is |
| `docs/architecture/` | Internal team | *How* the system is built — diagrams, data flow, per-mode deployment details |
| `docs/architecture/ADR/` | Internal team | *Why* a specific decision was made, at the time it was made |
| `docs/research/` | Internal team | Evidence and evaluation behind a decision, before it becomes an ADR |
| `planning/` | Internal team | Time-bound operational tracking — sprints, meeting notes, weekly reports |
| `docs/project/Roadmap.md` | Internal team and external visitors | Where the project is going, at a milestone level |

Rules:
- Never duplicate content across these documents — link instead. If the Technical Specification already explains BKT, an architecture doc references it rather than re-explaining it.
- The Technical Specification is updated only when the *system design* changes, not for implementation details — those belong in code comments, service-level docs, or ADRs.
- Every ADR is linked from `docs/architecture/SystemArchitecture.md` if it affects a described component.

---

## 8. Services Architecture

Each folder under `services/` is an independent domain module: `ingestion`, `ocr`, `embeddings`, `rag`, `knowledge-graph`, `student-model`, `adaptive-engine`, `generation`, `analytics`.

**Responsibility boundaries:**
- A service exposes a single interface (`interface.py`) that other services and `backend/` depend on. No service imports another service's internals — only its interface.
- Communication between services happens through direct interface calls within the `backend/` process (this is a modular monolith, not microservices — see the relevant ADR). No service should assume network-level isolation from another.
- Any call to an external AI provider (local or cloud) goes through the Provider Abstraction Layer, not directly from within a service's implementation.

**Creating a new service:**
- A new service is justified when a distinct domain responsibility emerges that doesn't fit an existing service's interface (e.g., a future `speech` service for TTS/STT).
- Before creating one: define its interface first, get it reviewed (as an ADR if it affects existing services), then implement.
- New services follow the same internal layout as existing ones: `interface.py`, `service.py`, `models.py`, tests.

**When NOT to create a new service:**
- Do not create a new service for a feature that is a variant of existing logic (e.g., a new question type belongs inside `generation`, not a new service).
- Do not create a service to avoid adding a method to an existing interface — extend the interface instead if the responsibility genuinely belongs there.
- Do not create a service as a place to put shared utility code — that belongs in a shared internal library, not a domain service.

---

## 9. Models Directory

`models/` holds configuration and assets related to AI models, not the application logic that uses them.

- `configs/` — YAML/JSON provider and model configuration (e.g., which reasoning model, which embedding model, parameters). Environment-specific overrides (API keys, hosts) stay out of version control — configs here define structure and defaults, not secrets.
- `prompts/` — Versioned prompt templates used by the reasoning interface (concept extraction, question generation, summarization). Each prompt template should be named for its purpose and versioned in its filename or a header comment (e.g., `concept_extraction_v2.txt`) so changes are traceable and A/B-testable.
- `embeddings/` — Embedding-model-specific configuration (dimension, normalization settings), not embedding vectors themselves (those belong in the vector database, never in the repository).
- `local/` — References/scripts for pulling local model weights (e.g., Ollama Modelfiles). Actual model weight files are never committed — they are pulled at setup/runtime and excluded via `.gitignore`.

**Versioning:** Prompt and config changes that affect output quality should be tracked with a version suffix or changelog entry within the file, so regressions can be traced to a specific prompt revision. Future model additions (new reasoning or embedding models) are added as new config entries, never by overwriting an existing default without discussion — defaults changes affect every deployment and should go through a lightweight review.

---

## 10. Datasets

- `datasets/samples/` — Small, representative files used for manual testing and demos. Safe to commit; keep individual files small (a few MB at most).
- `datasets/evaluation/` — Labeled data used to evaluate model or pipeline quality (e.g., OCR accuracy sets, RAG retrieval relevance sets). Should be paired with a description of how the data was collected/labeled.
- `datasets/benchmarks/` — Data and scripts used for performance benchmarking (latency, throughput), referenced by `experiments/benchmarks/`.
- **Large or sensitive datasets are never committed.** Anything beyond a few MB, or containing real student data, is referenced by a download script or external storage link, with the actual data path added to `.gitignore`.
- Any dataset committed here must include a short `README.md` in its subfolder stating source, license, and intended use.

---

## 11. Experiments

`experiments/` is where ideas are tested before they're trusted.

- `notebooks/` — Exploratory analysis, one-off investigations. Not expected to run reliably long-term; not covered by CI.
- `prototypes/` — Standalone proofs of concept (e.g., the current HTML prototypes), used to validate an interaction or UI idea before frontend implementation.
- `benchmarks/` — Scripts measuring performance of a candidate model or approach, whose conclusions typically feed into `docs/research/ModelEvaluation.md`.

**Lifecycle:** An experiment is promoted to production code only after: (1) its approach is documented (as research or an ADR if it affects architecture), (2) the logic is reimplemented with proper structure, types, and tests inside `backend/`, `frontend/`, or `services/`. Code is never moved directly from `experiments/` into production paths — it is rewritten to meet the standards in Section 6. Once promoted, the original experiment can remain for historical reference but should not be relied upon or imported by production code.

---

## 12. Planning

- `planning/Sprint-XX.md` — Goals and scope for each sprint. Created at sprint start, updated at sprint end with outcomes.
- `planning/weekly-reports/` — Short status updates; not a substitute for sprint documents.
- `planning/meeting-minutes/` — Decisions and action items from team meetings. If a meeting produces an architectural decision, it should also be captured as an ADR — meeting minutes are not a durable reference on their own.
- `planning/tasks/` — Task breakdowns feeding into sprint planning, mirrored in whatever issue tracker the team uses (GitHub Issues/Projects), not a replacement for it.
- `planning/team-roles/` — Current ownership/responsibility per team member, updated as roles shift.

Planning documents are operational and can be terse. They are not held to the same writing quality bar as `docs/`.

---

## 13. Architecture Decision Records (ADR)

ADRs live in `docs/architecture/ADR/` and record decisions that are costly to reverse or that future contributors will reasonably ask "why was it done this way?" about.

**An ADR is warranted when:**
- Choosing between two or more viable technologies or libraries (e.g., NetworkX vs. Neo4j for the knowledge graph).
- Changing a module boundary or service responsibility.
- Deviating from a default recommended in the Technical Specification.
- Making a decision that affects more than one service or the deployment model.

**An ADR is not warranted for:** routine implementation details, naming choices, or anything easily reversible in a single PR.

**Format:** `NNNN-short-decision-title.md` (e.g., `0007-use-networkx-for-dev-knowledge-graph.md`), numbered sequentially. Each ADR includes: Status (Proposed/Accepted/Superseded), Context, Decision, Consequences, and Alternatives Considered.

---

## 14. Adding a New Feature

Example: adding a new question type (e.g., matching questions) to the generation service.

1. **Research** — If a new technique is needed (e.g., a new prompting strategy), document findings in `docs/research/`.
2. **Architecture** — If it changes the `generation` service's interface, open an ADR describing the interface change.
3. **Backend/Service** — Implement the new question type inside `services/generation/`, extending its interface rather than creating a new service. Add unit tests alongside the implementation.
4. **Frontend** — Add the corresponding rendering/interaction component under `frontend/features/generation/` (or the relevant feature folder).
5. **Testing** — Unit tests for the service logic, integration test for the API endpoint, and manual verification in the frontend.
6. **Documentation** — Update `docs/architecture/SystemArchitecture.md` if the interface changed; update API docs if a new endpoint or field was added.
7. **Review** — Open a PR against `develop` following the checklist in Section 15.
8. **Merge** — Once approved and CI passes.

---

## 15. Pull Request Checklist

- [ ] Branch follows naming convention (Section 5)
- [ ] Commits follow Conventional Commits (Section 16)
- [ ] Code passes lint/format checks (`black`, `ruff` / `eslint`, `prettier`)
- [ ] Type checks pass (`mypy` / `tsc`)
- [ ] Unit tests added or updated for the change
- [ ] All tests pass locally and in CI
- [ ] No secrets, API keys, or credentials included
- [ ] No committed model weights, large datasets, or generated artifacts
- [ ] Relevant documentation updated (architecture, ADR, or API docs)
- [ ] PR description explains what changed and why, and links the related issue
- [ ] No unrelated changes bundled into the PR

---

## 16. Commit Convention

Conventional Commits, enforced via commit-msg hook.

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `build`, `ci`

**Examples:**
```
feat(rag): add hybrid semantic/keyword weighting

fix(ocr): correct Arabic diacritic handling in PaddleOCR pipeline

docs(architecture): add ADR for NetworkX vs Neo4j decision

refactor(student-model): extract BKT update into separate method

chore(deps): bump fastapi to 0.115
```

Scope should match the relevant `services/*` directory, `backend`, `frontend`, `docs`, or `infra`.

---

## 17. Repository Rules

Non-negotiable, enforced via `.gitignore`, pre-commit hooks, and review:

- Never commit API keys, tokens, or credentials of any kind — use environment variables and `.env.example` files.
- Never commit model weights (local LLMs, embedding models) — reference download scripts instead.
- Never commit large or real student datasets — see Section 10.
- Never commit generated or build artifacts (`node_modules/`, `__pycache__/`, `.next/`, coverage reports).
- Never commit notebooks outside `experiments/notebooks/`.
- Never duplicate documentation content across files — link instead (Section 7).
- Never merge directly into `main` or `develop` without a pull request.
- Never leave a prototype in `experiments/` referenced by production code — promoted logic must be reimplemented (Section 11).

---

## 18. Long-Term Repository Growth

Over the life of the project, the structure should grow by extension, not restructuring:

- New services are added as new folders under `services/`, each following the existing interface pattern — the number of services is expected to grow modestly (e.g., a future `speech` service), not proliferate without bound.
- New documentation is added under the existing `docs/` subfolders; a new subfolder under `docs/` should only be introduced via an ADR, since it changes a convention every contributor relies on.
- As the test suite grows, prefer expanding coverage within each service's existing `tests/` structure over introducing a separate top-level test framework.
- Periodically (every few sprints) review `planning/` and `experiments/` for stale content — operational documents and abandoned prototypes should be archived or removed rather than left to accumulate indefinitely, since they are the folders most prone to rot.
- Any structural change to the repository (new top-level folder, renamed service, changed module boundary) should be proposed and recorded as an ADR before being implemented, so the repository's evolution stays traceable.

---

## 19. Suggested Repository Improvements

The following are practical gaps observed against the current structure and Technical Specification. None require restructuring existing folders — they are additions.

1. **No `CHANGELOG.md` update process is defined.** Recommend tying `CHANGELOG.md` entries to release branches (Section 5), populated from Conventional Commit messages since the last tag.
2. **No shared/common code location for cross-service utilities** (e.g., logging setup, error types shared by multiple services). Recommend a `services/common/` (or `backend/app/core/`) module for genuinely shared code, to avoid duplication or inappropriate coupling between services as more are added.
3. **No explicit test directory convention for `services/*` and `frontend/`** is visible in the current tree. Recommend each service and each frontend feature include its own `tests/` (or colocated `*.test.ts`) directory, matching `backend/tests/`.
4. **Two roadmap files exist** (`ROADMAP.md` at root and `docs/project/Roadmap.md`). Recommend designating `docs/project/Roadmap.md` as canonical and reducing the root file to a one-line pointer, to avoid drift between the two.
5. **`docs/api/` exists but has no defined authoring process.** Recommend documenting whether this is auto-generated from FastAPI's OpenAPI schema or hand-maintained, to avoid it silently going stale.
6. **No `.env.example` is visible at the repository root or within `backend/`.** Recommend adding one as configuration surface grows, to keep the "never commit secrets" rule in Section 17 practical for new contributors.
