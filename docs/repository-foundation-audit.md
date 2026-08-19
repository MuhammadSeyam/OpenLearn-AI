# Repository Foundation Audit

> **Status:** Accepted baseline for the foundation cleanup (2026-08-16, Week 2).
> Evidence: every claim below was verified directly against the working tree at
> commit `8ea929c` plus the uncommitted foundation changes (P0 dependency fixes
> and the OCR benchmark scaffold described in §10).
> This document is a point-in-time record; it is not a living status page. For
> current state see `AI_CONTEXT.md`.

---

## 1. Current repository state (summary)

- **87 tracked files.** Product code: an 8-line FastAPI hello-world
  (`backend/app/main.py`), one smoke test, and a default Next.js 16 + shadcn
  scaffold. Everything else is documentation (~70%), planning, research dumps,
  or OCR experiment material.
- **19 tracked files are 0 bytes** (18 of them placeholders; 1 is a legitimate
  Python package marker `backend/app/__init__.py`).
- **Working infrastructure:** `infra/docker-compose.dev.yml` (backend + unused
  postgres), `backend/Dockerfile`, `.github/workflows/ci.yml` (2 jobs),
  dev deps now clean (§6).
- **Real engineering assets:** `experiments/OCR/OCR_BENCHMARKING_HANDBOOK.md`
  (1,545-line phased OCR evaluation methodology), PaddleOCR 3.x exploratory
  notebook (English + Arabic + PDF verified working), and — as of the
  foundation work — `experiments/OCR/ocr-benchmark/` (pinned, dependency-free
  scaffold with 4-document pilot dataset, manifest, provenance record).

## 2. Major structural problems

1. **Placeholder files masquerading as documentation.** All five
   `docs/architecture/*.md`, six of seven `docs/research/*.md`,
   `docs/design/{Scope,Vision}.md`, root `CHANGELOG.md`, `CONTRIBUTING.md`,
   `CODE_OF_CONDUCT.md`, and `planning/Sprint-{01,02}.md` are 0 bytes while
   several are linked from `README.md` as authoritative.
2. **README describes an aspirational repo, not the real one.** Its "Repository
   layout" block lists `services/`, `models/`, `infrastructure/`, `datasets/` —
   none exist (actual: `backend/`, `frontend/`, `infra/`, `experiments/`,
   `docs/`, `planning/`, `presentations/`). Five links point into a
   nonexistent `docs/project/` tree.
3. **A scaffolding script fights the decided structure.**
   `scripts/setup_project_structure.sh` re-creates `infrastructure/`,
   `services/` (×9), `models/`, `datasets/`, `assets/` and the empty
   placeholder files if ever re-run — directly contradicting the real layout
   and the modular-monolith decision.
4. **Raw AI research dumps live inside engineering docs.**
   `docs/ai-reports/` (~600 KB of Perplexity/Grok transcripts) and a 167 KB
   generated `docs/architecture/OpenLearn_AI_SaaS_Deployment_Blueprint.html`
   sit beside authoritative specifications with nothing marking them as
   non-authoritative.

## 3. Duplicated / conflicting sources of truth

| Topic | Competing sources | Status after cleanup |
|---|---|---|
| Vector store default | Tech Spec §10.3 (ChromaDB) vs Master Roadmap (Qdrant) | Contradiction preserved, decision **deferred** with evidence criteria → `docs/adr/0004` |
| Schedule authority | `MASTER_ROADMAP.md` (134 KB) vs `44-WEEK-EXECUTION-PLAN.md` (615 KB) vs `ROADMAP_GUIDE_AR.md` (150 KB) | Hierarchy declared in `docs/README.md`: execution plan = schedule SSOT; master roadmap = strategy; AR guide = reading companion |
| Requirements docs | `OpenLearn_AI_System_Requirements_and_Deployment_Profiles.md` vs `OpenLearn_AI_User_System_Requirements_Guide.md` | Both retained; authority declared (deployment profiles = engineering authority, user guide = derived user-facing text) in `docs/README.md` |
| ADR location | DeveloperGuide says `docs/architecture/ADR/`; cleanup uses `docs/adr/` | `docs/adr/` is canonical; DeveloperGuide reference updated |
| OCR engine version | Spec stack table "PaddleOCR v4" vs notebook running PP-OCRv5 models | Noted in ADR-0003 context; spec text unchanged (stale line, low risk) |

## 4. Empty placeholders (disposition)

| File | Disposition |
|---|---|
| `docs/architecture/SystemArchitecture.md`, `DataFlow.md` | **FILL** — short, accurate content (they are README-linked) |
| `docs/architecture/{OfflineMode,HybridArchitecture,CloudMode}.md` | **DELETE** — empty; content already lives in Tech Spec; README links repaired |
| `docs/research/{RAG,AdaptiveLearning,StudentModel,ModelEvaluation,LiteratureReview,CompetitorAnalysis}.md` | **DELETE** — empty stubs; `docs/research/README.md` now indexes real research (incl. raw archive) |
| `docs/design/{Scope,Vision}.md` | **DELETE** — empty; vision/scope content lives in the Tech Spec; README links repaired |
| `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` | **FILL** — minimal real content (all README-linked) |
| `planning/Sprint-01.md` | **FILL** — evidence-based retrospective from git history |
| `planning/Sprint-02.md` | **FILL** — actual current sprint scope |
| `backend/app/__init__.py` | **KEEP** — legitimate package marker |

## 5. Dead / misleading artifacts

- `scripts/setup_project_structure.sh` — **DELETE** (superseded; contradicts
  decided layout; re-running it reintroduces the placeholder mess).
- `docs/architecture/OpenLearn_AI_SaaS_Deployment_Blueprint.html` — **ARCHIVE**
  to `docs/archive/` (design-phase generated artifact).
- `docs/ai-reports/**` — **ARCHIVE** to `docs/research/raw/` (valuable raw
  research, explicitly non-authoritative).
- `experiments/prototypes/*.html`, `presentations/demo/*.html` — **KEEP in
  place** (correctly filed as experiments/presentations; no action).
- Stale statements inside `AI_CONTEXT.md` (claims "frontend/ 100% empty", "no
  CI", "17+ empty files" — all outdated) — **MODIFY** (status sections refreshed).

## 6. Dependency problems (and resolutions)

- `backend/requirements.txt` was a 53-line `pip freeze` (jax, jupyter stack,
  debugpy, sounddevice, duplicate OpenCV) with zero domain relevance.
  **Resolved:** curated to `fastapi==0.138.1`, `uvicorn==0.49.0`.
- `backend/requirements-dev.txt` contained `httpx2` **unpinned**.
  Investigation result: **not a typo** — starlette 1.6's TestClient requires
  the `httpx2` package line (verified: installing it removes the deprecation
  warning; tests pass with httpx2 alone). **Resolved:** `httpx2==2.10.0`.
- OCR experiments had **no pinned environment at all** (PaddleOCR version
  recorded nowhere). **Resolved:** `experiments/OCR/ocr-benchmark/` is a
  pinned uv project (runtime deps intentionally empty at foundation stage).
- Dockerfile installs only runtime requirements — consistent post-cleanup.

## 7. CI problems

- Backend job: install → `ruff check` → `pytest`. **Now valid** (deps fixed);
  verified locally in a clean venv.
- Frontend job: lint only; **no typecheck, no production build** — a green
  check did not prove the app compiles. **Resolved:** `tsc --noEmit` +
  `npm run build` steps added (executed on GitHub runners; this local
  environment has no Node, see §12).
- No silent-skips or `|| true` introduced; the existing Vitest skip is an
  explicit, documented conditional (kept).

## 8. Architecture contradictions & decisions

See `docs/adr/`: 0001 modular monolith (decided), 0002 documentation authority
(decided), 0003 OCR benchmark location/responsibility (decided), 0004 vector
store (deferred with explicit evidence criteria and a decision deadline).

## 9. Reproducibility & scientific problems

- Notebook hardcoded `/run/media/sadin/...` paths — **resolved** (repo-relative
  `../benchmarks/`; outputs kept as historical logs).
- No ground truth exists; none fabricated. Annotation guideline drafted
  (`experiments/OCR/ocr-benchmark/docs/annotation-guidelines.md`, DRAFT).
- Data provenance: all 4 pilot documents marked rights-**UNKNOWN**
  (`experiments/OCR/ocr-benchmark/docs/provenance.md`); `OL-C-004` is a named
  lecturer's material and needs permission or replacement (**human decision**).
- Metrics not yet implemented (deliberate; next task) — no scores exist.

## 10. Cleanup plan executed in this task

Phases: (1) structure cleanup — archive moves, placeholder
fill/delete, scaffolder deletion; (2) documentation authority — `docs/README.md`
hierarchy, README link repairs, AI_CONTEXT refresh, sprint records;
(3) ADRs 0001–0004; (4) dependency verification (done in the P0 task);
(5) CI repair (frontend typecheck + build); (6–7 foundations) benchmark
`results/` directory, manifest `source` field, annotation guideline draft.
Metrics/engines/ground-truth transcription intentionally **not** implemented
here (see ADR-0003 sequencing: GT → metrics → one engine → validate harness).

## 11. Files requiring human decision

1. `OL-C-004` (`Data+Structre+lect1.pdf`): obtain the lecturer's permission or
   replace the document. Blocking for any public dataset release; not blocking
   for internal benchmarking.
2. Vector store default (ChromaDB vs Qdrant) — evidence criteria in ADR-0004;
   decision due before the Week-3/4 embedding spike.
3. Team-capacity re-baseline of the 44-week plan (repo progress vs 9-person
   plan) — a planning decision, not a code decision.

## 12. Environment constraints noted during validation

- This workstation has **no Node.js** — frontend lint/typecheck/build were
  added to CI and YAML-validated, but executed only by GitHub runners on push,
  not locally. Backend install/lint/test were executed locally in a clean venv.
