# Contributing to OpenLearn AI

Thanks for contributing! The project is pre-alpha and spec-first; the fastest
way to help without wasted work is to start from the right document.

## Start here

1. [`AI_CONTEXT.md`](AI_CONTEXT.md) — current repository state (read this first).
2. [`docs/README.md`](docs/README.md) — which document is authoritative for what.
3. [`docs/design/DeveloperGuide.md`](docs/design/DeveloperGuide.md) — coding
   standards, git workflow, PR checklist, ADR format (detailed conventions).

## Ground rules

- **Check the plan before building.** The
  [44-week execution plan](planning/Roadmap/44-WEEK-EXECUTION-PLAN.md) is the
  schedule authority; anything not in the current phase needs an issue/discussion first.
- **Decisions live in ADRs.** If your change touches architecture, check
  [`docs/adr/`](docs/adr/) and add/update an ADR in the same PR when needed.
  ADRs override conflicting statements in older documents.
- **Keep boundaries.** Nothing under `experiments/` may be imported by
  `backend/` or `frontend/`. Benchmark data is evaluation-only.
- **Small, scoped PRs.** Branch from `main` as `feature/<scope>-...` or
  `bugfix/...`; Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, …).

## Development environment

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest && ruff check .

# Frontend (requires Node 20)
cd frontend && npm ci && npm run lint && npm run build

# OCR benchmark (requires uv)
cd experiments/OCR/ocr-benchmark && uv sync

# Full dev stack
docker compose -f infra/docker-compose.dev.yml up
```

CI must pass on your PR: backend (install, ruff, pytest) and frontend
(install, lint, typecheck, build).

## Reporting issues

Include: what you expected, what happened, and the smallest reproduction.
Check [Development Status](README.md#development-status) first — the repo is
pre-alpha and many planned features are intentionally not built yet.
