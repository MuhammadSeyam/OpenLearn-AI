# OpenLearn AI — Graduation Project Delivery Roadmap
**Engineering Plan | August 2026 → June 2027 | 9-Person Team**

Prepared as a startup-style delivery plan, not an academic timetable. Priorities: working software > perfect architecture, incremental delivery > big-bang integration, risk reduction > feature count.

---

## 0. Executive Summary

OpenLearn AI's own spec (v4.0) describes an 8-layer, provider-agnostic AI platform. Built exactly as specced, this is a 2-year startup roadmap, not a 10-month graduation project. **The single biggest risk to this project is scope, not skill.** This plan therefore does three things before anything else:

1. **Cuts scope aggressively** to an MVP that still demonstrates every layer in the spec, deferring breadth (multi-provider support, IRT/CAT, Neo4j, Speech/Vision interfaces, multi-language, teacher roles) in favor of depth on the core loop: *upload → understand → practice → adapt → show progress.*
2. **Front-loads the hardest, highest-uncertainty technical work** (Arabic OCR, embeddings, RAG, local LLM performance) into August–September, when the team has full-time capacity and no academic load — this is exactly when the team can afford to fail fast and pivot.
3. **Builds explicit slack into the calendar** around midterms, finals, and the graduation defense, instead of assuming linear productivity for 10 months.

Total elapsed time: **~43 weeks (Aug 3, 2026 → May 31, 2027)**, followed by defense in June 2027. Roughly **30% of that time is deliberately reserved as buffer, consolidation, or reduced-capacity** — this is not padding, it's what makes the plan survivable.

---

## 1. Scope Decisions (Read This First)

### 1.1 MVP — Must Ship
| Layer (from spec) | MVP Scope |
|---|---|
| Auth / User Mgmt | Register, login, JWT, roles (Student, Admin) |
| Course/Material Mgmt | Upload, organize, list, delete materials |
| Ingestion + OCR | PDF/DOCX/PPTX native text; PaddleOCR for scanned Arabic+English PDFs |
| Knowledge Base (RAG) | Embeddings (local, BGE-m3) + ChromaDB + hybrid search + cited chat answers |
| Knowledge Graph | Auto-extracted concepts + prerequisite edges, **NetworkX only** (no Neo4j) |
| Student Knowledge Model | Heuristic → weighted moving average mastery; BKT is a stretch goal, not a dependency |
| Customized Student Profile | Core fields only (level, goals, VARK-lite, daily time); auto-updated fields are stretch |
| Adaptive Engine | Rule-based candidate generation + prerequisite check + priority scoring (no ML required) |
| Generation | MCQ + True/False questions, flashcards, 1–2 summary types |
| Spaced Repetition | Full SM-2 |
| Adaptive Exam | Simplified sequential difficulty ladder (Easy→Medium→Hard); **not full IRT/CAT** |
| Analytics Dashboard | Progress chart, mastery heatmap, weak-area list |
| Admin Dashboard | User list, content moderation, basic stats |
| Deployment | **Local Mode only** (Docker Compose, one command) — this is the mode that must never fail |
| Docs / Testing / Demo | Full — these are graduation-critical, not optional |

### 1.2 Should-Have (build only if MVP lands early)
Bayesian Knowledge Tracing (pyBKT) replacing the heuristic · IRT + true CAT · Half-Life Regression forgetting model · Neo4j + interactive KG visualizer · Hybrid cloud mode (1 cloud LLM + 1 cloud embedding provider as a config option) · Multiple RAG explanation modes (Socratic/exam-focused)

### 1.3 Explicitly Cut for This Project (Year-2 vision, not graduation scope)
Speech Interface (TTS/STT) · Vision Interface · Teacher role / multi-user classrooms · Mobile app · Languages beyond Arabic/English · SaaS billing/multi-tenancy · Full 7-interface Provider Abstraction Layer (MVP abstracts only **Reasoning, Embedding, Vector DB** — the three that are actually swapped; OCR/Speech/Vision/Ranking are hard-coded to one implementation)

> **Rule for the team:** if a task doesn't sit in 1.1, it does not get sprint time before Phase 6 without an explicit trade (something else gets cut). One person (the Tech Lead) owns this gate.

---

## 2. Team Structure (9 People)

| ID | Role | Primary Ownership | Notes |
|---|---|---|---|
| **M1** | Tech Lead / Architect | Provider Abstraction Layer, sprint planning, cross-team integration, committee liaison | Also acts as scope gatekeeper |
| **M2** | Backend — Platform | Auth, User Mgmt, Course Mgmt, API Gateway, DB schema | |
| **M3** | Backend — Ingestion | Upload pipeline, OCR integration, chunking, Celery workers | Owns the #1 technical risk (Arabic OCR) |
| **M4** | AI Eng — Retrieval | Embeddings, Vector DB, hybrid search, RAG generation, latency tuning | |
| **M5** | AI Eng — Knowledge | Knowledge Graph extraction, prompt engineering, Question/Flashcard/Summary generation | |
| **M6** | AI/Data Eng — Cognitive Modeling | SKM (mastery model), CSP, Adaptive Engine, Recommendation logic, SM-2 | Hardest conceptual role — pair with M1 early |
| **M7** | Frontend — Core UX | Auth UI, material mgmt, chat interface, onboarding wizard | Good entry point for less-experienced members |
| **M8** | Frontend — Dashboards | Analytics dashboard, Admin dashboard, KG visualizer | Good entry point for less-experienced members |
| **M9** | DevOps / QA / Docs | CI/CD, Docker Compose, testing framework, documentation, release management, demo infra | |

**Mentorship rule:** the two least AI/backend-experienced members should sit on M7/M8/M9 for August–September, then rotate into a support role on M5/M6 from October once the core pipeline exists and there's real code to learn from — don't ask beginners to build the riskiest layer first.

**Cadence:** Daily 15-min standup (async-friendly for exam weeks), weekly M1-led sync across all leads, phase-end demo day for the whole team + advisor.

---

## 3. Timeline Overview

| Phase | Dates | Duration | Team Capacity | Focus |
|---|---|---|---|---|
| 0 — Kickoff & Setup | Aug 3 – Aug 16, 2026 | 2 wks | High (summer) | Architecture lock, repo/CI, dev environments |
| 1 — Foundation (highest risk) | Aug 17 – Sep 27, 2026 | 6 wks | High (summer) | Auth, Ingestion, OCR, Embeddings, Vector DB, RAG v1 |
| 2 — Knowledge & Content Layer | Sep 28 – Nov 8, 2026 | 6 wks | Medium (semester starts Oct 1) | Knowledge Graph, Question/Flashcard Gen, Course Mgmt UI |
| 3 — Cognitive & Adaptive Layer | Nov 9 – Dec 20, 2026 | 6 wks | Medium→Low (midterms) | SKM, CSP, Adaptive Engine v1, SM-2 |
| Winter Buffer | Dec 21, 2026 – Jan 3, 2027 | 2 wks | High (break) | Catch-up, refactor, tech debt, stretch: BKT |
| 4 — Finals Freeze (Term 1) | Jan 4 – Jan 24, 2027 | 3 wks | Very Low | Critical bug-fix only, no new features |
| 5 — Recommendation + Analytics | Jan 25 – Mar 7, 2027 | 6 wks | Medium (Term 2 starts) | Recommendation Engine, Analytics + Admin Dashboards, Adaptive Exam |
| 6 — Integration & Hardening | Mar 8 – Apr 11, 2027 | 5 wks | Medium | E2E integration, security, load testing, beta users |
| 7 — Code Freeze & Polish | Apr 12 – May 2, 2027 | 3 wks | Medium-High | Bug triage, docs sprint, demo rehearsal prep |
| 8 — Graduation Prep | May 3 – May 31, 2027 | ~4 wks | Low (Term 2 finals) | Slides, video, rehearsals, submission packaging |
| **Defense / Submission** | **June 2027** | — | — | Final presentation |

**Sprint length:** 2 weeks, standard, except Phase 0–1 which uses **weekly checkpoints** (not full sprints) because the risk is high enough that the team needs to catch a failing approach (e.g., OCR quality) within days, not two weeks.

---

## 4. Critical Path

```
Infra/Auth Setup
   → Ingestion Pipeline (extract + OCR)
      → Semantic Chunking
         → Embedding Pipeline
            → Vector DB
               → Hybrid Retrieval + RAG Generation   ◄── MVP CORE, must work by end Sep
                  → Question Generation Service
                     → Student interaction data starts flowing
                        → Student Knowledge Model (mastery tracking)
                           → Adaptive Learning Engine
                              → Recommendation Engine + SM-2 scheduling
                                 → Analytics Dashboard
                                    → Full Integration Testing
                                       → Deployment Hardening
                                          → Documentation + Demo Prep
                                             → Graduation Defense
```

**Off-critical-path (parallelizable):** Knowledge Graph (enriches RAG but system works without it), Admin Dashboard, Course/User Management UI, KG Visualizer, Frontend polish. These are scheduled in parallel tracks precisely because a delay in them must never block the core loop above.

**Hard dependency warning:** the Adaptive Engine (Phase 3) cannot be meaningfully tested until real quiz-attempt data exists, which requires Question Generation (Phase 2) to already be working. This is why Phase 2 is not deferred even though it feels "less core" than RAG — it's a data-generation prerequisite for Phase 3, not a nice-to-have.

---

## 5. Detailed Phase Plan

### Phase 0 — Kickoff & Setup (Aug 3–16, 2026)

| Week | Milestone | Deliverables | Owner |
|---|---|---|---|
| W1 (Aug 3–9) | Architecture lock | ADR: MVP scope doc (Section 1) approved by whole team; tech stack finalized; repo created; role assignments confirmed | M1 |
| W2 (Aug 10–16) | Dev environment ready | Docker Compose skeleton boots empty services; Postgres schema draft v1; OpenAPI stub for all MVP endpoints; CI pipeline (lint + test) green on every PR; 30-min AI/backend onboarding session for less-experienced members | M9 (CI), M1 (schema/API), M2 |

**Exit criteria:** Every team member can run `docker-compose up` locally and hit a health-check endpoint. Scope doc signed off — no MVP-scope debates after this week.

---

### Phase 1 — Foundation / Highest-Risk Core (Aug 17 – Sep 27, 2026)

This phase exists to fail fast on the things most likely to sink the project: Arabic OCR quality and local LLM viability. If either is going to be a real problem, the team needs to know in August, not February.

| Week | Focus | Deliverables | Owner |
|---|---|---|---|
| W3 (Aug 17–23) | Auth + Upload | Register/login/JWT/roles complete; file upload API + MinIO storage; native text extraction (PyMuPDF/python-docx/python-pptx) | M2, M3 |
| W4 (Aug 24–30) | **OCR (top risk)** | PaddleOCR integrated for scanned PDFs, Arabic+English; semantic chunking (~500-word target, structural-boundary aware) | M3 (2 people if possible) |
| W5 (Aug 31–Sep 6) | Embedding pipeline | BGE-m3 (local, sentence-transformers) wired end-to-end; ChromaDB storage; full async pipeline (upload→extract→OCR→chunk→embed→store) via Celery | M4 |
| W6 (Sep 7–13) | RAG v1 | Hybrid search (semantic + BM25); Ollama + Qwen2.5-7B generation with citation grounding; first working "chat with your PDF" | M4 |
| W7 (Sep 14–20) | RAG tuning + Course UI | Re-ranking (bge-reranker); latency optimization toward <3–5s; Course/Material management UI wired to real backend | M4, M7 |
| W8 (Sep 21–27) | **Buffer + freeze contracts** | Fix critical bugs from W3–W7; lock PAL interface contracts for Reasoning/Embedding/VectorDB (no more churn); **Demo Day 1** | M1 (contract freeze), all |

**Exit criteria (this is the real MVP gate):** A student can register, upload a PDF — including a scanned Arabic one — and ask questions in a chat interface that returns cited, grounded answers, running entirely through `docker-compose up` with no cloud dependency. If this doesn't work by Sep 27, **do not proceed to Phase 2 on schedule** — extend Phase 1 by pulling time from the Winter Buffer instead.

**Risk checkpoint:** If Arabic OCR quality is unacceptable by end of W4, invoke the spec's own fallback: support only text-native PDFs for the graduation demo, and document scanned-PDF support as future work. Decide this by W5 at the latest — don't let it drag silently.

---

### Phase 2 — Knowledge & Content Layer (Sep 28 – Nov 8, 2026)

| Sprint | Dates | Deliverables | Owner |
|---|---|---|---|
| S1 | Sep 28–Oct 11 | Knowledge Graph extraction v1 (LLM-prompted concepts + `prerequisite-of` relations, NetworkX); MCQ + True/False question generation; Course Mgmt full CRUD | M5, M2 |
| S2 | Oct 12–25 | Flashcard generation; 2 summary types (quick, detailed); prerequisite-aware query expansion feeding back into RAG; onboarding wizard v1 (CSP core fields) | M5, M7 |
| S3 | Oct 26–Nov 8 | KG visualizer v1 (basic Cytoscape.js rendering, no interactivity polish yet); question bank tied to materials; bug bash | M8, M5 | 

**Demo Day 2** (early Nov): Upload → auto-extracted concept graph → generated quiz, in one flow.

**Exit criteria:** Knowledge Graph populates automatically (quality can be rough — filtering is a should-have, not a blocker); question generation produces usable MCQs; course management is fully functional; CSP captures onboarding data.

---

### Phase 3 — Cognitive & Adaptive Layer (Nov 9 – Dec 20, 2026)

Midterms typically land in this window — **Sprint 4 is intentionally the lightest-scope sprint in the whole plan.**

| Sprint | Dates | Deliverables | Owner | Capacity Note |
|---|---|---|---|---|
| S4 | Nov 9–22 | SKM v0.5.0 heuristic (Correct/Total mastery); quiz-attempt + review-item data models | M6 | **Deliberately light — midterms** |
| S5 | Nov 23–Dec 6 | SKM v0.5.1 weighted moving average (recency-biased); full SM-2 spaced repetition scheduler | M6 |  |
| S6 | Dec 7–20 | Adaptive Learning Engine v1: candidate generation → prerequisite check → priority scoring (rule-based, no ML) → recommendation endpoint | M6, M1 (pairing) |  |

**Demo Day 3** (mid-late Dec): "The system tells me what to study next, and why."

**Exit criteria:** Adaptive Engine returns a ranked, explainable study recommendation grounded in mastery + prerequisites; spaced repetition schedules reviews; CSP auto-updates at least one field (e.g., learning speed) from real interaction timing.

---

### Winter Buffer (Dec 21, 2026 – Jan 3, 2027)

No new feature commitments. Priorities in order: (1) absorb any slippage from Phases 1–3, (2) pay down tech debt / refactor anything that got hacky under time pressure, (3) **only if fully caught up**, attempt SKM upgrade to BKT (pyBKT) as a should-have stretch. This buffer is what keeps a 2-week midterm slip from cascading into February.

---

### Phase 4 — Finals Freeze, Term 1 (Jan 4 – Jan 24, 2027)

Feature development pauses. One rotating on-call pair per week handles only critical (P0) bugs. This is explicit, planned reduced capacity — not a contingency, a default assumption.

---

### Phase 5 — Recommendation + Analytics (Jan 25 – Mar 7, 2027)

| Sprint | Dates | Deliverables | Owner |
|---|---|---|---|
| S7 | Jan 25–Feb 7 | Ramp-up week; Recommendation Engine v2 (weighted scoring: mastery deficit, goal alignment, time-fit); difficulty calibration from CSP | M6 |
| S8 | Feb 8–21 | Analytics Dashboard (progress-over-time chart, mastery heatmap, Recharts); Admin Dashboard v1 (user list, content moderation, basic stats) | M8 |
| S9 | Feb 22–Mar 7 | Simplified Adaptive Exam (sequential Easy→Medium→Hard, IRT deferred); readiness score + weak-area alerts on the dashboard | M6, M8 |

**Demo Day 4** (early Mar): Full closed loop — upload → study → quiz → adapt → see progress on the dashboard. This is functionally the whole product; everything after this phase is hardening, not new capability.

**Exit criteria:** All 8 spec layers are minimally functional end-to-end on real (not seeded) data.

---

### Phase 6 — Integration & Hardening (Mar 8 – Apr 11, 2027)

| Sprint | Dates | Deliverables | Owner |
|---|---|---|---|
| S10 | Mar 8–21 | Full E2E integration pass across all modules; security pass (JWT hardening, input validation, rate limiting) | M1, M9 |
| S11 | Mar 22–Apr 4 | Performance tuning (Redis caching, vector index tuning); cross-platform deployment verification (native Linux, WSL2/Windows, macOS); push test coverage toward 60–70% on core modules | M9, all |
| S12 | Apr 5–11 | Stabilization week; deploy to a demo-accessible environment; **beta test with 5+ real students** (this is a graduation-value criterion, don't skip it) | M9, M1 |

**Exit criteria:** One-command deployment verified on 2+ platforms; core NFRs met or gaps explicitly documented with rationale; beta feedback collected and triaged into the Phase 7 bug list.

---

### Phase 7 — Code Freeze & Polish (Apr 12 – May 2, 2027)

**April 12 = Code Freeze.** No new features after this date — only bug fixes and polish. This is 3 full weeks before finals-heavy May, on purpose.

| Sprint | Dates | Deliverables | Owner |
|---|---|---|---|
| S13 | Apr 12–18 | UI/UX polish pass; triage and fix all P0/P1 bugs from beta testing | M7, M8 |
| S14 | Apr 19–25 | Documentation sprint: finalize Technical Spec, User Guide, Developer Guide, auto-generated OpenAPI docs, deployment README | M9, M1 |
| S15 | Apr 26–May 2 | Final regression pass; **pre-generate and freeze a fallback demo dataset** (per the spec's own risk register — never rely on live LLM calls during the defense); slide deck v1 | M9, M1 |

**Exit criteria:** Zero P0 bugs open; documentation complete; demo has been run start-to-finish at least once using only the frozen fallback dataset, offline.

---

### Phase 8 — Graduation Preparation (May 3 – May 31, 2027)

This overlaps Term 2 finals — capacity is genuinely low. Everything here is rehearsal and packaging, not building.

| Sprint | Dates | Deliverables | Owner |
|---|---|---|---|
| S16 | May 3–9 | Slide deck finalized (20–25 slides); 3-minute demo video recorded and edited | M1, M8 |
| S17 | May 10–16 | Dry-run presentation #1; committee Q&A prep list | Whole team |
| S18 | May 17–23 | Dry-run #2; fix only what dry-runs surface (no scope additions) | Whole team |
| S19 | May 24–31 | Final rehearsal; package submission (repo, report, video, slides, docs) | M9, M1 |

**June 2027 — Defense / Submission.**

---

## 6. Gantt-Style Schedule (Text View)

Legend: 🟩 heavy build · 🟨 medium/tuning · 🟦 light maintenance · 🟥 freeze/finals · ⬜ not active

| Workstream | Aug26 | Sep26 | Oct26 | Nov26 | Dec26 | Jan27 | Feb27 | Mar27 | Apr27 | May27 |
|---|---|---|---|---|---|---|---|---|---|---|
| Infra / DevOps / CI | 🟩 | 🟩 | 🟦 | 🟦 | 🟦 | 🟥 | 🟦 | 🟩 | 🟨 | 🟦 |
| Auth / User / Course Mgmt | 🟩 | 🟩 | 🟨 | 🟦 | 🟦 | 🟥 | 🟦 | 🟦 | ⬜ | ⬜ |
| Ingestion / OCR | 🟩 | 🟩 | 🟦 | ⬜ | ⬜ | 🟥 | ⬜ | 🟦 | ⬜ | ⬜ |
| Embeddings / VectorDB / RAG | 🟩 | 🟩 | 🟨 | 🟦 | ⬜ | 🟥 | ⬜ | 🟨 | 🟦 | ⬜ |
| Knowledge Graph | ⬜ | 🟨 | 🟩 | 🟨 | ⬜ | 🟥 | ⬜ | 🟦 | ⬜ | ⬜ |
| Question / Content Generation | ⬜ | 🟨 | 🟩 | 🟨 | ⬜ | 🟥 | 🟦 | ⬜ | ⬜ | ⬜ |
| SKM / CSP (Cognitive Model) | ⬜ | ⬜ | 🟦 | 🟩 | 🟩 | 🟥 | 🟦 | ⬜ | ⬜ | ⬜ |
| Adaptive / Recommendation Engine | ⬜ | ⬜ | ⬜ | 🟨 | 🟩 | 🟥 | 🟩 | 🟦 | ⬜ | ⬜ |
| Analytics / Admin Dashboard | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟥 | 🟩 | 🟩 | 🟨 | ⬜ |
| Testing / QA | 🟦 | 🟦 | 🟦 | 🟦 | 🟦 | 🟥 | 🟦 | 🟩 | 🟩 | 🟦 |
| Documentation | 🟦 | 🟦 | 🟦 | 🟦 | 🟦 | 🟥 | 🟦 | 🟦 | 🟩 | 🟦 |
| Graduation Prep / Demo | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | 🟦 | 🟨 | 🟩 |

---

## 7. Testing Strategy & Milestones

| Milestone | Timing | Scope |
|---|---|---|
| Unit test baseline | Every sprint, continuous | Each new module ships with unit tests; enforced via CI, not optional |
| Ingestion→RAG integration suite | End of Phase 2 | Upload-to-cited-answer flow covered end-to-end |
| SKM/Adaptive Engine test suite | End of Phase 3 / Phase 5 | Mastery updates and recommendation logic covered with synthetic interaction data |
| Full E2E suite (Playwright/Cypress) | Phase 6, S10 | Critical user journeys: register→upload→chat→quiz→dashboard |
| Load testing (k6) | Phase 6, S11 | Target: 50 concurrent users on a single hybrid-mode server |
| Security audit checklist | Phase 6, S10 | Auth, input validation, rate limiting, HTTPS |
| Beta testing (5+ real students) | Phase 6, S12 | Real-world usability + bug discovery feed into Phase 7 |
| Regression pass | Phase 7, S15 | Full suite green before code freeze artifacts are locked |
| Coverage target | By Phase 6 exit | ≥60–70% on core modules (SKM, Adaptive Engine, Retrieval, Auth) |

---

## 8. Documentation Milestones

| Milestone | Timing |
|---|---|
| Architecture Decision Record + Tech Spec v1 | End of Phase 0 |
| OpenAPI docs (auto-generated from FastAPI) | Continuous from Phase 1 |
| README + one-command deployment guide | End of Phase 1, kept current after |
| User Guide (draft) | Phase 5 |
| Developer / Contributor Guide | Phase 7, S14 |
| Final Technical Specification (polished) | Phase 7, S14 |
| Docusaurus site (should-have, not blocking) | Phase 7, if time allows |

---

## 9. Demo & Presentation Milestones

| Milestone | Timing | What It Proves |
|---|---|---|
| Demo Day 1 | End Sep 2026 | RAG core: upload + ask + cited answer, fully local |
| Demo Day 2 | Early Nov 2026 | Knowledge Graph + auto-generated quizzes |
| Demo Day 3 | Mid-late Dec 2026 | Adaptive recommendation with rationale |
| Demo Day 4 | Early Mar 2027 | Full closed loop: study → quiz → adapt → dashboard |
| Beta demo | Apr 2027 (Phase 6) | Real students, real feedback |
| Dry-run #1 | May 10–16, 2027 | Full committee-style rehearsal |
| Dry-run #2 | May 17–23, 2027 | Incorporates dry-run #1 feedback |
| **Defense** | June 2027 | Live demo backed by frozen fallback dataset + recorded video as safety net |

---

## 10. Risk Matrix

| # | Risk | Prob. | Impact | Phase | Mitigation | Fallback | Owner |
|---|---|---|---|---|---|---|---|
| 1 | Arabic OCR quality insufficient | High | High | 1 | PaddleOCR + preprocessing, test on real scanned Arabic docs in W4 | Support text-native PDFs only for v1 | M3 |
| 2 | Local LLM too slow (NFR-1 <3s) | Med | Med | 1, 6 | Smaller model option (Qwen 1.5B/Phi-3.5), caching, GPU if available | Relax to <5s; document as known limitation | M4 |
| 3 | Team skill gap in cognitive modeling (BKT/IRT) | High | High | 3 | Use pyBKT library, not custom math; pair M6 with M1 | Stay on weighted-moving-average heuristic — it's still a valid, documented stage | M6/M1 |
| 4 | Scope creep (trying to build all 7 PAL interfaces) | High | Med | Ongoing | Section 1 scope doc + M1 as gatekeeper | Cut Speech/Vision/full abstraction immediately | M1 |
| 5 | Midterms/finals collapse productivity | High | High | 3, 4, 8 | Buffers built into calendar; S4 deliberately light | Pull time from Winter Buffer | All |
| 6 | Knowledge Graph extraction is noisy | Med | Med | 2 | Few-shot prompting, basic post-filtering | Ship concepts without relations; skip visual graph polish | M5 |
| 7 | Docker deployment fails on Windows | Med | High | 1, 6 | Standardize on WSL2 + Docker Desktop, test on all 3 OSes early | GitHub Codespaces as fallback dev/demo environment | M9 |
| 8 | Integration debt (modules break when combined) | Med | High | 6 | Contract-first API design from Phase 0; weekly cross-team sync | Use S12 stabilization week / pull from Phase 7 buffer | M1 |
| 9 | Team member unavailable/drops out | Low | High | Ongoing | Cross-training via rotation (see Section 2); no undocumented single points of failure | M1 redistributes ownership | M1 |
| 10 | Live demo fails during defense (latency/downtime) | Med | High | 8 | Pre-generated, frozen fallback dataset (Phase 7 S15) | Play recorded demo video | M9 |
| 11 | Documentation effort underestimated | Med | Med | 7 | Dedicated full sprint (S14), continuous OpenAPI generation | Cut Docusaurus, ship as Markdown only | M9 |
| 12 | Hybrid/cloud provider integration eats time | Low | Low | 5+ | Treated strictly as should-have | Cut entirely, ship local-only | M1 |

---

## 11. Buffer Time Summary

| Buffer | Location | Length |
|---|---|---|
| Foundation buffer | Phase 1, W8 | ~1 week |
| Winter Buffer | Dec 21 – Jan 3 | 2 weeks |
| Finals Freeze (implicit buffer — no new features) | Jan 4–24 | 3 weeks |
| Stabilization week | Phase 6, S12 | 1 week |
| Code Freeze → Polish period | Phase 7 | 3 weeks |
| Graduation Prep (mostly rehearsal, not build) | Phase 8 | ~4 weeks |

**Total explicit buffer/reduced-capacity time: ~14 of 43 weeks (≈32%).** This is intentional — a 9-person student team with mixed skill levels building an 8-layer AI system will lose time somewhere; the plan decides in advance where that's allowed to happen (never in the two weeks before a demo day) rather than discovering it under pressure.

---

## 12. Success Criteria / Definition of Done

The project is "done" for graduation purposes when:

- [ ] A student can register, upload materials (including scanned Arabic PDFs), and get cited, grounded answers via RAG chat — fully offline, one-command deployment.
- [ ] The system auto-extracts a knowledge graph and generates at least 2 question types and flashcards from uploaded material.
- [ ] Student mastery is tracked per concept and visibly changes based on quiz performance.
- [ ] The Adaptive Engine produces an explainable "what to study next" recommendation using mastery + prerequisites + profile.
- [ ] Spaced repetition (SM-2) schedules reviews automatically.
- [ ] A simplified adaptive exam adjusts difficulty based on performance.
- [ ] Analytics and Admin dashboards show real, non-seeded data.
- [ ] Test coverage ≥60–70% on core modules; E2E suite passes.
- [ ] Full documentation set (spec, API docs, user guide, deployment guide) exists.
- [ ] Demo has been rehearsed twice and has a working offline fallback.
- [ ] 5+ real students have used the system and given feedback that was triaged.

---

## 13. Self-Critique — Weak Assumptions & Adjustments Made

This plan was deliberately stress-tested against its own assumptions before being finalized. Below are the weak points identified, and how the plan above already accounts for them — plus what's still genuinely unresolved and needs the team's input in Week 1.

**Assumptions I made and adjusted for:**
- *Full-time summer availability for all 9 members* is unlikely in practice (internships, travel, family obligations). I didn't assume otherwise — Phase 1 has an explicit buffer week (W8), and the MVP gate is deliberately narrow enough that partial availability doesn't sink it.
- *University calendar* — I assumed a standard Egyptian academic structure (Term 1: Oct–Jan with January finals; Term 2: Feb–May/June with finals overlapping the defense window), inferred from the given semester-start and submission dates. **This is a guess, not a confirmed fact — the team should validate actual exam dates in Week 1 and shift Phases 3–4 and 8 by up to ±2 weeks if wrong.**
- *BKT is reachable in one semester by a mixed-skill team* — genuinely uncertain. The plan treats it as a should-have specifically so a missed BKT milestone doesn't threaten the MVP; the weighted-moving-average fallback is still defensible in a graduation report as a valid, documented "Stage 2 of 3" implementation, not a failure.
- *Knowledge Graph extraction quality* from LLM prompting alone is likely to be noisy at first pass. The plan builds in an explicit lower bound ("concepts without relations is acceptable") instead of assuming extraction will just work.
- *Local LLM latency* on unknown team hardware is unverified — this is flagged as Risk #2, tested as early as Week 6, with two named fallbacks rather than discovered late.
- *An original draft of this plan* clustered SKM + Adaptive Engine work directly across the midterm window with full-intensity sprints — I revised this so Sprint 4 (which overlaps midterms) is explicitly the lightest sprint in the entire roadmap, and heavier cognitive-modeling work was pushed to late Nov/Dec and the Winter Buffer instead.
- *An original draft* placed code freeze in late April, leaving almost no gap before Term 2 finals in May. I moved code freeze to April 12 specifically to guarantee 3 full weeks of polish/documentation before the lowest-capacity month of the whole project.
- *Onboarding for less-experienced members* wasn't in the first draft at all — added explicitly in Phase 0 W2, plus a rotation plan in Section 2 so beginners start on frontend/QA and move into AI work once there's real code to learn from, not on day one of the hardest sprint.
- *The spec's full 7-interface Provider Abstraction Layer* is architecturally elegant but is a 2-year-product feature, not a 10-month graduation feature. Scope was cut to 3 interfaces (Reasoning, Embedding, Vector DB) to prevent the team burning Phase 0–1 on abstraction instead of working software.

**Still open — needs team confirmation, not something a roadmap can resolve alone:**
- Actual individual skill levels and time availability per person (this plan assumes roughly even 9-way capacity, which is almost never true — M1 should re-balance Section 2 after a real skills audit in Week 1).
- Confirmed university exam dates for both terms.
- Whether the team has access to GPU hardware for local LLM inference — this materially affects whether Risk #2 becomes a real problem in September or stays theoretical.
- Advisor/committee expectations on what "adaptive" must demonstrably do live vs. what can be shown via pre-recorded results — worth clarifying before Phase 7 locks the demo format.
