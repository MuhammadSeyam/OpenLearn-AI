# Changelog

Notable repository changes. Format: Keep a Changelog style, newest first.
The project is pre-alpha: versions below are repository milestones, not
released software.

## [Unreleased] — 2026-08-16

### Foundation cleanup (Week 2)

**Fixed**
- Backend dependencies: `requirements.txt` curated from a raw `pip freeze`
  (53 entries) to the 2 packages the code actually runs (`fastapi`,
  `uvicorn`); `requirements-dev.txt` — `httpx2` now pinned (`httpx2==2.10.0`,
  verified to be the correct package for starlette 1.6 TestClient, not a typo).
- OCR notebook (`experiments/OCR/paddle-test/`) no longer hardcodes
  `/run/media/...` absolute paths (now repo-relative).
- CI: frontend job now runs typecheck (`tsc --noEmit`) and production build
  (`next build`) in addition to lint — a green check now means the app builds.

**Added**
- `experiments/OCR/ocr-benchmark/` — reproducible OCR benchmark foundation:
  pinned uv project, 4-document pilot dataset with SHA-256 provenance record
  (all rights status UNKNOWN), roadmap-compatible `manifest.json`, empty-by-
  design ground-truth directory with policy, adapter/core package skeleton.
- `docs/adr/0001–0004` — architecture decision records (modular monolith,
  documentation authority, OCR benchmark location, vector store deferral).
- `docs/README.md` — documentation authority hierarchy.
- `docs/repository-foundation-audit.md` — evidence-based repository audit.
- Annotation guideline draft (OCR benchmark, `docs/annotation-guidelines.md`).
- Sprint records: `planning/Sprint-01.md` (retrospective), `Sprint-02.md`
  (current scope).

**Changed**
- Documentation authority established (see `docs/README.md`); README links
  repaired to real paths; `AI_CONTEXT.md` stale statements refreshed.
- Raw AI research moved to `docs/research/raw/ai-reports/` (non-authoritative);
  SaaS blueprint HTML archived to `docs/archive/`.

**Removed**
- Empty placeholder files (6 research stubs, 2 design stubs, 3 architecture
  mode stubs) — content either never existed or lives in the Tech Spec.
- `scripts/setup_project_structure.sh` — superseded; re-running it would
  recreate directories that contradict the decided structure.
