# System Architecture

> Authority note: this file describes architecture at a glance and links to the
> authoritative sources. Detailed design lives in the
> [Technical Specification](../design/OpenLearn_AI_v4_Technical_Specification.md);
> binding decisions live in [ADRs](../adr/).

## Current architecture (implemented, 2026-08-16)

A **modular monolith** (ADR-0001) at pre-alpha stage:

```
Browser → Next.js 16 frontend (scaffold)   →   FastAPI backend (hello-world)
                                              infra/docker-compose.dev.yml
                                              (backend + PostgreSQL 16, unused by code yet)
experiments/OCR/  → self-contained OCR benchmark (isolated uv environment;
                    never imported by backend/frontend — repo boundary rule)
```

That is the entire implemented surface. Anything else described below is
**design intent, not implementation**.

## Intended architecture (per Tech Spec v4)

- Single FastAPI process, 9 internal modules (ingestion, OCR, embeddings, RAG,
  knowledge graph, student model, adaptive engine, generation, analytics)
  communicating through in-process interfaces — explicitly **not**
  microservices (ADR-0001).
- All AI-facing calls (reasoning / embeddings / OCR / speech / vision /
  ranking / vector DB) behind a Provider Abstraction Layer (PAL) so local,
  hybrid, and cloud execution are configuration presets, not forks.
- Three deployment modes (Local / Hybrid / Cloud) — profiles described in the
  [Tech Spec](../design/OpenLearn_AI_v4_Technical_Specification.md) and hardware
  profiles in the
  [deployment requirements](../design/OpenLearn_AI_System_Requirements_and_Deployment_Profiles.md).
- Target data stores (per spec, none implemented): PostgreSQL 16 (primary),
  vector store (**undecided** — see ADR-0004), Redis cache/queue, object
  storage, graph store for the knowledge graph.

## Decision log

All architecture decisions: [`docs/adr/`](../adr/). Decisions override
ambiguous or conflicting statements in older documents (ADR-0002).

## Data flow

See [DataFlow.md](DataFlow.md) for the document-ingestion data flow that the
OCR benchmark is the first stage of.
