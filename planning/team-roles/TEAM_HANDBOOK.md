# OpenLearn AI — Engineering Team Handbook

| Field | Value |
|---|---|
| **Version** | 1.0 |
| **Status** | Approved — Companion to `MASTER_ROADMAP.md` |
| **Audience** | All engineering team members (9-person graduation team) |
| **Document Owner** | TPM (rotating) |
| **Review Cadence** | At each TPM rotation (every 4 weeks) |
| **Source of Truth** | `MASTER_ROADMAP.md` is the SSOT for what ships and when. This handbook explains how we work together. |

---

## 1. Purpose

This handbook exists for one reason: **to help every engineer understand how we work together.** The `MASTER_ROADMAP.md` tells you *what* we are building and *when*. This handbook tells you *how* we operate as a team to deliver it.

If you are new, read this end-to-end before your first sprint. If you are returning, use it as a reference whenever you are unsure about a process, a responsibility, or a working agreement. This document is deliberately short — it is not a project plan and does not replace the roadmap. Whenever a roadmap detail already exists, we summarize it here and explain how it affects your daily work. If you ever find a contradiction between this handbook and the roadmap, **the roadmap wins**; raise it at the next retro.

---

## 2. Team Philosophy

Our six values take precedence over any rule written elsewhere. When unsure, come back to these.

- **Ownership.** Every piece of code has an owner who is accountable for it in production, not just on their laptop. "Not my code" is not an acceptable answer.
- **Collaboration.** No one ships alone. Every feature touches at least two pods. We design before we build, agree on interfaces before we implement, and demo together every Friday.
- **Communication.** Default to over-communication. If you are blocked for more than 2 hours, say so. If you are going to miss a deadline, the time to say so is the moment you know.
- **Accountability.** When you commit to a sprint deliverable, you are committing to the team. Missing a commitment is recoverable; hiding a missed commitment is not.
- **Continuous Learning.** This is a graduation project, which means it is also a learning experience. Budget real time for learning. What we do not expect is for you to learn in isolation and surface a half-baked solution at the Friday demo.
- **Shipping Working Software.** We optimize for working software over perfect architecture, incremental delivery over big-bang, and risk reduction over feature count. A deployed v0.4 thin MVP that is ugly but works beats a beautifully architected system that exists only in slideshows.

---

## 3. Team Structure

We are a 9-person team organized into **4 specialized pods** plus **3 rotating roles**. Pods are cross-functional enough to deliver vertical slices but specialized enough to build deep competence. Every pod has a single lead who is the point of contact for that pod.

```
                         ┌──────────────────────────────┐
                         │  Rotating TPM (4-week stint)  │
                         │  Roadmap · Sprints · Risks    │
                         └───────────────┬──────────────┘
                                         │
              ┌──────────────┬───────────┼───────────┬──────────────┐
              ▼              ▼           ▼           ▼              ▼
        ┌──────────┐   ┌──────────┐ ┌──────────┐ ┌──────────┐  ┌─────────────┐
        │  Pod A   │   │  Pod B   │ │  Pod C   │ │  Pod D   │  │ Rotating    │
        │ Backend  │   │  AI/ML   │ │Frontend  │ │DevOps/QA │  │ Firefighter │
        │  2 eng   │   │  3 eng   │ │  2 eng   │ │  2 eng   │  │  (2-wk stnt)│
        │ + Lead   │   │ + Lead   │ │ + Lead   │ │ + Lead   │  │             │
        └──────────┘   └──────────┘ └──────────┘ └──────────┘  └─────────────┘
              │              │           │           │
              └──────────────┴───────────┴───────────┘
                             │
                  ┌──────────▼──────────┐
                  │ Rotating Docs Owner │
                  │  (4-week stint, CI  │
                  │  gate enforced)     │
                  └─────────────────────┘
```

| Pod | Headcount | Lead | Focus |
|---|---|---|---|
| **A — Backend & Platform** | 2 | Backend Lead | APIs, DB, auth, async jobs, vector DB ops |
| **B — AI/ML** | 3 | AI Lead | OCR, embeddings, RAG, KG, cognitive model, adaptive engine |
| **C — Frontend & UX** | 2 | Frontend Lead | UI, dashboards, design system, accessibility |
| **D — DevOps, QA & Eval** | 2 | DevOps/QA Lead | CI/CD, environments, monitoring, security, eval harness |
| **Rotating: TPM** | 0 (shared) | — | Roadmap, sprint ops, risk register, advisor comms |
| **Rotating: Firefighter** | 0 (shared) | — | Picks up whatever is most behind each sprint |
| **Rotating: Docs Owner** | 0 (shared) | — | Doc completeness, CI gate, Docusaurus site |
| **Total** | **9** | — | — |

The firefighter, TPM, and docs owner are **rotating roles**, not additional headcount. One of the 9 engineers takes on each role for a defined stint (4 weeks for TPM and Docs Owner, 2 weeks for Firefighter) and then returns to their pod. This is how we share the management work without burning out any single person.

**Why this structure.** It solves four real problems: (1) bus factor — Pod D has 2 people from day one, and at least 3 people are cross-trained on DevOps tasks by Feature Freeze; (2) AI complexity — Pod B has 3 people because the AI work is the longest critical path; (3) operational realism — Pod D owns CI/monitoring/security so it does not become "everyone's job and therefore no one's"; (4) load-balancing — rotating roles redistribute management work so no one is permanently stuck in meetings.

---

## 4. Pod Overview

Each pod has a mission, responsibilities, a tech stack, and a definition of success. This section is a practical guide — it tells you what life in each pod looks like on a typical week.

### Pod A — Backend & Platform

- **Mission.** Build the reliable backbone every other pod depends on: APIs, data models, auth, and the services that connect AI components to the frontend.
- **Primary Responsibilities.** Auth (JWT + refresh, RBAC); user and course management; file upload pipeline (presigned S3/MinIO); ingestion, search (vector + hybrid), chat (SSE), KG, quiz, recommendation, analytics, and admin APIs; DB schema and migrations (PostgreSQL 16 + Alembic); vector DB ops (Qdrant); DB performance; auth hardening.
- **Secondary Responsibilities.** Integration testing across pods; cross-training with Pod D on infra tasks.
- **Technologies.** FastAPI (Python 3.12) + Pydantic v2; SQLAlchemy 2.0 + Alembic; PostgreSQL 16, Qdrant, Redis + Celery; LiteLLM (shared with Pod B); pytest.
- **Expected Skills.** Comfortable in Python and async; basic SQL with willingness to learn Postgres features; REST and HTTP understanding; willingness to learn Alembic and Docker.
- **Typical Weekly Work.** Monday: 30-min pod sync. Tue–Thu: implement endpoints, write migrations, add tests, review PRs touching backend contracts. Friday: demo the integrated flow on staging, retro, plan next sprint.
- **Deliverables.** Working documented API endpoints with tests; reversible migrations; updated OpenAPI spec; green CI on `main`.
- **Definition of Success.** Endpoints work on staging by Friday demo; coverage ≥ 60% on critical paths; no contract drift with frontend; Pod B and Pod C can build on your APIs without asking "what does this return?"
- **Interfaces with Other Pods.** Receives Pod B outputs (OCR/chunks/embeddings/RAG) and exposes them through APIs; provides API contracts to Pod C (agreed before implementation); depends on Pod D for CI/CD, monitoring, environments.

### Pod B — AI/ML

- **Mission.** Build the AI brain: ingest documents, retrieve relevant content, generate cited answers, extract concepts, model student cognition, drive adaptation.
- **Primary Responsibilities.** OCR (PaddleOCR + Tesseract + Document AI fallback); chunking (recursive + semantic); embeddings (BGE-M3, OpenAI fallback); hybrid retrieval (BM25 + vector + bge-reranker-v2-m3); RAG prompt assembly with citations; RAG eval harness (golden Q&A, faithfulness + relevance); concept extraction (LLM-assisted); Knowledge Graph (Neo4j); quiz generation (LLM MCQs); cognitive model (rolling-average v1, IRT in v0.8 if data supports); adaptive engine; recommendation engine v1.
- **Secondary Responsibilities.** Curate demo dataset (3 courses × 5–10 PDFs); maintain golden Q&A set; cross-train one engineer on vector DB ops.
- **Technologies.** Python 3.12, LangChain, LiteLLM; PaddleOCR, Tesseract, Document AI; BGE-M3, bge-reranker-v2-m3; Neo4j; Qdrant (shared with Pod A); pytest + custom eval harness.
- **Expected Skills.** Solid Python; comfort with notebooks; basic NLP (tokenization, embeddings, similarity); willingness to learn RAG patterns and prompt engineering; for cognitive/adaptive: basic probability and willingness to read papers.
- **Typical Weekly Work.** Monday: pod sync; agree on what to spike vs. productionize. Tue–Thu: run experiments, iterate on prompts, write production code for converged components, write eval tests, review PRs. Friday: demo AI behavior on staging (not just a notebook); show eval numbers, not a cherry-picked example.
- **Deliverables.** Production AI components meeting eval thresholds (faithfulness ≥ 0.7 on golden set); eval harness in CI; ADRs for every model choice; demo dataset loaded and reproducible.
- **Definition of Success.** AI components work end-to-end on staging by Friday demo; eval numbers tracked over time; research spikes converge to ADRs (decisions recorded, not lost in chat).
- **Interfaces with Other Pods.** Provides AI components as services that Pod A wraps in APIs (I/O contracts agreed before implementation); provides data shapes (chunks, citations, mastery, recommendations) that Pod C renders; provides eval specs and golden datasets that Pod D's CI runs.

### Pod C — Frontend & UX

- **Mission.** Build the interface that students and instructors actually touch. Make the AI work visible, usable, and demoable.
- **Primary Responsibilities.** Next.js 16 (App Router) with TypeScript; Tailwind CSS 4 + shadcn/ui; design tokens and Storybook; all student-facing UI (chat, quiz, mastery, recommendations); all instructor-facing UI (course mgmt, analytics dashboard, KG viz); admin dashboard (minimal); accessibility (WCAG 2.1 AA on critical paths); demo polish; fallback demo video.
- **Secondary Responsibilities.** Maintain the design system; cross-train one engineer on basic CI/CD and Sentry triage by Feature Freeze.
- **Technologies.** Next.js 16 (App Router, SSR), TypeScript, React 19; Tailwind 4, shadcn/ui, Radix; Recharts/Visx for charts, react-flow or d3 for KG viz; Storybook; Vitest + Playwright.
- **Expected Skills.** Solid TypeScript and React; comfortable with CSS and component libraries; willingness to learn Next.js App Router; basic accessibility understanding (semantic HTML, ARIA, keyboard nav).
- **Typical Weekly Work.** Monday: pod sync; agree on which screens ship this week. Tue–Thu: build components in Storybook first, wire to APIs, write Playwright E2E tests, review PRs. Friday: demo a real user flow on staging (not a Storybook story).
- **Deliverables.** Working responsive UI matching the design system; Playwright E2E tests for critical flows; Storybook updated; accessibility checks pass (axe-core clean) on critical paths.
- **Definition of Success.** A user can complete the demo flow on staging without encountering a broken state; UI reflects real API data, not hardcoded mocks; Friday demo works on staging, not localhost.
- **Interfaces with Other Pods.** Consumes Pod A APIs (contracts agreed before implementation); renders Pod B outputs (data shapes agreed); depends on Pod D for Sentry, E2E test infra, and deployment pipelines.

### Pod D — DevOps, QA & Eval

- **Mission.** Keep the platform running, observable, secure, and tested — so every other pod can ship with confidence.
- **Primary Responsibilities.** GitHub Actions CI/CD (lint, test, build, docs check, license scan, coverage); dev/staging/prod environments; monitoring (Grafana + Prometheus + Loki + OpenTelemetry); Sentry; ML eval harness (RAG golden set, KG sanity tests, adaptation trajectories); SLOs and alerting; security review (OWASP, Semgrep SAST, dependency scan); performance and load tests; backup and DR drills; runbooks (deploy, rollback, DR, on-call); production deployment and on-call.
- **Secondary Responsibilities.** License scan in CI; LLM cost monitoring (with Pod B); cross-training Pod A/B/C engineers on basic DevOps.
- **Technologies.** Docker, Docker Compose, k3s; GitHub Actions; Grafana, Prometheus, Loki, OpenTelemetry; Sentry, PostHog; Semgrep, Trivy; Terraform (light).
- **Expected Skills.** Comfortable on the command line and with Docker; basic CI/CD understanding; willingness to learn k3s, Prometheus, Loki, alerting rules; for eval harness: basic Python and willingness to learn eval methodology.
- **Typical Weekly Work.** Monday: pod sync; agree on infra/eval work for the week. Tue–Thu: maintain CI, ship eval harness improvements, run load tests, review PRs touching CI or infra. Friday: report system health (SLOs, error rates, eval numbers) at the demo.
- **Deliverables.** Green CI on `main`; working environments with documented access; eval harness in CI with published numbers; runbooks a non-Pod-D engineer can follow.
- **Definition of Success.** `main` always green and deployable; no critical/high vulnerabilities at Code Freeze; P95 < 2s on RAG under 50 concurrent users; ≥ 3 people across pods can do basic DevOps by Feature Freeze.
- **Interfaces with Other Pods.** Pod A instruments code with metrics and logs; Pod B provides eval specs and golden datasets that Pod D's CI runs; Pod C depends on Pod D for Sentry, E2E test infra, deployment pipelines.

---

## 5. Choosing Your Pod

You will choose a pod during Week 1. Pick the area where you most want to grow, but also be honest about where you can contribute most. The team needs balance; we cannot have 7 frontend engineers and 2 backend engineers.

**General guidance.**
- **Specialize, do not generalize.** Pick one pod and go deep. You will learn more by owning one area than by floating across three.
- **It is okay to be a beginner.** You do not need to be an expert to join a pod. You need to be willing to learn and to put in the hours.
- **It is not okay to stay a beginner.** By Feature Freeze (W38), you should be able to independently deliver a feature in your pod's area.
- **Switches are allowed but costly.** You can switch pods at a phase boundary (W4, W8, W20, W30, W38) with TPM approval. Mid-phase switches disrupt both pods; do not do them lightly.

**Who should join Backend (Pod A).** You like building APIs and data models. You are comfortable with Python (or willing to learn fast). You enjoy thinking about contracts, schemas, and request/response shapes. You are okay with the fact that your work is mostly invisible — when it works, no one notices; when it breaks, everyone notices.

**Who should join AI/ML (Pod B).** You are interested in NLP, retrieval, LLMs, and applied ML. You enjoy experimentation and are comfortable with the fact that some spikes will fail. You can read papers or blog posts and turn them into working code. You are okay with the highest-pressure pod — Pod B is on the critical path, and a slip here cascades.

**Who should join Frontend (Pod C).** You like building user interfaces and care about usability. You are comfortable with TypeScript and React (or willing to learn fast). You enjoy turning API contracts into screens that a real human can use. You care about accessibility, design consistency, and demo polish. You want to build the part of the product that the graduation committee will actually see and touch.

**Who should join DevOps/QA (Pod D).** You like infrastructure, automation, and "making things run reliably." You are comfortable on the command line and with Docker. You enjoy writing tooling that other engineers use. You care about security, observability, and operability. You want to learn the skills most valuable in industry — every company hires DevOps engineers; few hire graduation-project frontend specialists.

**Specialization vs. learning.** You are encouraged to learn across pods — pair-program with someone from another pod, shadow their standup, read their PRs. But your primary identity is your pod. The team needs specialists so that each pod has enough depth to deliver. A team where everyone is a generalist is a team where nothing ships well.

---

## 6. Pod Lead Responsibilities

Every pod has one lead. The lead is the single point of contact for the pod and the person accountable for the pod's deliverables. Being a lead is a serious commitment — it is not a title, it is a job. Leads spend ~80% of their time on engineering and ~20% on lead duties.

- **Technical ownership.** You set the technical direction (in consultation with the team). You approve architecture within your pod (cross-pod architecture needs ADR + TPM). You are the person who answers "how does X work?" for your area. You write code — leads are not pure managers.
- **Planning.** You run the Monday pod sync and Friday demo prep. You break the sprint deliverable into tasks and assign owners. You negotiate dependencies with other pod leads at the Tuesday cross-pod sync. You say "no" to scope the pod cannot absorb — leads who cannot say "no" burn out their teams.
- **Code review.** You are the default reviewer for PRs in your pod. You review within 24 hours or explicitly delegate. You hold the bar on quality, tests, and contract compliance. You approve PRs that touch frozen interfaces (these need 2 reviewers; the lead is one). You mentor junior members through review comments, not by rewriting their code.
- **Mentoring.** You pair-program with less-experienced members when they are stuck. You explain *why* the code looks the way it does, not just *what* to type. You delegate stretch tasks that help them grow, not just grunt work. You give feedback early and often, not just at retro time.
- **Quality.** You are accountable for the pod's output quality. Tests exist and pass before merge. Coverage on critical paths meets the bar (≥ 60% by Feature Freeze). Tech debt is logged, not hidden. The pod's work is demoable on staging by Friday.
- **Communication.** You attend the Tuesday cross-pod sync and represent your pod's status, blockers, and needs. You communicate contract changes to other pods before you write code. You escalate risks to the TPM as soon as you see them. You write the pod's section of the weekly status update.
- **Risk escalation.** You are the first line of defense on risks. You log risks to the register as soon as you spot them — do not wait for the monthly review. You escalate red risks to the TPM within 24 hours. You propose mitigations, not just problems. You trigger the relevant playbook when a trigger metric is met.

If you find yourself spending more than 20% of your week on lead duties, you are doing too much yourself; delegate.

---

## 7. Rotating TPM Responsibilities

The TPM (Technical Program Manager) role rotates every 4 weeks among pod leads. The TPM is the glue that holds the team together week-to-week. It is **not** a manager role; it is a facilitator role.

- **Sprint planning.** You run the Friday sprint planning session. You make sure every sprint has 1 owner, 1 deliverable, and 1 exit criterion. You balance pod allocations. You publish the sprint plan by Friday EOD.
- **Weekly meetings.** You facilitate the Tuesday cross-pod sync (30 min, blockers only), the Friday demo (30 min + 30 min discussion), the biweekly retrospective (60 min), and the monthly milestone review (90 min, last Friday of the month).
- **Roadmap tracking.** You track sprint exit criteria (met / at risk / missed) and update the roadmap weekly. You track buffer consumption and trigger the descope protocol if thresholds are crossed. You propose roadmap changes when reality diverges from plan. You maintain the Revision History.
- **Risk register.** You review the register at every biweekly retro. You add new risks surfaced by pod leads. You close mitigated risks. You trigger playbooks when trigger metrics are met.
- **Documentation.** The rotating Docs Owner handles day-to-day doc completeness, but the TPM ensures ADRs, the README, and the architecture diagram are current at phase boundaries.
- **Stakeholder communication.** You are the single point of contact for the advisor and graduation committee. You send a written status update to the advisor every month after the milestone review. You schedule and facilitate advisor demos. You communicate descopes and slip risks before they become surprises.

**Rotation process.** Stint length is 4 weeks. Eligibility: pod leads only (so the TPM has cross-pod context). Order: round-robin among the 4 pod leads. The outgoing TPM does a 30-minute handoff with the incoming TPM covering: open risks, in-flight roadmap changes, advisor expectations, anything sticky. Time commitment: ~20% of the TPM's week during their rotation.

**What the TPM is NOT.** The TPM is not your boss — they facilitate; your pod lead assigns you to tasks within your pod. The TPM is not the technical architect — architecture decisions are owned by the pod that owns the component; the TPM ensures ADRs are recorded. The TPM is not the product manager — product scope is defined in the roadmap; the TPM does not change it unilaterally.

---

## 8. Collaboration Rules

Most project failures are collaboration failures, not technical failures. This section defines how we work together so collaboration is a strength.

**When to communicate.** Communicate when you are starting work that touches another pod's area; when you are changing an interface another pod depends on; when you are blocked for more than 2 hours; when you are going to miss a deadline; when you have a decision that needs sign-off; when you learned something that changes the plan. Default to over-communication in the team channel.

**When to ask for help.** Ask when you have been stuck on the same problem for more than 2 hours; when you are not sure what the next step is; when you are about to change a frozen interface (ask before you write code); when you are about to invoke a fallback; when you are feeling overwhelmed (ask your pod lead or the TPM — they will not judge you). Asking early is professional, not weak. Asking after missing a deadline means you waited too long.

**How dependencies are handled.** Declare them early at the Monday pod sync. Surface them at the Tuesday cross-pod sync. Write them into the sprint plan with an owner and due date. Follow the integration protocol for each integration milestone (IM-1 through IM-15 in the roadmap): declare interfaces frozen T-3 days before, wire real calls T-2, test on staging T-1, demo on T-day (Friday), post-mortem on T+1.

**How APIs are agreed upon.** Docs-first workflow: (1) the consuming pod (usually Pod C) writes a draft of the API contract (request shape, response shape, error cases); (2) the producing pod (usually Pod A) reviews and negotiates; (3) both pods sign off; (4) the contract is committed as a design doc in `docs/`; (5) implementation begins — the contract does not change without an ADR. This prevents the most common collaboration failure: the frontend builds against one shape, the backend ships another, and the integration breaks at the Friday demo.

**How integration works.** Integration happens on staging, not localhost. Integration is demoed at the Friday demo — if it fails, the integration rolls into next week and a risk is logged. Integration failures trigger a post-mortem within 24 hours; root cause is added to an ADR if architectural. No integration is "done" until it survives the Friday demo on staging.

**How handoffs work.** When you hand off work: write a short handoff note (what is done, what is not done, next step, gotchas); pair with the receiver for 30 minutes to walk them through the code; stay available for questions for 1 week after; do not consider the work "handed off" until the receiver has merged at least one PR to it. Handoffs without context are not handoffs; they are abandonments.

---

## 9. Engineering Expectations

Every engineer — regardless of pod — is expected to meet these baseline expectations.

- **Learning.** Budget real time for learning. Do not learn in isolation — surface what you are learning in the pod sync so others learn too. Track what you learn each week; this becomes material for retros and for the "what would you do differently" section of the graduation presentation.
- **Documentation.** Write docs before code (docs-first workflow). Update docs when code changes — in the same PR. The CI gate enforces doc existence: a PR that adds a new endpoint/schema/ADR/component without a corresponding doc file is blocked. The rotating Docs Owner runs a 5-minute docs review at every Friday demo.
- **Git discipline.** Work on short-lived feature branches (`feature/<short-description>`), merged within 1 week. Use Conventional Commits (`feat(auth): add refresh token rotation`). Squash-merge to keep `main` history clean. Never commit directly to `main`. Never force-push to `main` or shared branches. Keep branches up to date with `main` before merging.
- **Testing.** Write tests alongside code, not after. Unit tests run in < 60 seconds and gate every PR. Integration tests run in < 5 minutes and gate every merge to `main`. E2E tests (Playwright) run nightly on staging and on every release tag. Coverage ≥ 60% on critical paths by Feature Freeze — this is a hard gate.
- **Code review.** Review PRs within 24 hours. Use the code review checklist (in the roadmap's Git Workflow section). Be kind — comment on the code, not the person. Approve explicitly — silence is not approval. Hold the bar — if a PR introduces tech debt, require it to be logged before approval.
- **Professional communication.** Be on time to meetings; if you cannot be, say so before the meeting starts. Use the team channel for project communication; do not make decisions in DMs. Disagree respectfully and in public — disagreement is healthy; hidden disagreement is toxic. When you commit to something, write it down. Verbal commitments do not count.
- **Meeting deadlines.** A deadline is a commitment to the team. If you are going to miss one, the time to say so is the moment you know — not the day before. When you miss a deadline, propose a new one. Do not leave the team guessing.
- **Ownership.** Own your code in production, not just on your laptop. If your code breaks at 2am before the demo, you fix it. If your code is hard to use, you make it easier. If your code has a bug, you fix the bug and write a regression test. "Not my code" is not an acceptable answer.

---

## 10. Communication Guidelines

**Daily communication.** Async standup in the team channel by 10:00 AM every working day. Format: "Yesterday / Today / Blockers." If you are blocked, tag the person who can unblock you — do not wait for them to notice. If you are taking a day off, announce it the day before. Use threads for topic-specific discussions so the main channel stays scannable.

**Weekly sync (Tuesday, 30 min).** Cross-pod, blockers-only. Each pod lead reports: what we shipped, what we are doing, what we are blocked on. The TPM resolves cross-pod blockers or schedules follow-ups. No status slides; no general discussion. This meeting is for unblocking, not informing.

**Sprint Review (Friday, 30 min).** Demo on staging, not localhost. 1–2 demos of work shipped that week. Live demo preferred; recorded fallback if the live demo fails. Whole team attends; advisor invited but not required. If a pod has nothing demoable for 2 consecutive weeks, the TPM escalates to the pod lead and the risk register.

**Sprint Planning (Friday, 30 min).** Right after the sprint review. The TPM facilitates; pod leads negotiate. Every sprint has 1 owner, 1 deliverable, 1 exit criterion. The sprint plan is published to the team channel by Friday EOD.

**Retrospectives (Biweekly, Friday, 60 min).** 5-stage format: set the stage, gather data, generate insights, decide what to do, close. Pick top 3 action items with owners and due dates ≤ 2 weeks out. Every action item becomes a GitHub issue tagged `retro-action`. Open retro items are reviewed at the start of the next retro. Anti-pattern: "we'll do better next time" with no concrete action.

**Monthly Milestone Review (Last Friday, 90 min).** Full team plus advisor. Demo the monthly milestone artifact on staging. Compare actual progress vs. plan; surface any slip ≥ 3 days. Update risk register; re-plan the next 4 weeks at sprint level. Decide any descopes — now, not at the next review.

**Emergency communication.**
- **P0** (system down, graduation at risk): page the TPM and the relevant pod lead in the team channel with `@here`. Do not use DMs.
- **P1** (graduation-blocking but not system-down): post in the team channel and tag the pod lead. Expect a response within 4 hours during working time.
- **P2** (important but not urgent): open a GitHub issue.
- **P3** (nice to have): mention it at the next retro.

---

## 11. Working Agreements

These are the team's rules. They are short, non-negotiable, and apply to everyone.

1. **Own your code.** If you wrote it, you support it — in production, not just on your laptop.
2. **Never merge unreviewed code.** Every PR needs at least 1 approval (2 for frozen interfaces).
3. **Never commit to `main`.** Every change goes through a PR.
4. **Keep documentation updated.** If you change code, update docs in the same PR.
5. **Ask early.** If you are blocked for more than 2 hours, say so.
6. **Commit often.** Small commits are easier to review and easier to revert.
7. **Test before pushing.** Run unit tests locally before opening a PR.
8. **Respect deadlines.** If you cannot meet a commitment, say so the moment you know.
9. **Communicate blockers immediately.** Do not wait for someone to notice.
10. **Do not work in isolation.** If no one knows what you are doing, you are doing it wrong.
11. **Quality before quantity.** A working feature with tests beats three features without.
12. **Demo on staging, not localhost.** "It works on my machine" is not a demo.
13. **Be on time to meetings.** If you cannot be, say so before the meeting starts.
14. **Use the team channel for project communication.** Decisions made in DMs do not count.
15. **Review PRs within 24 hours.** Your delay is someone else's blocker.
16. **Log tech debt when you introduce it.** Hidden debt is the most expensive debt.
17. **Respect the freezes.** Architecture, Feature, and Code freezes are real gates.
18. **No silent scope changes.** Adding scope requires an ADR.
19. **Be kind in code review.** Comment on the code, not the person.
20. **Ship the thin MVP at W16.** Everything else follows.

---

## 12. Frequently Asked Questions

**Q1. I am new and do not know the stack. How do I get started?**
Read the `MASTER_ROADMAP.md` sections on Technology Stack and Team Organization, then this handbook end-to-end. Then ask your pod lead to pair with you on your first task. We expect you to be slow in your first sprint; that is normal.

**Q2. How do I know which pod to join?**
See section 5. Talk to the pod leads. Be honest about your skills and interests. The team needs balance, so your first choice may not always be available.

**Q3. Can I switch pods mid-project?**
Yes, but only at a phase boundary (W4, W8, W20, W30, W38) and with TPM approval. Mid-phase switches disrupt both pods.

**Q4. What if my pod lead is the bottleneck?**
Tell the TPM. The TPM will either unblock the pod lead (by reallocating work) or escalate. Do not suffer in silence.

**Q5. How many hours per week am I expected to work?**
The capacity model assumes 8–18 hours per week per active member, depending on the calendar phase. The plan is sized so sustainable hours are enough. If you are regularly working more than 25 hours per week, something is wrong — tell your pod lead.

**Q6. What if I have an exam and cannot work that week?**
Tell your pod lead at the Monday sync (or earlier). The plan has exam-crunch buffer built in (W25–W27 and late April). You are expected to do minimal work during exam weeks; this is planned, not slacking.

**Q7. How do I propose a change to the roadmap?**
Open a GitHub issue tagged `roadmap-change`. The TPM triages within 3 business days. For Major or Critical changes, you will draft an ADR.

**Q8. How do I invoke a fallback (e.g., Qdrant → pgvector)?**
Fallbacks are invoked by the listed owner when the trigger metric is objectively met. The invocation is a single PR + ADR. Once invoked, the fallback is sticky — it does not auto-revert.

**Q9. What is the difference between a T1, T2, and T3 decision?**
T1 is tactical (single-pod, reversible) — pod lead decides. T2 is architectural (cross-pod, affects interfaces) — TPM + 2 pod leads. T3 is strategic (project-wide) — TPM + all pod leads + advisor.

**Q10. What happens if I break `main`?**
You fix it. If you cannot fix it within 1 hour, you revert your merge and try again on a feature branch. Breaking `main` is not a crime; leaving it broken is.

**Q11. Can I work on a feature that is not in the sprint plan?**
No, not without TPM approval. The sprint plan is the contract for the week. If you have capacity for more, ask the TPM — they will have a list of stretch tasks.

**Q12. How do I add a new risk to the risk register?**
Open a GitHub issue tagged `risk` with: description, likelihood (1–5), impact (1–5), owner, mitigation, trigger. The TPM reviews it at the next biweekly retro. If it is a red risk (score ≥ 12), tag the TPM immediately.

**Q13. What if I disagree with my pod lead's technical decision?**
Say so, respectfully, in the pod sync. If unresolved, escalate to the TPM. If it is a T2 or T3 decision, it goes through the ADR process. Disagreement is healthy; silent resentment is not.

**Q14. How do I demo something that did not work?**
Demo the progress. Show what you tried, what you learned, what you will do differently next week. "Nothing shipped" is not acceptable; "we tried X, it failed because Y, next week we will try Z" is.

**Q15. What if I am going to miss the Friday demo?**
Tell your pod lead by Thursday. Your pod lead will either re-allocate or move the demo to next week. Do not go dark and hope no one notices.

**Q16. Can I push directly to `main` if it is a tiny fix?**
No. Every change goes through a PR. There are no exceptions, even for typo fixes. The CI gate exists precisely to catch mistakes that "felt too small to break."

**Q17. How do I get review on a PR that touches a frozen interface?**
Tag 2 reviewers explicitly (your pod lead + one more). Tag the TPM if the change might need an ADR. Frozen-interface PRs take longer to review; plan for that.

**Q18. What if I do not understand the codebase?**
Read the README, the architecture diagram (in `docs/`), and the ADRs. Then ask your pod lead to pair with you on a small task. The codebase is yours to learn; do not wait for someone to teach it to you.

**Q19. What happens at Code Freeze (W42)?**
After Code Freeze, no new code merges to `main` except critical fixes (P0/P1) with TPM + D-Lead approval. Smoke tests are re-run before and after every merge. The week before graduation is for rehearsing the demo, not for debugging regressions.

**Q20. What is the single most important thing I should do?**
Ship the v0.4 thin MVP at W16 (21 November 2026). If the team ships that on time, the rest of the plan has enough slack to absorb almost any problem. If you are on Pod B, your work directly determines whether this happens. If you are on another pod, your job is to make Pod B's job easier — remove their blockers, agree on contracts early, do not introduce integration surprises.

---

*End of TEAM_HANDBOOK.md v1.0.*
