# Ground-Truth Annotation Guidelines — DRAFT v0.1

> **Status: DRAFT — requires team review before any page is transcribed.**
> These conventions define what "correct" means for every transcription in
> `data/ground_truth/`. They also fix the normalization contract that the
> metrics module (`ocrbench.core`) will implement — changing a rule here
> retroactively affects every published score, so changes require a changelog
> entry (see §9).
>
> Influences: OCR Benchmarking Handbook Phase 1/4 (Arabic diacritics policy,
> raw vs. normalized CER); common Arabic OCR evaluation practice (e.g.,
> KITAB-Bench normalization conventions — cite the exact version adopted when
> metrics are implemented).

## 1. Scope

One transcription **per page**, in two forms:

- `page_NNN.txt` — plain text, reading order, one paragraph per line.
- `page_NNN.md` — Markdown reflecting document structure (headings, lists,
  tables).
- `tables/page_NNN_tK.html` — additionally, for every table on the page, an
  HTML table (enables TEDS scoring later).
- `meta.json` — annotator, date, review status, conventions version, and any
  notes on ambiguous regions.

## 2. Arabic diacritics (tashkeel) — the core decision

- **Primary transcription (`page_NNN.txt`) preserves diacritics exactly as
  printed.** Do not add, remove, or "correct" them.
- Metrics will always report **raw CER (diacritics as-is)** and **normalized
  CER (diacritics stripped)** side by side — the gap between them is itself a
  reported result (handbook Phase 1). Never report only one.
- Rationale: stripping at transcription time destroys the ability to measure
  how engines handle diacritics — an explicit OpenLearn requirement.

## 3. Arabic character normalization (metrics-time, not transcription-time)

Normalization is applied by the metrics code to **both** prediction and ground
truth, never baked into transcriptions:

| Rule | Rationale |
|---|---|
| Strip diacritics (`U+064B–U+0652`, `U+0670`) | Optional in most texts; engines differ |
| Remove tatweel (`ـ`, `U+0640`) | Purely visual elongation |
| Unify alef variants: `أ` `إ` `آ` → `ا` | Common engine/GT convention mismatch |
| `ى` → `ي` (final alef maqsura) | Frequent confusion; standard in Arabic IR normalization |
| `ة` → `ه` **NOT applied** | Changes meaning (قطة/قطه); rejected |
| Unicode RLE/RLM marks stripped | Layout control, not content |
| NFC normalization | Deterministic byte stability |

Every rule must have this table's rationale; adding a rule requires updating
this table + tests. Rules still under debate (team review): `ٱ` (alef wasla),
`ؤ`/`ئ` handling, digit forms (Arabic-Indic ٠-٩ vs 0-9) — decide before
metrics implementation lands.

## 4. Punctuation & symbols

- Transcribe punctuation as printed, Latin or Arabic forms as they appear.
- Normalize at metrics time: ASCII/Arabic comma and question mark equivalence
  (`،`↔`,`, `؟`↔`?`) — documented in the same table as §3 when adopted.

## 5. English spans inside Arabic text (mixed documents)

- Transcribe exactly as printed, in logical order (RTL base direction,
  embedded LTR runs). **Never visually reorder** — logical order is what
  Unicode-correct engines should emit.
- The manifest's `tricky_regions` should flag pages with mixed spans; CER is
  additionally reported per-script segment when metrics support it.

## 6. Formulas, figures, tables

- **Formulas:** transcribe as LaTeX inside `$...$` (best-effort for simple
  math; a formula-specific metric is out of scope for the pilot — formulas
  are tagged, not scored, until TEDS-style structure metrics land).
- **Figures/diagrams:** represent as `![figure](figure_NN)` placeholder; any
  text *inside* a figure (axis labels, callouts) is transcribed inside the
  placeholder block — engines that hallucinate text into figure regions get
  penalized by CER, which is the point.
- **Tables:** Markdown table in `page_NNN.md` AND HTML in
  `tables/page_NNN_tK.html` (HTML is the TEDS reference). Cell text uses the
  same language conventions as body text.

## 7. Reading order

- Transcribe in the document's **logical reading order**: for Arabic pages,
  right column before left; for two-column academic layouts, full column then
  next. Headers/footers (page numbers, running titles) go at the end of the
  `.txt`, marked `%%header%%` / `%%footer%%` — excluded from CER, kept for
  reading-order evaluation later.

## 8. Quality control

- Pilot pages get a **second pass by a different annotator**; disagreements
  are resolved by discussion and the resolution recorded in `meta.json`.
- Illegible characters: `□` (U+25A1) with a note in `meta.json`. A page with
  > 5% illegible characters is excluded and flagged in the manifest
  (`scan_quality` → `low`), not silently transcribed.

## 9. Versioning

- `data/ground_truth/CHANGELOG.md` records every transcription and every
  correction (date, doc_id, page, what changed, why).
- Convention changes bump the version in this file's header and invalidate
  affected published metrics (re-run required).

## 10. Anti-circularity rule (hard constraint)

Ground truth is **never** derived from the output of an engine under
evaluation — including PaddleOCR, which has already been run on two of these
documents in the exploratory notebook. Annotators work from the page image
only.
