# OpenLearn AI — MVP Definition

| Field | Value |
|---|---|
| **Status** | Draft — pending Pod Leads + Advisor approval |
| **Source of Truth** | [MASTER_ROADMAP.md](../planning/Roadmap/MASTER_ROADMAP.md) (SSOT) |
| **Related Versions** | v0.4 Thin MVP (W16) · v0.5 Full MVP (W20) |
| **Owner** | Docs Owner (rotating) |
| **Last Updated** | 2026-08-20 |

> **Rule:** This document does **not** introduce any new requirements.  
> It only clarifies and organizes what is already defined in the Master Roadmap.

---

## 1. What is the MVP?

OpenLearn AI has **two staged MVP targets**:

| Version | Target Date | Name | Goal |
|---------|-------------|------|------|
| **v0.4** | 21 Nov 2026 (W16) | **Thin MVP** | Prove the AI pipeline works end-to-end |
| **v0.5** | 19 Dec 2026 (W20) | **Full MVP + Tier 1 Freeze** | Deliver a usable student flow with auth, courses, and upload |

The **critical milestone** is the **v0.4 Thin MVP**.  
If it ships on time, the rest of the plan has enough slack. If it slips, every subsequent date is at risk.

---

## 2. What the MVP Contains

### v0.4 — Thin MVP (Must Ship by W16)

- One **pre-loaded PDF** (no upload UI required)
- Simple **chat UI** (single chat box)
- **No authentication**
- End-to-end AI pipeline:
  - OCR (or pre-extracted text)
  - Chunking
  - Embeddings
  - Vector retrieval
  - RAG answer generation
- Answers include **citations** (source references)

### v0.5 — Full MVP (Target W20)

Everything in v0.4 **plus**:

- Authentication (student / instructor roles)
- Course management (basic CRUD)
- File upload (PDF + images)
- Full student flow: upload → process → chat with cited answers
- RAG chat with streaming responses and proper citation rendering

---

## 3. Basic Student Flow (MVP)

### Thin MVP (v0.4)
1. Student opens the chat page.
2. The system already has one pre-loaded educational PDF.
3. Student types a question.
4. System returns an answer grounded in the PDF with citations.

### Full MVP (v0.5)
1. Student signs up / logs in.
2. Student creates or joins a course.
3. Student uploads a PDF (or image).
4. System processes the document (OCR → chunk → embed).
5. Student asks questions in the chat.
6. System answers with citations from the uploaded material.

---

## 4. What the System Can Do in the MVP

| Capability | Thin MVP (v0.4) | Full MVP (v0.5) |
|------------|------------------|------------------|
| Pre-loaded document | ✅ | ✅ |
| Chat with cited answers | ✅ | ✅ |
| OCR / text extraction | ✅ (pipeline proven) | ✅ |
| Embeddings + vector search | ✅ | ✅ |
| RAG generation | ✅ | ✅ |
| Authentication | ❌ | ✅ |
| Course management | ❌ | ✅ |
| User upload | ❌ | ✅ |
| Streaming responses | Preferred | ✅ |
| Citation rendering | ✅ | ✅ |

---

## 5. What is Explicitly **Not** in the MVP

The following are **out of scope** for both Thin MVP and Full MVP (they belong to later versions or are permanently out of scope for v1.0):

- Knowledge Graph construction
- Concept extraction & prerequisite mapping
- Student cognitive / mastery model
- Adaptive recommendations / next-best-concept
- Quiz generation
- Spaced repetition scheduling
- Learning analytics dashboard
- Admin dashboard (beyond basic health)
- Mobile app / mobile-first design
- Multi-tenant / school isolation
- Real-time collaboration
- SSO / SAML
- Offline mode
- Cross-course queries
- Multi-language UI (beyond English + Arabic text support in content)

See the full signed **Out-of-Scope** list in the Master Roadmap.

---

## 6. Acceptance Criteria

### Thin MVP (v0.4) — Must Pass

- [ ] A single pre-loaded PDF is available in the system.
- [ ] User can open a chat interface (no login required).
- [ ] User can ask a natural-language question about the PDF.
- [ ] System returns an answer that is grounded in the document.
- [ ] Answer includes at least one citation (page / chunk reference).
- [ ] The full pipeline (text → chunk → embed → retrieve → generate) runs without manual intervention.
- [ ] Demo works on staging environment.

### Full MVP (v0.5) — Must Pass

All Thin MVP criteria **plus**:

- [ ] User can register and log in.
- [ ] Authenticated user can create / join a course.
- [ ] User can upload a PDF (or image).
- [ ] Uploaded document is processed automatically (OCR → chunk → embed).
- [ ] User can chat with the uploaded document and receive cited answers.
- [ ] End-to-end student flow works without developer intervention.
- [ ] Basic role separation (student vs instructor) exists.

---

## 7. Why This Definition Matters

- **v0.4 Thin MVP** is the earliest possible proof that the hardest technical path (OCR → RAG) actually works.
- Shipping it six weeks before the Full MVP gives the team time to fix integration problems while they are still cheap.
- Everything after W16 (Knowledge Graph, Cognitive Model, Adaptive Engine, Analytics) depends on a working RAG foundation.

---

## 8. Approval

This definition must be reviewed and approved by:

- [ ] Backend Pod Lead
- [ ] AI/ML Pod Lead
- [ ] Frontend Pod Lead
- [ ] DevOps/QA Pod Lead
- [ ] Advisor

Once approved, this file becomes the working definition of “MVP” for the rest of the project.

---

*Derived strictly from MASTER_ROADMAP.md — no new requirements added.*
