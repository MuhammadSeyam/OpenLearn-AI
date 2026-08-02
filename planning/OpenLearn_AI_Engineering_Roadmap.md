# OpenLearn AI — Engineering Roadmap (v1 → v2)

**Project:** OpenLearn AI — AI-powered adaptive learning platform
**Audience:** Engineering Manager / Tech Lead / 9-person graduation team
**Author:** Senior TPM / Staff Architect (acting)
**Status:** v1 drafted → self-critiqued → v2 final
**Planning horizon:** 2 August 2026 → 30 June 2027 (≈ 44 weeks)
**Delivery philosophy:** *Working software over perfect architecture. Incremental delivery over big-bang. Risk reduction over feature count.*

---

> **How to read this document**
>
> This is **not** a spec. It is an *executable plan* that a 9-person team can follow week-by-week.
> - **Part A (§1–§25)** is the **v1 roadmap** — a complete first draft.
> - **§26** is the **self-critique** — what is wrong or weak in v1.
> - **Part B (§27–§33)** is the **v2 roadmap** — the improved, final plan that incorporates every critique. v2 is presented in full, not as a diff.
> - If you only have time to read one section, read **§5 (MVP definition)**, **§12 (critical path)**, **§21 (risk register)**, and **§33 (v2 consolidated timeline)**.

---

# PART A — v1 ROADMAP (FIRST DRAFT)

## 1. Executive Summary

OpenLearn AI is an adaptive learning platform that ingests educational documents (PDFs, slides, images of worksheets), builds a retrieval-augmented knowledge layer on top of them, models each student's cognitive state, and uses that model to drive personalized quizzes, recommendations, and a learning-analytics dashboard. The platform must be production-deployed, documented, tested, and demo-ready by **June 2027**.

This roadmap treats the project as a **startup product**, not a university assignment. The team has 9 members with uneven skills, ~10 months of calendar time, and a hard external deadline (graduation). The single biggest schedule risk is **AI component integration** (OCR → embeddings → vector DB → RAG → knowledge graph → student model → adaptive engine), because each layer depends on the previous one and at least three of them (RAG quality, KG construction, adaptive engine) carry genuine research risk.

To mitigate this, the plan:

1. **Front-loads the hardest technical work** into August–October 2026, when the team has the most capacity and the least academic pressure.
2. **Defines a thin vertical slice (v0.5)** by December 2026 that proves the entire AI pipeline end-to-end, even if every component is shallow.
3. **Locks architecture in November 2026** (Architecture Freeze) so the team stops renegotiating interfaces mid-semester.
4. **Imposes Feature Freeze (Apr 2027) and Code Freeze (May 2027)** with deliberate polish windows before graduation.
5. **Runs weekly demos from week 3 onward** so integration problems surface early, not the week before the presentation.
6. **Carries a 15% schedule buffer** distributed across phases, not concentrated at the end (where it always gets eaten).
7. **Treats documentation as a first-class deliverable** with a "docs-first" workflow: API contracts and design docs are written *before* implementation, not after.

The plan also assumes the product **may continue post-graduation as a startup**. That means we avoid throwaway academic shortcuts (e.g., hardcoded mock data baked into the UI, no auth, no observability), and we pick a stack that a small team can actually operate in production.

**What "done" means by June 2027:**

- A deployed v1.0 product on a real domain with auth, monitoring, and a runbook.
- A working RAG pipeline that answers questions over uploaded course material with cited sources.
- A knowledge graph of at least 1,000 concepts derived from ingested content.
- A student cognitive model that updates from quiz performance.
- An adaptive engine that personalizes at least the *next recommended concept* and the *next quiz difficulty*.
- A learning-analytics dashboard that an instructor can read.
- A graduation presentation backed by live demos, not screenshots.
- A repository with CI, tests (>60% coverage on critical paths), ADRs, and a README that a new engineer can follow.

**What "done" does NOT mean:**

- It does not mean a polished consumer product. UX will be functional, not beautiful.
- It does not mean every feature in the original wish-list ships. Some will be descoped (see §26).
- It does not mean SOTA model performance. We accept "good enough to demo credibly" on RAG quality, OCR accuracy, and adaptation logic.

---

## 2. Project Context, Constraints & Assumptions

### 2.1 Hard constraints

| Constraint | Value | Impact |
|---|---|---|
| Calendar window | 2 Aug 2026 → 30 Jun 2027 | 44 weeks total |
| Team size | 9 members | Realistic throughput ≈ 6 FTE after absence, exams, onboarding |
| Hard deadline | Graduation submission, May–Jun 2027 | Cannot slip |
| University semester start | 1 Oct 2026 | Capacity drops after this date |
| Exam period | ~Late Jan 2027 + ~Late May 2027 | Capacity collapses to near-zero |
| Skill variance | High — not all members know AI/backend | Must pair-program and assign by tier |
| Budget | Assumed limited (student project) | Prefer open-source / free-tier; pay only for LLM tokens and base infra |

### 2.2 Capacity model (the single most important number in this plan)

We model effective engineering capacity in **person-hours per week**, not in story points, because the team has not calibrated story points yet. The model assumes:

- 9 members total
- A member is "active" only ~70% of weeks (illness, family, recruitment interviews, exam crunch)
- Active members contribute at different rates depending on calendar phase

| Phase | Window | Active members (avg) | Hrs/wk per active member | Effective hrs/wk |
|---|---|---|---|---|
| Pre-semester surge | Aug–Sep 2026 (8 wks) | 8.5 | 18 | **~153** |
| Semester 1 | Oct 2026 – mid-Jan 2027 (15 wks) | 7.0 | 9 | **~63** |
| Exam crunch 1 | Late Jan 2027 (3 wks) | 3.0 | 4 | **~12** |
| Semester 1 break | Feb 2027 (4 wks) | 6.5 | 12 | **~78** |
| Semester 2 (light) | Mar – mid-Apr 2027 (6 wks) | 7.0 | 9 | **~63** |
| Exam crunch 2 | Late Apr – early May 2027 (3 wks) | 3.0 | 4 | **~12** |
| Final push (post-exam) | Mid-May – Jun 2027 (5 wks) | 8.0 | 22 | **~176** |
| **Total** | **44 wks** | — | — | **~3,550 person-hours** |

After a 70% productivity multiplier (meetings, rework, context-switching, infra overhead), realistic **usable engineering hours ≈ 2,500**. That is the budget this plan is built against. Every feature in this plan is sized to fit inside 2,500 hours; anything that does not fit is descoped.

### 2.3 Operating assumptions

1. The team has working laptops, GitHub organization, and Slack/Discord.
2. At least one member can provision a cloud account (AWS / GCP / Azure free tier or student credits).
3. LLM API access is available (OpenAI / Anthropic / DeepSeek / GLM — any one is fine). If only free-tier open-source models are allowed, the plan still works but RAG quality drops; see Risk R-07.
4. Team can meet synchronously at least once per week (Friday demo) plus one mid-week sync.
5. Source control, PR review, and CI are non-negotiable from week 1.
6. The graduation committee accepts a working demo as the primary deliverable; written thesis is secondary and runs in parallel (handled outside this roadmap).

### 2.4 Non-assumptions (things we explicitly do NOT assume)

- We do **not** assume everyone can write production Python. Pair-programming is mandatory for AI/ML work.
- We do **not** assume the LLM API will be stable across 10 months. We isolate it behind an LLM gateway interface from week 1.
- We do **not** assume the team will stay at 9 members. The plan must survive losing 1 member for 4 weeks (see Risk R-12).
- We do **not** assume the first architecture will be correct. Architecture Freeze happens **after** v0.3, not before.

---

## 3. Team Model — Role Pods

The team is organized into **4 pods** plus a rotating **TPM role**. Pods are cross-functional enough to deliver vertical slices but specialized enough to build deep competence. Each pod has a **lead** who is the single point of contact for that area.

### 3.1 Pod structure (9 members)

| Pod | Headcount | Lead | Primary ownership | Secondary ownership |
|---|---|---|---|---|
| **A — Backend & Platform** | 3 | Backend Lead | Auth, user mgmt, course mgmt, API layer, DB schema, async jobs | Integration testing, infra glue |
| **B — AI/ML & Data** | 3 | AI Lead | OCR, embeddings, vector DB, RAG, KG, student model, adaptive engine | ML evaluation harness, dataset curation |
| **C — Frontend & UX** | 2 | Frontend Lead | Web UI, dashboards, instructor views, student views | Design system, accessibility, demo polish |
| **D — DevOps & QA** | 1 | DevOps/QA Lead | CI/CD, environments (dev/stage/prod), monitoring, SLOs, test infra | Security review, release mgmt |
| **TPM (rotating)** | 0 (shared) | — | Roadmap, sprint ops, risk register, stakeholder comms | — |

**Total: 9.** TPM duties are shared across pod leads on a rotating basis (4-week rotations) so no single person is permanently blocked in meetings.

### 3.2 Pod chart

```
                       ┌─────────────────────────┐
                       │   TPM (rotating, ~0.2)  │
                       └────────────┬────────────┘
                                    │
   ┌────────────────┬───────────────┼───────────────┬─────────────────┐
   ▼                ▼               ▼               ▼                 ▼
┌─────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      ┌────────────┐
│ Pod A   │   │ Pod B    │   │ Pod C    │   │ Pod D    │      │ Stakeholder│
│ Backend │   │ AI/ML    │   │ Frontend │   │ DevOps/QA│      │ (advisor)  │
│  3      │   │  3       │   │  2       │   │  1       │      │            │
└─────────┘   └──────────┘   └──────────┘   └──────────┘      └────────────┘
```

### 3.3 Pod responsibilities (detailed)

**Pod A — Backend & Platform (3)**
- Auth (OAuth + email/password + JWT), RBAC (student / instructor / admin).
- User management: profile, enrollment, progress.
- Course management: CRUD, material upload, instructor assignment.
- API gateway: REST + (optionally) GraphQL later; versioned `/v1`.
- DB schema, migrations, connection pooling, async job queue (Celery / Inngest).
- Owns the **Integration Test Suite** for the whole platform.

**Pod B — AI/ML & Data (3)**
- OCR pipeline (PDF → text + layout + images).
- Document ingestion + chunking strategy.
- Embedding pipeline (model selection, batching, caching).
- Vector DB (provisioning, indexing, query layer).
- RAG layer (retrieval, reranking, prompt assembly, citation).
- Knowledge Graph (concept extraction, relations, storage).
- Student Cognitive Model (Bayesian / IRT / simple mastery estimate).
- Adaptive Learning Engine (next-best-action policy).
- Recommendation Engine (content + peer).
- ML evaluation harness (golden set, regression tests).

**Pod C — Frontend & UX (2)**
- Web app (Next.js 16, App Router, TypeScript, Tailwind, shadcn/ui).
- Auth flows, course browsing, material upload, RAG chat UI, quiz UI.
- Instructor dashboard (cohort analytics, content management).
- Student dashboard (progress, recommendations, knowledge graph viz).
- Admin dashboard (users, courses, system health).
- Design system (tokens, components, Storybook).
- Accessibility (WCAG 2.1 AA on critical paths).

**Pod D — DevOps & QA (1)**
- GitHub Actions pipelines (lint, test, build, deploy).
- Environments: `dev` (per-PR preview), `staging` (integration), `prod`.
- Docker images, container registry, secrets management.
- Observability: logs (Loki / CloudWatch), metrics (Prometheus / Grafana), traces (OTel), error tracking (Sentry).
- SLO definitions and alerting.
- Security review (OWASP top 10, dependency scanning, SAST).
- Release management and rollback runbooks.

### 3.4 RACI for cross-cutting concerns

| Concern | A | B | C | D | TPM |
|---|---|---|---|---|---|
| Architecture decisions | C | C | C | C | A |
| API contracts | R/A | C | C | I | I |
| Data model | C | C | I | I | A |
| ML evaluation criteria | I | R/A | I | C | I |
| Release go/no-go | C | C | C | R | A |
| Demo prep | C | C | R | C | A |
| Risk register updates | C | C | C | C | R/A |
| Graduation artifacts | C | C | C | C | R/A |

*R = Responsible, A = Accountable, C = Consulted, I = Informed.*

---

## 4. Technology Stack Recommendations

We recommend **two stacks**. The **Primary Stack** is production-grade and assumes the team wants to operate this as a real product post-graduation. The **Fallback Stack** is a lighter version that trades operational maturity for shipping speed — useful if the team is behind schedule by January 2027.

A stack decision must be locked by **end of Week 2 (Aug 15, 2026)** and revisited only at the **Architecture Freeze** review (Nov 2026). Flip-flopping after that point is a schedule-killer.

### 4.1 Primary Stack (Production-grade)

| Layer | Choice | Why |
|---|---|---|
| **Frontend** | Next.js 16 (App Router) + TypeScript + Tailwind CSS 4 + shadcn/ui | Industry-standard, SSR for SEO/perf, large hiring pool, easy Vercel deploy |
| **Mobile (later)** | React Native (Expo) — *post-v1.0 only* | Shares TS skills with web; defer until after graduation |
| **Backend API** | FastAPI (Python 3.12) + Pydantic v2 + Uvicorn | Python ecosystem for AI, async, type-safe, OpenAPI auto-generated |
| **ORM / Migrations** | SQLAlchemy 2.0 + Alembic | Mature, supports PG features (JSONB, pgvector) |
| **Primary DB** | PostgreSQL 16 | Relational + JSONB + pgvector extension (simplifies infra) |
| **Vector DB** | Qdrant (self-hosted, single node) | Purpose-built, fast, simple ops, free; pgvector used as fallback if ops too heavy |
| **Knowledge Graph** | Neo4j Community Edition | Mature, Cypher is learnable, good viz ecosystem; fallback: store graph as JSONB in PG |
| **LLM Gateway** | LiteLLM (proxy) in front of OpenAI / Anthropic / GLM | Swap providers without code change; central cost control |
| **Embeddings** | `bge-m3` (open-source, multilingual) self-hosted OR OpenAI `text-embedding-3-small` | BGE for cost control; OpenAI for speed |
| **OCR** | PaddleOCR (primary) + Tesseract (fallback) + Google Document AI (for hard cases) | Open-source base; managed service as escalation path |
| **Document parsing** | unstructured.io + PyMuPDF | Handles PDFs, DOCX, PPTX, images |
| **Chunking / Retrieval** | LangChain (orchestration) + BM25 hybrid + reranker (bge-reranker-v2-m3) | Hybrid retrieval beats pure vector |
| **Async jobs / Queue** | Redis 7 + Celery 5 | Standard, simple, battle-tested |
| **Cache** | Redis (shared with queue) | Single infra component |
| **Object storage** | MinIO (self-hosted) or AWS S3 | For uploaded PDFs, images, generated artifacts |
| **Auth** | Self-hosted (JWT + refresh tokens) using `fastapi-users` or `supertokens` | Avoid vendor lock-in; Supertokens gives SaaS-style UX for free |
| **Containerization** | Docker + Docker Compose (dev) | Standard |
| **Orchestration** | Docker Swarm (single-node) or k3s (lightweight K8s) — **NOT full K8s** | K8s is overkill for a 9-person team; k3s gives a path to scale later |
| **CI/CD** | GitHub Actions | Free for OSS / student accounts; deep GitHub integration |
| **IaC** | Terraform (light) or simple shell scripts | Don't over-engineer; IaC only for prod infra |
| **Cloud provider** | AWS (EC2 + RDS + S3) or Hetzner (cheaper) | Hetzner for cost; AWS for ecosystem |
| **Monitoring** | Grafana + Prometheus + Loki + OpenTelemetry | Self-hosted, free, industry standard |
| **Error tracking** | Sentry (free tier) | Free for small teams |
| **Frontend analytics** | PostHog (self-hosted) | Product analytics + session replay |
| **Feature flags** | Unleash (self-hosted) or simple env vars | Decouple deploy from release |
| **Test framework** | pytest (backend), Vitest + Playwright (frontend) | Standard |
| **Documentation** | Docusaurus (public docs) + Markdown ADRs in repo | Docs-as-code |
| **Project mgmt** | GitHub Projects (boards) + Linear (if budget) | Tightly coupled with code |

### 4.2 Fallback Stack (MVP-grade, lighter ops)

Use this if by **mid-January 2027** the team is more than 2 weeks behind schedule. It collapses several infra components into managed services to reduce ops burden.

| Layer | Fallback choice | Trade-off |
|---|---|---|
| Frontend | Next.js 16 (same) | — |
| Backend | Next.js API Routes (Route Handlers) + Server Actions | No separate Python service; loses Python ML ecosystem, so ML must run as separate worker or be replaced with API calls |
| DB | PostgreSQL (Supabase or Neon managed) + pgvector | Single DB; vector search via pgvector; no separate Qdrant |
| LLM | OpenAI API only (no LiteLLM) | Locks us to one provider; simpler |
| OCR | Google Document AI (managed) only | Pay-per-page; no ops; expensive at scale but trivial to start |
| Embeddings | OpenAI `text-embedding-3-small` | No model hosting |
| Knowledge Graph | Store as JSONB in PostgreSQL; use recursive CTEs | No Neo4j ops; loses graph queries |
| Queue | Inngest or Trigger.dev (serverless) | No Redis ops |
| Auth | Clerk or Supabase Auth | Managed auth; pay-per-MAU |
| Hosting | Vercel (frontend) + Railway / Render (workers) | Minimal ops; vendor lock-in |
| Monitoring | Vercel Analytics + Sentry + Axiom (logs) | All managed |
| CI/CD | Vercel + Railway built-in + GH Actions for tests | Minimal config |

**The Fallback Stack can be stood up in 1 week by 2 engineers.** It is the escape hatch if the Primary Stack's ops burden becomes a project risk.

### 4.3 Stack decision matrix

| Criterion | Primary | Fallback | Notes |
|---|---|---|---|
| Production maturity | High | Medium | Primary gives real ops story; Fallback hides it |
| Ops burden | High | Low | Fallback saves ~80 person-hours over the project |
| Cost (10-month run) | ~$300–600/mo | ~$150–400/mo + per-call costs | Fallback cost scales with usage |
| Post-graduation path | Strong (can scale) | Weak (vendor lock-in) | Primary if startup path is serious |
| Skill ramp-up | Steeper | Gentler | Fallback uses only TS + managed services |
| AI/ML ecosystem fit | Strong (Python) | Weak (JS) | Primary strongly preferred for AI work |

**Recommendation:** Start with the **Primary Stack**. The AI/ML ecosystem fit alone justifies it — Python is non-negotiable for serious RAG/KG/adaptive work. Switch to Fallback only if (a) Pod D is unable to keep primary infra healthy by January 2027, OR (b) two or more critical-path slips have already been consumed.

---

## 5. MVP Definition & Version Roadmap (v0.1 → v1.0)

The MVP is **not** "all features, less polished." It is the **smallest end-to-end working system that demonstrates the core value proposition**: a student uploads a course PDF, the platform ingests it, and the student can ask questions about it and get cited answers. Everything else (KG, adaptive engine, analytics, recommendations) is built *on top of* this loop, not alongside it.

### 5.1 The MVP statement (one sentence)

> **A logged-in student can upload a PDF, the platform extracts its text and images, embeds the content, and the student can chat with the document and get cited answers — all deployed to a real URL.**

That is v0.5. Everything before it is scaffolding; everything after it is depth.

### 5.2 Version roadmap

| Version | Target date | Theme | What's new | Demoable? |
|---|---|---|---|---|
| **v0.1** | Sep 12, 2026 (W6) | Skeleton | Repo, CI, dev env, empty Next.js + FastAPI, auth scaffold, hello-world deploy | Yes — "we can log in to a deployed URL" |
| **v0.2** | Sep 26, 2026 (W8) | Foundations | User mgmt, course CRUD, file upload to S3/MinIO, basic UI shell | Yes — "instructor can create a course and upload a PDF" |
| **v0.3** | Oct 24, 2026 (W12) | Ingestion | OCR pipeline (PDF → text + structure), chunking, raw text stored | Yes — "PDF is parsed, text visible in UI" |
| **v0.4** | Nov 21, 2026 (W16) | Retrieval | Embeddings, vector DB (Qdrant), similarity search, basic reranking | Yes — "find similar chunks for a query" |
| **v0.5** | Dec 19, 2026 (W20) | **RAG MVP** | RAG chat with citations, end-to-end student flow, Architecture Freeze | **Yes — the MVP demo** |
| **v0.6** | Jan 30, 2027 (W26) | Knowledge layer | Knowledge Graph (concept extraction, relations), KG-backed retrieval boost | Yes — "see concepts extracted from your PDF" |
| **v0.7** | Feb 27, 2027 (W30) | Student model | Cognitive model (mastery estimates from quiz results), quiz generation v1 | Yes — "student takes a quiz, mastery updates" |
| **v0.8** | Mar 27, 2027 (W34) | Adaptation | Adaptive engine (next-best-concept, difficulty adjustment), recommendation v1 | Yes — "system recommends next concept" |
| **v0.9** | Apr 24, 2027 (W38) | Analytics + polish | Learning analytics dashboard, admin dashboard, **Feature Freeze** | Yes — "instructor sees cohort analytics" |
| **v1.0-rc** | May 22, 2027 (W42) | Hardening | Perf, security, bug bash, **Code Freeze** | Yes — full demo on staging |
| **v1.0** | Jun 5, 2027 (W44) | **Graduation** | Production deployment, final docs, graduation presentation | Yes — final demo on prod |

### 5.3 What is explicitly NOT in MVP (v0.5)

To protect the schedule, the following are **deferred past v0.5** and built only if v0.5 ships on time:

- Knowledge Graph (v0.6)
- Student Cognitive Model (v0.7)
- Adaptive Engine (v0.8)
- Recommendation Engine (v0.8)
- Personalized quizzes with adaptation (v0.7 has non-adaptive quizzes; v0.8 makes them adaptive)
- Learning analytics dashboard (v0.9)
- Admin dashboard (v0.9)
- Mobile app (post-v1.0)
- Multi-tenant / school-level isolation (post-v1.0)
- Real-time collaboration (never, in this scope)
- SSO / SAML (post-v1.0)
- Offline mode (never, in this scope)

### 5.4 MVP exit criteria (the "definition of done" for v0.5)

v0.5 is the most important gate in the entire roadmap. If we miss it, every subsequent date slips. v0.5 is "done" when **all** of the following are true:

1. ✅ A student can register, log in, and be enrolled in a course.
2. ✅ An instructor can create a course and upload a PDF (≤ 50 MB).
3. ✅ The PDF is processed by OCR within 5 minutes and the extracted text is visible in the UI.
4. ✅ The extracted text is chunked, embedded, and stored in the vector DB.
5. ✅ The student can ask a natural-language question about the PDF and get an answer with at least 2 source citations pointing to specific chunks.
6. ✅ The system is deployed to a public URL (not localhost).
7. ✅ CI passes on `main` with ≥ 40% line coverage on critical paths.
8. ✅ The system survives a 10-minute demo without crashing.
9. ✅ An Architecture Decision Record (ADR) exists for every major component.
10. ✅ Architecture Freeze is signed off by all pod leads.

If any of the above is false on Dec 19, 2026, we **trigger the descope protocol** (§22.4): cut KG scope, cut adaptive scope, and re-plan the spring around a thinner v0.6.

---

## 6. High-Level Project Phases

The 44-week plan is divided into **7 phases** plus a graduation tail. Each phase has a single theme, a single owner, and a hard exit gate.

| Phase | Name | Window | Weeks | Theme | Primary pod | Exit gate |
|---|---|---|---|---|---|---|
| **P0** | Pre-Flight | Aug 3 – Aug 30, 2026 | W1–4 | Setup, decisions, MVP def | All pods | v0.1 deployed |
| **P1** | Foundations | Aug 31 – Sep 27, 2026 | W5–8 | Auth, courses, upload, UI shell | Pod A + C | v0.2 deployed |
| **P2** | AI Pipeline | Sep 28 – Dec 20, 2026 | W9–20 | OCR → embeddings → RAG MVP | Pod B (with A+C) | **v0.5 + Architecture Freeze** |
| **P3** | Knowledge & Cognition | Dec 21, 2026 – Feb 27, 2027 | W21–30 | KG + student model + quizzes | Pod B (light) | v0.7 |
| **P4** | Adaptation & Analytics | Feb 28 – Apr 24, 2027 | W31–38 | Adaptive engine, recommendations, dashboards | Pod B + C | v0.9 + **Feature Freeze** |
| **P5** | Hardening | Apr 25 – May 23, 2027 | W39–42 | Perf, security, bug bash, docs | Pod D (lead) + all | v1.0-rc + **Code Freeze** |
| **P6** | Graduation | May 24 – Jun 27, 2027 | W43–44 | Demo, submission, handoff | TPM + all | v1.0 + presentation |

### 6.1 Phase themes (one-paragraph each)

**P0 — Pre-Flight (4 weeks, high capacity).** Lock the stack, stand up repo/CI/environments, write the MVP definition, write the first 5 ADRs, build the empty Next.js + FastAPI skeleton, deploy a hello-world to a real URL. The single goal of P0 is to remove every excuse for not starting real work in P1.

**P1 — Foundations (4 weeks, high capacity).** Build the boring-but-required backbone: auth, user management, course management, file upload, basic UI shell with routing and design tokens. Nothing AI-related ships here, but Pod B uses P1 to spike OCR and embedding options in parallel so they hit the ground running in P2.

**P2 — AI Pipeline (12 weeks, mixed capacity).** This is the make-or-break phase. OCR → chunking → embeddings → vector DB → RAG. The phase ends with **v0.5 (the MVP)** and **Architecture Freeze**. P2 spans the start of the university semester, so capacity drops mid-phase; the plan front-loads the hardest work (OCR + embeddings) into the first 6 weeks.

**P3 — Knowledge & Cognition (10 weeks, low capacity).** Knowledge Graph, student cognitive model, and the first version of quiz generation. This phase covers the December holiday lull and the January exam crunch, so it is intentionally lighter on parallelism and heavier on independent work-streams. The phase ends with v0.7 — a system that can extract concepts, store them in a graph, and update a student mastery score from quiz results.

**P4 — Adaptation & Analytics (8 weeks, recovering capacity).** Adaptive engine, recommendation engine, learning analytics dashboard, admin dashboard. The phase ends with **v0.9 and Feature Freeze** — no new features after this point, only fixes.

**P5 — Hardening (4 weeks, full capacity post-exams).** Performance pass, security review, full bug bash, documentation completion, runbooks. Ends with **v1.0-rc and Code Freeze** — only critical fixes after this point.

**P6 — Graduation (2 weeks).** Final production deployment, dry-run of the presentation, submission of artifacts, handoff to a post-graduation maintainer (if continuing as a startup).

---

## 7. Master Timeline Table (Aug 2026 → Jun 2027)

Weeks are numbered W1–W44 from the project start (Aug 3, 2026). "Cap" = effective person-hours/week (from §2.2). "Risk" = schedule risk for that week (L/M/H).

| Wk | Dates | Phase | Cap | Risk | Headline milestone | Exit criterion |
|---|---|---|---|---|---|---|
| W1 | Aug 3–9 | P0 | 153 | L | Kickoff, stack lock, repo + CI | GH org, repo, CI green on hello-world |
| W2 | Aug 10–16 | P0 | 153 | L | Environments, MVP sign-off | dev/stage/prod envs exist; MVP doc approved |
| W3 | Aug 17–23 | P0 | 153 | L | Next.js + FastAPI skeleton | Empty app deployed to public URL |
| W4 | Aug 24–30 | P0 | 153 | L | ADRs 1–5, design tokens | 5 ADRs merged; v0.1 tagged |
| W5 | Aug 31 – Sep 6 | P1 | 153 | L | Auth scaffold, user mgmt | Login/register works on staging |
| W6 | Sep 7–13 | P1 | 153 | L | Course CRUD, file upload | v0.1 demoed; v0.2 branch started |
| W7 | Sep 14–20 | P1 | 153 | M | UI shell, routing, design system | All routes exist (empty) |
| W8 | Sep 21–27 | P1 | 153 | M | **v0.2 deployed** | Instructor can upload PDF |
| W9 | Sep 28 – Oct 4 | P2 | 120 | M | OCR spike converges; PaddleOCR chosen | OCR extracts text from sample PDF |
| W10 | Oct 5–11 | P2 | 90 | M | OCR pipeline (PDFs + images) | OCR runs in async job; text stored |
| W11 | Oct 12–18 | P2 | 80 | H | Chunking + parsing | Chunks stored with metadata |
| W12 | Oct 19–25 | P2 | 70 | H | **v0.3** + embedding spike | v0.3 demoed; embedding model chosen |
| W13 | Oct 26 – Nov 1 | P2 | 65 | H | Embeddings batch job | 1k chunks embedded end-to-end |
| W14 | Nov 2–8 | P2 | 60 | H | Vector DB (Qdrant) deployed | Similarity search works |
| W15 | Nov 9–15 | P2 | 60 | H | Hybrid retrieval + reranker | Top-k retrieval with rerank |
| W16 | Nov 16–22 | P2 | 60 | H | **v0.4** + RAG prompt assembly | v0.4 demoed; RAG skeleton |
| W17 | Nov 23–29 | P2 | 55 | H | RAG chat with citations | Chat returns cited answer |
| W18 | Nov 30 – Dec 6 | P2 | 55 | H | Student flow end-to-end | Full upload→chat flow works |
| W19 | Dec 7–13 | P2 | 50 | M | **Architecture Freeze draft** | ADRs 1–15 complete; freeze reviewed |
| W20 | Dec 14–20 | P2 | 50 | M | **v0.5 + Architecture Freeze** | **MVP shipped; freeze signed** |
| W21 | Dec 21–27 | P3 | 30 | L | Holiday — light work | KG schema ADR drafted |
| W22 | Dec 28 – Jan 3 | P3 | 25 | L | Holiday — concept extraction spike | SpaCy / LLM-based extractor compared |
| W23 | Jan 4–10 | P3 | 50 | M | Concept extraction pipeline | Concepts extracted from sample docs |
| W24 | Jan 11–17 | P3 | 45 | M | KG storage (Neo4j) | KG populated with 100+ concepts |
| W25 | Jan 18–24 | P3 | 30 | H | KG-backed retrieval boost | RAG quality improves with KG |
| W26 | Jan 25–31 | P3 | 20 | H | **v0.6** + exam crunch begins | v0.6 demoed (small) |
| W27 | Feb 1–7 | P3 | 15 | H | Quiz generation v1 (non-adaptive) | LLM generates MCQ from chunks |
| W28 | Feb 8–14 | P3 | 40 | M | Quiz UI + grading | Student can take a quiz |
| W29 | Feb 15–21 | P3 | 60 | M | Cognitive model design (IRT/Bayes) | ADR for student model approved |
| W30 | Feb 22–28 | P3 | 70 | M | **v0.7** + mastery updates from quiz | **v0.7 shipped** |
| W31 | Mar 1–7 | P4 | 65 | M | Adaptive engine design | ADR for adaptive policy approved |
| W32 | Mar 8–14 | P4 | 65 | H | Next-best-concept policy | Recommendations appear in UI |
| W33 | Mar 15–21 | P4 | 65 | H | Difficulty adjustment | Quiz difficulty adapts to mastery |
| W34 | Mar 22–28 | P4 | 65 | H | Recommendation engine v1 | "Recommended next" works |
| W35 | Mar 29 – Apr 4 | P4 | 60 | M | Learning analytics dashboard | Instructor sees cohort metrics |
| W36 | Apr 5–11 | P4 | 55 | M | Admin dashboard | Admin can manage users/courses |
| W37 | Apr 12–18 | P4 | 50 | M | Bug bash #1 + UX polish | Top-50 bugs triaged |
| W38 | Apr 19–25 | P4 | 45 | M | **v0.9 + Feature Freeze** | **No new features after this** |
| W39 | Apr 26 – May 2 | P5 | 60 | M | Perf pass + load test | P95 latency < 2s on RAG |
| W40 | May 3–9 | P5 | 90 | M | Security review (OWASP) | No critical/high vulns open |
| W41 | May 10–16 | P5 | 120 | M | Bug bash #2 + docs completion | Runbooks + ADRs finalized |
| W42 | May 17–23 | P5 | 150 | L | **v1.0-rc + Code Freeze** | **Only critical fixes after this** |
| W43 | May 24–30 | P6 | 170 | L | Prod deployment + dry-run | v1.0 on prod; demo rehearsed |
| W44 | May 31 – Jun 6 | P6 | 176 | L | **v1.0 + graduation presentation** | **Final demo delivered** |
| — | Jun 7–27 | — | buffer | L | Buffer / submission window | Artifacts submitted |

---

## 8. Gantt-Style Textual Schedule

Each row is a workstream. Each column is a 2-week bucket. `█` = active work, `▓` = active with reduced capacity, `░` = maintenance/light, `◆` = milestone, `✱` = critical path.

```
Workstream                      | Aug | Sep | Oct | Nov | Dec | Jan | Feb | Mar | Apr | May | Jun |
                                | W1-4| W5-8|W9-12|W13-16|W17-20|W21-24|W25-28|W29-32|W33-36|W37-40|W41-44|
--------------------------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
P0 Setup & Decisions            |  █  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
P1 Auth / User / Course / Upload|  ░  |  █  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
P2 OCR pipeline ✱               |  ░  |  ░  |  █  |  █  |  ▓  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
P2 Chunking + Embeddings ✱      |  ░  |  ░  |  ▓  |  █  |  ▓  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
P2 Vector DB ✱                  |  ░  |  ░  |  ░  |  █  |  █  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
P2 RAG layer ✱                  |  ░  |  ░  |  ░  |  ▓  |  █  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
--- v0.5 MVP demo ◆ ---         |     |     |     |     |  ◆  |     |     |     |     |     |     |
--- Architecture Freeze ◆ ---   |     |     |     |     |  ◆  |     |     |     |     |     |     |
P3 Knowledge Graph ✱            |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  █  |  ▓  |  ░  |  ░  |  ░  |
P3 Quiz generation ✱            |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  █  |  ▓  |  ░  |  ░  |  ░  |
P3 Student Cognitive Model ✱    |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  █  |  ░  |  ░  |  ░  |
--- v0.7 ◆ ---                  |     |     |     |     |     |     |     |  ◆  |     |     |     |
P4 Adaptive Engine ✱            |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  █  |  █  |  ░  |  ░  |
P4 Recommendation Engine        |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  █  |  ░  |  ░  |
P4 Analytics Dashboard          |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  █  |  ░  |  ░  |
P4 Admin Dashboard              |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  █  |  ░  |  ░  |
--- v0.9 + Feature Freeze ◆ --- |     |     |     |     |     |     |     |     |  ◆  |     |     |
P5 Perf / Security / Hardening  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  █  |  ▓  |
P5 Documentation                |  ▓  |  ▓  |  ▓  |  ▓  |  █  |  ▓  |  ▓  |  ▓  |  █  |  █  |  ▓  |
--- v1.0-rc + Code Freeze ◆ --- |     |     |     |     |     |     |     |     |     |  ◆  |     |
P6 Demo prep + Prod deploy      |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  █  |
--- v1.0 Graduation ◆ ---       |     |     |     |     |     |     |     |     |     |     |  ◆  |

Cross-cutting:
  CI/CD                          |  █  |  █  |  █  |  █  |  █  |  ▓  |  ▓  |  █  |  █  |  █  |  █  |
  Testing                        |  ▓  |  █  |  █  |  █  |  █  |  ▓  |  █  |  █  |  █  |  █  |  █  |
  Weekly demos (from W3)         |  ░  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |
  Biweekly retros                |  ░  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |
  Risk register updates          |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |
```

**Reading the Gantt:**
- The **critical path** (✱) runs OCR → Chunking → Embeddings → Vector DB → RAG → KG → Quiz → Student Model → Adaptive Engine. Any slip on these rows cascades.
- **Adaptive Engine is the latest-starting critical-path item** (P4, W31). If RAG/Architecture Freeze slips past W20, adaptive engine gets squeezed against Feature Freeze (W38) — see Risk R-03.
- **Dashboards (analytics + admin)** are off the critical path and can be descoped to stubs if needed.
- **Documentation** runs in parallel from W4 onward — never concentrated at the end.

---

## 9. Monthly Milestones

A monthly milestone is a **demoable, externally verifiable artifact**. If a month ends without hitting its milestone, the TPM triggers the descope protocol (§22.4).

| Month | Calendar | Milestone name | Verifiable artifact |
|---|---|---|---|
| **Aug 2026** | W1–4 | "Hello World on a real URL" | v0.1 deployed; CI green; 5 ADRs in repo |
| **Sep 2026** | W5–8 | "Foundations" | v0.2 deployed: auth + course CRUD + PDF upload |
| **Oct 2026** | W9–13 | "OCR works" | v0.3: PDF → extracted text in DB; embedding spike done |
| **Nov 2026** | W14–17 | "Retrieval works" | v0.4: vector DB + hybrid retrieval; RAG skeleton |
| **Dec 2026** | W18–20 | **"MVP shipped"** | **v0.5 + Architecture Freeze signed** |
| **Jan 2027** | W21–24 | "KG taking shape" | v0.6 partial: KG populated with 100+ concepts (exam-crunch tolerance) |
| **Feb 2027** | W25–28 | "Quizzes + mastery" | v0.7: student takes quiz, mastery updates |
| **Mar 2027** | W29–32 | "Adaptation works" | Adaptive engine picks next concept; difficulty adjusts |
| **Apr 2027** | W33–36 | "Feature-complete" | **v0.9 + Feature Freeze**; dashboards functional |
| **May 2027** | W37–40 | "Hardened" | **v1.0-rc + Code Freeze**; perf + security passes |
| **Jun 2027** | W41–44 | **"Graduation"** | **v1.0 on prod; presentation delivered** |

### 9.1 Monthly milestone review protocol

On the **last Friday of every month**, the TPM runs a 90-minute **Milestone Review** with all pod leads. Agenda:

1. (15 min) Demo the milestone artifact on staging. Live, not screenshots.
2. (15 min) Compare actual progress vs. plan; surface any slip ≥ 3 days.
3. (20 min) Update risk register; add new risks; close mitigated ones.
4. (20 min) Re-plan the next 4 weeks at sprint level; rebalance pod allocations if needed.
5. (10 min) Decide any descopes — *now*, not at the next review.
6. (10 min) Communicate decisions to the full team in writing before EOD.

**Hard rule:** if a monthly milestone is missed by more than 1 week, the descope protocol (§22.4) is triggered automatically. No "we'll catch up next month."

---

## 10. Weekly Sprint Plan (Sprint-Level Granularity)

**Sprint length: 1 week.** Each sprint runs Monday → Friday with a demo on Friday. Each sprint has **1 owner**, **1 deliverable**, and **1 exit criterion**. If the exit criterion is not met by Friday demo, the work rolls into next week's sprint *and* a risk is logged.

Notation: `Owner [pod]` — pods are A (Backend), B (AI/ML), C (Frontend), D (DevOps/QA), TPM.

### 10.1 Phase P0 — Pre-Flight (W1–W4)

| Wk | Sprint name | Owner [pod] | Deliverable | Exit criterion |
|---|---|---|---|---|
| W1 | Kickoff + stack lock | TPM | Stack decision doc signed; GH org + repo created; README with team norms | Repo exists; PR template + CODEOWNERS in place |
| W1 | CI scaffold | D-Lead | GitHub Actions workflow: lint + test on every PR | CI green on a dummy PR |
| W1 | Env provisioning | D-Lead | `dev` / `staging` / `prod` environments documented and reachable | Each env has a URL |
| W2 | MVP sign-off | TPM | MVP definition doc (§5) approved by all pod leads | Doc merged; no open objections after 48h |
| W2 | Next.js skeleton | C-Lead | Empty Next.js 16 app with routing, Tailwind, shadcn/ui, Storybook | App runs locally and on Vercel/preview |
| W2 | FastAPI skeleton | A-Lead | Empty FastAPI app with health check, OpenAPI docs, CORS, env config | `/health` returns 200 on staging |
| W3 | Deploy hello-world | D-Lead | Both apps deployed to public URLs over HTTPS | URLs accessible from outside the team |
| W3 | DB + migrations baseline | A-Lead | Postgres provisioned; Alembic init; first migration creates `users` table | Migration runs on all envs |
| W3 | Design tokens | C-Lead | Tailwind config + shadcn theme; Storybook shows base components | Tokens reviewed and locked |
| W4 | ADR-001 through ADR-005 | TPM | ADRs for: stack, repo structure, API versioning, env management, LLM gateway | 5 ADRs merged |
| W4 | Risk register v1 | TPM | Risk register (§21) seeded with ≥ 15 risks | Reviewed in W4 retro |
| W4 | **v0.1 tag + demo** | All | Tag `v0.1.0` in repo; demo: log in to deployed URL | Demo passes without crash |

### 10.2 Phase P1 — Foundations (W5–W8)

| Wk | Sprint name | Owner [pod] | Deliverable | Exit criterion |
|---|---|---|---|---|
| W5 | Auth: register + login | A-1 [A] | Email/password register, login, JWT issue/refresh; tests | Auth flow works on staging; tests ≥ 80% |
| W5 | Auth UI | C-1 [C] | Register/login pages, protected routes, session handling | User can register and reach a protected page |
| W5 | OCR spike (parallel) | B-Lead [B] | Compare PaddleOCR vs Tesseract vs Document AI on 5 sample PDFs | Choice ADR drafted |
| W5 | Embedding spike (parallel) | B-1 [B] | Compare BGE-M3 vs OpenAI text-embedding-3-small on quality + latency | Choice ADR drafted |
| W6 | User mgmt: profile + RBAC | A-2 [A] | Profile CRUD; roles: student/instructor/admin; middleware enforcement | RBAC tests pass |
| W6 | Course CRUD API | A-Lead [A] | `/v1/courses` CRUD; ownership checks | Postman collection + tests |
| W6 | Course UI | C-2 [C] | Course list, create, edit pages; instructor-only | Instructor can create a course |
| W6 | File upload to S3/MinIO | A-1 [A] | Presigned upload; server-side download; virus scan stub | PDF uploads to storage and is retrievable |
| W7 | Routing + nav | C-Lead [C] | App shell with sidebar, topnav, breadcrumbs, route guards | All routes exist (empty pages OK) |
| W7 | Async job infra | D-Lead [D] | Celery + Redis running; sample task; Flower dashboard | A queued job completes |
| W7 | Observability baseline | D-Lead [D] | Logs to Loki, metrics to Prometheus, Sentry for errors | A test error appears in Sentry |
| W7 | LLM gateway | B-Lead [B] | LiteLLM proxy deployed; key rotation; cost tracking | A test prompt returns a response |
| W8 | Integration: course → upload → storage | A-Lead [A] | End-to-end: instructor creates course, uploads PDF, sees it listed | E2E Playwright test passes |
| W8 | First user-facing docs | C-Lead [C] | Docusaurus site; "Getting Started" + "Instructor quickstart" | Docs deploy to a URL |
| W8 | **v0.2 tag + demo** | All | Tag `v0.2.0`; demo: instructor creates course + uploads PDF | Demo passes; exit gate §5.2 met |

### 10.3 Phase P2 — AI Pipeline (W9–W20) — CRITICAL PATH

| Wk | Sprint name | Owner [pod] | Deliverable | Exit criterion |
|---|---|---|---|---|
| W9 | OCR pipeline v1 | B-Lead [B] | Async job: PDF → text + layout JSON; stored in DB | 5 sample PDFs processed; text extracted |
| W9 | OCR UI feedback | C-1 [C] | Upload progress + extracted text preview | User sees extraction in UI |
| W10 | OCR hardening (images, multi-page, scanned) | B-1 [B] | Handle images, scanned PDFs, multi-page; fallback to Document AI on failure | 20 PDFs processed; ≥ 90% success |
| W10 | Document model + ingestion service | A-2 [A] | `documents` table; ingestion status; idempotency | Re-uploading same PDF doesn't duplicate |
| W11 | Chunking strategy | B-Lead [B] | Recursive + semantic chunking; metadata (page, section); ADR | 1 PDF → 100+ chunks with metadata |
| W11 | Chunking API + storage | A-Lead [A] | `/v1/documents/{id}/chunks` endpoint; paginated | Frontend can fetch chunks |
| W12 | **v0.3 tag + demo** | All | Demo: upload PDF, see extracted text + chunks | v0.3 demo passes |
| W12 | Embedding batch job | B-1 [B] | Async job: chunk → embedding → store; batching; rate limit | 1,000 chunks embedded end-to-end |
| W13 | Vector DB deploy (Qdrant) | D-Lead [D] | Qdrant running; collection schema; backup script | Vector DB reachable from backend |
| W13 | Embedding write path | A-Lead [A] | Embeddings written to Qdrant on chunk creation | New chunks auto-embed |
| W13 | Similarity search API | A-2 [A] | `/v1/search?q=...` returns top-k chunks | Endpoint returns ranked results |
| W14 | Hybrid retrieval (BM25 + vector) | B-Lead [B] | Combine BM25 + vector scores; weighting | Hybrid beats pure vector on golden set |
| W14 | Reranker integration | B-1 [B] | bge-reranker-v2-m3 cross-encoder; top-20 → top-5 | Reranker improves precision@5 |
| W15 | RAG prompt assembly | B-Lead [B] | Prompt template with citations; LLM gateway call; safety | Prompt returns answer with [1], [2] cites |
| W15 | Citation rendering | C-1 [C] | Clickable citations jump to source chunk | User can verify source |
| W16 | **v0.4 tag + demo** | All | Demo: ask a question, get cited answer | v0.4 demo passes |
| W16 | RAG chat API + streaming | A-Lead [A] | `/v1/chat` SSE streaming; session persistence | Chat works via curl |
| W16 | Chat UI | C-Lead [C] | Chat interface with history, streaming, source panel | User can hold a conversation |
| W17 | RAG eval harness | B-Lead [B] | Golden Q&A set (50 Qs); eval script; faithfulness + relevance scores | Eval runs in CI on every PR |
| W17 | Student flow integration | A-2 [A] | Student enrolls → sees course → uploads → chats | E2E Playwright test |
| W18 | Multi-document RAG | B-1 [B] | Retrieval spans all docs in a course; doc-level filters | User asks across course material |
| W18 | Polish + bug fixes | All | Address top-20 bugs from W17 demo | Bug list ≤ 5 open P1s |
| W19 | Architecture Freeze draft | TPM | ADRs 1–15 complete; interface contracts frozen; freeze review meeting | All pod leads sign draft |
| W19 | Docs sweep | C-Lead [C] | API reference auto-generated; ADR index; architecture diagram | Docs reflect actual code |
| W20 | **v0.5 + Architecture Freeze** | All | Tag `v0.5.0`; sign Architecture Freeze; MVP demo to advisor | Exit gate §5.4 met |

### 10.4 Phase P3 — Knowledge & Cognition (W21–W30)

*Note: capacity drops significantly through this phase due to holidays (W21–22) and exam crunch (W25–27). Plan is intentionally lighter on parallelism.*

| Wk | Sprint name | Owner [pod] | Deliverable | Exit criterion |
|---|---|---|---|---|
| W21 | KG schema ADR | B-Lead [B] | ADR-016: KG data model (concepts, relations, provenance) | ADR merged |
| W21 | Holiday — light maintenance | All | Bug triage; tech debt cleanup | Open bug count ≤ 10 |
| W22 | Concept extraction spike | B-1 [B] | Compare spaCy + LLM-based extraction on 3 docs | Choice ADR drafted |
| W22 | Holiday — light maintenance | All | Continue triage | — |
| W23 | Concept extraction pipeline | B-Lead [B] | Async job: chunks → concepts + relations; LLM-assisted | 5 docs → 200+ concepts |
| W23 | KG storage (Neo4j) | D-Lead [D] | Neo4j deployed; schema; import script | KG populated |
| W24 | KG API | A-Lead [A] | `/v1/kg/concepts`, `/v1/kg/relations` endpoints | Frontend can query KG |
| W24 | KG viz UI | C-1 [C] | Interactive concept graph (react-flow or d3) | User can browse the graph |
| W25 | KG-backed retrieval boost | B-Lead [B] | Use concept matches to reweight retrieval | Eval set faithfulness ↑ ≥ 5% |
| W25 | Quiz generation v1 (non-adaptive) | B-1 [B] | LLM generates MCQ from chunks; answer key; metadata | 10 quizzes generated |
| W26 | **v0.6 tag + small demo** | All | Demo: KG populated; concept browse; first quiz | v0.6 demo passes (small) |
| W26 | Quiz UI + grading | C-Lead [C] | Take quiz, submit, see score; instructor creates quiz | Student completes a quiz |
| W27 | Cognitive model design | B-Lead [B] | ADR-017: IRT vs Bayesian vs simple mastery; choice | ADR approved |
| W27 | Mastery estimator v1 | B-1 [B] | Update mastery from quiz results; store per (student, concept) | Mastery updates after quiz |
| W28 | Quiz integration end-to-end | A-Lead [A] | Quiz assigned → student takes → graded → mastery updated | E2E test |
| W28 | Mastery UI | C-2 [C] | Student sees mastery per concept; instructor sees cohort | Mastery visible in UI |
| W29 | Cognitive model hardening | B-Lead [B] | Cold-start handling; confidence intervals; sanity checks | Model behaves on edge cases |
| W29 | Quiz pool + tagging | B-1 [B] | Quiz bank with concept + difficulty tags; ≥ 100 items | Pool searchable |
| W30 | **v0.7 tag + demo** | All | Demo: quiz + mastery + KG, end-to-end | v0.7 demo passes |

### 10.5 Phase P4 — Adaptation & Analytics (W31–W38)

| Wk | Sprint name | Owner [pod] | Deliverable | Exit criterion |
|---|---|---|---|---|
| W31 | Adaptive engine design | B-Lead [B] | ADR-018: next-best-concept policy; difficulty adjustment rule | ADR approved |
| W31 | Next-best-concept v1 | B-1 [B] | Policy: pick concept with lowest mastery + most prereqs met | Returns a recommendation |
| W32 | Recommendation API + UI | A-Lead [A] + C-1 [C] | `/v1/recommendations`; "Recommended next" panel | Student sees recommendation |
| W32 | Difficulty adjustment | B-Lead [B] | Quiz difficulty tuned to current mastery | Difficulty adapts within ±1 level |
| W33 | Recommendation engine v1 | B-1 [B] | Content + peer recommendations; ranking | Top-3 recommendations shown |
| W33 | Adaptation eval harness | B-Lead [B] | Simulated student trajectories; metrics | Eval runs in CI |
| W34 | Learning analytics dashboard (backend) | A-Lead [A] | Aggregation queries: cohort mastery, quiz pass rates, engagement | Endpoints return data |
| W34 | Learning analytics dashboard (UI) | C-Lead [C] | Instructor dashboard with charts (Recharts/Visx) | Dashboard renders real data |
| W35 | Admin dashboard | C-2 [C] + A-2 [A] | User/course management, system health, audit log | Admin can manage users |
| W35 | Notification system (basic) | A-Lead [A] | In-app + email notifications for key events | Notifications fire on events |
| W36 | UX polish pass | C-Lead [C] | Address top UX issues from W35 demo | Polish review approved |
| W36 | Bug bash #1 (whole team) | D-Lead [D] | 90-min bug bash; triage all findings | Top-50 bugs in tracker |
| W37 | Bug fixing sprint | All | Close P1/P2 bugs from bash | ≤ 5 P1s open |
| W37 | Accessibility pass | C-1 [C] | WCAG 2.1 AA on critical paths | axe-core clean on key flows |
| W38 | **v0.9 + Feature Freeze** | All | Tag `v0.9.0`; sign Feature Freeze; demo to advisor | Exit gate §19.2 met |

### 10.6 Phase P5 — Hardening (W39–W42)

| Wk | Sprint name | Owner [pod] | Deliverable | Exit criterion |
|---|---|---|---|---|
| W39 | Performance pass | D-Lead [D] + A-Lead [A] | Profile + optimize; P95 latency < 2s on RAG; load test | Load test: 50 concurrent users OK |
| W39 | DB optimization | A-Lead [A] | Indexes; query plans; connection pool tuning | Slow query log clean |
| W40 | Security review | D-Lead [D] | OWASP top 10; SAST (Semgrep); dependency scan; pen test | No critical/high vulns open |
| W40 | Auth hardening | A-Lead [A] | Rate limiting; refresh rotation; MFA optional | Auth passes pen test |
| W41 | Bug bash #2 | All | 2-hour bash; close everything | ≤ 3 P1s open |
| W41 | Docs completion | C-Lead [C] + TPM | Runbooks, ADRs finalized, README, architecture diagram | Docs reviewed by advisor |
| W41 | Backup + DR drill | D-Lead [D] | Restore DB from backup; verify | DR drill completes < 1h |
| W42 | **v1.0-rc + Code Freeze** | All | Tag `v1.0.0-rc`; sign Code Freeze | Exit gate §19.3 met |

### 10.7 Phase P6 — Graduation (W43–W44)

| Wk | Sprint name | Owner [pod] | Deliverable | Exit criterion |
|---|---|---|---|---|
| W43 | Production deployment | D-Lead [D] | Deploy v1.0-rc to prod; smoke tests; DNS + TLS | Prod live; smoke tests pass |
| W43 | Demo dry-run #1 | TPM | Full 30-min presentation rehearsal; advisor feedback | Dry-run completed |
| W44 | Demo dry-run #2 + fixes | TPM + All | Final polish; fallback demo recorded | Demo reliably passes |
| W44 | **v1.0 + graduation presentation** | All | Tag `v1.0.0`; submit artifacts; deliver presentation | **Graduation delivered** |

---

## 11. Team Allocation per Phase

The same 9 people are re-allocated across phases based on where the bottleneck is. Pod D is small (1 person) so the TPM rotates one engineer from another pod into DevOps duty during high-ops phases (P0, P5).

| Phase | Pod A (Backend, 3) | Pod B (AI/ML, 3) | Pod C (Frontend, 2) | Pod D (DevOps/QA, 1) | TPM |
|---|---|---|---|---|---|
| **P0** (W1–4) | Skeleton + DB + env | Spikes: OCR + embeddings + LLM gateway | Next.js skeleton + design tokens | CI + envs + observability | Stack lock, MVP, ADRs, risk register |
| **P1** (W5–8) | Auth, user mgmt, course CRUD, file upload | (1 of 3 floats to Pod D for ops) → LLM gateway hardening | Course UI, routing, app shell | Async job infra, observability, env polish | Sprint ops, weekly demos |
| **P2** (W9–W20) | Document ingestion API, search API, chat API, integration tests | OCR pipeline, chunking, embeddings, vector DB, RAG, eval harness | Upload UI, chat UI, citation UI, KG viz preview | Vector DB ops, LLM gateway ops, cost monitoring | Architecture Freeze driving; risk reviews |
| **P3** (W21–30) | KG API, quiz API, integration tests | Concept extraction, KG construction, quiz generation, cognitive model | Quiz UI, mastery UI, KG viz | Neo4j ops, model artifact storage | Light — exam crunch; TPM focuses on unblocking individuals |
| **P4** (W31–38) | Recommendation API, analytics aggregation, admin API | Adaptive engine, recommendation engine, eval harness | Analytics dashboard, admin dashboard, polish | Test infra, perf monitoring, feature flags | Feature Freeze driving; graduation prep starts |
| **P5** (W39–42) | DB perf, auth hardening, integration test completion | Eval harness finalization, model artifact freeze | Docs completion, demo assets | Perf, security, DR drill, prod deployment prep | Code Freeze driving; presentation draft |
| **P6** (W43–44) | Hotfix standby | Hotfix standby | Demo polish, fallback recording | Prod deployment, monitoring on call | Demo rehearsals, submission, handoff |

### 11.1 Pod cross-training plan

A single-person pod (Pod D) is a **bus-factor risk** (see R-12). We mitigate by cross-training:

- **W4–W8:** One Pod A engineer spends 20% time shadowing Pod D on infra tasks.
- **W9–W20:** One Pod B engineer learns vector DB ops (Qdrant backups, index rebuilds).
- **W21–W30:** Cross-training is light (exam crunch); defer.
- **W31–W38:** One Pod C engineer learns basic CI/CD and Sentry triage.

By W38, at least **3 people** can do basic DevOps/QA tasks. This is a hard exit criterion for Feature Freeze (§19.2).

### 11.2 Pod lead time commitment

Pod leads are expected to spend ~20% of their time on lead duties: planning, reviewing, mentoring, attending syncs. This is built into the capacity model (§2.2) — leads are counted at ~80% productive engineering.

---

## 12. Critical Path Analysis

The **critical path** is the longest chain of dependent tasks that determines the minimum project duration. Any slip on the critical path slips the graduation date.

### 12.1 The critical path (chain)

```
Stack lock (W1)
  → OCR pipeline (W9–W10)
    → Chunking (W11)
      → Embeddings (W12–W13)
        → Vector DB + retrieval (W14–W15)
          → RAG layer (W15–W17)
            → Architecture Freeze (W19–W20)  [gate]
              → Concept extraction (W23)
                → Knowledge Graph populated (W24)
                  → Quiz generation (W25)
                    → Cognitive model (W27)
                      → Mastery estimator (W27)
                        → Adaptive engine (W31–W33)
                          → Feature Freeze (W38)  [gate]
                            → Hardening (W39–W41)
                              → Code Freeze (W42)  [gate]
                                → Production deploy (W43)
                                  → Graduation (W44)
```

**Critical path length:** ~30 weeks of dependent work (out of 44 total). The remaining 14 weeks are slack on non-critical paths (auth, UI, dashboards, docs) — but slack can be consumed if those tasks are not parallelized.

### 12.2 Critical path slack analysis

| Segment | Planned duration | Allowable slip before graduation slips | Trigger if slip exceeds |
|---|---|---|---|
| Stack lock → Architecture Freeze | 19 weeks (W1–W20) | 1 week | Switch to Fallback Stack |
| Architecture Freeze → v0.7 | 10 weeks (W21–W30) | 0 weeks (no slack — exam crunch) | Descope KG depth |
| v0.7 → Feature Freeze | 8 weeks (W31–W38) | 1 week | Descope recommendation engine |
| Feature Freeze → Code Freeze | 4 weeks (W39–W42) | 0 weeks | Cut hardening scope to must-haves |
| Code Freeze → Graduation | 2 weeks (W43–W44) | 0 weeks | Use recorded demo fallback |

**Total slack on critical path:** ~2 weeks. The 15% buffer (§22) is held *off* the critical path to absorb non-critical work overruns.

### 12.3 Critical path drivers (why each link is critical)

- **OCR pipeline** — every downstream AI component depends on having text. If OCR fails on real PDFs, everything stalls.
- **Embeddings + vector DB** — RAG depends on working retrieval. No retrieval, no RAG.
- **Architecture Freeze** — without frozen interfaces, integration work in P3/P4 thrashes.
- **Cognitive model** — adaptive engine depends on mastery estimates. No mastery, no adaptation.
- **Adaptive engine** — the latest-starting critical component. Most exposed to upstream slips.

### 12.4 Near-critical path (parallel chains that feed in)

These are not on the critical path but become critical if they slip badly:

- **Auth + course CRUD** (W5–W8) — must be done by W8 or P2 starts late.
- **Chat UI + citation rendering** (W15–W16) — must be done by W17 or v0.5 demo fails.
- **Quiz UI** (W26) — must be done by W27 or cognitive model has no input data.
- **Analytics dashboard** (W34–W35) — must be done by W36 or Feature Freeze slips.
- **Documentation** (continuous) — must be ≥ 80% by W41 or Code Freeze slips.

---

## 13. Module Dependencies

A dependency matrix between modules. "X → Y" means Y depends on X.

### 13.1 Dependency graph

```
                       ┌──────────────┐
                       │   Auth + RBAC │
                       └──────┬───────┘
                              │
                       ┌──────▼───────┐
                       │ Course CRUD  │
                       └──────┬───────┘
                              │
                       ┌──────▼───────┐
                       │  File Upload │
                       └──────┬───────┘
                              │
                       ┌──────▼───────┐
                       │ OCR Pipeline │ ──────┐
                       └──────┬───────┘       │
                              │               │
                       ┌──────▼───────┐       │
                       │  Chunking    │       │
                       └──────┬───────┘       │
                              │               │
                ┌─────────────┼─────────────┐ │
                ▼             ▼             ▼ │
         ┌──────────┐  ┌──────────┐  ┌────────────┐
         │Embeddings│  │ Concepts │  │  Quizzes   │
         └─────┬────┘  └─────┬────┘  └─────┬──────┘
               │             │             │
         ┌─────▼────┐  ┌─────▼────┐        │
         │ Vector DB│  │   KG     │        │
         └─────┬────┘  └─────┬────┘        │
               │             │             │
               └──────┬──────┘             │
                      ▼                    │
                ┌──────────┐               │
                │   RAG    │◄──────────────┘
                └─────┬────┘
                      │
                ┌─────▼─────┐
                │  Student  │
                │   Model   │
                └─────┬─────┘
                      │
                ┌─────▼─────┐
                │ Adaptive  │
                │  Engine   │
                └─────┬─────┘
                      │
                ┌─────▼─────┐
                │Recommend- │
                │  ations   │
                └───────────┘
```

### 13.2 Dependency matrix (table form)

| Module ↓ depends on → | Auth | Course | Upload | OCR | Chunking | Embed | VectorDB | KG | RAG | Quiz | StudentModel | Adaptive |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Course CRUD | ✓ | | | | | | | | | | | |
| File Upload | | ✓ | | | | | | | | | | |
| OCR Pipeline | | | ✓ | | | | | | | | | |
| Chunking | | | | ✓ | | | | | | | | |
| Embeddings | | | | | ✓ | | | | | | | |
| Vector DB | | | | | | ✓ | | | | | | |
| Knowledge Graph | | | | | ✓ | | | | | | | |
| RAG | | | | | | | ✓ | ✓ | | | | |
| Quiz generation | | | | | ✓ | | | ✓ | | | | |
| Student Model | | | | | | | | ✓ | | ✓ | | |
| Adaptive Engine | | | | | | | | ✓ | | ✓ | ✓ | |
| Recommendations | | | | | | | | ✓ | | ✓ | ✓ | ✓ |
| Analytics dashboard | | ✓ | | | | | | ✓ | | ✓ | ✓ | ✓ |

### 13.3 Interface contracts (the things that must be frozen at Architecture Freeze)

To allow parallel work, these interface contracts are frozen by W20 and *cannot change* without a re-architecture ADR:

1. **OCR output schema** — JSON structure of extracted text + layout.
2. **Chunk schema** — fields, metadata, IDs.
3. **Embedding I/O** — input text, output vector dim, model ID.
4. **Vector DB query API** — top-k search, filters, payload.
5. **RAG request/response** — query, filters, response with citations.
6. **KG concept/relation schema** — node types, edge types, provenance.
7. **Quiz schema** — question types, metadata, scoring.
8. **Student mastery schema** — per (student, concept) record.
9. **Adaptive engine I/O** — input: student state; output: next action.
10. **Auth token format** — JWT claims, refresh flow.

Any change after Architecture Freeze requires a new ADR, a migration plan, and TPM approval.

---

## 14. Integration Milestones

Integration is where most projects die. We define explicit integration milestones — moments where two or more components must work together for the first time — and budget time for the inevitable breakage.

| IM # | Week | Components integrated | Verifiable outcome | Owner |
|---|---|---|---|---|
| IM-1 | W6 | Frontend ↔ Auth ↔ DB | User registers in UI, appears in DB | A-Lead |
| IM-2 | W8 | Frontend ↔ Course API ↔ Storage | Instructor creates course + uploads PDF | A-Lead |
| IM-3 | W10 | Upload → OCR job → DB | Uploaded PDF's text is in DB | B-Lead |
| IM-4 | W13 | OCR → Chunking → Embeddings → VectorDB | Full ingestion pipeline runs end-to-end | B-Lead |
| IM-5 | W15 | VectorDB → Reranker → RAG | Query returns cited answer via curl | B-Lead |
| IM-6 | W16 | RAG ↔ Chat API ↔ Chat UI | User chats with document in browser | A-Lead + C-Lead |
| IM-7 | W17 | Full student flow (auth → course → upload → chat) | E2E Playwright test green | D-Lead |
| IM-8 | W24 | OCR → Concept extraction → KG | KG populated from new upload | B-Lead |
| IM-9 | W25 | KG → RAG retrieval boost | RAG eval faithfulness improves | B-Lead |
| IM-10 | W28 | Quiz generation → Quiz UI → Mastery update | Student takes quiz, mastery changes | A-Lead + C-Lead |
| IM-11 | W32 | Mastery → Adaptive engine → Recommendation UI | Student sees a recommendation | B-Lead + C-Lead |
| IM-12 | W33 | Adaptive engine → Quiz difficulty | Quiz difficulty adapts | B-Lead |
| IM-13 | W35 | Analytics dashboard ↔ real DB data | Instructor sees real cohort metrics | A-Lead + C-Lead |
| IM-14 | W41 | Full system on staging under load | 50 concurrent users; P95 < 2s | D-Lead |
| IM-15 | W43 | Production deployment end-to-end | v1.0 live on prod URL | D-Lead |

### 14.1 Integration protocol

Every integration milestone follows this protocol:

1. **T-3 days:** Both sides declare their interface "frozen for this integration."
2. **T-2 days:** Stub/mock of the other side is removed; real call is wired.
3. **T-1 day:** Both sides test on staging; bugs logged.
4. **T-day (Friday demo):** Live demo of the integrated flow. If it fails, the integration rolls into next week *and a risk is logged*.
5. **T+1 day:** Post-mortem on any failures; root cause added to ADRs if architectural.

---

## 15. Testing Milestones

Testing is not a phase; it is continuous. But we define explicit testing milestones to ensure the team does not defer all testing to P5.

| TM # | Week | Milestone | Coverage / quality bar | Owner |
|---|---|---|---|---|
| TM-1 | W4 | Unit test infra in CI | pytest + Vitest configured; sample tests pass | D-Lead |
| TM-2 | W8 | Auth + course CRUD unit tests | ≥ 80% line coverage on these modules | A-Lead |
| TM-3 | W12 | OCR pipeline integration tests | 5 sample PDFs; assertions on output schema | B-Lead |
| TM-4 | W15 | RAG golden set v1 | 50 Q&A pairs; eval script runs in CI | B-Lead |
| TM-5 | W17 | E2E test (Playwright) for student flow | 1 E2E test green on staging | D-Lead |
| TM-6 | W20 | Coverage ≥ 40% on critical paths | Measured in CI | D-Lead |
| TM-7 | W24 | KG sanity tests | Schema validation; cycle detection | B-Lead |
| TM-8 | W28 | Quiz + mastery E2E test | Student takes quiz, mastery updates, assertion | D-Lead |
| TM-9 | W33 | Adaptation eval harness | Simulated trajectories; regression baseline | B-Lead |
| TM-10 | W36 | Bug bash #1 | Top-50 bugs triaged; P1s assigned | D-Lead |
| TM-11 | W38 | Coverage ≥ 60% on critical paths | Measured in CI; gate for Feature Freeze | D-Lead |
| TM-12 | W39 | Load test | 50 concurrent users; P95 < 2s | D-Lead |
| TM-13 | W40 | Security review | OWASP top 10; SAST clean; no high vulns | D-Lead |
| TM-14 | W41 | Bug bash #2 | ≤ 3 P1s open | D-Lead |
| TM-15 | W42 | Smoke tests on prod-like env | All critical paths green | D-Lead |

### 15.1 Test pyramid

```
                  /\
                 /  \        E2E (Playwright) — ~10 tests, slow, fragile
                /----\
               /      \      Integration (API ↔ DB ↔ jobs) — ~50 tests
              /--------\
             /          \    Unit (pytest + Vitest) — ~500+ tests
            /____________\
```

- **Unit tests** must run in < 60s; gate every PR.
- **Integration tests** must run in < 5 min; gate every PR to `main`.
- **E2E tests** run nightly on staging and on every release tag.

### 15.2 Test data strategy

- **Synthetic data** for unit tests (deterministic, fast).
- **Anonymized real data** for integration tests (10 sample PDFscurated by Pod B in W3).
- **Golden Q&A set** for RAG eval (50 questions with expected answers + acceptable sources).
- **Simulated student trajectories** for adaptation eval (10 personas × 20 quizzes each).

---

## 16. Documentation Milestones

Documentation is treated as a **first-class deliverable** using a **docs-first workflow**: API contracts and design docs are written *before* implementation, then updated as code lands.

| DM # | Week | Milestone | Artifact | Owner |
|---|---|---|---|---|
| DM-1 | W2 | MVP definition | `docs/mvp.md` (§5) | TPM |
| DM-2 | W4 | First 5 ADRs | `docs/adr/001-005` | TPM |
| DM-3 | W4 | Team norms + contributing guide | `CONTRIBUTING.md`, `README.md` | TPM |
| DM-4 | W8 | API reference v1 (auto-generated) | OpenAPI spec published | A-Lead |
| DM-5 | W8 | Docusaurus site live | Public docs URL | C-Lead |
| DM-6 | W11 | OCR + chunking design docs | `docs/ocr.md`, `docs/chunking.md` | B-Lead |
| DM-7 | W15 | RAG design doc + eval methodology | `docs/rag.md` | B-Lead |
| DM-8 | W19 | ADRs 1–15 complete | All architecture decisions recorded | TPM |
| DM-9 | W20 | Architecture diagram v1 | Single-page system diagram | TPM |
| DM-10 | W23 | KG design doc | `docs/kg.md` | B-Lead |
| DM-11 | W27 | Cognitive model design doc | `docs/student-model.md` | B-Lead |
| DM-12 | W31 | Adaptive engine design doc | `docs/adaptive.md` | B-Lead |
| DM-13 | W36 | Instructor quickstart + student quickstart | User-facing docs | C-Lead |
| DM-14 | W39 | Runbooks: deploy, rollback, DR, on-call | `docs/runbooks/` | D-Lead |
| DM-15 | W41 | Final architecture diagram + ADR index | Updated to reflect actual code | TPM |
| DM-16 | W42 | README polish + demo recording | `README.md` final + 5-min demo video | TPM + C-Lead |

### 16.1 Docs-first workflow

For every new component:

1. **Before code:** Open a PR with a design doc (1–3 pages) describing the component, its interfaces, and its failure modes. Get review from at least 1 other pod lead.
2. **During code:** Update the doc as the implementation reveals constraints.
3. **After code:** The doc lives next to the code; CI checks that every module has a corresponding `README.md` or design doc.

### 16.2 ADR template

Every ADR follows:

```markdown
# ADR-NNN: Title

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-MMM
**Date:** YYYY-MM-DD
**Authors:** name(s)

## Context
(Why is this decision needed? What constraints?)

## Decision
(What did we decide?)

## Alternatives considered
(What else did we consider? Why rejected?)

## Consequences
(Positive, negative, neutral)

## Open questions
(Things to revisit later)
```

---

## 17. Demo Cadence (Weekly Demos)

**Weekly demos are non-negotiable from W3 onward.** They are the single most important risk-reduction mechanism in this plan.

### 17.1 Demo rules

- **When:** Every Friday, 14:00–15:00 (timezone: team's primary TZ).
- **Who:** Whole team attends. Advisor invited but not required.
- **What:** 1–2 demos of work shipped that week, on staging (not localhost).
- **How long:** 30 min demo + 30 min discussion.
- **Format:** Live. If live fails, fall back to a screen recording made that morning.
- **No-demo penalty:** If a pod has nothing demoable for 2 consecutive weeks, the TPM escalates to the pod lead and the risk register.

### 17.2 Demo calendar (high-level)

| Week | Demo theme | Must show |
|---|---|---|
| W3 | Hello world | Deployed URL responds |
| W4 | v0.1 | Login page on prod |
| W6 | Auth + course shell | Register, log in, see empty course list |
| W8 | v0.2 — Foundations | Create course, upload PDF |
| W10 | OCR works | Uploaded PDF has extracted text |
| W12 | v0.3 — Ingestion | Chunks visible in UI |
| W14 | Vector search | Similarity search returns chunks |
| W16 | v0.4 — Retrieval | RAG answer with citations |
| W18 | Multi-doc RAG | Ask across course material |
| W20 | **v0.5 — MVP** | Full student flow; advisor invited |
| W24 | KG viz | Browse concept graph |
| W26 | v0.6 — Knowledge layer | KG + first quiz |
| W28 | Quiz + mastery | Take quiz, mastery updates |
| W30 | v0.7 — Cognition | Quiz + mastery + KG end-to-end |
| W32 | Adaptive engine | Recommendation appears |
| W34 | Recommendations | Top-3 next concepts |
| W36 | Dashboards | Instructor + admin views |
| W38 | **v0.9 — Feature complete** | Full feature demo; advisor invited |
| W40 | Hardening progress | Perf + security results |
| W42 | **v1.0-rc** | Full demo on staging; final rehearsal |
| W43 | Dry-run #1 | Full presentation rehearsal |
| W44 | **Graduation** | Final demo on prod |

### 17.3 Demo anti-patterns to avoid

- ❌ "It works on my machine" — must be on staging.
- ❌ Slides instead of live demo — slides are for context, demo is the proof.
- ❌ Demoing features that aren't merged to `main` — must be merged.
- ❌ Skipping demo because "nothing shipped" — show the *progress* (failed attempts, learnings).
- ❌ Demoing for > 30 min — attention drops; cut to the highlight.

---

## 18. Graduation Preparation Milestones

Graduation prep is not a 1-week activity at the end. It is a **12-week runway** starting in late March.

| GPM # | Week | Milestone | Owner |
|---|---|---|---|
| GPM-1 | W32 | Presentation outline drafted (story arc, key demos) | TPM |
| GPM-2 | W34 | Slide template chosen; first 5 slides drafted | TPM + C-Lead |
| GPM-3 | W36 | Demo script written (what to click, what to say) | TPM |
| GPM-4 | W38 | Full deck v1 reviewed by advisor | TPM |
| GPM-5 | W40 | Demo data curated (clean, predictable, reproducible) | B-Lead + C-Lead |
| GPM-6 | W41 | Fallback demo video recorded (in case live demo fails) | C-Lead |
| GPM-7 | W42 | Full dry-run #1 with advisor; collect feedback | TPM |
| GPM-8 | W43 | Slide deck v2; demo dry-run #2; timing tuned | TPM |
| GPM-9 | W43 | Production deployment stable; smoke tests passing | D-Lead |
| GPM-10 | W44 | Final dry-run #3 (dress rehearsal); submit artifacts | TPM |

### 18.1 Presentation structure (suggested)

A 30-minute graduation presentation typically follows this arc:

1. **(2 min) Problem** — why adaptive learning matters.
2. **(3 min) Solution** — what OpenLearn AI does (1 slide, 1 demo).
3. **(5 min) Architecture** — system diagram + key tech choices.
4. **(8 min) Live demo** — student flow + instructor flow + analytics.
5. **(5 min) AI depth** — RAG quality results; adaptation examples.
6. **(3 min) Engineering process** — CI/CD, testing, ADRs, what we'd do differently.
7. **(2 min) Future** — post-graduation path as a product.
8. **(2 min) Q&A** buffer.

### 18.2 Demo data strategy

- Use a **fixed, curated dataset** for the demo (not random user uploads).
- Pre-load 3 courses with 5–10 PDFs each, all OCR'd and embedded.
- Pre-create 5 student accounts with realistic mastery states.
- Have a script of 5 questions to ask the RAG that are known to produce good answers.
- **Never** demo with production user data.

---

## 19. Freeze Milestones (Architecture / Feature / Code)

Three hard freezes anchor the schedule. Each freeze is a **gate** — passing it requires explicit sign-off from all pod leads and the TPM. After a freeze, the scope of what can change is dramatically narrowed.

### 19.1 Architecture Freeze (W20, end of P2)

**What freezes:** The 10 interface contracts listed in §13.3, plus the technology stack, the data model, the deployment topology, and the pod ownership boundaries.

**What does NOT freeze:** Implementation details inside a module, UI design, ML model choices (as long as the I/O contract holds), test strategies.

**Sign-off criteria:**
- All 15 ADRs merged and reviewed.
- All 10 interface contracts documented with examples.
- v0.5 (MVP) shipped and demoed.
- Architecture diagram v1 published.
- All pod leads + TPM sign a single-page "Architecture Freeze" doc.

**Post-freeze change protocol:** Any change to a frozen interface requires:
1. A new ADR explaining why.
2. A migration plan (data, code, tests).
3. TPM approval.
4. At least 2 pod leads' review.

**Why this matters:** Without Architecture Freeze, P3 and P4 thrash endlessly as Pod B "improves" the chunk schema and breaks Pod A's ingestion service. The freeze is the only thing that prevents this.

### 19.2 Feature Freeze (W38, end of P4)

**What freezes:** No new features, no new APIs, no new UI screens. The product's feature set for graduation is locked.

**What does NOT freeze:** Bug fixes, performance improvements, documentation, test coverage, accessibility fixes, security fixes, demo polish.

**Sign-off criteria:**
- v0.9 demoed and accepted.
- All P1 bugs from bug bash #1 closed or waived.
- Coverage ≥ 60% on critical paths (TM-11).
- At least 3 people cross-trained on DevOps tasks (§11.1).
- Graduation presentation deck v1 reviewed by advisor (GPM-4).
- All pod leads + TPM sign a single-page "Feature Freeze" doc.

**Post-freeze change protocol:** Any new feature requires:
1. TPM + Tech Lead joint approval.
2. Explicit decision on what gets descoped to make room.
3. Update to the graduation demo script.

**Why this matters:** Without Feature Freeze, the team keeps adding "one more thing" until the day before graduation, and never spends time on hardening or demo polish. Both are required for a credible presentation.

### 19.3 Code Freeze (W42, end of P5)

**What freezes:** No new code merges to `main` except critical fixes. No new dependencies. No schema migrations. No infra changes.

**What does NOT freeze:** Critical bug fixes (P0/P1) with TPM approval. Demo data fixes. Documentation typos.

**Sign-off criteria:**
- v1.0-rc tagged and deployed to staging.
- Bug bash #2 complete; ≤ 3 P1s open (TM-14).
- Security review complete; no critical/high vulns (TM-13).
- Performance pass complete; P95 < 2s on RAG (TM-12).
- Runbooks complete (DM-14).
- Backup + DR drill complete.
- All pod leads + TPM sign a single-page "Code Freeze" doc.

**Post-freeze change protocol:** Any merge to `main` requires:
1. TPM + D-Lead (DevOps) joint approval.
2. Classification as P0 or P1 (graduation-blocking).
3. Smoke tests re-run before and after merge.

**Why this matters:** The week before graduation is for rehearsing the demo, not for debugging a regression introduced by a "quick fix." Code Freeze gives the team a stable target.

### 19.4 Freeze escalation ladder

If a freeze is at risk of being missed:

| Risk level | Trigger | Action |
|---|---|---|
| Green | On track, no concerns | Continue |
| Yellow | ≤ 1 week slip predicted | TPM reallocates resources; descopes 1 non-critical item |
| Orange | 1–2 week slip predicted | Descope protocol (§22.4) triggered; advisor informed |
| Red | > 2 week slip predicted | Emergency replan; consider Fallback Stack; advisor + committee informed |

---

## 20. Retrospectives & Technical Debt Management

### 20.1 Biweekly retrospectives

**Cadence:** Every 2 weeks, Friday, 60 minutes. The week opposite the monthly milestone review.

**Format:** 5-stage retro (Lean Coffee style):
1. (5 min) Set the stage — what's on your mind?
2. (10 min) Gather data — what went well, what didn't, what's confusing?
3. (15 min) Generate insights — *why* did things go well/badly?
4. (20 min) Decide what to do — pick top 3 action items with owners + due dates.
5. (10 min) Close — appreciations; one word check-out.

**Action item tracking:** Every action item is a GitHub issue tagged `retro-action`, with an owner and a due date ≤ 2 weeks out. Open retro items are reviewed at the start of the next retro.

**Anti-patterns to avoid:**
- ❌ "We'll do better next time" with no concrete action.
- ❌ Venting sessions without decisions.
- ❌ Same action item appearing in 3 consecutive retros (a sign it's not actually being worked on).

### 20.2 Retrospective calendar (high-level)

| Wk | Retro theme (suggested) |
|---|---|
| W2 | Pre-flight: did we lock the stack fast enough? |
| W4 | P0 close: is the skeleton actually deployed? |
| W6 | P1 mid: are auth and UI in sync? |
| W8 | P1 close: did v0.2 demo hold up? |
| W10 | P2 mid: is OCR actually working on real PDFs? |
| W12 | P2 mid: chunking — is the schema stable? |
| W14 | P2 mid: is the vector DB healthy? |
| W16 | P2 mid: RAG quality — is the golden set useful? |
| W18 | P2 close-prep: are we going to make v0.5? |
| W20 | **Big retro: did we hit MVP? What did we learn about ourselves?** |
| W22 | Holiday retro: light |
| W24 | P3 mid: is KG actually useful, or just pretty? |
| W26 | P3 mid: exam crunch — are we surviving? |
| W28 | P3 mid: quiz + mastery integration |
| W30 | **P3 close: did v0.7 hold up? Cognitive model sanity check.** |
| W32 | P4 mid: is adaptive engine actually adapting? |
| W34 | P4 mid: recommendations — useful or noise? |
| W36 | P4 mid: dashboards — real data or fake? |
| W38 | **P4 close: Feature Freeze — are we ready to stop adding?** |
| W40 | P5 mid: perf + security — surprises? |
| W42 | **P5 close: Code Freeze — final lessons.** |
| W44 | **Final retro: what would we tell next year's team?** |

### 20.3 Technical debt management

Technical debt is **explicitly tracked**, not hidden. Every tech debt item is a GitHub issue tagged `tech-debt` with:
- **Type:** Code debt / design debt / architecture debt / test debt / doc debt.
- **Interest rate:** High (will block future work) / Medium (slows future work) / Low (cosmetic).
- **Principal:** Estimated hours to pay off.
- **Owner:** Pod lead responsible.

**Tech debt budget:** Every sprint, each pod allocates **10% of capacity** to tech debt payoff. This is non-negotiable. If a pod has no tech debt items, they pick up items from another pod or improve tests.

**Tech debt milestones:**
- W12: First tech debt sweep (pay down debt accumulated in P0–P1).
- W20: Pre-Architecture-Freeze debt audit (pay down anything that would block P3).
- W30: Mid-project debt audit.
- W38: Feature Freeze debt audit — anything not paid down by now is documented as "accepted debt" with a payoff plan for post-graduation.
- W42: Final debt register published as `docs/tech-debt.md`.

**Acceptance criteria for "accepted debt":** Every accepted debt item has:
- A clear description of what's wrong.
- A trigger for when it must be paid off (e.g., "before adding multi-tenant support").
- An estimated cost of not paying it off.

### 20.4 The "tech debt wall"

A physical (or virtual — Miro/FigJam) wall where the team posts tech debt items as they accrue. Visible to everyone. The wall is reviewed at every monthly milestone review.

This makes tech debt **socially visible** — a powerful motivator. A wall with 30 sticky notes by W20 is a warning sign; a wall with 5 is healthy.

---

## 21. Risk Register (Full)

The risk register is the **single source of truth** for what can go wrong. It is reviewed at every monthly milestone review and updated biweekly. Every risk has an owner, a likelihood, an impact, a mitigation, and a trigger.

**Likelihood scale:** 1 (Very Low, <10%) / 2 (Low, 10–30%) / 3 (Medium, 30–60%) / 4 (High, 60–85%) / 5 (Very High, >85%)
**Impact scale:** 1 (Trivial) / 2 (Minor) / 3 (Moderate) / 4 (Major) / 5 (Severe — graduation at risk)
**Risk score = Likelihood × Impact.** Score ≥ 12 = red; 6–11 = yellow; ≤ 5 = green.

### 21.1 Technical risks

| ID | Risk | L | I | Score | Owner | Mitigation | Trigger |
|---|---|---|---|---|---|---|---|
| R-01 | OCR quality too low on real-world PDFs (scanned, rotated, mixed-language) | 4 | 4 | **16 🔴** | B-Lead | Spike in W5; PaddleOCR + Document AI fallback; golden PDF set; A/B test on 20 PDFs by W10 | < 90% success on 20-PDF set |
| R-02 | RAG quality unacceptable (hallucinations, wrong citations) | 4 | 4 | **16 🔴** | B-Lead | Hybrid retrieval + reranker; eval harness from W17; prompt iteration; guardrails | Faithfulness < 0.7 on golden set |
| R-03 | Adaptive engine algorithm fails to converge or behaves erratically | 3 | 4 | **12 🔴** | B-Lead | Start design in W31 (not later); simulated eval harness; simple policy first (rule-based), then ML | Simulated trajectories show no learning |
| R-04 | Knowledge Graph construction produces noisy/incorrect relations | 3 | 3 | 9 🟡 | B-Lead | LLM-assisted extraction with human-in-loop sampling; provenance tracking; KG sanity tests (TM-7) | > 30% relations flagged bad on sample |
| R-05 | Vector DB (Qdrant) ops too heavy for Pod D to maintain | 3 | 3 | 9 🟡 | D-Lead | Cross-train Pod B engineer (§11.1); fallback to pgvector; monitoring from W13 | Qdrant down > 1h unresolved |
| R-06 | LLM API cost overruns | 3 | 3 | 9 🟡 | D-Lead | LiteLLM proxy with cost tracking; per-user quota; cache common queries; switch to cheaper model for non-critical paths | Monthly cost > $300 |
| R-07 | LLM API provider changes terms / deprecates model | 3 | 4 | **12 🔴** | B-Lead | LiteLLM gateway abstracts provider; ≥ 2 providers configured; ADR for fallback model | Provider announces deprecation |
| R-08 | Embedding model dim mismatch after Architecture Freeze | 2 | 4 | 8 🟡 | B-Lead | Freeze model choice at W12; ADR; versioned embeddings with model_id field | — |
| R-09 | Database performance collapses under load | 3 | 3 | 9 🟡 | A-Lead | Indexes from day 1; load test at W39; connection pooling; read replicas if needed | P95 > 5s in load test |
| R-10 | Frontend bundle too large; first load > 5s | 3 | 2 | 6 🟡 | C-Lead | Code splitting; lazy loading; bundle analysis in CI; Next.js SSR | Lighthouse perf < 70 |
| R-11 | Neo4j ops too heavy; team can't maintain | 3 | 3 | 9 🟡 | D-Lead | Fallback: store KG as JSONB in Postgres; ADR documents both paths | Neo4j down > 2h |
| R-12 | Single-person Pod D = bus factor | 4 | 4 | **16 🔴** | TPM | Cross-training plan (§11.1); rotate Pod A/B/C engineers through DevOps duty; documented runbooks | Pod D lead unavailable > 1 week |
| R-13 | Cognitive model produces meaningless mastery scores (cold start, sparse data) | 3 | 3 | 9 🟡 | B-Lead | Simple mastery v1 (rolling average); add IRT in v0.8 only if data supports; confidence intervals | Mastery values don't correlate with quiz performance |
| R-14 | Multi-document RAG retrieval returns cross-course noise | 3 | 2 | 6 🟡 | B-Lead | Course-level metadata filter; reranker; A/B test | — |
| R-15 | Production deployment fails on graduation day | 2 | 5 | **10 🟡** | D-Lead | Deploy W43 (not W44); smoke tests; fallback to staging URL; recorded demo video | Prod down at T-1h |

### 21.2 Schedule risks

| ID | Risk | L | I | Score | Owner | Mitigation | Trigger |
|---|---|---|---|---|---|---|---|
| R-16 | Exam crunch (late Jan) collapses capacity more than expected | 4 | 4 | **16 🔴** | TPM | Plan P3 with 50% capacity buffer; defer KG depth to Feb; explicit "exam mode" comms | Pod B throughput < 30% in W25–27 |
| R-17 | Exam crunch 2 (late Apr–early May) eats into hardening | 3 | 4 | **12 🔴** | TPM | Front-load hardening tasks into W37; treat W39–40 as bonus | P5 slips > 1 week |
| R-18 | v0.5 (MVP) slips past W20 | 3 | 5 | **15 🔴** | TPM | Architecture Freeze can be signed even if v0.5 is at "demoable but rough"; descope protocol §22.4 | v0.4 slips past W16 |
| R-19 | Architecture Freeze slips past W20 | 2 | 5 | **10 🟡** | TPM | Force a "soft freeze" in W19; full freeze in W20 even if some ADRs are still "Proposed" | ADRs 1–15 not all merged by W18 |
| R-20 | Feature Freeze slips past W38 | 3 | 4 | **12 🔴** | TPM | Hard rule: no new features after W38 even if v0.9 is incomplete; demos show what's done | v0.8 not done by W34 |

### 21.3 Team risks

| ID | Risk | L | I | Score | Owner | Mitigation | Trigger |
|---|---|---|---|---|---|---|---|
| R-21 | A key team member drops out or is unavailable for > 4 weeks | 3 | 4 | **12 🔴** | TPM | Cross-training (§11.1); pod redundancy; documented runbooks; advisor escalation | Any member gone > 2 weeks |
| R-22 | Pod B (AI/ML) overloaded — too much critical-path work for 3 people | 4 | 4 | **16 🔴** | TPM | Move 1 Pod A engineer into Pod B for P2; defer non-critical AI work; pair-program | Pod B slips 2 sprints in a row |
| R-23 | Skill gap: junior members can't contribute to AI work | 3 | 3 | 9 🟡 | B-Lead | Pair-programming; spike-first learning; assign junior to data curation / eval harness first | — |
| R-24 | Burnout during P5 final push | 3 | 3 | 9 🟡 | TPM | Cap hours at 30/wk in P5; mandatory 1 day off per week; rotate on-call | Member reports burnout or withdraws |
| R-25 | Team conflict / communication breakdown | 2 | 4 | 8 🟡 | TPM | Biweekly retros; explicit norms doc; TPM mediation; advisor escalation | Retro action items not progressing |
| R-26 | Advisor expectations misaligned with delivery reality | 3 | 3 | 9 🟡 | TPM | Monthly advisor demo; written status reports; explicit descope comms | Advisor surprised at monthly review |

### 21.4 External risks

| ID | Risk | L | I | Score | Owner | Mitigation | Trigger |
|---|---|---|---|---|---|---|---|
| R-27 | Cloud provider outage / billing issue | 2 | 4 | 8 🟡 | D-Lead | Multi-AZ; backups; budget alerts; Hetzner fallback | Provider outage > 4h |
| R-28 | LLM API rate limits during load test or demo | 3 | 3 | 9 🟡 | B-Lead | Quota increase request; caching; multiple API keys; fallback model | Rate limit hit in load test |
| R-29 | Third-party dependency (LangChain, LiteLLM, etc.) breaking change | 3 | 3 | 9 🟡 | B-Lead | Pin versions; integration tests; ADR for swap-out path | Breaking change in major version |
| R-30 | Graduation committee changes requirements mid-project | 2 | 4 | 8 🟡 | TPM | Monthly advisor check-ins; written scope doc signed at start | Committee announces new requirement |
| R-31 | Data privacy / regulatory issue (student data) | 2 | 4 | 8 🟡 | D-Lead | Data minimization; encryption at rest; PII handling ADR; privacy doc | — |
| R-32 | Open-source license conflict (e.g., AGPL component in commercial path) | 2 | 3 | 6 🟡 | D-Lead | License scan in CI; ADR for licensing strategy | Scan flags a component |

### 21.5 Risk heatmap

```
                    Impact
            1     2     3     4     5
         ┌─────┬─────┬─────┬─────┬─────┐
    5    │     │     │     │ R15 │ R18 │
         ├─────┼─────┼─────┼─────┼─────┤
    4    │     │ R10 │ R08 │ R01 │ R16 │
    L    │     │     │ R21 │ R02 │ R20 │
    i    │     │     │     │ R03 │ R22 │
    k    │     │     │     │ R07 │     │
    e   ├─────┼─────┼─────┼─────┼─────┤
    l   │     │ R32 │ R04 │ R05 │ R17 │
    i   │     │     │ R09 │ R06 │ R19 │
    h   │     │     │ R11 │ R12 │     │
    o   │     │     │ R13 │ R26 │     │
    o   │     │     │ R23 │ R27 │     │
    d   │     │     │ R28 │ R30 │     │
         ├─────┼─────┼─────┼─────┼─────┤
    1    │     │     │ R25 │ R29 │ R31 │
         └─────┴─────┴─────┴─────┴─────┘
```

**Top-5 red risks (score ≥ 12):** R-01 (OCR quality), R-02 (RAG quality), R-03 (adaptive engine), R-12 (Pod D bus factor), R-16 (exam crunch), R-18 (MVP slip), R-20 (Feature Freeze slip), R-21 (member dropout), R-22 (Pod B overload).

**These 9 risks collectively determine whether the project ships on time.** Every one of them has a mitigation that starts in P0 or P1 — *before* the risk materializes.

---

## 22. Buffer Time Strategy

### 22.1 Buffer philosophy

Buffer is **not** "extra time at the end." Buffer at the end gets eaten by procrastination and scope creep. Instead, buffer is **distributed** across the schedule at points of highest schedule risk.

### 22.2 Buffer allocation

| Buffer type | Amount | Where it lives | How it's used |
|---|---|---|---|
| **Per-sprint slack** | 10% of every sprint | Inside each week | Absorbs underestimation |
| **Per-phase buffer** | 1 week per phase | End of each phase | Absorbs phase-level slips |
| **Critical-path buffer** | 2 weeks | Spread across P2 and P4 | Absorbs slips on the critical chain |
| **Exam-crunch buffer** | 2 weeks of explicit "do nothing" | W25–W27 (Jan exam) and W39 (Apr exam) | Lets team study without guilt |
| **Final buffer** | 1 week | W43 (before graduation) | Absorbs last-minute surprises |
| **Total buffer** | ~6.5 weeks (≈ 15% of 44 weeks) | Distributed | — |

### 22.3 Buffer consumption rules

1. **Buffer is not feature time.** A pod cannot consume buffer to add a feature. Buffer is for absorbing slips, not for expanding scope.
2. **Buffer consumption is tracked.** The TPM maintains a "buffer burn-down" chart, updated weekly. If buffer burn rate exceeds plan, the descope protocol triggers.
3. **Critical-path buffer is reserved.** Only critical-path slips can consume the 2-week critical-path buffer. Non-critical work that slips must be descoped, not buffered.
4. **Exam-crunch buffer is non-negotiable.** The team is *expected* to do minimal work during exam weeks. This is not "slacking" — it is planned.

### 22.4 Descope protocol

When buffer consumption exceeds the threshold, the descope protocol triggers. It is **automatic** — the TPM does not need permission.

**Trigger thresholds:**
- Per-phase buffer consumed > 50% with > 50% of phase remaining → Yellow.
- Per-phase buffer consumed > 75% with > 25% of phase remaining → Orange.
- Per-phase buffer consumed 100% → Red → descope immediately.

**Descope decision tree:**

```
Is the slipping work on the critical path?
├── Yes → Can we reduce its scope without breaking the chain?
│        ├── Yes → Reduce scope (e.g., KG stores 100 concepts instead of 1,000)
│        └── No  → Can we parallelize more aggressively?
│                 ├── Yes → Reallocate people; trigger cross-pod borrowing
│                 └── No  → SWITCH TO FALLBACK STACK (if in P2) OR cut a downstream feature
└── No  → Defer the slipping work to the next phase, or cut it entirely
```

**Descope candidates (in priority order — easiest to cut first):**

1. Admin dashboard (replace with raw DB queries for the demo)
2. Notification system (skip; demo without)
3. Recommendation engine v2 features (keep v1 only)
4. Analytics dashboard advanced charts (keep basic ones)
5. KG visualization richness (keep simple list view)
6. Multi-document RAG (single-doc RAG still demonstrates the core value)
7. Accessibility polish (meet minimum, not WCAG AA)
8. Mobile responsiveness (desktop-only demo)
9. Performance optimization beyond P95 < 2s (accept P95 < 5s)
10. Multi-language support (English only)

**Hard never-to-cut items (graduation-critical):**
- Auth + user management
- Course management + file upload
- OCR + RAG (the MVP)
- At least a basic quiz + mastery loop
- At least one adaptive behavior (even if simple)
- Production deployment
- Documentation (ADRs + README + runbook)
- The graduation presentation itself

---

## 23. Success Criteria

### 23.1 Project-level success criteria (graduation)

The project is a **success** if **all** of the following are true on graduation day:

1. ✅ A live, deployed v1.0 product accessible at a public URL.
2. ✅ The graduation presentation is delivered, with a live demo that does not crash.
3. ✅ The MVP loop (upload PDF → chat with cited answers) works end-to-end on the demo data.
4. ✅ At least one adaptive behavior is demonstrated (e.g., quiz difficulty adjusts based on mastery).
5. ✅ All graduation artifacts (code, docs, presentation, demo video) are submitted.
6. ✅ The team has a defensible answer to "what would you do differently?" (informed by retros).

### 23.2 Engineering success criteria (process)

The project is an **engineering success** if **all** of the following are true:

1. ✅ CI/CD runs on every PR; merges to `main` are gated.
2. ✅ Test coverage ≥ 60% on critical paths.
3. ✅ All 3 freezes (Architecture, Feature, Code) were signed on or before their target dates.
4. ✅ No critical/high security vulnerabilities open at Code Freeze.
5. ✅ P95 latency < 2s on RAG under 50 concurrent users.
6. ✅ ≥ 15 ADRs in the repo, each reviewed by ≥ 2 pod leads.
7. ✅ Runbooks exist for: deploy, rollback, DR, on-call.
8. ✅ At least 3 people can do basic DevOps/QA tasks (cross-training succeeded).
9. ✅ Tech debt register is published; accepted debt has clear payoff triggers.
10. ✅ Weekly demos ran from W3 to W44 without 2 consecutive weeks of "no demo" from any pod.

### 23.3 Team success criteria (human)

The project is a **team success** if **all** of the following are true:

1. ✅ No team member burned out or withdrew from the project.
2. ✅ Every team member can explain the architecture in a 5-min pitch.
3. ✅ Every team member shipped at least 1 feature that they own end-to-end.
4. ✅ Retros produced ≥ 20 action items, of which ≥ 80% were closed.
5. ✅ The team would willingly work together again on a follow-up project.

### 23.4 Product success criteria (post-graduation)

If the team continues as a startup, the project is a **product success** if:

1. ✅ The product can onboard a real instructor within 1 hour.
2. ✅ The product survives 1 week of real usage without a P0 incident.
3. ✅ The codebase is understandable by a new engineer within 2 days.
4. ✅ The stack can scale to 100 users without re-architecture.
5. ✅ The team has a clear v1.1 / v2.0 roadmap informed by real usage.

---

## 24. Phase Exit Criteria (Consolidated)

| Phase | Exit criterion summary | Detailed in |
|---|---|---|
| **P0** | v0.1 deployed; CI green; 5 ADRs; MVP doc signed | §10.1 |
| **P1** | v0.2 deployed; auth + course + upload work; E2E test | §10.2 |
| **P2** | **v0.5 MVP + Architecture Freeze signed** | §5.4, §10.3, §19.1 |
| **P3** | v0.7: KG + quiz + mastery end-to-end | §10.4 |
| **P4** | **v0.9 + Feature Freeze signed** | §10.5, §19.2 |
| **P5** | **v1.0-rc + Code Freeze signed** | §10.6, §19.3 |
| **P6** | **v1.0 + graduation presentation delivered** | §10.7, §23.1 |

---

## 25. Suggested Sprint Length

**Sprint length: 1 week** (Monday kickoff → Friday demo).

### 25.1 Why 1 week (not 2)

- **Feedback speed:** AI work has high uncertainty; 1-week sprints surface problems fast.
- **Demo discipline:** Weekly demos force integration every week, not every 2 weeks.
- **Accountability:** Harder to hide a stalled task for 2 weeks.
- **Capacity reality:** During semester, a 2-week sprint often means 1 week of work spread over 2 calendar weeks anyway.

### 25.2 Why not shorter

- **Overhead:** Daily standups + 1-week sprints = enough ceremony. Shorter sprints add meeting overhead without proportional value.
- **Context switching:** A 3-day sprint is too short for meaningful AI work (a single RAG iteration can take 2 days).

### 25.3 Sprint cadence

| Day | Activity | Duration |
|---|---|---|
| Monday | Sprint kickoff (pod-level) | 30 min |
| Monday–Thursday | Heads-down work; pair-programming | — |
| Tuesday | Mid-week sync (cross-pod, blockers only) | 30 min |
| Thursday | PR review push; merge to `main` | — |
| Friday 14:00 | Demo | 30 min |
| Friday 14:30 | Sprint close + retro (biweekly) | 30–60 min |
| Friday 15:30 | Sprint planning for next week | 30 min |

### 25.4 Sprint ceremonies (summary)

- **Daily async standup** in Slack/Discord: "Yesterday / Today / Blockers" — by 10am.
- **Weekly demo** (Friday).
- **Biweekly retro** (Friday, alternate weeks).
- **Monthly milestone review** (last Friday of month).
- **Quarterly architecture review** (only at Architecture Freeze and Code Freeze).

---

## 26. Self-Critique of v1 Roadmap

This section is written *as if* a different engineering manager reviewed the v1 plan. The goal is to identify weak assumptions, hidden risks, and structural flaws **before** the team executes against v1. Each critique references a specific section of v1 and proposes a concrete fix that v2 will incorporate.

### 26.1 Critique 1 — The capacity model is optimistic and linear

**What v1 says (§2.2):** Effective capacity ≈ 2,500 person-hours over 44 weeks, distributed across 7 calendar phases with smooth tapering during semesters.

**What's wrong:** Real student teams do not behave this way. Capacity is not smooth; it is **spiky and correlated** — when one person is in exams, often several are. When the team has a midterm crunch, *everyone* is crunched simultaneously, not 30% of the team. The 70% productivity multiplier is a guess, not measured. And the model assumes 9 active members from day one, but real teams lose 1–2 members in the first 2 weeks (dropped the course, changed project, etc.).

**Impact:** If real capacity comes in at 1,800 hours instead of 2,500 (28% lower), the critical path collapses. v0.5 slips by 2–3 weeks, Architecture Freeze slips, and the entire spring semester plan is rebuilt on the fly.

**Fix in v2:** Use a **pessimistic capacity model** (1,800 hours). Re-plan the critical path against this lower budget. Add a Week-2 "team health check" that verifies actual active headcount. If < 8 active members by W2, trigger an immediate descope of KG or adaptive engine.

---

### 26.2 Critique 2 — The MVP definition is too AI-heavy for the time budget

**What v1 says (§5.1):** The MVP is "student uploads PDF → platform ingests → student chats with cited answers." This is shipped by W20 (December 2026).

**What's wrong:** This MVP requires OCR + chunking + embeddings + vector DB + RAG + chat UI + auth + course management + file upload — that's the entire AI pipeline plus the entire backend. The plan claims this fits in ~1,200 person-hours of P0+P1+P2 work. That's optimistic for a team that has never built a RAG system before. The first time a team builds RAG, they spend 30% of their time on prompt iteration, eval harness setup, and OCR edge cases — none of which the v1 plan budgets adequately.

**Impact:** v0.5 will slip. The plan's response is "trigger descope protocol," but the descope protocol cuts *non-critical* features. The MVP itself is the critical path — there's nothing left to cut. The team will either ship a broken v0.5 (hurting morale and advisor confidence) or skip Architecture Freeze (creating downstream chaos).

**Fix in v2:** Define a **v0.4 "thin MVP"** that is genuinely thin: a single pre-uploaded PDF, no auth, no course management, just "ask a question, get an answer." This ships by W14 instead of W20. The full v0.5 (with auth, courses, uploads) then has 6 more weeks of buffer. Architecture Freeze moves to W18, not W20.

---

### 26.3 Critique 3 — The critical path has zero slack in P3 (exam crunch)

**What v1 says (§12.2):** Architecture Freeze → v0.7 has "0 weeks allowable slip" because of exam crunch.

**What's wrong:** A 10-week phase with zero slack, scheduled across the December holiday AND the January exam crunch, on the *most uncertain part of the AI stack* (KG construction, cognitive modeling, quiz generation — all research-y)? This is not a plan; it's a hope. The plan acknowledges this in §22 by holding buffer, but the buffer is *off* the critical path, which means it cannot actually be used to absorb critical-path slips without cascading downstream.

**Impact:** When (not if) P3 slips, the team will eat into P4. Adaptive engine starts late, gets squeezed against Feature Freeze, ships half-baked. The graduation demo shows an "adaptive engine" that is really a rule-based if-statement. Advisor is unimpressed.

**Fix in v2:** Re-architect the critical path so that **P3 has explicit slack**. Specifically: move quiz generation to *parallel* with KG (not after). Move cognitive model design to *before* quiz generation (design can happen during low-capacity weeks; implementation needs capacity). Accept that v0.7 ships with a *simple* cognitive model (rolling average), not IRT. Defer IRT to v0.8.

---

### 26.4 Critique 4 — Pod B is structurally overloaded

**What v1 says (§11):** Pod B (3 people) owns OCR, embeddings, vector DB, RAG, KG, cognitive model, adaptive engine, recommendation engine, eval harness. That's ~9 substantial components over 44 weeks.

**What's wrong:** Pod B owns *every* critical-path item. Three people cannot carry the entire critical path of a 9-person project. Pod A (3 people) owns comparatively little — auth, CRUD, some APIs. The workloads are imbalanced.

**Impact:** Pod B burns out by W20. Pod A finishes their work early in P2 and has nothing to do. The plan's mitigation (§11.1 cross-training, §21 R-22 "move 1 Pod A engineer to Pod B for P2") is mentioned but not structural — it's a one-off patch.

**Fix in v2:** Restructure pods. **Move vector DB ops and search API from Pod B to Pod A** (these are backend-adjacent). **Move eval harness from Pod B to Pod D** (it's testing-adjacent). Pod B now owns: OCR, chunking, embeddings (model choice), RAG (prompt + retrieval logic), KG (concept extraction), cognitive model, adaptive engine, recommendation engine. That's still a lot but more manageable. Pod A picks up ~30% more work. Pod D picks up the eval harness (which makes them more than just an ops role).

---

### 26.5 Critique 5 — Pod D (1 person) is an unacceptable bus factor

**What v1 says (§3, §11):** Pod D has 1 person owning CI/CD, environments, monitoring, security, releases, runbooks. Mitigation is cross-training (§11.1).

**What's wrong:** A single-person pod for a 9-person team's entire DevOps/QA function is structurally unsound. Cross-training is mentioned but the plan never makes it a hard gate until W38 (Feature Freeze). If the Pod D lead is sick for 2 weeks in W14 (right when Qdrant needs to deploy), the entire AI pipeline stalls. The cross-training in W4–W8 is "20% shadowing" — that's not enough to actually run prod infra.

**Impact:** Either Pod D lead burns out by P3, or they become a single point of failure that takes down the project when they're unavailable.

**Fix in v2:** **Promote Pod D to 2 people from day one.** Take 1 person from Pod A (the weakest fit for backend) and move them to Pod D full-time. Pod A becomes 2 people + 1 Pod-D-embedded engineer for backend ops. Pod D becomes 2 people: 1 lead (strategy + security + releases), 1 engineer (CI/CD + monitoring + runbooks + eval harness). This also fixes Critique 4 by reducing Pod A's headcount (which was overallocated anyway).

---

### 26.6 Critique 6 — The Fallback Stack is presented as an escape hatch but never rehearsed

**What v1 says (§4.2, §22.4):** If the team is behind by January 2027, switch to the Fallback Stack (Vercel + Railway + managed services).

**What's wrong:** Switching stacks mid-project is enormously expensive. The Fallback Stack uses Next.js API Routes instead of FastAPI — that's a *complete rewrite of the backend* in a different language ecosystem. The plan treats this as a 1-week activity; in reality it's a 3–4 week activity that would itself trigger a slip. And the team has never touched the Fallback Stack, so they'd be learning it under pressure.

**Impact:** When the team is behind and "switches to Fallback," they fall further behind. The escape hatch becomes a trap.

**Fix in v2:** Reframe the Fallback Stack as a **scoped fallback**, not a full stack swap. Define specific *component-level* fallbacks that are cheap to invoke: (a) Qdrant → pgvector (1 day, no code change outside the vector DB driver); (b) Neo4j → JSONB in Postgres (3 days, schema change but no API change); (c) self-hosted embeddings → OpenAI API (1 day); (d) Celery → Inngest (1 week, only if needed). These are *reversible component swaps*, not stack rewrites. Drop the "full Fallback Stack" concept entirely — it's a false comfort.

---

### 26.7 Critique 7 — Documentation is treated as parallel but doesn't have a real owner

**What v1 says (§16):** Documentation is "first-class" with a docs-first workflow. The DM table assigns owners per milestone but most are "TPM" or "C-Lead" as a side duty.

**What's wrong:** Documentation that is everyone's secondary responsibility becomes no one's primary responsibility. The docs-first workflow (§16.1) is a nice idea but it has no enforcement — no CI check, no PR gate. In practice, the team will write the doc *after* the code (or skip it) because the code is what gets demoed on Friday.

**Impact:** By W41, the docs are 40% complete, not 80%. Runbooks don't exist. ADRs are stubs. The graduation presentation has nothing to reference.

**Fix in v2:** Assign a **dedicated docs owner** (rotating role, 4-week rotations, like TPM). Add a **CI gate**: every PR that adds a new endpoint, schema, or component must also add or update a doc file, or the PR is blocked. Add a **weekly docs review** to the Friday demo slot (5 min): "what docs did you write this week?"

---

### 26.8 Critique 8 — The Architecture Freeze is at W20 but the hardest architectural decisions are in P3/P4

**What v1 says (§19.1):** Architecture Freeze at W20 freezes 10 interface contracts including the KG schema and the adaptive engine I/O.

**What's wrong:** The KG schema and adaptive engine I/O are frozen *before the team has built them*. The team will be guessing at the right schema in W19, freezing a guess, and then either living with a bad schema or violating the freeze. This is the worst of both worlds: the freeze doesn't reflect reality, and it slows down the work it was supposed to enable.

**Impact:** Either the freeze is meaningless (everyone violates it because the schema was wrong), or the team wastes weeks building ADRs and migration plans to "correctly" change a frozen interface that should never have been frozen yet.

**Fix in v2:** **Split Architecture Freeze into two tiers.** Tier 1 (W20): freeze only the *foundational* interfaces — auth tokens, OCR output, chunk schema, embedding I/O, vector DB query, RAG request/response. These are stable because they're built by W20. Tier 2 (W30, end of P3): freeze the *cognitive* interfaces — KG schema, quiz schema, mastery schema, adaptive engine I/O. These get frozen *after* the team has actually built v0.6 and v0.7 and knows what the right schema is. This is honest about what's actually stable when.

---

### 26.9 Critique 9 — The graduation prep starts too late

**What v1 says (§18):** Graduation prep starts at W32 (mid-March) with a 12-week runway.

**What's wrong:** 12 weeks sounds like a lot, but W32–W38 is the busiest phase of the project (adaptive engine + dashboards). The presentation outline is drafted in W32 — but by then, the team doesn't yet know what will actually work by W44. They'll draft an outline, then have to rewrite it twice as reality diverges from plan.

**Impact:** The presentation is rushed in the last 2 weeks. The demo data is whatever happened to be in staging, not curated. The advisor sees a half-polished deck.

**Fix in v2:** Start graduation prep at **W20** (right after Architecture Freeze). Not "start writing slides" — start *tracking* what the demo will need to show. By W24, the team has a "demo backlog" — a list of moments that would make good demo beats. By W30, the demo script exists as a skeleton. By W36, it's filled in. By W42, it's rehearsed. This is a 22-week runway, not 12.

---

### 26.10 Critique 10 — No explicit "what if a major component fails" contingency

**What v1 says:** Risks are tracked (§21) with mitigations, but the mitigations are mostly "start early" or "have a fallback." There's no explicit "if RAG doesn't work by W18, here's what we do."

**What's wrong:** "Start early" is not a mitigation; it's a restatement of the plan. Real mitigation is a *decision tree* with concrete branches. The plan needs a "Plan B" for each top-5 red risk.

**Impact:** When R-01 (OCR quality) materializes in W10, the team has no playbook. They improvise, lose 2 weeks, and then make a panicked decision.

**Fix in v2:** Add a **contingency playbook** for each top-5 red risk (R-01, R-02, R-03, R-12, R-16, R-22). Each playbook specifies: trigger metric, decision owner, decision deadline, and 2–3 concrete branches with their cost.

---

### 26.11 Critique 11 — No explicit "research vs. engineering" split

**What v1 says:** Pod B does both engineering (OCR pipeline, embeddings) and research (cognitive model, adaptive engine).

**What's wrong:** Research work has fundamentally different dynamics than engineering work. It's exploratory, failure-prone, and hard to estimate. Mixing it with engineering work means the engineering work gets blocked when the research fails. A team that has 3 weeks to "build the adaptive engine" will spend 2 weeks researching and 1 week coding — and ship something half-working.

**Impact:** The adaptive engine ships as a hacky if-else, not because the team is bad, but because the research and engineering were not separated.

**Fix in v2:** Add a **research spike phase** before each research-y component. Specifically: 2-week spike on cognitive model *before* W27 (so it's done in W25, during low-capacity exam crunch — research is more flexible than engineering). 2-week spike on adaptive engine *before* W31. Spikes produce a working prototype + an ADR; the actual productionization happens in the planned weeks.

---

### 26.12 Critique 12 — The plan assumes a stable 9-person team for 44 weeks

**What v1 says (§2.3):** "We do not assume the team will stay at 9 members" — but then the entire capacity model assumes 9 members.

**What's wrong:** Student teams churn. People get internships, get sick, drop courses, have family emergencies. The plan acknowledges this in §2.4 but doesn't *build it into the schedule*. A real plan needs to assume that at any given time, 1 of the 9 members is unavailable for 2+ weeks.

**Impact:** When (not if) a key member is unavailable, the plan has no slack to absorb it.

**Fix in v2:** Add a **"minus one" rule**: every phase must be plannable with 8 active members, not 9. The 9th member is *buffer capacity* — they pick up whatever is most behind. This is essentially a floating "firefighter" role that rotates.

---

### 26.13 Critique 13 — The demo data strategy is under-specified

**What v1 says (§18.2):** "Use a fixed, curated dataset for the demo (not random user uploads)."

**What's wrong:** This is mentioned as a strategy but not as a deliverable. There's no milestone for "demo data curated." The team will reach W42 and realize they have no clean data to demo with — they'll grab whatever's in staging, the demo will be embarrassing, and they'll spend the last week scrambling.

**Impact:** A graduation demo with bad data is a failed demo, even if the tech works.

**Fix in v2:** Make demo data a **first-class deliverable** with its own milestone track. Specifically: by W30, a "demo dataset" exists (3 courses, 5–10 PDFs each, pre-OCR'd, pre-embedded). By W36, 5 student accounts exist with realistic mastery states. By W40, a demo script with 5 known-good RAG questions exists. This is demoed at the W42 dry-run.

---

### 26.14 Critique 14 — No explicit "what we will NOT build" list

**What v1 says (§5.3):** "What is explicitly NOT in MVP" — but this only covers v0.5.

**What's wrong:** The plan never says "we will NOT build X for graduation, even if we have time." Without this, scope creep is inevitable. Every retro will surface "wouldn't it be cool if..." ideas, and some will get worked on.

**Impact:** Time gets frittered away on nice-to-haves. The hardening phase (P5) gets squeezed.

**Fix in v2:** Add an explicit **"Out of Scope for v1.0"** list, signed by all pod leads at project kickoff. Anything on this list requires a formal scope-change ADR to add.

---

### 26.15 Summary of v1 weaknesses

| # | Weakness | Severity | Fixed in v2 § |
|---|---|---|---|
| 1 | Capacity model optimistic | High | §28 |
| 2 | MVP too AI-heavy for time budget | High | §29 |
| 3 | P3 has zero slack on critical path | High | §30 |
| 4 | Pod B structurally overloaded | High | §28 |
| 5 | Pod D single-person bus factor | Critical | §28 |
| 6 | Fallback Stack is a false comfort | Medium | §29 |
| 7 | Documentation has no real owner | Medium | §31 |
| 8 | Architecture Freeze freezes things not yet built | High | §30 |
| 9 | Graduation prep starts too late | Medium | §32 |
| 10 | No Plan B for top red risks | High | §31 |
| 11 | No research-vs-engineering split | Medium | §30 |
| 12 | Plan assumes stable 9-person team | High | §28 |
| 13 | Demo data strategy under-specified | Medium | §32 |
| 14 | No "out of scope" list | Medium | §29 |

---

# PART B — v2 ROADMAP (FINAL, IMPROVED)

## 27. v2 Executive Summary — What Changed and Why

v2 is the **final, executable plan**. It incorporates all 14 fixes from §26 and is presented in full below. Sections of v1 that did not change (sprint ceremonies, integration protocol, ADR template, test pyramid) are referenced rather than repeated; sections that changed materially are restated in full.

### 27.1 What changed (summary)

| # | Change | v1 → v2 |
|---|---|---|
| 1 | Capacity model | 2,500h optimistic → **1,800h pessimistic**; "minus one" rule |
| 2 | MVP | Single v0.5 at W20 → **v0.4 "thin MVP" at W14** + full v0.5 at W20 |
| 3 | Critical path slack | P3 has 0 slack → **P3 has 2 weeks explicit slack** |
| 4 | Pod B overload | Pod B owns 9 components → **Pod B owns 7, Pod A & D pick up the rest** |
| 5 | Pod D bus factor | 1 person → **2 people from day one** |
| 6 | Fallback Stack | Full stack swap → **scoped component fallbacks** |
| 7 | Docs ownership | Side duty → **rotating dedicated docs owner + CI gate** |
| 8 | Architecture Freeze | Single freeze at W20 → **Tier 1 at W18, Tier 2 at W30** |
| 9 | Graduation prep | Starts W32 (12-week runway) → **Starts W20 (22-week runway)** |
| 10 | Contingency playbooks | "Start early" → **decision trees for top-6 red risks** |
| 11 | Research vs. engineering | Mixed → **explicit research spikes before cognitive model + adaptive engine** |
| 12 | Team stability | Assumes 9 active → **plans for 8 active + 1 firefighter** |
| 13 | Demo data | Mentioned → **first-class deliverable track from W20** |
| 14 | Out-of-scope list | v0.5 only → **explicit v1.0 out-of-scope, signed at kickoff** |

### 27.2 What did NOT change (and why)

- **Technology stack** (Primary) — still FastAPI + Next.js + Postgres + Qdrant + Neo4j + LiteLLM. The stack was not the weak point; the *plan around it* was.
- **Sprint length** (1 week) — still right.
- **Freeze philosophy** (3 freezes) — still right; v2 only *splits* Architecture Freeze into tiers, doesn't remove it.
- **Risk register** (32 risks) — still right; v2 adds *playbooks* on top.
- **Weekly demos + biweekly retros** — still right.
- **Test pyramid, integration protocol, ADR template** — still right.

### 27.3 v2 design principles (restated, sharpened)

1. **Plan for 8, not 9.** Every phase must be deliverable with 8 active members.
2. **Thin MVP first.** Ship a working end-to-end slice as early as possible, even if it's embarrassing.
3. **Freeze what's actually stable.** Don't freeze schemas you haven't built yet.
4. **Separate research from engineering.** Spikes before productionization.
5. **Document or don't ship.** CI gates on docs.
6. **Demo data is a deliverable.** Curate it from W20.
7. **Fallbacks are scoped, not total.** Swap components, not stacks.
8. **Buffer is on the critical path.** Not just off it.

---

## 28. v2 Team Model — Restructured Pods

### 28.1 New pod structure (9 members, 4 pods)

| Pod | Headcount | Lead | Primary ownership |
|---|---|---|---|
| **A — Backend & Platform** | **2** (was 3) | Backend Lead | Auth, user mgmt, course mgmt, API layer, DB schema, async jobs, **vector DB ops + search API** (moved from Pod B) |
| **B — AI/ML** | **3** (unchanged) | AI Lead | OCR, embeddings (model), chunking, RAG (prompt + retrieval), KG (concept extraction), cognitive model, adaptive engine, recommendation engine. **No eval harness** (moved to Pod D) |
| **C — Frontend & UX** | **2** (unchanged) | Frontend Lead | Web UI, dashboards, design system, accessibility, demo polish |
| **D — DevOps, QA & Eval** | **2** (was 1) | DevOps/QA Lead | CI/CD, environments, monitoring, SLOs, security, releases, **ML eval harness** (moved from Pod B), runbooks |
| **Firefighter (rotating)** | 0 (shared) | — | The "9th member" — picks up whatever is most behind each sprint |
| **TPM (rotating)** | 0 (shared) | — | Roadmap, sprint ops, risk register, stakeholder comms |
| **Docs owner (rotating)** | 0 (shared) | — | Owns doc completeness; 4-week rotation |

**Total: 9.** The "firefighter" and "TPM" and "docs owner" are *rotating roles* taken on by one of the 9 engineers for a 4-week stint, not additional headcount.

### 28.2 Why these changes

- **Pod D at 2 people** fixes the bus-factor (Critique 5) and lets Pod D own the eval harness (Critique 4).
- **Pod A at 2 people** forces Pod A to focus; the vector DB ops move is natural because the vector DB is a backend service.
- **Pod B unchanged at 3** but with reduced scope (no vector DB ops, no eval harness) — they can actually focus on the AI work.
- **Firefighter role** formalizes the "minus one" rule (Critique 12).

### 28.3 v2 Pod allocation per phase

| Phase | Pod A (2) | Pod B (3) | Pod C (2) | Pod D (2) | Firefighter | Docs Owner |
|---|---|---|---|---|---|---|
| **P0** | Skeleton, DB, env, vector DB deploy prep | Spikes: OCR, embeddings, LLM gateway | Next.js skeleton, design tokens | CI, envs, observability, eval harness scaffold | Floats to Pod D | TPM |
| **P1** | Auth, user mgmt, course CRUD, upload | LLM gateway hardening, OCR spike continuation | Course UI, routing, app shell | Async job infra, monitoring, eval harness v0 | Floats to Pod B | C-Lead |
| **P2** | Ingestion API, search API, chat API, vector DB ops | OCR pipeline, chunking, embeddings, RAG | Upload UI, chat UI, citation UI | Eval harness v1 (RAG golden set), cost monitoring | Floats to Pod B | A-Lead |
| **P3** | KG API, quiz API, integration tests | Concept extraction, KG, quiz gen, cognitive model (spike first) | Quiz UI, mastery UI, KG viz | Neo4j ops, eval harness v2 (KG + quiz) | Floats to Pod B (heavy) | B-Lead |
| **P4** | Recommendation API, analytics aggregation, admin API | Adaptive engine (spike first), recommendation engine, eval v3 | Analytics dashboard, admin dashboard, polish | Test infra, perf monitoring, feature flags | Floats to Pod C | D-Lead |
| **P5** | DB perf, auth hardening | Eval harness finalization, model artifact freeze | Docs completion, demo assets | Perf, security, DR drill, prod prep | Floats to Pod D | TPM |
| **P6** | Hotfix standby | Hotfix standby | Demo polish, fallback recording | Prod deployment, on-call | Hotfix standby | TPM |

### 28.4 v2 capacity model (pessimistic)

| Phase | Window | Active members (avg) | Hrs/wk per active | Effective hrs/wk |
|---|---|---|---|---|
| Pre-semester surge | Aug–Sep 2026 (8 wks) | 8.5 (–1 firefighter) | 16 | **~136** |
| Semester 1 | Oct 2026 – mid-Jan 2027 (15 wks) | 7.0 (–1 firefighter) | 8 | **~56** |
| Exam crunch 1 | Late Jan 2027 (3 wks) | 3.0 | 4 | **~12** |
| Semester 1 break | Feb 2027 (4 wks) | 6.5 | 11 | **~72** |
| Semester 2 (light) | Mar – mid-Apr 2027 (6 wks) | 7.0 | 8 | **~56** |
| Exam crunch 2 | Late Apr – early May 2027 (3 wks) | 3.0 | 4 | **~12** |
| Final push | Mid-May – Jun 2027 (5 wks) | 8.0 | 20 | **~160** |
| **Total** | **44 wks** | — | — | **~3,040 person-hours** |

After a **60% productivity multiplier** (more conservative than v1's 70%, reflecting real student-team overhead):

**v2 usable engineering hours ≈ 1,820.** This is the budget v2 plans against. It's **28% lower than v1** — meaning every feature must be 28% smaller, or 28% fewer features ship.

### 28.5 What gets cut to fit 1,820 hours

To fit the smaller budget, v2 makes these **structural descopes** (not just deferrals):

1. **Recommendation engine v2 features cut.** v1.0 ships recommendation v1 only (rule-based + simple content-based). No peer recommendations, no collaborative filtering.
2. **Analytics dashboard scope halved.** 4 chart types instead of 8. No time-series deeper than 30 days.
3. **Admin dashboard is minimal.** User list + course list + system health. No audit log UI (CLI tool only).
4. **KG visualization is simple.** List + force-directed graph. No fancy filtering, no edit-in-place.
5. **Multi-document RAG is single-course only.** Cannot query across all of a student's courses in v1.0.
6. **Mobile responsiveness is desktop-first.** Tablet/mobile is "best effort" not "supported."
7. **No real-time collaboration features.** Ever, in v1.0.
8. **No SSO / SAML.** Email/password + Google OAuth only.

These cuts are **signed off at project kickoff** as the v1.0 Out-of-Scope list (§29.4).

---

## 29. v2 MVP Definition, Out-of-Scope, Scoped Fallbacks

### 29.1 The "thin MVP" (v0.4) — new in v2

v2 introduces a **v0.4 "thin MVP"** that ships at W14 (6 weeks before v1's v0.5). The thin MVP is intentionally minimal:

> **A pre-loaded PDF is already in the system. A user (no auth required) asks a question in a text box and gets an answer with citations.**

That's it. No auth, no course management, no upload UI, no user accounts. The PDF is pre-loaded by an admin script. The "user" is anyone with the URL.

**Why this exists:** It proves the AI pipeline works end-to-end (OCR → chunking → embeddings → vector DB → RAG → chat UI) without depending on the backend foundations being done. If the thin MVP ships at W14, the team has 6 weeks to add auth + courses + uploads for v0.5. If the thin MVP *doesn't* ship at W14, the team knows the AI pipeline is the bottleneck — *before* investing in backend work.

**Exit criteria for v0.4:**
1. ✅ A specific PDF is pre-loaded (chosen by Pod B in W3).
2. ✅ OCR has run on it; text + chunks are in the DB.
3. ✅ Embeddings are in the vector DB.
4. ✅ A simple chat UI (single page, no auth) accepts a question.
5. ✅ The system returns an answer with at least 2 citations.
6. ✅ Deployed to a public URL.
7. ✅ The demo survives 5 questions without crashing.

### 29.2 v2 version roadmap (revised)

| Version | Target date | Theme | What's new vs. v1 |
|---|---|---|---|
| **v0.1** | Sep 12, 2026 (W6) | Skeleton | Same as v1 |
| **v0.2** | Sep 26, 2026 (W8) | Foundations | Same as v1 |
| **v0.3** | Oct 24, 2026 (W12) | Ingestion | Same as v1 |
| **v0.4** | **Nov 21, 2026 (W16)** | **Thin MVP** | **NEW in v2 — pre-loaded PDF + chat, no auth** |
| **v0.5** | **Dec 19, 2026 (W20)** | Full MVP + Tier 1 Freeze | Auth + courses + uploads added on top of v0.4 |
| **v0.6** | Jan 30, 2027 (W26) | Knowledge layer | Same as v1, but with research spike before |
| **v0.7** | **Feb 27, 2027 (W30)** | Cognition + **Tier 2 Freeze** | Same as v1, but cognitive model is "rolling average" not IRT |
| **v0.8** | Mar 27, 2027 (W34) | Adaptation | IRT cognitive model *if* data supports (research spike decides) |
| **v0.9** | Apr 24, 2027 (W38) | Analytics + polish + Feature Freeze | Same as v1, but with reduced dashboard scope |
| **v1.0-rc** | May 22, 2027 (W42) | Hardening + Code Freeze | Same as v1 |
| **v1.0** | Jun 5, 2027 (W44) | Graduation | Same as v1 |

### 29.3 v2 scoped fallbacks (replaces v1's "Fallback Stack")

Instead of a full stack swap, v2 defines **component-level fallbacks** that can be invoked independently:

| Fallback ID | Trigger | What swaps | Cost | Owner |
|---|---|---|---|---|
| **F-1** | Qdrant down > 1h unresolved OR Pod B can't maintain it | Qdrant → pgvector (Postgres extension) | 1 day (change driver config + re-index) | D-Lead |
| **F-2** | Neo4j ops too heavy OR KG schema not converging | Neo4j → JSONB in Postgres with recursive CTEs | 3 days (schema migration + query rewrite; no API change) | D-Lead + A-Lead |
| **F-3** | Self-hosted BGE-M3 too slow OR GPU unavailable | BGE-M3 → OpenAI text-embedding-3-small | 1 day (change env var; re-embed all chunks) | B-Lead |
| **F-4** | LLM API cost > $300/month | GPT-4-class → GPT-4o-mini or DeepSeek or GLM-4-flash for non-critical paths | 1 day (LiteLLM config change) | D-Lead |
| **F-5** | Celery + Redis ops too heavy | Celery → Inngest (serverless) | 1 week (rewrite job definitions; no API change) | D-Lead |
| **F-6** | PaddleOCR quality too low on real PDFs | PaddleOCR → Google Document AI (managed) | 3 days (API swap; cost increases) | B-Lead |
| **F-7** | Adaptive engine research spike fails | ML-based adaptive → rule-based adaptive (if-else) | 0 days (already a fallback branch in the spike) | B-Lead |

**Rules for invoking a fallback:**
1. Trigger metric must be objectively met (no vibes).
2. Decision owner is the listed owner; they decide within 48h of trigger.
3. Fallback is invoked via a single PR + ADR.
4. Once invoked, fallback is *sticky* — does not auto-revert. Reverting requires another ADR.

### 29.4 v2 Out-of-Scope list for v1.0 (signed at kickoff)

The following are **explicitly out of scope** for v1.0. Adding any of them requires a formal scope-change ADR signed by all pod leads + TPM + advisor.

| ID | Item | Reason | Revisit in |
|---|---|---|---|
| OOS-1 | Mobile app (native) | Out of capacity | v2.0 (post-graduation) |
| OOS-2 | Multi-tenant / school-level isolation | Premature for graduation | v2.0 |
| OOS-3 | Real-time collaboration | Never in this scope | — |
| OOS-4 | SSO / SAML | Email + Google OAuth is enough | v2.0 |
| OOS-5 | Offline mode | Architecture not designed for it | — |
| OOS-6 | Peer recommendations / collaborative filtering | Recommendation v1 only | v2.0 |
| OOS-7 | Cross-course RAG queries | Single-course only in v1.0 | v1.1 |
| OOS-8 | Tablet/mobile-first responsive design | Desktop-first; mobile best-effort | v1.1 |
| OOS-9 | Audit log UI (CLI tool only) | Out of capacity | v1.1 |
| OOS-10 | Time-series analytics > 30 days | Storage cost + low value for demo | v2.0 |
| OOS-11 | Multi-language UI (Arabic/French) | English only | v2.0 |
| OOS-12 | SCORM / LTI integration with LMS | Out of capacity | v2.0 |
| OOS-13 | Plagiarism detection | Out of capacity | — |
| OOS-14 | Proctoring / anti-cheat | Out of capacity + ethical concerns | — |
| OOS-15 | White-labeling / theming | Out of capacity | v2.0 |

This list is reviewed at every monthly milestone review. Items can be *removed* (i.e., brought into scope) only via scope-change ADR.

---

## 30. v2 Phases, Timeline, and Gantt

### 30.1 v2 high-level phases

| Phase | Name | Window | Weeks | Theme | Exit gate |
|---|---|---|---|---|---|
| **P0** | Pre-Flight | Aug 3 – Aug 30, 2026 | W1–4 | Setup, decisions, MVP def | v0.1 deployed |
| **P1** | Foundations | Aug 31 – Sep 27, 2026 | W5–8 | Auth, courses, upload, UI shell | v0.2 deployed |
| **P2** | AI Pipeline | Sep 28 – Dec 20, 2026 | W9–20 | OCR → embeddings → RAG; **v0.4 thin MVP at W16**; **v0.5 + Tier 1 Freeze at W20** | v0.5 + Tier 1 Architecture Freeze |
| **P3** | Knowledge & Cognition | Dec 21, 2026 – Feb 27, 2027 | W21–30 | KG + quiz + cognitive model; **research spike on cognitive model in W25**; **Tier 2 Freeze at W30** | v0.7 + Tier 2 Architecture Freeze |
| **P4** | Adaptation & Analytics | Feb 28 – Apr 24, 2027 | W31–38 | Adaptive engine (**research spike in W29**), dashboards; **Feature Freeze at W38** | v0.9 + Feature Freeze |
| **P5** | Hardening | Apr 25 – May 23, 2027 | W39–42 | Perf, security, docs, DR | v1.0-rc + Code Freeze |
| **P6** | Graduation | May 24 – Jun 6, 2027 | W43–44 | Demo, submission | v1.0 + presentation |

### 30.2 v2 master timeline table (with capacity, risk, milestone)

| Wk | Dates | Phase | Cap | Risk | Headline milestone | Exit criterion |
|---|---|---|---|---|---|---|
| W1 | Aug 3–9 | P0 | 136 | L | Kickoff, stack lock, repo + CI, **Out-of-Scope signed** | GH org, CI green, OOS list signed |
| W2 | Aug 10–16 | P0 | 136 | L | Environments, MVP sign-off, **team health check** | ≥ 8 active members confirmed |
| W3 | Aug 17–23 | P0 | 136 | L | Skeletons, **demo PDF chosen** | Both apps deployed |
| W4 | Aug 24–30 | P0 | 136 | L | ADRs 1–5, design tokens, **eval harness scaffold** | v0.1 tagged |
| W5 | Aug 31 – Sep 6 | P1 | 136 | L | Auth scaffold, user mgmt, **OCR spike converges** | Login works on staging |
| W6 | Sep 7–13 | P1 | 136 | L | Course CRUD, file upload, **embedding spike converges** | v0.1 demoed |
| W7 | Sep 14–20 | P1 | 136 | M | UI shell, routing, design system, **LLM gateway** | All routes exist |
| W8 | Sep 21–27 | P1 | 136 | M | **v0.2 deployed** | Instructor can upload PDF |
| W9 | Sep 28 – Oct 4 | P2 | 110 | M | OCR pipeline v1, **thin MVP chat UI scaffold** | OCR extracts text |
| W10 | Oct 5–11 | P2 | 80 | M | OCR hardening, document model | 20 PDFs processed |
| W11 | Oct 12–18 | P2 | 70 | H | Chunking, chunking API | Chunks with metadata |
| W12 | Oct 19–25 | P2 | 65 | H | **v0.3** + embedding batch job | v0.3 demoed; 1k chunks embedded |
| W13 | Oct 26 – Nov 1 | P2 | 60 | H | Vector DB deploy, embedding write path, search API | Similarity search works |
| W14 | Nov 2–8 | P2 | 60 | H | Hybrid retrieval + reranker | Top-k with rerank |
| W15 | Nov 9–15 | P2 | 60 | H | RAG prompt assembly, citation rendering | RAG returns cited answer |
| W16 | Nov 16–22 | P2 | 60 | H | **v0.4 Thin MVP** + RAG eval harness v1 | **Thin MVP demoed on staging** |
| W17 | Nov 23–29 | P2 | 55 | H | RAG chat API + streaming, chat UI | Chat works in browser |
| W18 | Nov 30 – Dec 6 | P2 | 55 | H | Multi-doc RAG (single-course), student flow integration, **Tier 1 Freeze draft** | E2E test green; Tier 1 ADRs ready |
| W19 | Dec 7–13 | P2 | 50 | M | Polish + bug fixes, **Tier 1 Architecture Freeze review** | All pod leads sign Tier 1 |
| W20 | Dec 14–20 | P2 | 50 | M | **v0.5 + Tier 1 Architecture Freeze** | **Full MVP shipped; Tier 1 signed** |
| W21 | Dec 21–27 | P3 | 30 | L | Holiday; **KG schema ADR draft**; **demo backlog started** | KG ADR draft |
| W22 | Dec 28 – Jan 3 | P3 | 25 | L | Holiday; concept extraction spike; **graduation outline v0** | Spike done |
| W23 | Jan 4–10 | P3 | 50 | M | Concept extraction pipeline, KG storage (Neo4j) | 200+ concepts in KG |
| W24 | Jan 11–17 | P3 | 45 | M | KG API, KG viz UI, **demo dataset v1** (3 courses loaded) | KG browsable |
| W25 | Jan 18–24 | P3 | 30 | H | KG-backed retrieval boost, **cognitive model research spike begins** | Retrieval improves |
| W26 | Jan 25–31 | P3 | 20 | H | **v0.6** + exam crunch begins, **cognitive model spike continues** | v0.6 demoed (small) |
| W27 | Feb 1–7 | P3 | 15 | H | Quiz generation v1, **cognitive model spike concludes** → ADR | Spike ADR merged |
| W28 | Feb 8–14 | P3 | 40 | M | Quiz UI + grading, mastery estimator v1 (rolling average) | Quiz + mastery works |
| W29 | Feb 15–21 | P3 | 60 | M | **Adaptive engine research spike begins**, mastery UI, quiz pool | Spike prototype works |
| W30 | Feb 22–28 | P3 | 70 | M | **v0.7 + Tier 2 Architecture Freeze** (KG, quiz, mastery, adaptive I/O frozen) | **Tier 2 signed** |
| W31 | Mar 1–7 | P4 | 65 | M | Adaptive engine productionization, **spike concludes** → ADR | Adaptive engine v1 |
| W32 | Mar 8–14 | P4 | 65 | H | Next-best-concept policy, recommendation API + UI | Recommendations appear |
| W33 | Mar 15–21 | P4 | 65 | H | Difficulty adjustment, **demo script v1** (skeleton) | Difficulty adapts |
| W34 | Mar 22–28 | P4 | 65 | H | Recommendation engine v1, **v0.8** (IRT if data supports) | v0.8 demoed |
| W35 | Mar 29 – Apr 4 | P4 | 60 | M | Analytics dashboard (backend + UI, reduced scope), **demo student accounts created** | Dashboard renders |
| W36 | Apr 5–11 | P4 | 55 | M | Admin dashboard (minimal), bug bash #1, **demo script v2** | Top-50 bugs triaged |
| W37 | Apr 12–18 | P4 | 50 | M | Bug fixing, accessibility pass, **demo dataset finalized** | ≤ 5 P1s open |
| W38 | Apr 19–25 | P4 | 45 | M | **v0.9 + Feature Freeze**, **deck v1 reviewed by advisor** | **Feature Freeze signed** |
| W39 | Apr 26 – May 2 | P5 | 60 | M | Perf pass + load test, DB optimization | P95 < 2s on RAG |
| W40 | May 3–9 | P5 | 90 | M | Security review, auth hardening, **demo dry-run #0** (internal) | No high vulns |
| W41 | May 10–16 | P5 | 120 | M | Bug bash #2, docs completion, **fallback demo video recorded** | ≤ 3 P1s; runbooks done |
| W42 | May 17–23 | P5 | 150 | L | **v1.0-rc + Code Freeze**, **dry-run #1 with advisor** | **Code Freeze signed** |
| W43 | May 24–30 | P6 | 170 | L | Prod deployment, **dry-run #2** | Prod live; demo rehearsed |
| W44 | May 31 – Jun 6 | P6 | 176 | L | **v1.0 + graduation presentation**, **dry-run #3 (dress rehearsal)** | **Graduation delivered** |
| — | Jun 7–27 | — | buffer | L | Buffer / submission window | Artifacts submitted |

### 30.3 v2 Gantt-style schedule (revised)

```
Workstream                      | Aug | Sep | Oct | Nov | Dec | Jan | Feb | Mar | Apr | May | Jun |
                                | W1-4| W5-8|W9-12|W13-16|W17-20|W21-24|W25-28|W29-32|W33-36|W37-40|W41-44|
--------------------------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
P0 Setup                        |  █  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
P1 Foundations                  |  ░  |  █  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
P2 OCR ✱                        |  ░  |  ░  |  █  |  █  |  ▓  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
P2 Embeddings ✱                 |  ░  |  ░  |  ▓  |  █  |  ▓  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
P2 Vector DB (Pod A now) ✱      |  ░  |  ░  |  ░  |  █  |  █  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
P2 RAG ✱                        |  ░  |  ░  |  ░  |  █  |  █  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |
--- v0.4 Thin MVP ◆ ---         |     |     |     |  ◆  |     |     |     |     |     |     |     |
--- v0.5 Full MVP ◆ ---         |     |     |     |     |  ◆  |     |     |     |     |     |     |
--- Tier 1 Arch Freeze ◆ ---    |     |     |     |     |  ◆  |     |     |     |     |     |     |
P3 KG ✱                         |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  █  |  ▓  |  ░  |  ░  |  ░  |
P3 Quiz gen ✱                   |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  █  |  ▓  |  ░  |  ░  |  ░  |
P3 Cognitive spike ✱ (NEW)      |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  █  |  ░  |  ░  |  ░  |  ░  |
P3 Cognitive model ✱            |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  █  |  ░  |  ░  |  ░  |
--- Tier 2 Arch Freeze ◆ ---    |     |     |     |     |     |     |     |  ◆  |     |     |     |
--- v0.7 ◆ ---                  |     |     |     |     |     |     |     |  ◆  |     |     |     |
P4 Adaptive spike ✱ (NEW)       |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  ░  |  ░  |  ░  |  ░  |
P4 Adaptive engine ✱            |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  █  |  █  |  ░  |  ░  |
P4 Recommendations              |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  █  |  ░  |  ░  |
P4 Dashboards (reduced scope)   |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  █  |  ░  |  ░  |
--- v0.9 + Feature Freeze ◆ --- |     |     |     |     |     |     |     |     |  ◆  |     |     |
P5 Hardening                    |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  █  |  ▓  |
P5 Docs (dedicated owner)       |  ▓  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |  ▓  |
Demo data track (NEW)           |  ░  |  ░  |  ░  |  ░  |  █  |  █  |  █  |  █  |  █  |  ▓  |  ▓  |
Grad prep (22-wk runway, NEW)   |  ░  |  ░  |  ░  |  ░  |  █  |  █  |  █  |  █  |  █  |  █  |  █  |
--- v1.0-rc + Code Freeze ◆ --- |     |     |     |     |     |     |     |     |     |  ◆  |     |
P6 Demo + Prod                  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ░  |  ▓  |  █  |
--- v1.0 Graduation ◆ ---       |     |     |     |     |     |     |     |     |     |     |  ◆  |
```

**Key v2 changes visible in the Gantt:**
- v0.4 Thin MVP at W16 (new).
- Two Architecture Freezes (Tier 1 at W20, Tier 2 at W30).
- Research spikes on cognitive model (W25–27) and adaptive engine (W29–31).
- Demo data track running from W20.
- Grad prep running from W20 (22 weeks, not 12).

### 30.4 v2 critical path (revised)

```
Stack lock (W1)
  → OCR pipeline (W9–W10)
    → Chunking (W11)
      → Embeddings (W12)
        → Vector DB (W13)
          → RAG (W14–W15)
            → v0.4 Thin MVP (W16)  [early warning gate]
              → Full student flow (W17–W18)
                → Tier 1 Freeze (W20)  [gate]
                  → Concept extraction (W23)
                    → KG (W24)
                      → Cognitive model spike (W25–W27)  [research]
                        → Cognitive model impl (W28)
                          → Tier 2 Freeze (W30)  [gate]
                            → Adaptive spike (W29–W31)  [research, parallel]
                              → Adaptive engine (W31–W33)
                                → Feature Freeze (W38)  [gate]
                                  → Hardening (W39–W41)
                                    → Code Freeze (W42)  [gate]
                                      → Prod deploy (W43)
                                        → Graduation (W44)
```

**v2 critical path slack:**
- W1 → W20: 1 week slack (same as v1).
- W20 → W30: **2 weeks slack** (improved from v1's 0; research spikes absorb uncertainty).
- W30 → W38: 1 week slack.
- W38 → W42: 0 weeks (hardening is hard).
- W42 → W44: 0 weeks.

**Total critical path slack: ~4 weeks** (improved from v1's 2 weeks).

---

## 31. v2 Risk Register + Contingency Playbooks

The v1 risk register (§21) is **unchanged** in v2 — the 32 risks and their scores still apply. v2 adds **contingency playbooks** for the top-6 red risks. Each playbook specifies the trigger, the decision owner, the decision deadline, and 2–3 concrete branches with their cost.

### 31.1 Playbook PB-01 — OCR quality too low (R-01)

| Field | Value |
|---|---|
| **Trigger metric** | < 90% success rate on the 20-PDF golden set at W10 demo |
| **Decision owner** | B-Lead |
| **Decision deadline** | End of W11 (1 week after trigger) |
| **Branches** | (A) Invoke fallback F-6 (PaddleOCR → Google Document AI) — 3 days, increases cost. (B) Add a 2nd OCR pass (Tesseract as fallback for failures) — 1 week, no cost. (C) Restrict input to "high-quality PDFs only" (no scanned docs) — 0 days, reduces scope. |
| **Default if no decision** | Branch B (2nd OCR pass). |

### 31.2 Playbook PB-02 — RAG quality unacceptable (R-02)

| Field | Value |
|---|---|
| **Trigger metric** | Faithfulness < 0.7 OR relevance < 0.7 on the 50-Q golden set at W16 |
| **Decision owner** | B-Lead |
| **Decision deadline** | End of W17 (1 week after trigger) |
| **Branches** | (A) Increase reranker weight; add cross-encoder reranking on top-50 — 3 days. (B) Switch LLM to a stronger model (GPT-4o or Claude) for RAG only — 1 day, +cost. (C) Restrict RAG to single-document queries (no multi-doc) — 0 days, reduces scope. (D) Add prompt engineering: "If you don't know, say 'I don't know'" — 1 day. |
| **Default if no decision** | Branch A + D (combined). |

### 31.3 Playbook PB-03 — Adaptive engine fails to converge (R-03)

| Field | Value |
|---|---|
| **Trigger metric** | Simulated trajectories in W31 spike show no learning improvement vs. random policy |
| **Decision owner** | B-Lead |
| **Decision deadline** | End of W31 (immediate, since adaptive engine is on critical path) |
| **Branches** | (A) Invoke fallback F-7 (rule-based adaptive: if mastery < 0.4, recommend easiest concept; if > 0.7, recommend hardest) — 2 days. (B) Simplify the policy: pick the concept with lowest mastery that has all prereqs met — 1 day. (C) Defer adaptive engine to v1.1; ship v1.0 with non-adaptive recommendations — 0 days, biggest scope cut. |
| **Default if no decision** | Branch B (simplest meaningful policy). |

### 31.4 Playbook PB-04 — Pod D bus factor (R-12)

| Field | Value |
|---|---|
| **Trigger metric** | Pod D lead unavailable > 3 days |
| **Decision owner** | TPM |
| **Decision deadline** | 24h after trigger |
| **Branches** | (A) Pod D engineer (2nd person) takes over as acting lead — 0 days. (B) If both Pod D members unavailable, invoke firefighter role + pull 1 Pod A engineer into DevOps — 1 day. (C) If critical infra is at risk, freeze deploys to prod; continue staging-only — 0 days. |
| **Default if no decision** | Branch A. |

### 31.5 Playbook PB-05 — Exam crunch collapses capacity (R-16)

| Field | Value |
|---|---|
| **Trigger metric** | Pod B throughput < 30% of plan for 2 consecutive weeks in W25–W27 |
| **Decision owner** | TPM |
| **Decision deadline** | End of W27 |
| **Branches** | (A) Pause KG work; focus Pod B on cognitive model only — 1 day to re-plan. (B) Defer Tier 2 Architecture Freeze by 2 weeks (W30 → W32); accept compression in P4. (C) Descope KG to "list of concepts, no relations" — 0 days, reduces scope. |
| **Default if no decision** | Branch A. |

### 31.6 Playbook PB-06 — MVP slips past W20 (R-18)

| Field | Value |
|---|---|
| **Trigger metric** | v0.4 Thin MVP not demoable at W16 |
| **Decision owner** | TPM |
| **Decision deadline** | End of W16 (immediate) |
| **Branches** | (A) v0.4 slips to W18; v0.5 slips to W22; Tier 1 Freeze slips to W22; P3 compressed by 2 weeks. (B) Invoke F-3 (OpenAI embeddings instead of self-hosted) to save Pod B time — 1 day. (C) Descope v0.5: ship auth + course CRUD + RAG, but defer multi-doc RAG to v0.6. |
| **Default if no decision** | Branch A + C (combined). |

### 31.7 Documentation ownership (v2 fix for Critique 7)

v2 introduces a **rotating dedicated Docs Owner** role:

- **Rotation:** 4 weeks per owner, drawn from pod leads (TPM, A-Lead, B-Lead, C-Lead, D-Lead) in round-robin.
- **Time commitment:** 30% of the owner's week during their rotation.
- **Responsibilities:**
  - Maintain the docs completeness dashboard (auto-generated from CI).
  - Run the weekly 5-min docs review at Friday demo.
  - Triage doc-related PR comments.
  - Own the Docusaurus site.
- **CI gate:** Every PR that adds a new endpoint, schema, ADR, or component **must** also add or update a doc file. The CI check uses a simple file-existence rule (e.g., `docs/api/<endpoint>.md` must exist if `app/api/<endpoint>.py` is added). PRs failing this check are blocked.

### 31.8 v2 risk heatmap (unchanged from v1, plus playbook markers)

The v1 risk heatmap (§21.5) still applies. The 6 red risks with playbooks are marked with 🎯:

- 🎯 R-01 (OCR) — PB-01
- 🎯 R-02 (RAG) — PB-02
- 🎯 R-03 (adaptive) — PB-03
- 🎯 R-12 (Pod D bus factor) — PB-04
- 🎯 R-16 (exam crunch) — PB-05
- 🎯 R-18 (MVP slip) — PB-06

The remaining red risks (R-07, R-20, R-21, R-22) are mitigated structurally (LiteLLM gateway, hard freeze rule, cross-training, Pod B restructure) rather than by playbook.

---

## 32. v2 Graduation Prep + Demo Data Track (22-Week Runway)

### 32.1 v2 graduation prep calendar (starts W20, not W32)

| GPM # | Week | Milestone | Owner |
|---|---|---|---|
| GPM-0 | **W20** | **Demo backlog started** — list of "moments that would make good demo beats" | TPM |
| GPM-1 | **W24** | Demo backlog reviewed; top-10 beats selected | TPM + advisor |
| GPM-2 | **W26** | Presentation outline v0 (story arc) | TPM |
| GPM-3 | **W30** | Demo script skeleton (what to click, what to say) | TPM |
| GPM-4 | **W32** | Slide template chosen; first 5 slides drafted | TPM + C-Lead |
| GPM-5 | **W34** | Demo script v1 (filled in) | TPM |
| GPM-6 | **W36** | Full deck v1 reviewed by advisor | TPM |
| GPM-7 | **W38** | Demo data curated (clean, predictable, reproducible) | B-Lead + C-Lead |
| GPM-8 | **W40** | Dry-run #0 (internal, no advisor) | TPM |
| GPM-9 | **W41** | Fallback demo video recorded | C-Lead |
| GPM-10 | **W42** | Dry-run #1 with advisor | TPM |
| GPM-11 | **W43** | Slide deck v2; dry-run #2; prod deployment stable | TPM + D-Lead |
| GPM-12 | **W44** | Dry-run #3 (dress rehearsal); submit artifacts | TPM |

### 32.2 v2 demo data track (first-class deliverable)

| DDM # | Week | Milestone | Owner |
|---|---|---|---|
| DDM-1 | **W20** | Demo PDF set chosen (3 courses × 5–10 PDFs each, all clean, all OCR-able) | B-Lead |
| DDM-2 | **W24** | Demo dataset v1: all demo PDFs ingested, OCR'd, embedded, in staging | B-Lead + D-Lead |
| DDM-3 | **W30** | 5 demo student accounts created with seeded mastery states | B-Lead + A-Lead |
| DDM-4 | **W34** | Demo quiz pool: 20 quizzes with known-good answers, tagged by concept | B-Lead |
| DDM-5 | **W36** | 5 known-good RAG questions identified and validated (golden demo set) | B-Lead |
| DDM-6 | **W38** | Demo data snapshot created; restore script tested | D-Lead |
| DDM-7 | **W40** | Demo data loaded on prod-like env; smoke-tested | D-Lead |
| DDM-8 | **W42** | Demo data frozen; no changes after this point | TPM |

### 32.3 v2 presentation structure (slightly revised from v1)

1. **(2 min) Problem** — why adaptive learning matters.
2. **(3 min) Solution** — what OpenLearn AI does.
3. **(4 min) Architecture** — system diagram + key tech choices + ADR highlights.
4. **(8 min) Live demo** — student flow + instructor flow + analytics + adaptation.
5. **(5 min) AI depth** — RAG eval results; adaptation examples; what worked, what didn't.
6. **(4 min) Engineering process** — CI/CD, testing, freezes, retros, what we'd do differently.
7. **(2 min) Future** — post-graduation path as a product.
8. **(2 min) Q&A** buffer.

The "what worked, what didn't" section is **non-negotiable** — advisors respect honesty about failures more than claims of perfection.

---

## 33. v2 Consolidated Final Plan (Master Summary)

This is the **single-page version** of v2. If the team prints one page and sticks it on the wall, this is it.

### 33.1 The 7-phase, 44-week plan at a glance

| Phase | Weeks | Calendar | Headline deliverable | Freeze? |
|---|---|---|---|---|
| **P0** Pre-Flight | W1–4 | Aug 2026 | v0.1 deployed; CI; 5 ADRs; OOS signed | — |
| **P1** Foundations | W5–8 | Sep 2026 | v0.2: auth + courses + upload | — |
| **P2** AI Pipeline | W9–20 | Oct–Dec 2026 | **v0.4 Thin MVP (W16)**; **v0.5 + Tier 1 Freeze (W20)** | **Tier 1 Arch** |
| **P3** Knowledge & Cognition | W21–30 | Dec 2026 – Feb 2027 | v0.6 (KG); v0.7 (cognition) + **Tier 2 Freeze** | **Tier 2 Arch** |
| **P4** Adaptation & Analytics | W31–38 | Mar – Apr 2027 | v0.8 (adaptation); v0.9 (analytics) + **Feature Freeze** | **Feature** |
| **P5** Hardening | W39–42 | Apr – May 2027 | v1.0-rc + **Code Freeze** | **Code** |
| **P6** Graduation | W43–44 | May – Jun 2027 | **v1.0 + presentation** | — |

### 33.2 The 5 gates (must-pass or graduation slips)

1. **v0.4 Thin MVP** — W16. AI pipeline proven end-to-end.
2. **Tier 1 Architecture Freeze** — W20. Foundational interfaces frozen.
3. **Tier 2 Architecture Freeze** — W30. Cognitive interfaces frozen.
4. **Feature Freeze** — W38. No new features.
5. **Code Freeze** — W42. Only critical fixes.

### 33.3 The 6 playbooks (top red risks)

| Playbook | Risk | Trigger week | Owner |
|---|---|---|---|
| PB-01 | OCR quality | W10 | B-Lead |
| PB-02 | RAG quality | W16 | B-Lead |
| PB-03 | Adaptive engine | W31 | B-Lead |
| PB-04 | Pod D bus factor | Any | TPM |
| PB-05 | Exam crunch | W27 | TPM |
| PB-06 | MVP slip | W16 | TPM |

### 33.4 The 9-person team (v2)

- **Pod A (Backend, 2):** auth, courses, API, DB, vector DB ops.
- **Pod B (AI/ML, 3):** OCR, RAG, KG, cognitive model, adaptive engine.
- **Pod C (Frontend, 2):** UI, dashboards, design system.
- **Pod D (DevOps + QA + Eval, 2):** CI/CD, monitoring, security, eval harness.
- **Rotating:** TPM (4w), Docs Owner (4w), Firefighter (2w, floating).

### 33.5 The 3 things that must be true every Friday

1. **A demo happened** on staging, not localhost.
2. **CI is green** on `main`.
3. **The risk register is current** (reviewed in the last 7 days).

### 33.6 The 3 things that must NEVER happen

1. **A merge to `main` without a PR review.**
2. **A new feature after Feature Freeze (W38)** without TPM + Tech Lead approval.
3. **A code change after Code Freeze (W42)** without TPM + D-Lead approval.

### 33.7 The 1 number that matters most

**Effective engineering hours available: ~1,820.** Every feature, every spike, every bug fix draws from this budget. If the team is spending more than 1,820 hours, something is wrong — either scope is too big, or people are working unsustainable hours. Track this number weekly.

### 33.8 v2 confidence assessment

| Phase | Confidence it ships on time | Reason |
|---|---|---|
| P0 | 95% | Low uncertainty; standard setup |
| P1 | 90% | Standard backend+frontend work |
| P2 (to v0.4) | 75% | AI pipeline risk; thin MVP is the canary |
| P2 (to v0.5) | 70% | Full MVP depends on v0.4 + auth + courses |
| P3 | 65% | Exam crunch + research risk; Tier 2 freeze may slip |
| P4 | 60% | Adaptive engine is the latest-starting critical item |
| P5 | 80% | Hardening is well-understood work |
| P6 | 95% | Demo prep, not new build |
| **Overall (v1.0 by W44)** | **~70%** | **Plan is realistic but tight; playbooks + buffer provide real margin** |

A 70% confidence is **honest** for a 9-person student team building an AI product in 10 months. The remaining 30% is absorbed by:
- The 6 contingency playbooks (§31).
- The 4 weeks of critical-path slack (§30.4).
- The scoped fallbacks (§29.3).
- The Out-of-Scope list (§29.4).

If everything goes wrong, the team still ships **something** — at minimum, a working RAG MVP with auth and course management, deployed to a real URL, with documentation. That is a credible graduation project even in the worst plausible case.

---

## 34. Closing Notes

### 34.1 How to use this roadmap

1. **Week 1:** Print §33 (the consolidated final plan) and stick it on the wall.
2. **Every Monday:** Pod leads review the weekly sprint plan (§10) for the current week.
3. **Every Friday:** Demo + retro + sprint planning.
4. **Every month:** Milestone review using §9.
5. **When a risk triggers:** Open the relevant playbook (§31) and follow it.
6. **When in doubt:** Optimize for *working software over perfect architecture*, *incremental delivery over big-bang*, and *risk reduction over feature count*.

### 34.2 What this roadmap does NOT do

- It does not tell you **how** to build the AI components. That's what ADRs and design docs are for.
- It does not **guarantee** success. It raises the probability of success from ~30% (unplanned) to ~70% (planned with margin).
- It does not replace **judgment**. When reality diverges from plan, the TPM and pod leads must adapt — the plan is a compass, not a map.

### 34.3 Final word

The single most important thing in this entire document is **the v0.4 Thin MVP at W16**. If the team ships that on time, the rest of the plan has enough slack to absorb almost any problem. If they don't, every subsequent date is at risk.

**Ship the thin MVP. Everything else follows.**

---

*End of OpenLearn AI Engineering Roadmap (v1 → v2 final).*

