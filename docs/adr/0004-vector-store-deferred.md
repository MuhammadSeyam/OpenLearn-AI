# ADR-0004: Vector store default (ChromaDB vs Qdrant) — DEFERRED

- **Status:** Deferred (2026-08-16) — decision required by end of Week 4
  (before the embedding spike, W5)
- **Deciders:** Pending — AI/ML pod lead + tech lead (this ADR records the
  deferral, not a choice)

## Context

The two authoritative-adjacent documents disagree on the default vector
store:

- **Tech Spec v4 §10.3** default: **ChromaDB** (embedded mode, local-first;
  ~15 mentions; Qdrant appears only as a scaling alternative, §1218 table).
- **Master Roadmap / deployment docs**: **Qdrant** as default, with fallback
  F-1 "Qdrant → pgvector".

`AI_CONTEXT.md` already flagged this as unresolved. Neither document records
an evaluation; the counts of mentions are not evidence. No vector-store code
exists anywhere in the repository, so nothing currently depends on either.

## Decision

**Defer the choice.** Do not treat either document's default as binding.
Record the contradiction, define the evidence required, and decide once, in a
superseding ADR, before the embedding spike needs a store (roadmap W5;
decision deadline: end of W4, 2026-08-30).

### Evidence required before deciding

1. **Embedding spike results (W3–4)** — BGE-M3 vs OpenAI embedding quality on
   the 10–20 Arabic/English query–chunk pairs (roadmap W2 methodology doc) —
   including vector dimension and index size for a realistic course corpus
   (target: 3 courses × 5–10 PDFs).
2. **Local-mode constraint check** — ChromaDB embedded (in-process, zero
   extra services) vs Qdrant (extra container; Qdrant also offers a local
   mode that must be validated) on the Local profile's 16 GB RAM target.
3. **Metadata filtering needs** — chunk filtering by course/document/concept
   from the spec's retrieval design; compare filter capabilities and query
   ergonomics in current Python clients.
4. **Persistence/backup story** per deployment mode (Local student machines
   vs Cloud), including pgvector's appeal as a Postgres-only fallback (F-1)
   if a second storage system proves operationally expensive.
5. **Migration cost** — collection export/import between ChromaDB and Qdrant,
   since the PAL vector-DB interface means application code should not care,
   but operational tooling will.

### What remains flexible until then

- No code may hard-depend on either store. The eventual integration goes
  through the PAL vector-DB interface (per spec), which is itself
  intentionally not implemented yet (ADR-0001 rule: no speculative
  infrastructure).
- The roadmap's fallback F-1 (pgvector) remains valid regardless of the
  winner.

## Consequences

- Prevents a coin-flip choice from becoming load-bearing.
- Creates a hard deadline: if evidence is not ready by W4's end, the team
  must either extend the deferral explicitly (update this ADR) or choose with
  partial evidence and record the risk.

## Alternatives considered

- **Adopt ChromaDB now** (spec default; embedded; simplest local story) —
  plausible but premature: the spec's local-first framing predates the
  roadmap's Qdrant alignment, and filtering/persistence evidence is missing.
- **Adopt Qdrant now** (roadmap default) — same objection in reverse.
- **pgvector immediately** — attractive operationally (one datastore), but
  the spec's multi-store design and the roadmap's fallback ordering both
  treat it as a fallback, not a first choice; changing that ordering is
  itself a decision requiring evidence.
