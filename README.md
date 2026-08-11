<div align="center">

# OpenLearn  AI

**Open-source adaptive learning, without the vendor lock-in.**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![Contributing](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Docs](docs/) · [Architecture](docs/architecture/SystemArchitecture.md) · [Roadmap](planning/Roadmap/MASTER_ROADMAP.md) · [Contributing](CONTRIBUTING.md)

</div>

> **Status: pre-alpha.** Architecture, research, and design docs are in place; the backend, frontend, and services are under active construction and not yet runnable end-to-end. See [Development Status](#development-status) before opening issues about broken setup steps.

---

## What it is

OpenLearn AI turns study material — PDFs, slides, notes, scans — into an adaptive learning loop instead of a static chat window. It builds a model of what a learner actually understands, maps how concepts depend on each other, and uses both to decide what to study next and when to review it, before it's forgotten.

Every AI-facing component (LLM reasoning, embeddings, OCR, vector storage) sits behind a provider interface, so the same deployment can run fully offline, fully on managed cloud APIs, or any mix — a configuration choice, not a fork.

## Why this exists

Tools that "chat with your PDF" answer questions but remember nothing between sessions — no sense of what you struggle with, no concept dependencies, no review scheduling. The handful of products that do this well are closed-source, cloud-only, and priced for institutions, not individual students in underserved language markets.

|                                   | Chat-with-PDF tools | Closed adaptive platforms | OpenLearn AI |
| --------------------------------- | ------------------- | ------------------------- | ------------ |
| Tracks per-concept mastery        | ✗                   | ✓                         | ✓            |
| Prerequisite-aware study paths    | ✗                   | Partial                   | ✓            |
| Spaced repetition scheduling      | ✗                   | Sometimes                 | ✓            |
| Runs fully offline                | ✗                   | ✗                         | ✓            |
| Open source                       | ✗                   | ✗                         | ✓ (AGPL-3.0) |
| Arabic-first multilingual support | ✗                   | ✗                         | ✓            |

## Core capabilities

- Multi-format ingestion — PDF, DOCX, PPTX, images, OCR for scanned content
- Retrieval-augmented Q&A with citation-grounded answers, not just plausible text
- Auto-extracted knowledge graph of concepts and prerequisites
- Per-concept mastery tracking (starts heuristic, upgrades to Bayesian Knowledge Tracing as data accumulates)
- Adaptive engine that turns mastery + graph + learner profile into concrete study recommendations
- Spaced repetition scheduling driven by forgetting curves
- Generated flashcards, adaptive quizzes, and CAT-style exam simulation
- Learning analytics: progress, weak areas, readiness

Full detail: [Technical Specification](docs/project/OpenLearn_AI_v4_Technical_Specification.md).

## Deployment modes

One codebase, three presets:

| Mode       | AI runs                                     | Internet             | Typical hardware           |
| ---------- | ------------------------------------------- | -------------------- | -------------------------- |
| **Local**  | Entirely on-device                          | Not required         | 16 GB RAM, GPU recommended |
| **Hybrid** | Local core, cloud augmentation where useful | Only for cloud calls | 8 GB RAM                   |
| **Cloud**  | Entirely managed APIs                       | Required             | 4 GB RAM                   |

Mode-specific guides: [Local](docs/architecture/OfflineMode.md) · [Hybrid](docs/architecture/HybridArchitecture.md) · [Cloud](docs/architecture/CloudMode.md)

## Architecture, briefly

Content moves through ingestion → knowledge base → knowledge graph → student model → learner profile → adaptive engine → generation → analytics, with feedback loops that let every study session refine future recommendations. Nothing calls an AI provider directly — everything goes through a provider abstraction layer, so swapping a model or vendor is a config change, not a rewrite.

Diagrams and full rationale: [`docs/architecture/SystemArchitecture.md`](docs/architecture/SystemArchitecture.md) · [`docs/architecture/DataFlow.md`](docs/architecture/DataFlow.md) · [ADRs](docs/architecture/ADR/)

## Repository layout

```
backend/         FastAPI service, migrations, tests
frontend/        Next.js app
services/        ingestion · ocr · embeddings · rag · knowledge-graph ·
                  student-model · adaptive-engine · generation · analytics
models/          configs, prompts, local model assets
infrastructure/  docker, kubernetes, nginx, monitoring
docs/            project docs, architecture, research
datasets/        sample data, evaluation sets, benchmarks
experiments/     notebooks, prototypes
```

## Getting started

There is no working `docker-compose up` yet — don't file an issue if one doesn't exist. The fastest way to get oriented right now:

1. Read [`docs/project/Vision.md`](docs/project/Vision.md) and the [Technical Specification](docs/project/OpenLearn_AI_v4_Technical_Specification.md).
2. Look at [`experiments/prototypes/`](experiments/prototypes/) for the current interactive prototypes.
3. Check [Development Status](#development-status) and [`docs/project/Roadmap.md`](docs/project/Roadmap.md) for what's actively being built.

A real quickstart will replace this section once the backend and frontend are runnable — tracked in the roadmap.

## Documentation map

| You want to...                                      | Go to                                                        |
| --------------------------------------------------- | ------------------------------------------------------------ |
| Understand the vision and scope                     | [`docs/project/Vision.md`](docs/project/Vision.md), [`docs/project/Scope.md`](docs/project/Scope.md) |
| Read the full technical design                      | [`docs/project/OpenLearn_AI_v4_Technical_Specification.md`](docs/project/OpenLearn_AI_v4_Technical_Specification.md) |
| See why a decision was made                         | [`docs/architecture/ADR/`](docs/architecture/ADR/)           |
| Check hardware/deployment requirements              | [`docs/project/OpenLearn_AI_System_Requirements_and_Deployment_Profiles.md`](docs/project/OpenLearn_AI_System_Requirements_and_Deployment_Profiles.md) |
| Understand the research basis (BKT, RAG, OCR, etc.) | [`docs/research/`](docs/research/)                           |
| Track progress                                      | [`docs/project/Roadmap.md`](docs/project/Roadmap.md) *(canonical — the root `ROADMAP.md` is a short pointer to this file)* |

## Development status

Active, pre-alpha. Documentation and architecture are ahead of implementation by design — this is a deliberate spec-first approach, not neglect. Expect frequent breaking changes until v1.0.

## Contributing

Start here: [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

Right now, the highest-value contributions are:
- Implementing a single `services/*` module against its documented interface
- Reviewing or proposing an [ADR](docs/architecture/ADR/) for an open architectural question
- Improving OCR/embedding coverage for Arabic in [`docs/research/`](docs/research/)

Avoid opening large, unscoped PRs — module boundaries are intentional; check the relevant ADR before restructuring anything.

## License

[AGPL-3.0](LICENSE).
