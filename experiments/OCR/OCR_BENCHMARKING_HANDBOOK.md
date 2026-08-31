# OpenLearn-AI OCR Benchmark — Methodology Handbook

**Status:** Active methodology authority for `experiments/OCR/ocr-benchmark/`
**Version:** 1.0.0 · Supersedes the previous OCR benchmarking handbook
**Owner:** OpenLearn-AI graduation project

This document is the working methodology the benchmark implementation must
follow. It is operational, not theoretical. If a section doesn't change how
the developer runs the benchmark, it doesn't belong here.

---

## 1. Purpose and Scope

**Goal:** select a practical default OCR / document-understanding engine for
the OpenLearn-AI ingestion pipeline, based on evidence, not assumption.

**In scope now:**
- Screening, benchmarking, and comparing candidate engines on the datasets
  currently in `data/raw/`.
- Producing a defensible, explainable recommendation (which may be a single
  default, a default + category-specific fallback, or an explicit
  "unresolved, needs more data" verdict).

**Out of scope now** (future pipeline stages — informed by, but not built
in, this benchmark):

```
Document → Document Inspector → Native Parser / OCR / Doc-Understanding
  → Quality Gate / Routing → Unified Document Representation
  → Markdown / JSON → Embeddings / Vector / Graph / Citations / RAG
```

Do not build the quality gate, the unified schema, embeddings, or the
retrieval stack here. When evaluating a candidate, consider whether its
output format, licensing, and resource footprint are *compatible* with that
future pipeline — that's a factor in the decision, not a deliverable of
this benchmark.

**Two questions this benchmark must answer:**
1. Which candidate gives the best practical OCR / document-understanding
   result for OpenLearn-AI's current document mix?
2. Are there cases (e.g. clean born-digital PDFs) where native parsing
   (Docling) is clearly preferable to running a full OCR/VLM engine?
   Keep this lightweight — it is a routing *hint* for later, not a routing
   system to build now.

---

## 2. Current Benchmark Decisions (do not re-litigate without new evidence)

| Decision | Status |
|---|---|
| MISRAJ is the primary OCR text-accuracy benchmark | Fixed |
| BCE-Arabic-v1 contains **no transcription ground truth** — never used for CER/WER | Fixed (confirmed: 0/1996 XML files have non-empty `TextEquiv`) |
| BCE-Arabic-v1 is used for layout/region/reading-order evaluation | Fixed |
| Custom dataset requires ground-truth verification before any formal accuracy scoring | Fixed |
| OCR/engine selection happens before quality-gate / routing design | Fixed |
| Embedding selection happens after OCR/routing decisions | Fixed |
| Raw datasets are never modified in place | Fixed |
| Raw engine outputs are always preserved | Fixed |
| Engine runtime environments are isolated where practical | Fixed |
| No single arbitrary weighted score decides the winner | Fixed |

---

## 3. Dataset Roles

Every dataset has an explicit role. A dataset is **not** required to support
every evaluation dimension — forcing a dataset to answer a question its
annotations don't support produces fabricated evidence.

### 3.1 MISRAJ

| Property | Value |
|---|---|
| Location | `data/raw/misraj/data` |
| Unit | 1 row = 1 page |
| Size | 400 pages |
| Ground truth | Markdown transcription, 400/400 non-empty, 0 duplicates |
| Language mix | Arabic-dominant (mean Arabic char ratio 0.64, Latin 0.08, digits 0.02) |
| Structure annotation | Markdown only: headings, bold/italic, lists, `<page_number>` tags, a handful of tables (5 rows / 2 separators across the corpus) |
| Region/box annotation | **None** — no word/line/char coordinates |
| Reading order | Implicit (markdown document order only) |

**Role:** primary answer to *"how accurately does the engine reproduce
text?"* Page-level CER/WER. **Must not** be used for layout/region scoring —
it has no coordinates to score against.

### 3.2 BCE-Arabic-v1

| Property | Value |
|---|---|
| Location | `data/raw/bce-arabic-v1` |
| Unit | 1 PAGE-XML file = 1 page |
| Size | 1996 XML files across 8 categories (Charts, Headers, graphics, multi-columns, tables, text and images, textonly, titles) |
| Transcription ground truth | **None** — 0/1996 files contain non-empty `TextEquiv`/Unicode text |
| Region annotation | Rich: 13,184 TextRegion, 559 ImageRegion, 133 ChartRegion, 30 TableRegion, plus Noise/Graphic/Maths/LineDrawing regions, all with `<Coords>` |
| Reading order | Explicit `<ReadingOrder>` in 1945/1996 files |
| Language / direction metadata | `primaryLanguage`: Arabic 1988, English 25, Amharic 2. `readingDirection`: RTL 1974, LTR 6, top-to-bottom 3 |
| Known defect | 433/1996 XML files reference an image file that could not be matched on disk (likely `.tif`→`.jpg` conversion gaps) — **must be resolved before any image-based BCE evaluation run** |

**Role:** answers *"how well does the engine handle layout/structure/reading
order?"* — region-level, qualitative-guided or coordinate-based layout
comparison. **Must not** be used to compute CER/WER; there is no
transcription to compare against, full stop.

### 3.3 Custom (OpenLearn-specific difficult cases)

| Property | Value |
|---|---|
| Config | `configs/datasets/custom_v1.yaml`, version `0.2.0`, status `active` |
| Split | Single `pilot` split — **evaluation-only**, must never be used to tune an engine |
| Raw samples | 85 physical files across 9 category folders (each file = exactly one benchmark sample) |
| Canonical identity | raw filename stem == GT filename stem == metadata key == manifest `sample_id` (exact, case-sensitive; enforced by builder/auditor) |
| Categories | Multi-label taxonomy: english/arabic_born_digital, english/arabic_scanned, arabic_english_mixed, multi_column, tables, formulas, figures_diagrams, slides, dense_academic, noisy_low_quality |
| Mixed Arabic/English | **Included** — first-class benchmark samples, never excluded |
| Document-level exception | `custom_multi_column_004.pdf` is intentionally one document-level sample (`page: null`) |
| Ground truth | 85 flat `<sample_id>.txt` files (UTF-8); convention documented in `docs/annotation-guidelines.md` §1 |
| GT status | **`verified` for all 85 samples** — manually reviewed, content accepted as correct; 0 missing / 0 orphan / 0 empty |
| Known limitation | Provenance coverage is incomplete (~4/85 historical records); UNKNOWN-provenance material is internal-research-only (see `docs/provenance.md`) |

**Role:** answers *"how does the engine behave on
OpenLearn-AI's own hard cases?"* — targeted robustness testing across
category types the general datasets don't cover (formulas, slides, mixed
Arabic/English, noisy scans).

**Current reality:** all 85 Custom samples have verified ground-truth text
(`ground_truth.status: verified`). Per §4, this makes them *eligible* for
formal CER/WER scoring. One additional policy gate remains before the first
formal Custom run: a one-time **content-convention validation** confirming
the verified GT complies with the annotation guidelines' scoring conventions
(§6.2 normalization compatibility, reading-order sanity on multi-column
pages). This is a methodology check performed once over the dataset — it does
not demote any sample's `verified` status, and until it runs, Custom results
should be labeled accordingly.

### 3.4 Dataset role summary

| Dataset | OCR text accuracy (CER/WER) | Layout/region eval | Qualitative robustness |
|---|---|---|---|
| MISRAJ | ✅ primary | ❌ no coordinates | — |
| BCE-Arabic-v1 | ❌ no transcription — forbidden | ✅ primary | — |
| Custom | ⚠️ GT verified (85/85); formal scoring gated on one-time content-convention validation (§3.3) | ⚠️ features flags only, no coords | ✅ |

Adding a new dataset later: document its role using this same table
structure (unit, size, GT type, what it can/can't validly evaluate) before
it's wired into the runner. Do not assume a new dataset is multi-purpose by
default.

---

## 4. Ground-Truth Policy

- **MUST NOT** treat any OCR engine's own output as ground truth, ever —
  including as a stand-in for missing custom-dataset labels.
- **MUST NOT** treat unverified PDF text-layer extraction as ground truth.
  If used at all, it is a labeled `extracted_unverified` **baseline**, kept
  visibly separate from verified results in every report (different
  section, different symbol, never averaged into the same number).
- **MUST** record, per sample: ground-truth source (manual / pdftotext
  extraction / dataset-provided), verification status, and verifier
  (if manual).
- **MUST NOT** fabricate or estimate ground truth to fill coverage gaps.
  A missing-GT sample is excluded from formal scoring and reported as
  excluded, not silently dropped.
- Custom dataset: a sample only counts toward formal (CER/WER) scoring once
  its `ground_truth_status` is `verified`. All 85 Custom samples are now
  `verified`; the remaining eligibility gate is the dataset-level
  content-convention validation described in §3.3.

---

## 5. Evaluation Methodology — Category Separation

Keep these four categories strictly separate in code, in results files, and
in the final report. Never blend numbers across them.

| Category | Question it answers | Requires |
|---|---|---|
| **A. Engine screening** | Is this engine worth full benchmark effort? | Install + tiny smoke set |
| **B. Formal benchmark** | How accurate/robust is it, quantitatively? | Valid ground truth (MISRAJ, BCE-layout, verified custom) |
| **C. Qualitative evaluation** | How good is structure/tables/formulas/reading order where no numeric GT exists? | Controlled human review protocol (§9) |
| **D. Operational evaluation** | Is it practical to run/maintain? | Timing, resource, failure-rate, license data |

---

## 6. Metrics

Keep the metric set small and each metric traceable to a decision it
informs.

### 6.1 Core text-accuracy metrics (MISRAJ only)

- **CER** (character error rate) — primary metric.
- **WER** (word error rate) — secondary, reported alongside CER.
- Both computed **raw** (no normalization) and **normalized** (§6.2).
  Report both; the raw score is the ground truth of engine behavior, the
  normalized score is the ground truth of "engine behavior we actually
  care about."

No BLEU, ROUGE, embedding-similarity, or LLM-judge text-accuracy metrics
unless a specific, named benchmark question later requires one. None do
today.

### 6.2 Text Normalization Policy (explicit — do not silently normalize)

Normalization is applied identically to hypothesis and reference before
computing the *normalized* score. The *raw* score is always computed first,
unmodified.

| Transformation | Applied in normalized score? | Rationale |
|---|---|---|
| Unicode NFC normalization | ✅ Yes | Different engines may emit NFC/NFD forms of the same glyph; this is not an OCR error. |
| Leading/trailing whitespace, whitespace run collapsing | ✅ Yes | Layout-driven whitespace differences aren't transcription errors. |
| Arabic diacritics (tashkeel) | ✅ Yes, stripped | MISRAJ ground truth is not consistently diacritized; scoring diacritics would measure GT inconsistency, not OCR quality. **Flag if this changes** — if a future dataset has verified diacritic-complete GT, diacritics must be scored, not stripped. |
| Arabic character variant folding (e.g. ألإآ → ا, ة↔ه *is NOT folded*) | ⚠️ Partial — only alef-hamza forms folded to bare alef; teh marbuta/heh are kept distinct | These are the standard, defensible Arabic OCR-normalization folds; teh marbuta vs heh is a real spelling distinction and folding it would hide genuine errors. |
| Punctuation | ❌ Not stripped | Punctuation errors are real transcription errors in educational documents (list markers, decimal points). |
| Digits (Arabic-Indic ٠-٩ vs Western 0-9) | ❌ Not folded | A digit-form mismatch is a real OCR/rendering difference worth measuring, not noise. |
| Markdown syntax (`**bold**`, `#`, `<page_number>` tags, etc.) | ✅ Stripped to plain text before scoring | CER/WER measure text transcription, not markdown-emission fidelity. Markdown/structure fidelity is scored separately, qualitatively (§9), not folded into CER. |
| Case folding (Latin) | ✅ Yes | Case is rarely meaningful in this document set and varies by renderer. |

Any normalization not listed here is **not applied** by default. Adding one
requires updating this table with a rationale.

### 6.3 Aggregation

- **Primary reported number:** micro-averaged CER/WER across all
  reference characters/words in the evaluated subset (i.e. pooled
  edit-distance / pooled reference length), not a mean of per-page scores.
  Micro-averaging avoids letting many short pages dominate the score.
- **Secondary:** macro-average (mean of per-page CER/WER) reported
  alongside, to expose whether a few long/short pages are skewing the
  micro result.
- **Empty reference pages:** excluded from CER/WER (undefined denominator),
  counted and reported separately as "N pages excluded (empty reference)."
- **Failed OCR runs** (engine crash, timeout, empty output on a non-empty
  reference): **do not exclude.** Score as CER = 1.0 / WER = 1.0 for that
  page (worst-case), and separately report the raw failure count/rate.
  Silently excluding failures rewards fragility.

---

## 7. Engine Screening (Category A)

Purpose: cheaply eliminate engines not worth a full benchmark run.

**Checklist per candidate:**

- [ ] Installs in an isolated environment without unresolved dependency conflicts
- [ ] License permits our evaluation use (record license name + link — see §11)
- [ ] Model weights/API are actually obtainable (not gated/waitlisted indefinitely)
- [ ] Declared/tested language support includes Arabic and English
- [ ] Smoke test: processes 1 simple English page without crashing
- [ ] Smoke test: processes 1 simple Arabic page without crashing
- [ ] Smoke test: processes 1 mixed Arabic/English page without crashing
- [ ] Output is parseable into plain text (markdown/JSON/etc. — record format)

**Screening is a pass/fail gate, not a scored dimension.** A slower or
currently-lower-capability engine is **not** eliminated here — screening
only removes engines that are unusable (won't install, no Arabic support,
crashes on smoke tests, unusable license). Accuracy/speed trade-offs are
resolved in §13, with evidence, not by screening them out early.

Record screening results in `results/screening/<engine>.md` — pass/fail per
checklist item, plus raw stdout/stderr on failure.

---

## 8. Formal Benchmark (Category B)

### 8.1 Fair-comparison rules

**Must be identical across all engines:**
- Input images (same files, same resolution/format as delivered by the dataset)
- Dataset subset/split evaluated
- Common preprocessing (§8.3, tier 1)
- Hardware (same machine/GPU for a given comparison run — cross-hardware
  runs are not comparable and must be labeled separately)
- Timing methodology: wall-clock per page, first request excluded if the
  engine has a documented model-load/warm-up cost (load time reported
  separately, not folded into per-page timing)
- Retry policy: 1 automatic retry on transient error (timeout, OOM); a
  second failure counts as a failure, not a retry

**Legitimately engine-specific (record, don't force uniform):**
- Batch size (use each engine's recommended/stable batch size)
- Internal model configuration (e.g. detection thresholds) — use documented
  defaults unless a specific config is required to run at all
- Output format before parsing to plain text

**External/API engines:** if any candidate is API-based rather than local,
record network dependency explicitly as a factor in §11 (offline operation
requirement) and in timing (network latency is not comparable to local
inference latency — report separately, don't merge into the same "speed"
number as local engines).

### 8.2 MISRAJ run (text accuracy)

- Evaluate all 400 pages unless an engine's failure rate makes a smaller
  documented subset necessary (record why).
- Compute CER/WER per §6, both raw and normalized, both micro and macro.
- Report per-page results in a raw output file, not just the aggregate.

### 8.3 BCE-Arabic-v1 run (layout/structure)

Formal, coordinate-based scoring only where BCE's annotation genuinely
supports it:
- **Region-count / region-type agreement:** does the engine's output
  identify a comparable number/type of regions (text vs. table vs. image
  vs. chart) per page, compared to BCE's `region_types`?
- **Reading-order agreement:** for the 1945 files with explicit
  `<ReadingOrder>`, compare the engine's emitted paragraph/block order
  against BCE's order (e.g. Kendall-tau or simple sequence agreement on
  matched regions).
- Skip the 433 pages with unmatched image references until that data
  hygiene issue is resolved (§3.2) — do not silently substitute a
  different image.

This does **not** attempt word/line-box IoU scoring — BCE has no
transcription, so text-region content can't be verified, only region
presence/type/order.

### 8.4 Custom dataset run

Blocked until §3.3 reconciliation is complete. Once ≥1 sample has verified
GT, formal scoring uses the same CER/WER methodology as §8.2, reported
**per category** (formulas, tables, mixed-language, etc.), not pooled with
MISRAJ — the sample sizes and difficulty are not comparable, and pooling
would mislabel a hard-case failure as a general-accuracy failure or vice
versa.

### 8.5 Preprocessing tiers

1. **Common (applied to all engines):** none beyond what the dataset
   already provides, unless a specific transform is required for *every*
   engine to run at all (e.g. converting an unsupported image mode).
   Document any tier-1 transform here explicitly if one is added.
2. **Engine-required:** transforms an engine's own documentation mandates
   (e.g. a specific max input resolution). Record per engine.
3. **Engine-specific optimization:** anything beyond what's required to
   run (e.g. denoising a scan to improve accuracy). **Allowed only if
   documented** in the engine's results file, so evaluators can see it was
   applied and to whom.

---

## 9. Qualitative Evaluation (Category C)

Used where MISRAJ/BCE/custom don't provide numeric ground truth for a
dimension: tables, formulas, figures/diagrams, Markdown/structure quality,
reading order on non-BCE pages.

**Protocol (controlled, not ad hoc):**
1. Fixed sample set per dimension (e.g. 15 pages containing tables, drawn
   from custom + BCE `tables` category), same pages for every engine.
2. Single rubric per dimension, defined in advance (example — tables):
   - 0: table not detected / output unusable
   - 1: detected but structure (rows/cols) wrong
   - 2: structure mostly correct, some cell content errors
   - 3: structurally and substantively correct
3. Rated blind to engine identity where feasible (shuffle/anonymize output
   files before review).
4. Record rater, date, rubric version alongside scores.
5. Report as a distribution (counts per rubric level) per engine, not a
   single averaged "quality score" — a mean hides whether an engine is
   consistently mediocre vs. bimodal (great or broken).

Do not convert every qualitative dimension into a single number "to make
it comparable" — a documented strengths/weaknesses table (§13) is the
correct output, not a synthetic composite score.

---

## 10. Performance / Operational Measurement (Category D)

Minimum recorded per engine, per run:

| Metric | Notes |
|---|---|
| Processing time (s/page, mean + p95) | Warm state only; load/warm-up time reported separately |
| Peak VRAM | If GPU-based |
| Peak RAM | If CPU-based or in addition to VRAM |
| Failure rate | % pages that crashed/timed out/returned empty on non-empty input |
| Failure modes | Short free-text categorization (OOM, timeout, malformed input, unknown) |

No distributed/multi-node benchmarking infrastructure. Single-machine,
sequential-per-engine runs are sufficient at this project's scale.

---

## 11. Licensing / Practical Viability

Record per engine (not a scored metric — a gating/context factor):

- License name + link (model weights and code license, if different)
- Commercial-use restriction, if any
- Redistribution restriction, if any
- Offline/local operation possible? (relevant given §8.1 network-dependency note)
- Model availability (open weights vs. gated vs. API-only)
- Maintenance signal (last release date, open issue activity) — record
  the observation, not a legal judgment
- Dependency burden (rough: light / moderate / heavy, with what it pulls in)

This handbook does not give legal advice. **If a license's terms are
ambiguous for OpenLearn-AI's intended use, flag it explicitly for human
legal review before that engine is recommended as default** — do not
resolve ambiguity by assumption.

---

## 12. Results & Reproducibility

**Every benchmark run records:**

```
engine, model, version, configuration
dataset, dataset version, sample count evaluated, samples excluded (+why)
hardware, software environment (OS, driver/CUDA version, key package versions)
preprocessing applied (tier 1/2/3, per §8.5)
metrics (raw + normalized CER/WER, or qualitative rubric scores, as applicable)
runtime (per-page timing, resource usage)
failures (count, rate, modes)
date
notes
```

**File layout (flat, no database):**

```
results/
  screening/<engine>.md
  formal/<dataset>/<engine>/
    config.yaml          # exact run configuration
    raw_outputs/          # engine output per page, untouched
    metrics.json          # computed CER/WER/layout scores
    run_log.md            # timing, failures, environment
  qualitative/<dimension>/<engine>/
    ratings.csv
    rubric_v<N>.md
  report.md                # the synthesized comparison + recommendation
```

Raw outputs are never overwritten by a re-run — write to a new
timestamped/version-suffixed directory and update `metrics.json`'s pointer,
so a previous result remains inspectable.

---

## 13. Decision / Winner Criteria

No fixed-weight composite score (e.g. "CER 40% + speed 20% + ..."). Use this
sequence instead:

1. **Hard blockers first.** Eliminate any engine that: fails screening
   (§7), has a license incompatible with OpenLearn-AI's use, or has a
   failure rate high enough to be operationally unusable (document the
   threshold used and why, per run — don't pick one after seeing results).
2. **Primary evidence.** For remaining engines, compare MISRAJ CER/WER
   (normalized, micro-averaged) as the primary text-accuracy signal.
3. **Secondary evidence.** BCE layout/reading-order agreement, qualitative
   ratings (tables/formulas/figures), and operational metrics (§10) are
   compared as a documented table — strengths and weaknesses in plain
   language, per engine.
4. **Trade-off resolution.** Where no engine dominates on all axes, state
   the trade-off explicitly (e.g. "Engine X: best Arabic CER, 3x slower and
   needs 2x VRAM vs Engine Y"). The final call weighs this against
   OpenLearn-AI's actual deployment constraints (documented separately, not
   invented here) — not an arbitrary formula.
5. **Outcome types**, any of which is a valid, complete result:
   - Single default engine
   - Default + named fallback for a specific category (e.g. "Engine X
     default; Engine Z for formula-heavy pages")
   - One or more engines explicitly rejected, with reasons
   - Unresolved: evidence insufficient, more testing specified and scoped

Do not force a single universal winner if the evidence doesn't support one.

---

## 14. Stopping Criteria

Benchmark this deep, and no deeper, for a v1 decision:

- **Minimum evidence to decide:** all screening-passing engines have a
  completed MISRAJ formal run, a completed BCE layout run, and at least
  the qualitative table/formula/figure ratings (§9) — even if custom-set
  quantitative data isn't ready yet (§3.3).
- **Additional testing is justified** only when: two top candidates are
  within noise of each other on primary evidence (§13.2) and a specific,
  named additional test would separate them — not open-ended "let's test
  more."
- **Results are stable enough** when re-running the same engine/config on
  the same subset changes CER by less than ~1 absolute point (record actual
  observed variance, don't assume this number).
- **Retest triggers:** engine/model version change, dataset version change,
  preprocessing policy change, or hardware change. Any of these
  invalidates a prior result for comparison purposes (it can still be kept
  for historical record, clearly labeled with the old config).

---

## 15. Change Log

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-08-22 | Initial handbook, replacing prior OCR benchmarking handbook. Based on confirmed dataset-inspection evidence (`dataset_inspection.json`, generated 2026-08-22): MISRAJ 400/400 usable pages; BCE 1996 XML files, 0 with transcription, 433 with unmatched image refs; Custom 3 manifest samples, 0 with any ground truth today, 19 orphan GT dirs, 3 manifest/filesystem mismatches. |
| 1.1.0 | Phase 3 | §3.3 reconciled with the current Custom dataset: 85 raw samples / 85 verified GT files under the canonical identity contract (raw stem == GT stem == metadata key == manifest ID); flat `<sample_id>.txt` GT convention (annotation-guidelines v0.2); mixed-language samples included; `custom_multi_column_004.pdf` document-level. Formal Custom CER/WER scoring additionally gated on a one-time content-convention validation (§3.3). Historical reports in `reports/` are superseded evidence for the Custom section. |

---

## Open Methodology Questions

Only genuinely unresolved decisions — not implementation detail.

1. **Custom-dataset scoring timeline.** Custom GT is now complete and
   verified (85/85, §3.3). Decide whether the formal Custom CER/WER run
   (after the one-time content-convention validation) happens inside v1 or
   in a v1.1 pass. This changes what "enough evidence" (§14) means for v1.
2. **BCE unmatched-image resolution.** 433/1996 BCE pages can't be matched
   to an image file. Is this fixable (re-run a `.tif`→`.jpg` conversion,
   locate a missing archive) or is that subset permanently excluded from
   layout evaluation? Affects the usable BCE sample size.
3. **Failure-rate hard-blocker threshold (§13.1).** No threshold is fixed
   yet for "operationally unusable." Needs a number (e.g. >10% page
   failure rate) agreed before the first formal run, so it isn't chosen
   after seeing which engines it would eliminate.
4. **Deployment constraints for trade-off resolution (§13.4).** The
   handbook references "OpenLearn-AI's actual deployment constraints" (GPU
   budget, latency requirement, offline requirement) as an input to the
   final decision — these constraints aren't documented anywhere in the
   current materials and need to be captured before Step 4 of §13 can run.
5. **BCE layout-agreement metric choice (§8.3).** A specific metric
   (region-count/type agreement, reading-order agreement method) is
   proposed but not yet validated against a pilot run. May need adjustment
   once real engine output is seen.
